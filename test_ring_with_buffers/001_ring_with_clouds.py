import sys, os
BIN=os.path.expanduser('../../')
sys.path.append(BIN)
BIN=os.path.expanduser('../')
sys.path.append(BIN)

sys.path.append(BIN)

import numpy as np
import time
from scipy.constants import c,e
from mpi4py import MPI
comm = MPI.COMM_WORLD

import communication_helpers as ch

macroparticlenumber_track = 50000
N_turns = 2

epsn_x  = 2.5e-6
epsn_y  = 3.5e-6
sigma_z = 0.05

intensity = 1e11

n_slices = 150
z_cut = 2.5e-9*c


# config e-cloud
chamb_type = 'polyg'
x_aper = 2.300000e-02
y_aper = 1.800000e-02
filename_chm = '../pyecloud_config/LHC_chm_ver.mat'
B_multip_per_eV = [1.190000e-12]
B_multip_per_eV = np.array(B_multip_per_eV)

fraction_device = 0.65
intensity = 1.150000e+11
epsn_x = 2.5e-6
epsn_y = 2.5e-6
init_unif_edens_flag = 1
init_unif_edens = 9.000000e+11
N_MP_ele_init = 100000
N_mp_max = N_MP_ele_init*4.
Dh_sc = .2e-3
nel_mp_ref_0 = init_unif_edens*4*x_aper*y_aper/N_MP_ele_init

n_segments = 70


# get info on the grid
N_nodes = comm.Get_size()
N_wkrs = N_nodes-1
master_id = N_nodes-1
myid = comm.Get_rank()
I_am_a_worker = myid!=master_id
I_am_the_master = not(I_am_a_worker)

# allocate buffers for communation
N_buffer_float_size = 1000000
buf_float = np.array(N_buffer_float_size*[0.])
N_buffer_int_size = 100
buf_int = np.array(N_buffer_int_size*[0])

print 'I am %d of %d'%(myid, N_nodes)	
	
from LHC import LHC
machine = LHC(machine_configuration='Injection', n_segments=n_segments, 
				RF_at='end_of_transverse')

# We suppose that all the object that cannot be slice parallelized are at the end of the ring
i_end_parallel = len(machine.one_turn_map)-1 #only RF is not parallelizable

N_elements_per_worker = int(np.floor(float(i_end_parallel)/N_wkrs))
print 'N_elements_per_worker', N_elements_per_worker

comm.Barrier() # only for stdoutp

# split the machine
if I_am_a_worker:
	mypart = machine.one_turn_map[N_elements_per_worker*myid:N_elements_per_worker*(myid+1)]
	print 'I am id=%d and my part is %d long'%(myid, len(mypart))
else: 	
	mypart = machine.one_turn_map[N_elements_per_worker*(N_wkrs):i_end_parallel]
	non_parallel_part = machine.one_turn_map[i_end_parallel:]
	print 'I am id=%d (master) and my part is %d long'%(myid, len(mypart))
	
# initialization bunch
if I_am_the_master:
	bunch   = machine.generate_6D_Gaussian_bunch_matched(
		macroparticlenumber_track, intensity, epsn_x, epsn_y, sigma_z=sigma_z)
	print 'Bunch initialized.'
	
# initial slicing
if I_am_the_master:
	from PyHEADTAIL.particles.slicing import UniformBinSlicer
	slicer = UniformBinSlicer(n_slices = n_slices, z_cuts=(-z_cut, z_cut))
	slice_obj_list = bunch.extract_slices(slicer)
	print 'Bunch sliced.'
	

# install e-cloud(s)
if I_am_a_worker or I_am_the_master:
	import PyECLOUD.PyEC4PyHT as PyEC4PyHT
	my_new_part = []
	my_list_eclouds = []
	for ele in mypart:
		my_new_part.append(ele)
		if ele in machine.transverse_map:
			ecloud_new = PyEC4PyHT.Ecloud(L_ecloud=machine.circumference/n_segments, slicer=None , 
				Dt_ref=10e-12, pyecl_input_folder='../pyecloud_config',
				chamb_type = chamb_type,
				x_aper=x_aper, y_aper=y_aper,
				filename_chm=filename_chm, Dh_sc=Dh_sc,
				init_unif_edens_flag=init_unif_edens_flag,
				init_unif_edens=init_unif_edens, 
				N_mp_max=N_mp_max,
				nel_mp_ref_0=nel_mp_ref_0,
				B_multip=B_multip_per_eV*machine.p0/e*c,
				slice_by_slice_mode=True)
			my_new_part.append(ecloud_new)
			my_list_eclouds.append(ecloud_new)
	mypart = my_new_part

comm.Barrier() # only for stdoutp

# simulation
if I_am_the_master:
	
	pieces_to_be_treated = slice_obj_list
	
	N_pieces = len(pieces_to_be_treated)
	pieces_treated = []
	i_turn = 0
	piece_to_send = None
	
	print 'Sim. start'
	
	t_last_turn = time.mktime(time.localtime()) 	
	
	while True:	
		orders_from_master = []
				
		try:
			piece_to_send = pieces_to_be_treated.pop() 	#pop starts for the last slices 
														#(it is what we want, for the HEADTAIL 
														#slice order convention, z = -beta*c*t)
		except IndexError:
			piece_to_send = None
		
		sendbuf = ch.beam_2_buffer(piece_to_send)	
		comm.Sendrecv(sendbuf, dest=0, sendtag=0, 
		 recvbuf=buf_float, source=master_id-1, recvtag=myid)
		piece_received = ch.buffer_2_beam(buf_float)

		
		if piece_received is not None:
			for ele in mypart: 
				ele.track(piece_received)
			pieces_treated.append(piece_received)
		
		
		if len(pieces_treated)==N_pieces: # the full list has gone through the ring
			pieces_treated = pieces_treated[::-1] #restore the HEADTAIL order
			
			# re-merge bunch
			bunch = sum(pieces_treated)
			
			# finalize present turn (with non parallel part)
			for ele in non_parallel_part:
				ele.track(bunch)
			
			# prepare next turn
			pieces_to_be_treated = bunch.extract_slices(slicer)
			pieces_treated = []		
			
			t_now = time.mktime(time.localtime())
			print 'Turn %d, %d s'%(i_turn,t_now-t_last_turn) 
			t_last_turn = t_now
												
			i_turn+=1
			# check if stop is needed
			orders_from_master.append('reset_clouds')
			if i_turn == N_turns: orders_from_master.append('stop')
			
		
		buforders = ch.list_of_strings_2_buffer(orders_from_master)
		comm.Bcast(buforders, master_id)
		
		
		if 'reset_clouds' in orders_from_master:
			for ec in my_list_eclouds: ec.finalize_and_reinitialize()
		
		if 'stop' in orders_from_master:
			break

else: # workers
	
	# initialization 
	piece_to_send = None
	
	while True:
			
		if myid==0:
			left = master_id
		else:
			left = myid-1
		
		right = myid+1
		
		sendbuf = ch.beam_2_buffer(piece_to_send)	
		comm.Sendrecv(sendbuf, dest=right, sendtag=right, 
		 recvbuf=buf_float, source=left, recvtag=myid)
		piece_received = ch.buffer_2_beam(buf_float)
		
				
		# if you get something do your job
		if piece_received is not None:
			for ele in mypart: 
				ele.track(piece_received)
		
		# prepare for next iteration
		piece_to_send = piece_received
		
		comm.Bcast(buf_int, master_id)
		orders_from_master = ch.buffer_2_list_of_strings(buf_int)
		
		if 'reset_clouds' in orders_from_master:
			for ec in my_list_eclouds: ec.finalize_and_reinitialize()
		
		if 'stop' in orders_from_master:
			break	
	


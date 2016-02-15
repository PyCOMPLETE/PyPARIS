import sys, os
BIN=os.path.expanduser('../')

sys.path.append(BIN)

import numpy as np
from scipy.constants import c
from mpi4py import MPI
comm = MPI.COMM_WORLD


macroparticlenumber_track = 50000
N_turns = 512*4

epsn_x  = 2.5e-6
epsn_y  = 3.5e-6
sigma_z = 0.05

intensity = 1e11

n_slices = 100
z_cut = 2.5e-9*c


# get info on the grid
N_nodes = comm.Get_size()
N_wkrs = N_nodes-1
master_id = N_nodes-1
myid = comm.Get_rank()
I_am_a_worker = myid!=master_id
I_am_the_master = not(I_am_a_worker)

		
from LHC import LHC
machine = LHC(machine_configuration='Injection', n_segments=43, D_x=10, 
				RF_at='end_of_transverse', use_cython=False)

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
	part_for_master = machine.one_turn_map[N_elements_per_worker*(N_wkrs):i_end_parallel]
	non_parallel_part = machine.one_turn_map[i_end_parallel:]
	print 'I am id=%d (master) and my part is %d long'%(myid, len(part_for_master))
	
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


# simulation
if I_am_the_master:
	
	pieces_to_be_treated = slice_obj_list
	
	N_pieces = len(pieces_to_be_treated)
	pieces_treated = []
	i_turn = 0
	piece_to_send = None	
	
	while True:	
		orders_from_master = []
				
		try:
			piece_to_send = pieces_to_be_treated.pop() 	#pop starts for the last slices 
														#(it is what we want, for the HEADTAIL 
														#slice order convention, z = -beta*c*t)
		except IndexError:
			piece_to_send = None
		
		piece_received = comm.sendrecv(sendobj=piece_to_send, dest=0, sendtag=0, 
				source=master_id-1, recvtag=myid)
		
		if piece_received is not None:
			for ele in part_for_master: 
				ele.track(piece_received)
			pieces_treated.append(piece_received)
		
		
		if len(pieces_treated)==N_pieces: # the full list has gone through the ring
			pieces_treated = pieces_treated[::-1] #restore the HEADTAIL order
			
			# finalize present turn
			#print pieces_treated
			
			# prepare next turn
			pieces_to_be_treated = pieces_treated
			pieces_treated = []			
								
			print i_turn
								
			i_turn+=1
			# check if stop is needed
			if i_turn == N_turns: orders_from_master.append('stop')
			
		
		orders_from_master = comm.bcast(orders_from_master, root=master_id)
		
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
		piece_received = comm.sendrecv(sendobj=piece_to_send, dest=right, sendtag=right, 
				source=left, recvtag=myid)
				
		# if you get something do your job
		if piece_received is not None:
			for ele in mypart: 
				ele.track(piece_received)
		
		# prepare for next iteration
		piece_to_send = piece_received
		
		
		orders_from_master = comm.bcast(None, root=master_id)
		
		if 'stop' in orders_from_master:
			break	
	
	

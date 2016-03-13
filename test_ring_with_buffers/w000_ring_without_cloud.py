import sys, os
BIN=os.path.expanduser('../../')
sys.path.append(BIN)
BIN=os.path.expanduser('../')
sys.path.append(BIN)

import numpy as np
from scipy.constants import c
from mpi4py import MPI
comm = MPI.COMM_WORLD

import communication_helpers as ch


macroparticlenumber_track = 50000
N_turns = 128

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

# allocate buffers for communation
N_buffer_float_size = 1000000
buf_float = np.array(N_buffer_float_size*[0.])
N_buffer_int_size = 100
buf_int = np.array(N_buffer_int_size*[0])

		
from LHC import LHC
machine = LHC(machine_configuration='Injection', n_segments=43, D_x=0., 
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


# initialize savings
if I_am_the_master:
	beam_x, beam_y, beam_z = [], [], []
	sx, sy, sz = [], [], []
	epsx, epsy, epsz = [], [], []

# simulation
if I_am_the_master:
	
	pieces_to_be_treated = slice_obj_list
	
	N_pieces = len(pieces_to_be_treated)
	pieces_treated = []
	i_turn = 0
	piece_to_send = None	
	
	while True:	
'		orders_from_master = []
				
'		try:
'			piece_to_send = pieces_to_be_treated.pop() 	#pop starts for the last slices 
'														#(it is what we want, for the HEADTAIL 
'														#slice order convention, z = -beta*c*t)
'		except IndexError:
'			piece_to_send = None
		
'		sendbuf = ch.beam_2_buffer(piece_to_send)	
'		comm.Sendrecv(sendbuf, dest=0, sendtag=0, 
'		 recvbuf=buf_float, source=master_id-1, recvtag=myid)
'		piece_received = ch.buffer_2_beam(buf_float)

		
		if piece_received is not None:
			for ele in part_for_master: 
				ele.track(piece_received)
			pieces_treated.append(piece_received)
		
		
		if len(pieces_treated)==N_pieces: # the full list has gone through the ring
'			pieces_treated = pieces_treated[::-1] #restore the HEADTAIL order
			
			# re-merge bunch
			bunch = sum(pieces_treated)

			# finalize present turn (with non parallel part)
			for ele in non_parallel_part:
				ele.track(bunch)
				
			# save results
			beam_x.append(bunch.mean_x())
			beam_y.append(bunch.mean_y())
			beam_z.append(bunch.mean_z())
			sx.append(bunch.sigma_x())
			sy.append(bunch.sigma_y())
			sz.append(bunch.sigma_z())
			epsx.append(bunch.epsn_x()*1e6)
			epsy.append(bunch.epsn_y()*1e6)
			epsz.append(bunch.epsn_z())
			
			# prepare next turn
			pieces_to_be_treated = bunch.extract_slices(slicer)
'			pieces_treated = []			
								
'			print i_turn
								
'			i_turn+=1
			# check if stop is needed
'			if i_turn == N_turns: orders_from_master.append('stop')
			
'		buforders = ch.list_of_strings_2_buffer(orders_from_master)
'		comm.Bcast(buforders, master_id)'
		
		if 'stop' in orders_from_master:
			break

else: # workers
	
	# initialization 
'	piece_to_send = None
	
	while True:
			
'		if myid==0:
'			left = master_id
'		else:
'			left = myid-1
		
'		right = myid+1

'		sendbuf = ch.beam_2_buffer(piece_to_send)	
'		comm.Sendrecv(sendbuf, dest=right, sendtag=right, 
'		 recvbuf=buf_float, source=left, recvtag=myid)
'		piece_received = ch.buffer_2_beam(buf_float)

		
		# if you get something do your job
		if piece_received is not None:
			for ele in mypart: 
				ele.track(piece_received)
		
'		# prepare for next iteration
'		piece_to_send = piece_received
		

'		comm.Bcast(buf_int, master_id)
		orders_from_master = ch.buffer_2_list_of_strings(buf_int)
		
		if 'stop' in orders_from_master:
			break
	
	
# output plots
if False and I_am_the_master:
	import pylab as plt
	
	plt.figure(2, figsize=(16, 8), tight_layout=True)
	plt.subplot(2,3,1)
	plt.plot(beam_x)
	plt.ylabel('x [m]');plt.xlabel('Turn')
	plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
	plt.subplot(2,3,2)
	plt.plot(beam_y)
	plt.ylabel('y [m]');plt.xlabel('Turn')
	plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
	plt.subplot(2,3,3)
	plt.plot(beam_z)
	plt.ylabel('z [m]');plt.xlabel('Turn')
	plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
	plt.subplot(2,3,4)
	plt.plot(np.fft.rfftfreq(len(beam_x), d=1.), np.abs(np.fft.rfft(beam_x)))
	plt.ylabel('Amplitude');plt.xlabel('Qx')
	plt.subplot(2,3,5)
	plt.plot(np.fft.rfftfreq(len(beam_y), d=1.), np.abs(np.fft.rfft(beam_y)))
	plt.ylabel('Amplitude');plt.xlabel('Qy')
	plt.subplot(2,3,6)
	plt.plot(np.fft.rfftfreq(len(beam_z), d=1.), np.abs(np.fft.rfft(beam_z)))
	plt.xlim(0, 0.1)
	plt.ylabel('Amplitude');plt.xlabel('Qz')
	
	fig, axes = plt.subplots(3, figsize=(16, 8), tight_layout=True)
	twax = [plt.twinx(ax) for ax in axes]
	axes[0].plot(sx)
	twax[0].plot(epsx, '-g')
	axes[0].set_xlabel('Turns')
	axes[0].set_ylabel(r'$\sigma_x$')
	twax[0].set_ylabel(r'$\varepsilon_y$')
	axes[1].plot(sy)
	twax[1].plot(epsy, '-g')
	axes[1].set_xlabel('Turns')
	axes[1].set_ylabel(r'$\sigma_x$')
	twax[1].set_ylabel(r'$\varepsilon_y$')
	axes[2].plot(sz)
	twax[2].plot(epsz, '-g')
	axes[2].set_xlabel('Turns')
	axes[2].set_ylabel(r'$\sigma_x$')
	twax[2].set_ylabel(r'$\varepsilon_y$')
	axes[0].grid()
	axes[1].grid()
	axes[2].grid()
	for ax in list(axes)+list(twax): 
		ax.ticklabel_format(useOffset=False, style='sci', scilimits=(0,0),axis='y')
	plt.show()	

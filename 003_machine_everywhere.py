import sys, os
BIN=os.path.expanduser('../')

sys.path.append(BIN)

import numpy as np
from mpi4py import MPI
comm = MPI.COMM_WORLD


macroparticlenumber_track = 50000
n_turns = 512*4

epsn_x  = 2.5e-6
epsn_y  = 3.5e-6
sigma_z = 0.05

intensity = 1e11


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
	part_for_master = machine.one_turn_map[N_elements_per_worker*(N_wkrs):]
	print 'I am id=%d (master) and my part is %d long'%(myid, len(part_for_master))
	
# initialization bunch
if I_am_the_master:
	bunch   = machine.generate_6D_Gaussian_bunch_matched(
		macroparticlenumber_track, intensity, epsn_x, epsn_y, sigma_z=sigma_z)
	print 'Bunch initialized.'
	


	

	
	
	
	

	
	
	
	

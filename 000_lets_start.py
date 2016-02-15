import sys, os
BIN=os.path.expanduser('../')

sys.path.append(BIN)

import numpy as np
from mpi4py import MPI
comm = MPI.COMM_WORLD


# get info on the grid
N_nodes = comm.Get_size()
N_wkrs = N_nodes-1
master_id = N_nodes-1
myid = comm.Get_rank()

#for ipython testing
if N_nodes==1:
	N_nodes=2
	N_wkrs = N_nodes-1
	master_id = 1
	myid = 1

# initialization to be done only by the master
if myid==master_id:
	from LHC import LHC
	machine = LHC(machine_configuration='Injection', n_segments=29, D_x=10, 
					RF_at='end_of_transverse', use_cython=False)
	# We suppose that all the object that cannot be slice parallelized are at the end of the ring
	i_end_parallel = len(machine.one_turn_map)-1 #only RF is not parallelizable
	
	N_elements_per_worker = int(np.floor(float(i_end_parallel)/N_wkrs))
	
	print 'N_elements_per_worker', N_elements_per_worker
	
	list_of_machine_parts = []
	for ii in xrange(N_wkrs):
		list_of_machine_parts.append(machine.one_turn_map[\
			N_elements_per_worker*ii:N_elements_per_worker*(ii+1)])
	
	part_for_master = list_of_machine_parts[N_elements_per_worker*(ii+1):]
			
	#scatter machine parts	
	list_of_machine_parts.append(None)
	_ = comm.scatter(sendobj=list_of_machine_parts, root=master_id)
	
	
	
	

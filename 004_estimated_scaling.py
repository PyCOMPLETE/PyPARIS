import pylab as pl
import numpy as np

N_segments = 35
i_end_parallel = N_segments

N_per_worker_list = []
N_master_list = []
N_nodes_list = range(2,N_segments+1) 
for N_nodes in N_nodes_list:
	N_per_worker = N_segments/(N_nodes-1)
	N_master = N_segments-(N_nodes-1)*N_per_worker
	
	N_per_worker_list.append(N_per_worker)
	N_master_list.append(N_master)
	
pl.figure(1)	
pl.plot(N_per_worker_list, 'b.-')
pl.plot(N_master_list, 'r.-')

N_per_worker_list = []
N_master_list = []
N_nodes_list = range(2,N_segments+1) 
for N_nodes in N_nodes_list:
	N_wkrs = N_nodes-1
	N_per_worker = int(np.ceil(float(i_end_parallel)/N_nodes))

	N_master = N_segments-(N_nodes-1)*N_per_worker
	
	N_per_worker_list.append(N_per_worker)
	N_master_list.append(N_master)
	
pl.figure(2)	
pl.plot(N_per_worker_list, 'b.-')
pl.plot(N_master_list, 'r.-')

pl.show()

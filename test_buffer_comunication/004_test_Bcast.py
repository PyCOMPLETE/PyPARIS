

import sys, os
BIN = os.path.expanduser("../")
sys.path.append(BIN)

from mpi4py import MPI
comm = MPI.COMM_WORLD


import numpy as np

myid = comm.Get_rank()

N_buffer_float_size = 1000000
buf_float = np.array(N_buffer_float_size*[0.])


# test send
if myid == 0:
	comm.Bcast(np.array([]), 0)
		
else:
	buf = np.array(4*[0])
	comm.Bcast(buf, 0)
	print 'I am %d and I received'%myid, buf
	


import sys, os
BIN = os.path.expanduser("../../")
sys.path.append(BIN)
BIN = os.path.expanduser("../")
sys.path.append(BIN)

from mpi4py import MPI
comm = MPI.COMM_WORLD

import communication_helpers as ch

import numpy as np

myid = comm.Get_rank()

# test send
if myid == 0:
    list_of_orders = ['order1', 'order2']
    buf_to_send = ch.list_of_strings_2_buffer(list_of_orders)
    comm.Send(buf_to_send, dest=1, tag=11)
elif myid == 1:
	buf = np.array(100*[0])
	comm.Recv(buf, source=0, tag=11)
	list_of_orders_received = ch.buffer_2_list_of_strings(buf)
	print 'I am 1 and I received:', repr(list_of_orders_received)
	

	


from mpi4py import MPI
comm = MPI.COMM_WORLD

import numpy as np

myid = comm.Get_rank()

if myid>1: raise ValueError('To be tested with 2 processors')


if myid == 0:
    list_of_orders = ['order1', 'order2']
    data = ''.join(map(lambda s:s+';', list_of_orders))+'\n'
    buf_to_send = np.int_(np.array(map(ord, list(data))))
    print 'buf_to_send',buf_to_send
    comm.Send(buf_to_send, dest=1, tag=11)
elif myid == 1:
	buf = np.array(100*[0])
	comm.Recv(buf, source=0, tag=11)
	str_received = ''.join(map(unichr, list(buf)))
	list_of_rders_received = map(str, str_received.split('\n')[0].split(';'))
	print 'I am 1 and I received:', repr(list_of_rders_received)
	


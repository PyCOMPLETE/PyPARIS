from mpi4py import MPI
comm = MPI.COMM_WORLD

myid = comm.Get_rank()

if myid == 0:
    data = 10#{'a': 7, 'b': 3.14}
    comm.send(data, dest=1, tag=11)
elif myid == 1:
    datarec = comm.recv(source=0, tag=11)
    print 'I am 2 and I recived:', datarec
	


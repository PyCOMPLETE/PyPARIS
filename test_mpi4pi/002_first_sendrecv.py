from mpi4py import MPI
comm = MPI.COMM_WORLD

myid = comm.Get_rank()

#Comm.sendrecv(self, sendobj=None, int dest=0, int sendtag=0, recvobj=None, int source=0, int recvtag=0, Status status=None)


if myid == 0:
    datasend1 = 10#{'a': 7, 'b': 3.14}
    datarecv1 = comm.sendrecv(sendobj=datasend1, dest=1, sendtag=11,
		source=1, recvtag=22)
    print 'I am 0 and I recived:', datarecv1
elif myid == 1:
    datasend2 = 20
    datarecv2 = comm.sendrecv(sendobj=datasend2, dest=0, sendtag=22,
		source=0, recvtag=11)
    print 'I am 1 and I recived:', datarecv2
	


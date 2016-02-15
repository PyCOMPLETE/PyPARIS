from mpi4py import MPI
comm = MPI.COMM_WORLD

N_nodes = comm.Get_size()

N_wkrs = N_nodes-1
master_id = N_nodes-1


myid = comm.Get_rank()

piece_to_send = None

if myid == master_id:
	list_of_pieces = 'a b c d e'.split()


count = 0 

for ii in xrange(15):
	if myid==master_id:			
		try:
			piece_to_send = list_of_pieces.pop()
		except IndexError:
			piece_to_send = None
		
		piece_received = comm.sendrecv(sendobj=piece_to_send, dest=0, sendtag=0, 
				source=master_id-1, recvtag=myid)
		
		print "I am", myid, 'and I received', piece_received


	else:
		
		if myid==0:
			left = master_id
		else:
			left = myid-1
		
		right = myid+1
		piece_received = comm.sendrecv(sendobj=piece_to_send, dest=right, sendtag=right, 
				source=left, recvtag=myid)
				
		# if you get something do your job
		if piece_received is not None:
			piece_received+="%d"%myid
		
		piece_to_send = piece_received
		
	comm.barrier()
		



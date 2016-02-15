from mpi4py import MPI
comm = MPI.COMM_WORLD

# get info on the grid
N_nodes = comm.Get_size()
N_wkrs = N_nodes-1
master_id = N_nodes-1
myid = comm.Get_rank()


# initialization
if myid == master_id:
	# for master
	N_turns = 5
	pieces_to_be_treated = 'a b c d e'.split()
	N_pieces = len(pieces_to_be_treated)
	print pieces_to_be_treated
	pieces_treated = []
	i_turn = 0
	piece_to_send = None
else:
 	# for slaves 
	piece_to_send = None


# simulation
while True:
	if myid==master_id:	
		
		orders_from_master = None
				
		try:
			piece_to_send = pieces_to_be_treated.pop()
		except IndexError:
			piece_to_send = None
		
		piece_received = comm.sendrecv(sendobj=piece_to_send, dest=0, sendtag=0, 
				source=master_id-1, recvtag=myid)
		
		if piece_received is not None:
			pieces_treated.append(piece_received)
		
		#print "I am", myid, 'and I received', piece_received
		
		if len(pieces_treated)==N_pieces:
			pieces_treated = pieces_treated[::-1]
			print pieces_treated
			pieces_to_be_treated = pieces_treated
			pieces_treated = []			
			i_turn+=1
			if i_turn == N_turns: orders_from_master = 'stop'
		
		orders_from_master = comm.bcast(orders_from_master, root=master_id)
		
		if orders_from_master=='stop':
			break
		
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
		
		# prepare for next iteration
		piece_to_send = piece_received
		
		
		orders_from_master = comm.bcast(None, root=master_id)
		
		if orders_from_master=='stop':
			break



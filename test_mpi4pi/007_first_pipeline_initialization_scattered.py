from mpi4py import MPI
comm = MPI.COMM_WORLD

from numpy import mod

# get info on the grid
N_nodes = comm.Get_size()
N_wkrs = N_nodes-1
master_id = N_nodes-1
myid = comm.Get_rank()


#master
if myid==master_id:
	
	# initialization
	N_turns = 5
	pieces_to_be_treated = 'A B C D E'.split()
	N_pieces = len(pieces_to_be_treated)
	print pieces_to_be_treated
	pieces_treated = []
	i_turn = 0
	piece_to_send = None	
	
	#scatter initialization info
	letters_to_add = 'g i a n n i'.split()
	letters_to_add.append(None)
	letters_to_add = letters_to_add[:N_nodes]
	_ = comm.scatter(sendobj=letters_to_add, root=master_id)
	

	# simulation
	while True:	
		orders_from_master = []
				
		try:
			piece_to_send = pieces_to_be_treated.pop() 	#pop starts for the last slices 
														#(it is what we want, for the HEADTAIL 
														#slice order convention, z = -beta*c*t)
		except IndexError:
			piece_to_send = None
		
		piece_received = comm.sendrecv(sendobj=piece_to_send, dest=0, sendtag=0, 
				source=master_id-1, recvtag=myid)
		
		if piece_received is not None:
			pieces_treated.append(piece_received)
		
		
		if len(pieces_treated)==N_pieces: # the full list has gone through the ring
			pieces_treated = pieces_treated[::-1] #restore the HEADTAIL order
			
			# finalize present turn
			print pieces_treated
			
			
			# prepare next turn
			pieces_to_be_treated = pieces_treated
			pieces_treated = []			
			
			
			# send a command once per turn (e.g. reset clouds)
			if mod(i_turn, 3)==0:
				orders_from_master.append('uppercase')
			else: 
				orders_from_master.append('lowercase')
				
				
			i_turn+=1
			# check if stop is needed
			if i_turn == N_turns: orders_from_master.append('stop')
			
		
		orders_from_master = comm.bcast(orders_from_master, root=master_id)
		
		if 'stop' in orders_from_master:
			break

# workers		
else:
	
	# initialization 
	piece_to_send = None
	
	#scatter initialization info
	myletter = comm.scatter(sendobj=None, root=master_id)
	print "I am", myid, 'and I received', myletter
	
	while True:
			
		if myid==0:
			left = master_id
		else:
			left = myid-1
		
		right = myid+1
		piece_received = comm.sendrecv(sendobj=piece_to_send, dest=right, sendtag=right, 
				source=left, recvtag=myid)
				
		# if you get something do your job
		if piece_received is not None:
			piece_received+=myletter
		
		# prepare for next iteration
		piece_to_send = piece_received
		
		
		orders_from_master = comm.bcast(None, root=master_id)
		
		if 'uppercase' in orders_from_master:
			myletter = myletter.upper()
		elif 'lowercase' in orders_from_master:
			myletter = myletter.lower()
		
		if 'stop' in orders_from_master:
			break



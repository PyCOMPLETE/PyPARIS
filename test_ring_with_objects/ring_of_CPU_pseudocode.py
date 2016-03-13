from mpi4py import MPI

import communication_helpers as ch


class RingOfCPUs(object):
	def __init__(self, sim_content):
		
		self.comm = MPI.COMM_WORLD
		
		# get info on the grid
		self.N_nodes = comm.Get_size()
		self.N_wkrs = self.N_nodes-1
		self.master_id = self.N_nodes-1
		self.myid = self.comm.Get_rank()
		self.I_am_a_worker = self.myid!=self.master_id
		self.I_am_the_master = not(self.I_am_a_worker)

		# allocate buffers for communation
		self.N_buffer_float_size = 1000000
		self.buf_float = np.array(N_buffer_float_size*[0.])
		self.N_buffer_int_size = 100
		self.buf_int = np.array(N_buffer_int_size*[0])

		self.sim_content.init_all()

		comm.Barrier() # only for stdoutp

		if self.I_am_the_master:
			self.pieces_to_be_treated = self.sim_content.init_master()
			self.N_pieces = len(pieces_to_be_treated)
			self.pieces_treated = []
			self.i_turn = 0
			self.piece_to_send = None
		elif self.I_am_a_worker:
			self.sim_content.init_worker()
			# Identify CPUs on my left and my right
			if self.myid==0:
				self.left = self.master_id
			else:
				self.left = self.myid-1
			self.right = self.myid+1

	def run(self):
		if self.I_am_the_master:
			
			while True: #(it will be stopped with a break)
				orders_from_the_master = []
				# pop a piece
				try:
					piece_to_send = pieces_to_be_treated.pop() 	#pop starts for the last slices 
																#(it is what we want, for the HEADTAIL 
																#slice order convention, z = -beta*c*t)
				except IndexError:
					piece_to_send = None

				# send it to the first element of the ring and receive from the last
				sendbuf = self.sim_content.piece_to_buffer(piece_to_send)
				if len(sendbuf)	> self.N_buffer_float_size:
					raise ValueError('Float buffer is too small!')
				self.comm.Sendrecv(sendbuf, dest=0, sendtag=0, 
							recvbuf=self.buf_float, source=self.master_id-1, recvtag=self.myid)
				piece_received = self.sim_content.buffer_to_piece(buf_float)

				# treat received piece
				if piece_received is not None:
					self.sim_content.treat_piece()
					self.pieces_treated.append(piece_received)	

				# end of turn
				if len(self.pieces_treated)==self.N_pieces:	
					print 'Turn', self.i_turn

					self.pieces_treated = self.pieces_treated[::-1] #restore the original order

					# perform global operations and reslice
					orders_to_pass, new_pieces_to_be_treated = \
						self.sim_content.finalize_turn_on_master(self.pieces_treated)
					orders_from_master += orders_to_pass

					# prepare next turn
					self.pieces_to_be_treated = new_pieces_to_be_treated
					self.N_pieces = len(self.pieces_to_be_treated)
					self.pieces_treated = []			
					self.i_turn+=1

					# check if stop is needed
					if self.i_turn == N_turns: orders_from_master.append('stop')		
								
				# send orders
				buforders = ch.list_of_strings_2_buffer(orders_from_master)
				if len(buforders) > self.N_buffer_int_size:
					raise ValueError('Int buffer is too small!')
				self.comm.Bcast(buforders, self.master_id)

				#execute orders from master (the master executes its own orders :D)
				self.sim_content.execute_orders_from_master()

				# check if simulation has to be ended
				if 'stop' in orders_from_master:
					break

			# finalize simulation (savings etc.)	
			self.sim_content.finalize_simulation()				

		elif self.I_am_a_worker:
			# initialization 
			piece_to_send = None
			
			while True:

				sendbuf = self.sim_content.piece_to_buffer(piece_to_send)
				if len(sendbuf)	> self.N_buffer_float_size:
					raise ValueError('Float buffer is too small!')
				self.comm.Sendrecv(sendbuf, dest=self.right, sendtag=self.right, 
							recvbuf=self.buf_float, source=self.left, recvtag=self.myid)
				piece_received = self.sim_content.buffer_to_piece(buf_float)

				# treat received piece
				if piece_received is not None:
					self.sim_content.treat_piece()
					self.pieces_treated.append(piece_received)

				# prepare for next iteration
				piece_to_send = piece_received	

				# receive orders from the master
				self.comm.Bcast(buforders, self.master_id)
				orders_from_master = ch.buffer_2_list_of_strings(buf_int)

				#execute orders from master
				self.sim_content.execute_orders_from_master()

				# check if simulation has to be ended
				if 'stop' in orders_from_master:
					break


# # usage
# from Simulation import Simulation
# sim_content = Simulation()

# myring = RingOfCPUs(sim_content, N_turns)

# myring.run()
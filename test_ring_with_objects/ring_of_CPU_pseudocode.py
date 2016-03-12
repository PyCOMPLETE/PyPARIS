from mpi4py import MPI


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

		

		ALLOCATE BUFFERS!



		self.sim_content.init_all()
		if self.I_am_the_master:
			self.pieces_to_be_treated = self.sim_content.init_master()
			self.N_pieces = len(pieces_to_be_treated)
			self.pieces_treated = []
			self.i_turn = 0
			self.piece_to_send = None
		elif self.I_am_a_worker:
			self.sim_content.init_worker()

	def run(self):
		if self.I_am_the_master:
			try:
				piece_to_send = pieces_to_be_treated.pop() 	#pop starts for the last slices 
															#(it is what we want, for the HEADTAIL 
															#slice order convention, z = -beta*c*t)
			except IndexError:
				piece_to_send = None

			sendbuf = self.sim_content.piece_to_buffer(piece_to_send)	
			self.comm.Sendrecv(sendbuf, dest=0, sendtag=0, 
						recvbuf=self.buf_float, source=self.master_id-1, recvtag=self.myid)
			piece_received = self.sim_content.buffer_to_piece(buf_float)

			if piece_received is not None:
				self.sim_content.treat_piece()
				pieces_treated.append(piece_received)			


		elif self.I_am_a_worker:





# usage
from Simulation import Simulation
sim_content = Simulation()

myring = RingOfCPUs(sim_content, N_turns)

myring.run()
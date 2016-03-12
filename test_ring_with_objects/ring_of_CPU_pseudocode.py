from mpi4py import MPI


class RingOfCPUs(object):
	def __init__(self, sim_content, N_turns):
		

		self.comm = MPI.COMM_WORLD
		
		# get info on the grid
		self.N_nodes = comm.Get_size()
		self.N_wkrs = self.N_nodes-1
		self.master_id = self.N_nodes-1
		self.myid = self.comm.Get_rank()
		self.I_am_a_worker = self.myid!=self.master_id
		self.I_am_the_master = not(self.I_am_a_worker)

		self.sim_content.init_all()
		if self.I_am_the_master:
			 self.pieces_to_be_treated = self.sim_content.init_master()
		elif self.I_am_a_worker:
			self.sim_content.init_worker()







# usage
from Simulation import Simulation
sim_content = Simulation()

myring = RingOfCPUs(sim_content, N_turns)

myring.run()
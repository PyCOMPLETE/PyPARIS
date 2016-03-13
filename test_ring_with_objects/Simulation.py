



class Simulation(object):
	def __init__(self):
		self.N_turns = 3

	def init_all(self):
		n_slices = 100
		z_cut = 2.5e-9*c

		from LHC import LHC
		self.machine = LHC(machine_configuration='Injection', n_segments=43, D_x=0., 
						RF_at='end_of_transverse')
		
		# We suppose that all the object that cannot be slice parallelized are at the end of the ring
		i_end_parallel = len(machine.one_turn_map)-1 #only RF is not parallelizable
		
		N_elements_per_worker = int(np.floor(float(i_end_parallel)/N_wkrs))
		print 'N_elements_per_worker', N_elements_per_worker

	def init_master(self):
		

		epsn_x  = 2.5e-6
		epsn_y  = 3.5e-6
		sigma_z = 0.05
		intensity = 1e11
		macroparticlenumber_track = 50000

		return pieces_to_be_treated



	def init_worker(self):
		pass

	def treat_piece(self, piece):
		pass

	def execute_orders_from_master(self, orders_from_master):
		pass

	def finalize_turn_on_master(self, pieces_treated):


		return orders_to_pass, new_pieces_to_be_treated

	def finalize_simulation(self):

		pass

	def piece_to_buffer(self, piece):
		

		return buf

	def buffer_to_piece(self, buf):


		return piece





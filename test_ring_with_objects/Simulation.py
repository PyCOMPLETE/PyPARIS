
import communication_helpers as ch


class Simulation(object):
	def __init__(self, ring_of_CPUs):
		self.N_turns = 3
		self.ring_of_CPUs = ring_of_CPUs

	def init_all(self):
		n_slices = 100
		z_cut = 2.5e-9*c

		from LHC import LHC
		self.machine = LHC(machine_configuration='Injection', n_segments=43, D_x=0., 
						RF_at='end_of_transverse')
		
		# We suppose that all the object that cannot be slice parallelized are at the end of the ring
		i_end_parallel = len(machine.one_turn_map)-1 #only RF is not parallelizable

		# split the machine
		N_elements_per_worker = int(np.floor(float(i_end_parallel)/N_wkrs))
		myid = self.ring_of_CPUs.myid
		print 'N_elements_per_worker', N_elements_per_worker
		if self.ring_of_CPUs.I_am_a_worker:
			self.mypart = machine.one_turn_map[N_elements_per_worker*myid:N_elements_per_worker*(myid+1)]
			print 'I am id=%d and my part is %d long'%(myid, len(self.mypart))
		elif self.ring_of_CPUs.I_am_the master:
			N_wkrs = self.ring_of_CPUs.N_wkrs 	
			self.mypart = machine.one_turn_map[N_elements_per_worker*(N_wkrs):i_end_parallel]
			non_parallel_part = machine.one_turn_map[i_end_parallel:]
			print 'I am id=%d (master) and my part is %d long'%(myid, len(self.mypart))

	def init_master(self):
		
		# beam parameters
		epsn_x  = 2.5e-6
		epsn_y  = 3.5e-6
		sigma_z = 0.05
		intensity = 1e11
		macroparticlenumber_track = 50000

		# initialization bunch
		bunch   = machine.generate_6D_Gaussian_bunch_matched(
			macroparticlenumber_track, intensity, epsn_x, epsn_y, sigma_z=sigma_z)
		print 'Bunch initialized.'

		# initial slicing
		from PyHEADTAIL.particles.slicing import UniformBinSlicer
		self.slicer = UniformBinSlicer(n_slices = n_slices, z_cuts=(-z_cut, z_cut))
		
		#slice for the first turn
		slice_obj_list = bunch.extract_slices(slicer)

		#prepare to save results
		self.beam_x, self.beam_y, self.beam_z = [], [], []
		self.sx, self.sy, self.sz = [], [], []
		self.epsx, self.epsy, self.epsz = [], [], []

		pieces_to_be_treated = slice_obj_list

		return pieces_to_be_treated

	def init_worker(self):
		pass

	def treat_piece(self, piece):
		for ele in self.mypart: 
				ele.track(piece)

	def finalize_turn_on_master(self, pieces_treated):
		
		# re-merge bunch
		bunch = sum(pieces_treated)

		#finalize present turn (with non parallel part, e.g. synchrotron motion)
		for ele in non_parallel_part:
			ele.track(bunch)

		#csave results
		self.beam_x.append(bunch.mean_x())
		self.beam_y.append(bunch.mean_y())
		self.beam_z.append(bunch.mean_z())
		self.sx.append(bunch.sigma_x())
		self.sy.append(bunch.sigma_y())
		self.sz.append(bunch.sigma_z())
		self.epsx.append(bunch.epsn_x()*1e6)
		self.epsy.append(bunch.epsn_y()*1e6)
		self.epsz.append(bunch.epsn_z())

		# prepare next turn (re-slice)
		new_pieces_to_be_treated = bunch.extract_slices(self.slicer)
		orders_to_pass = []

		return orders_to_pass, new_pieces_to_be_treated


	def execute_orders_from_master(self, orders_from_master):
		pass



		
	def finalize_simulation(self):

		pass

	def piece_to_buffer(self, piece):
		buf = ch.beam_2_buffer(piece_to_send)
		return buf

	def buffer_to_piece(self, buf):
		piece = ch.buffer_2_beam(buf_float)
		return piece





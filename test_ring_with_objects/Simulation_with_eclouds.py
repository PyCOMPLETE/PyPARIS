import communication_helpers as ch
import numpy as np
from scipy.constants import c, e


class Simulation(object):
	def __init__(self):
		self.N_turns = 2

	def init_all(self):
		n_slices = 100
		z_cut = 2.5e-9*c
		
		self.n_slices = n_slices
		self.z_cut = z_cut

		n_segments=70

		from LHC import LHC
		self.machine = LHC(machine_configuration='Injection', n_segments=n_segments, D_x=0., 
						RF_at='end_of_transverse')
		
		# We suppose that all the object that cannot be slice parallelized are at the end of the ring
		i_end_parallel = len(self.machine.one_turn_map)-1 #only RF is not parallelizable

		# split the machine
		N_wkrs = self.ring_of_CPUs.N_wkrs 	
		N_elements_per_worker = int(np.floor(float(i_end_parallel)/N_wkrs))
		myid = self.ring_of_CPUs.myid
		print 'N_elements_per_worker', N_elements_per_worker
		if self.ring_of_CPUs.I_am_a_worker:
			self.mypart = self.machine.one_turn_map[N_elements_per_worker*myid:N_elements_per_worker*(myid+1)]
			print 'I am id=%d and my part is %d long'%(myid, len(self.mypart))
		elif self.ring_of_CPUs.I_am_the_master:
			self.mypart = self.machine.one_turn_map[N_elements_per_worker*(N_wkrs):i_end_parallel]
			self.non_parallel_part = self.machine.one_turn_map[i_end_parallel:]
			print 'I am id=%d (master) and my part is %d long'%(myid, len(self.mypart))

	
		# config e-cloud
		chamb_type = 'polyg'
		x_aper = 2.300000e-02
		y_aper = 1.800000e-02
		filename_chm = '../pyecloud_config/LHC_chm_ver.mat'
		B_multip_per_eV = [1.190000e-12]
		B_multip_per_eV = np.array(B_multip_per_eV)
		fraction_device = 0.65
		intensity = 1.150000e+11
		epsn_x = 2.5e-6
		epsn_y = 2.5e-6
		init_unif_edens_flag = 1
		init_unif_edens = 9.000000e+11
		N_MP_ele_init = 100000
		N_mp_max = N_MP_ele_init*4.
		Dh_sc = .2e-3
		nel_mp_ref_0 = init_unif_edens*4*x_aper*y_aper/N_MP_ele_init

		import PyECLOUD.PyEC4PyHT as PyEC4PyHT
		my_new_part = []
		self.my_list_eclouds = []
		for ele in self.mypart:
			my_new_part.append(ele)
			if ele in self.machine.transverse_map:
				ecloud_new = PyEC4PyHT.Ecloud(L_ecloud=self.machine.circumference/n_segments, slicer=None, 
					Dt_ref=10e-12, pyecl_input_folder='../pyecloud_config',
					chamb_type = chamb_type,
					x_aper=x_aper, y_aper=y_aper,
					filename_chm=filename_chm, Dh_sc=Dh_sc,
					init_unif_edens_flag=init_unif_edens_flag,
					init_unif_edens=init_unif_edens, 
					N_mp_max=N_mp_max,
					nel_mp_ref_0=nel_mp_ref_0,
					B_multip=B_multip_per_eV*self.machine.p0/e*c,
					slice_by_slice_mode=True)
				my_new_part.append(ecloud_new)
				self.my_list_eclouds.append(ecloud_new)
		self.mypart = my_new_part

	def init_master(self):
		
		# beam parameters
		epsn_x  = 2.5e-6
		epsn_y  = 3.5e-6
		sigma_z = 0.05
		intensity = 1e11
		macroparticlenumber_track = 50000

		# initialization bunch
		bunch = self.machine.generate_6D_Gaussian_bunch_matched(
			macroparticlenumber_track, intensity, epsn_x, epsn_y, sigma_z=sigma_z)
		print 'Bunch initialized.'

		# initial slicing
		from PyHEADTAIL.particles.slicing import UniformBinSlicer
		self.slicer = UniformBinSlicer(n_slices = self.n_slices, z_cuts=(-self.z_cut, self.z_cut))
		
		#slice for the first turn
		slice_obj_list = bunch.extract_slices(self.slicer)

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
		for ele in self.non_parallel_part:
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
		orders_to_pass = ['reset_clouds']

		return orders_to_pass, new_pieces_to_be_treated


	def execute_orders_from_master(self, orders_from_master):
		if 'reset_clouds' in orders_from_master:
			for ec in self.my_list_eclouds: ec.finalize_and_reinitialize()


		
	def finalize_simulation(self):
		
		# save results
		import myfilemanager as mfm
		mfm.save_dict_to_h5('beam_coord.h5',{\
			'beam_x':self.beam_x,
			'beam_y':self.beam_y,
			'beam_z':self.beam_z,
			'sx':self.sx,
			'sy':self.sy,
			'sz':self.sz,
			'epsx':self.epsx,
			'epsy':self.epsy,
			'epsz':self.epsz})
		
		# output plots
		if False:
			beam_x = self.beam_x
			beam_y = self.beam_y
			beam_z = self.beam_z
			sx = self.sx
			sy = self.sy 
			sz = self.sz
			epsx = self.epsx
			epsy =	self.epsy
			epsz =	self.epsz
			
			import pylab as plt
			
			plt.figure(2, figsize=(16, 8), tight_layout=True)
			plt.subplot(2,3,1)
			plt.plot(beam_x)
			plt.ylabel('x [m]');plt.xlabel('Turn')
			plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
			plt.subplot(2,3,2)
			plt.plot(beam_y)
			plt.ylabel('y [m]');plt.xlabel('Turn')
			plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
			plt.subplot(2,3,3)
			plt.plot(beam_z)
			plt.ylabel('z [m]');plt.xlabel('Turn')
			plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
			plt.subplot(2,3,4)
			plt.plot(np.fft.rfftfreq(len(beam_x), d=1.), np.abs(np.fft.rfft(beam_x)))
			plt.ylabel('Amplitude');plt.xlabel('Qx')
			plt.subplot(2,3,5)
			plt.plot(np.fft.rfftfreq(len(beam_y), d=1.), np.abs(np.fft.rfft(beam_y)))
			plt.ylabel('Amplitude');plt.xlabel('Qy')
			plt.subplot(2,3,6)
			plt.plot(np.fft.rfftfreq(len(beam_z), d=1.), np.abs(np.fft.rfft(beam_z)))
			plt.xlim(0, 0.1)
			plt.ylabel('Amplitude');plt.xlabel('Qz')
			
			fig, axes = plt.subplots(3, figsize=(16, 8), tight_layout=True)
			twax = [plt.twinx(ax) for ax in axes]
			axes[0].plot(sx)
			twax[0].plot(epsx, '-g')
			axes[0].set_xlabel('Turns')
			axes[0].set_ylabel(r'$\sigma_x$')
			twax[0].set_ylabel(r'$\varepsilon_y$')
			axes[1].plot(sy)
			twax[1].plot(epsy, '-g')
			axes[1].set_xlabel('Turns')
			axes[1].set_ylabel(r'$\sigma_x$')
			twax[1].set_ylabel(r'$\varepsilon_y$')
			axes[2].plot(sz)
			twax[2].plot(epsz, '-g')
			axes[2].set_xlabel('Turns')
			axes[2].set_ylabel(r'$\sigma_x$')
			twax[2].set_ylabel(r'$\varepsilon_y$')
			axes[0].grid()
			axes[1].grid()
			axes[2].grid()
			for ax in list(axes)+list(twax): 
				ax.ticklabel_format(useOffset=False, style='sci', scilimits=(0,0),axis='y')
			plt.show()	

	def piece_to_buffer(self, piece):
		buf = ch.beam_2_buffer(piece)
		return buf

	def buffer_to_piece(self, buf):
		piece = ch.buffer_2_beam(buf)
		return piece





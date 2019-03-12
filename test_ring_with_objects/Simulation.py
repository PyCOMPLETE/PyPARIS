import os, sys
BIN = os.path.expanduser("../../")
sys.path.append(BIN)

import PyPARIS.share_segments as shs
import PyPARIS.communication_helpers as ch

import numpy as np
from scipy.constants import c


class Simulation(object):
	def __init__(self):
		self.N_turns = 128
		self.N_buffer_float_size = 500000
		self.N_buffer_int_size = 450

	def init_all(self):
		n_slices = 100
		z_cut = 2.5e-9*c
		
		self.n_slices = n_slices
		self.z_cut = z_cut

		from LHC import LHC
		self.machine = LHC(machine_configuration='Injection', n_segments=43, D_x=0., 
						RF_at='end_of_transverse')
		
		# We suppose that all the object that cannot be slice parallelized are at the end of the ring
		i_end_parallel = len(self.machine.one_turn_map)-1 #only RF is not parallelizable

		# split the machine
		sharing = shs.ShareSegments(i_end_parallel, self.ring_of_CPUs.N_nodes)
		myid = self.ring_of_CPUs.myid
		i_start_part, i_end_part = sharing.my_part(myid)
		self.mypart = self.machine.one_turn_map[i_start_part:i_end_part]
		if self.ring_of_CPUs.I_am_a_worker:
			print 'I am id=%d (worker) and my part is %d long'%(myid, len(self.mypart))
		elif self.ring_of_CPUs.I_am_the_master:
			self.non_parallel_part = self.machine.one_turn_map[i_end_parallel:]
			print 'I am id=%d (master) and my part is %d long'%(myid, len(self.mypart))

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

		#save results
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
		
		# save results
		import PyPARIS.myfilemanager as mfm
		mfm.dict_to_h5('beam_coord.h5',{\
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




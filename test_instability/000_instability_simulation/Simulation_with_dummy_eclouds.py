import sys, os
BIN = os.path.expanduser("../../../")
sys.path.append(BIN)
BIN = os.path.expanduser("../../")
sys.path.append(BIN)

import communication_helpers as ch
import numpy as np
from scipy.constants import c, e
import share_segments as shs
import time

n_segments = 15#79
N_turns = 512

Dh_sc = .2e-3


intensity = 1.300000e+11
epsn_x = 2.5e-6
epsn_y = 2.5e-6

machine_configuration = 'HLLHC-injection'

init_unif_edens_flag = 1
init_unif_edens = 1.5e+12
N_MP_ele_init = 100000
N_mp_max = N_MP_ele_init*4.

x_kick_in_sigmas = 0.1
y_kick_in_sigmas = 0.1


chamb_type = 'polyg'
x_aper = 2.300000e-02
y_aper = 1.800000e-02
filename_chm = 'LHC_chm_ver.mat'

B_multip_per_eV = [1.190000e-12]
B_multip_per_eV = np.array(B_multip_per_eV)

Dt_ref=10e-12
pyecl_input_folder='./pyecloud_config'

n_macroparticles=300000
sigma_z=1.35e-9/4*c

n_slices = 64
n_sigma_z = 2.

class Simulation(object):
	def __init__(self):
		self.N_turns = N_turns

	def init_all(self):

		
		self.n_slices = n_slices
		self.n_segments = n_segments

		# define the machine
		from LHC_custom import LHC
		self.machine = LHC(n_segments = n_segments, machine_configuration = machine_configuration)
		
		# define MP size
		nel_mp_ref_0 = init_unif_edens*4*x_aper*y_aper/N_MP_ele_init
		
		# prepare e-cloud
		import PyECLOUD.PyEC4PyHT as PyEC4PyHT
		ecloud = PyEC4PyHT.Ecloud(slice_by_slice_mode=True,
						L_ecloud=self.machine.circumference/n_segments, slicer=None , 
						Dt_ref=Dt_ref, pyecl_input_folder=pyecl_input_folder,
						chamb_type = chamb_type,
						x_aper=x_aper, y_aper=y_aper,
						filename_chm=filename_chm, Dh_sc=Dh_sc,
						init_unif_edens_flag=init_unif_edens_flag,
						init_unif_edens=init_unif_edens, 
						N_mp_max=N_mp_max,
						nel_mp_ref_0=nel_mp_ref_0,
						B_multip=B_multip_per_eV*self.machine.p0/e*c)

		# setup transverse losses (to "protect" the ecloud)
		import PyHEADTAIL.aperture.aperture as aperture
		apt_xy = aperture.EllipticalApertureXY(x_aper=ecloud.cloudsim.cloud_list[0].impact_man.chamb.x_aper, 
                        y_aper=ecloud.cloudsim.cloud_list[0].impact_man.chamb.y_aper)
		self.machine.one_turn_map.append(apt_xy)
		
		n_non_parallelizable = 2 #rf and aperture
		
		# We suppose that all the object that cannot be slice parallelized are at the end of the ring
		i_end_parallel = len(self.machine.one_turn_map)-n_non_parallelizable

		# split the machine
		sharing = shs.ShareSegments(i_end_parallel, self.ring_of_CPUs.N_nodes)
		myid = self.ring_of_CPUs.myid
		i_start_part, i_end_part = sharing.my_part(myid)
		self.mypart = self.machine.one_turn_map[i_start_part:i_end_part]
		if self.ring_of_CPUs.I_am_a_worker:
			print 'I am id=%d/%d (worker) and my part is %d long'%(myid, self.ring_of_CPUs.N_nodes, len(self.mypart))
		elif self.ring_of_CPUs.I_am_the_master:
			self.non_parallel_part = self.machine.one_turn_map[i_end_parallel:]
			print 'I am id=%d/%d (master) and my part is %d long'%(myid, self.ring_of_CPUs.N_nodes, len(self.mypart))
		
		#install eclouds in my part
		my_new_part = []
		self.my_list_eclouds = []
		for ele in self.mypart:
			my_new_part.append(ele)
			if ele in self.machine.transverse_map:
				#ecloud_new = ecloud.generate_twin_ecloud_with_shared_space_charge()
				ecloud_new = DummyEcloud()
				my_new_part.append(ecloud_new)
				self.my_list_eclouds.append(ecloud_new)
		self.mypart = my_new_part

	def init_master(self):
		
		# generate a bunch 
		bunch = self.machine.generate_6D_Gaussian_bunch_matched(
						n_macroparticles=n_macroparticles, intensity=intensity, 
						epsn_x=epsn_x, epsn_y=epsn_y, sigma_z=sigma_z)
		print 'Bunch initialized.'

		# initial slicing
		from PyHEADTAIL.particles.slicing import UniformBinSlicer
		self.slicer = UniformBinSlicer(n_slices = n_slices, n_sigma_z = n_sigma_z)

		# compute initial displacements
		inj_opt = self.machine.transverse_map.get_injection_optics()
		sigma_x = np.sqrt(inj_opt['beta_x']*epsn_x/self.machine.betagamma)
		sigma_y = np.sqrt(inj_opt['beta_y']*epsn_y/self.machine.betagamma)
		x_kick = x_kick_in_sigmas*sigma_x
		y_kick = y_kick_in_sigmas*sigma_y
		
		# apply initial displacement
		bunch.x += x_kick
		bunch.y += y_kick
		
		# define a bunch monitor 
		from PyHEADTAIL.monitors.monitors import BunchMonitor
		self.bunch_monitor = BunchMonitor('bunch_evolution', N_turns, {'Comment':'PyHDTL simulation'}, 
							write_buffer_every = 8)

		
		#slice for the first turn
		slice_obj_list = bunch.extract_slices(self.slicer)

		pieces_to_be_treated = slice_obj_list
		
		print 'N_turns', self.N_turns

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
			
		# save results		
		#print '%s Turn %d'%(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()), i_turn)
		self.bunch_monitor.dump(bunch)
		
		# prepare next turn (re-slice)
		new_pieces_to_be_treated = bunch.extract_slices(self.slicer)
		orders_to_pass = ['reset_clouds']

		return orders_to_pass, new_pieces_to_be_treated


	def execute_orders_from_master(self, orders_from_master):
		if 'reset_clouds' in orders_from_master:
			for ec in self.my_list_eclouds: ec.finalize_and_reinitialize()


		
	def finalize_simulation(self):
		pass
		
	def piece_to_buffer(self, piece):
		buf = ch.beam_2_buffer(piece)
		return buf

	def buffer_to_piece(self, buf):
		piece = ch.buffer_2_beam(buf)
		return piece

class DummyEcloud(object):
	def __init__(self):
		pass
	def track(self, bunch):
		pass
	def finalize_and_reinitialize(self):
		pass



import sys, os
BIN=os.path.expanduser('../../../')
sys.path.append(BIN)


import numpy as np
from scipy.constants import c, e


jobid = 'LH0136'
queue = '1nw'

n_segments = 79
N_turns = 512


intensity = 1.300000e+11
epsn_x = 2.5e-6
epsn_y = 2.5e-6

machine_configuration = 'HLLHC-injection'

init_unif_edens_flag = 1
init_unif_edens = 1.000000e+12
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


# define the machine
from LHC_custom import LHC
machine = LHC(n_segments = n_segments, machine_configuration = machine_configuration)

# compute sigma x and y
inj_opt = machine.transverse_map.get_injection_optics()
sigma_x = np.sqrt(inj_opt['beta_x']*epsn_x/machine.betagamma)
sigma_y = np.sqrt(inj_opt['beta_y']*epsn_y/machine.betagamma)

x_kick = x_kick_in_sigmas*sigma_x
y_kick = y_kick_in_sigmas*sigma_y

# define PIC grid size
Dh_sc = .2e-3

# define MP size
nel_mp_ref_0 = init_unif_edens*4*x_aper*y_aper/N_MP_ele_init



# define an electron cloud
import PyECLOUD.PyEC4PyHT as PyEC4PyHT
from PyHEADTAIL.particles.slicing import UniformBinSlicer
slicer = UniformBinSlicer(n_slices = 64, n_sigma_z = 2.)
ecloud = PyEC4PyHT.Ecloud(L_ecloud=machine.circumference/n_segments, slicer=slicer , 
				Dt_ref=10e-12, pyecl_input_folder='./pyecloud_config',
				chamb_type = chamb_type,
				x_aper=x_aper, y_aper=y_aper,
				filename_chm=filename_chm, Dh_sc=Dh_sc,
				init_unif_edens_flag=init_unif_edens_flag,
				init_unif_edens=init_unif_edens, 
				N_mp_max=N_mp_max,
				nel_mp_ref_0=nel_mp_ref_0,
				B_multip=B_multip_per_eV*machine.p0/e*c)

# install ecloud in the machine
machine.install_after_each_transverse_segment(ecloud)

# setup transverse losses (to "protect" the ecloud)
import PyHEADTAIL.aperture.aperture as aperture
apt_xy = aperture.EllipticalApertureXY(x_aper=ecloud.impact_man.chamb.x_aper, y_aper=ecloud.impact_man.chamb.y_aper)
machine.one_turn_map.append(apt_xy)

# generate a bunch 
bunch = machine.generate_6D_Gaussian_bunch_matched(n_macroparticles=300000, intensity=intensity, 
		epsn_x=epsn_x, epsn_y=epsn_y, sigma_z=1.35e-9/4*c)

# apply initial displacement
bunch.x += x_kick
bunch.y += y_kick

# define a bunch monitor 
from PyHEADTAIL.monitors.monitors import BunchMonitor
bunch_monitor = BunchMonitor('bunch_evolution.h5', N_turns, {'Comment':'PyHDTL simulation'}, 
					write_buffer_every = 8)

# simulate
import time
for i_turn in xrange(N_turns):
	print '%s Turn %d'%(time.strftime("%d/%m/%Y %H:%M:%S", time.localtime()), i_turn)
	machine.track(bunch, verbose = False)
	bunch_monitor.dump(bunch)
	








	
	


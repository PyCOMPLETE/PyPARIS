import sys, os
BIN=os.path.expanduser('../')
sys.path.append(BIN)

import numpy as np
import time

from scipy.constants import c,e

n_segments=4

N_turns = 5

macroparticlenumber_track = 50000

epsn_x  = 2.5e-6
epsn_y  = 3.5e-6
sigma_z = 0.05

intensity = 1e11


from LHC import LHC
machine = LHC(machine_configuration='Injection', n_segments=n_segments, 
				RF_at='end_of_transverse')


chamb_type = 'polyg'
x_aper = 2.300000e-02
y_aper = 1.800000e-02
filename_chm = './pyecloud_config/LHC_chm_ver.mat'
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

n_slices = 150
z_cut = 2.5e-9*c

# define MP size
nel_mp_ref_0 = init_unif_edens*4*x_aper*y_aper/N_MP_ele_init

import PyECLOUD.PyEC4PyHT as PyEC4PyHT
from PyHEADTAIL.particles.slicing import UniformBinSlicer
slicer = UniformBinSlicer(n_slices = n_slices, z_cuts=(-z_cut, z_cut) )
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
				
machine.install_after_each_transverse_segment(ecloud)

bunch   = machine.generate_6D_Gaussian_bunch_matched(
		macroparticlenumber_track, intensity, epsn_x, epsn_y, sigma_z=sigma_z)

print 'Start track'
t_start = time.mktime(time.localtime())
machine.track(bunch)
t_end = time.mktime(time.localtime())

print 'elapsed time: %.2f s'%(t_end-t_start)
				


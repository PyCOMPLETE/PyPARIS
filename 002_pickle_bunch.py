import sys, os
BIN=os.path.expanduser('../')

sys.path.append(BIN)

import numpy as np

N_wkrs = 5

from LHC import LHC
machine = LHC(machine_configuration='Injection', n_segments=29, D_x=10, 
				RF_at='end_of_transverse', use_cython=False)
# We suppose that all the object that cannot be slice parallelized are at the end of the ring

epsn_x  = 2.5e-6
epsn_y  = 3.5e-6
sigma_z = 0.05

intensity = 1e11

macroparticlenumber_track = 1000

bunch   = machine.generate_6D_Gaussian_bunch_matched(
    macroparticlenumber_track, intensity, epsn_x, epsn_y, sigma_z=sigma_z)

import pickle
with open('test_pickle.pkl', 'w') as fid:
	pickle.dump({'test':bunch}, fid)
print 'ALL', ' OK'	

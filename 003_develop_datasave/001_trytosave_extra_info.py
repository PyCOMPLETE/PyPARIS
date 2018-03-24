import sys
sys.path.append('../../')
sys.path.append('../')

from scipy.constants import c as clight, e as qe
import numpy as np

import gen_multibunch_beam as gmb

from machines_for_testing import SPS

n_segments = 1
bunch_intensity = 1e11
epsn_x = 2.5e-6
epsn_y = 3.5e-6
sigma_z = 10e-2

n_slices = 20
z_cut = 2*sigma_z

min_inten_slice4EC = 1e3


non_linear_long_matching = False



b_spac_s = 25e-9

#Here head is left and tail is right
filling_pattern = [1., 0., 0., 1., 1., 1., 0.]
filling_pattern = 6*[1]

macroparticlenumber = 100000

machine = SPS(n_segments = n_segments, 
            machine_configuration = 'Q20-injection', accQ_x=20., accQ_y=20., 
            RF_at='end_of_transverse', longitudinal_mode = 'non-linear')
            
bucket_length_m = machine.circumference/(machine.longitudinal_map.harmonics[0])
b_spac_m =  b_spac_s*machine.beta*clight
b_spac_buckets = np.round(b_spac_m/bucket_length_m)
            
list_bunches = gmb.gen_matched_multibunch_beam(machine, macroparticlenumber, filling_pattern, b_spac_s, bunch_intensity, epsn_x, epsn_y, sigma_z, non_linear_long_matching, min_inten_slice4EC)

bunch = list_bunches[0]


import types
bunch.i_bunch = types.MethodType(lambda self: self.slice_info['i_bunch'], bunch)
bunch.i_turn = types.MethodType(lambda self: self.slice_info['i_turn'], bunch)

# define a bunch monitor 
stats_to_store = [
 'mean_x',
 'mean_xp',
 'mean_y',
 'mean_yp',
 'mean_z',
 'mean_dp',
 'sigma_x',
 'sigma_y',
 'sigma_z',
 'sigma_dp',
 'epsn_x',
 'epsn_y',
 'epsn_z',
 'macroparticlenumber',
 'i_bunch',
 'i_turn']


N_turns_mon = 10
from PyHEADTAIL.monitors.monitors import BunchMonitor
bunch_monitor = BunchMonitor('testmon',
                    N_turns_mon, {'Comment':'PyHDTL simulation'}, 
                    write_buffer_every = 1,
                    stats_to_store = stats_to_store)

bunch_monitor.dump(bunch)

import myfilemanager as mfm

dath5 =  mfm.bunchh5_to_obj('testmon.h5')
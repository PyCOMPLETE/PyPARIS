import sys
sys.path.append('../../')
sys.path.append('../')
import numpy as np

from scipy.constants import c as clight, e as qe

from PyHEADTAIL.particles.slicing import UniformBinSlicer



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


macroparticlenumber = 100000

machine = SPS(n_segments = n_segments, 
            machine_configuration = 'Q20-injection', accQ_x=20., accQ_y=20., 
            RF_at='end_of_transverse', longitudinal_mode = 'non-linear')
            
bucket_length_m = machine.circumference/(machine.longitudinal_map.harmonics[0])
b_spac_m =  b_spac_s*machine.beta*clight
b_spac_buckets = np.round(b_spac_m/bucket_length_m)
            

list_bunches = gmb.gen_matched_multibunch_beam(machine, macroparticlenumber, filling_pattern, b_spac_s, bunch_intensity, epsn_x, epsn_y, sigma_z, non_linear_long_matching, min_inten_slice4EC)

beam = sum(list_bunches)

import slicing_tool as st
import PyPARIS.communication_helpers as ch

# Turn slices into buffer
list_buffers = []
for bb in list_bunches:
    these_slices = st.slice_a_bunch(bb, z_cut=z_cut, n_slices=n_slices)
    for ss in these_slices:
        list_buffers.append(ch.beam_2_buffer(ss,verbose=True, mode='pickle'))
big_buffer = ch.combine_float_buffers(list_buffers)

# Build profile of the full beam
thin_slicer = UniformBinSlicer(n_slices=10000, z_cuts=(-len(filling_pattern)*bucket_length_m*b_spac_buckets, bucket_length_m))
thin_slice_set = beam.get_slices(thin_slicer, statistics=True)

import matplotlib.pyplot as plt

plt.close('all')
plt.figure(1)


# re-split buffer
list_buffers_rec = ch.split_float_buffers(big_buffer)

#~ import json
sp1 = plt.subplot(2,1,1)
sp2 = plt.subplot(2,1,2, sharex=sp1)
sp1.plot(thin_slice_set.z_centers, thin_slice_set.charge_per_slice)

for ibuf, buf in enumerate(list_buffers_rec):
        ss = ch.buffer_2_beam(buf)
        sp1.axvline(x=ss.slice_info['z_bin_center'], color='k', alpha=0.5, linestyle='--')
        sp1.axvspan(xmin=ss.slice_info['z_bin_left'], xmax=ss.slice_info['z_bin_right'],
            color={0:'r', 1:'b'}[ibuf%2], alpha = 0.3)
        sp2.stem([ss.slice_info['z_bin_center']], [ss.slice_info['interact_with_EC']])
sp2.grid('on')



plt.show()


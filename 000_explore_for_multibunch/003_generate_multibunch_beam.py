import sys
sys.path.append('../../')
import numpy as np

from scipy.constants import c as clight, e as qe

from machines_for_testing import SPS

n_segments = 1
intensity = 1e11
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


macroparticlenumber_track = 10000

machine = SPS(n_segments = n_segments, 
			machine_configuration = 'Q20-injection', accQ_x=20., accQ_y=20., 
			RF_at='end_of_transverse', longitudinal_mode = 'non-linear')


bucket_length_m = machine.circumference/(machine.longitudinal_map.harmonics[0])
b_spac_m =  b_spac_s*machine.beta*clight
b_spac_buckets = np.round(b_spac_m/bucket_length_m)

if non_linear_long_matching:
	generate_bunch = machine.generate_6D_Gaussian_bunch_matched
else:
	generate_bunch = machine.generate_6D_Gaussian_bunch

list_genbunches = []
for i_slot, inten_slot in enumerate(filling_pattern):
	if inten_slot>0:
		bunch = generate_bunch(macroparticlenumber_track, inten_slot*intensity, epsn_x, epsn_y, sigma_z=sigma_z)
		bunch.z -= b_spac_buckets*bucket_length_m*i_slot
		list_genbunches.append(bunch)

beam = sum(list_genbunches)

bucket = machine.longitudinal_map.get_bucket(gamma=machine.gamma, mass=machine.mass, charge=machine.charge)
# z_beam_center = bucket.z_ufp_separatrix + bucket_length - self.circumference/2.

from PyHEADTAIL.particles.slicing import UniformBinSlicer


# Here the center of the bucket
bucket.z_sfp

# I want to re-separate the bunches
buncher = UniformBinSlicer(n_slices = 0, z_sample_points = np.arange(bucket.z_sfp-len(filling_pattern)*bucket_length_m*b_spac_buckets, 
										bucket.z_sfp+bucket_length_m, bucket_length_m*b_spac_buckets))
buncher_slice_set = beam.get_slices(buncher, statistics=True)
list_bunches = beam.extract_slices(buncher, include_non_sliced='never')
list_bunches = list_bunches[::-1] # I want the head at the beginning of the list

# Add further information to bunches
for bb in list_bunches:
	slice4EC = bb.intensity>min_inten_slice4EC
	bb.slice_info['slice4EC'] = slice4EC
	bb.slice_info['kickEC'] = slice4EC

# Slice bunch if populated
this_bunch = list_bunches[3]
if this_bunch.slice_info['slice4EC']:
	bunch_center = this_bunch.slice_info['z_bin_center']
	this_slicer = UniformBinSlicer(z_cuts=(bunch_center-z_cut, bunch_center+z_cut), n_slices=n_slices)
	this_slices = this_bunch.extract_slices(this_slicer, include_non_sliced='always')[::-1]
	#split_unsliced...
else:
	pass
	#simple list with one long slice

thin_slicer = UniformBinSlicer(n_slices=1000, z_cuts=(-len(filling_pattern)*bucket_length_m*b_spac_buckets, bucket_length_m))
thin_slice_set = beam.get_slices(thin_slicer, statistics=True)

import matplotlib.pyplot as plt

plt.close('all')
plt.figure(1)
sp1 = plt.subplot(1,1,1)
sp1.plot(thin_slice_set.z_centers, thin_slice_set.charge_per_slice)
for ibinm, zbin in enumerate(buncher_slice_set.z_centers):
	sp1.axvline(x=zbin, color='k', alpha=0.5)

for ibb, bb in enumerate(list_bunches):
	sp1.axvspan(xmin=bb.slice_info['z_bin_left'], xmax=bb.slice_info['z_bin_right'],
		color={0:'r', 1:'b'}[ibb%2], alpha = 0.3)


plt.show()



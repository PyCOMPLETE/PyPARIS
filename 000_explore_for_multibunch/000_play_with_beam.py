import sys
sys.path.append('../../')

from machines_for_testing import SPS

n_segments = 1
intensity = 1e11
epsn_x = 2.5e-6
epsn_y = 3.5e-6
sigma_z = 30e-2

n_slices = 20
z_cut = 2*sigma_z

macroparticlenumber_track = 1000

machine = SPS(n_segments = n_segments, 
			machine_configuration = 'Q20-injection', accQ_x=20., accQ_y=20., 
			RF_at='end_of_transverse')

bunch = machine.generate_6D_Gaussian_bunch(
			macroparticlenumber_track, intensity, epsn_x, epsn_y, sigma_z=sigma_z)

from PyHEADTAIL.particles.slicing import UniformBinSlicer


slicer = UniformBinSlicer(n_slices = n_slices, z_cuts=(-z_cut, z_cut))
slices = bunch.extract_slices(slicer, include_non_sliced='always')


# I get a slice
aslice = slices[10]
# aslice = slices[-1]


# I get its slice_info
sinfo = aslice.slice_info

# I print slice_info
print("\nSlice info:")
print(sinfo)

import json, numpy as np
# I make it into a json string
sinfo_str = json.dumps(sinfo)
# I convert it into an array of int
sinfo_int = np.array(map(ord, sinfo_str), dtype=np.int)
# I convert it to an array of floats
sinfo_float = sinfo_int.astype(np.float, casting='safe')

# I reconstruct the original dictionary
si_int = sinfo_float.astype(np.int)
si_str = ''.join(map(unichr, list(si_int)))
sinfo_rec = json.loads(si_str)

print("\nSlice info reconstructed:")
print(sinfo_rec)

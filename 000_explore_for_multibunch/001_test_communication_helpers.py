import sys
sys.path.append('../../')
import numpy as np

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
aslice = slices[0]

# What I want to buffer
tobebuffered = bunch
tobebuffered = aslice

import PyPARIS.communication_helpers as ch

# buffer
buf = ch.beam_2_buffer(tobebuffered)

# unbuffer
beamfrombuf = ch.buffer_2_beam(buf)

# check
attr_list = dir(tobebuffered)
for att in attr_list:

	v1 = getattr(tobebuffered, att)
	v2 = getattr(beamfrombuf, att)

	if type(v1) is np.ndarray:
		print att, '1', v1[0:3], '...', v1[-3:]
		print att, '2', v2[0:3], '...', v2[-3:]
	else:
		print att, '1', v1
		print att, '2', v2
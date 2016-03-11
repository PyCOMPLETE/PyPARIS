

import sys, os
BIN = os.path.expanduser("../")
sys.path.append(BIN)
BIN = os.path.expanduser("../../")
sys.path.append(BIN)

from mpi4py import MPI
comm = MPI.COMM_WORLD

import communication_helpers as ch

import numpy as np

myid = comm.Get_rank()

if myid>1: raise ValueError('To be tested with 2 processors')

N_buffer_float_size = 1000000
buf_float = np.array(N_buffer_float_size*[0.])


# test send
if myid == 0:
	
	#test None
	bufbun = ch.beam_2_buffer(None)
	comm.Send(bufbun, dest=1, tag=1)
	
	epsn_x  = 2.5e-6
	epsn_y  = 3.5e-6
	sigma_z = 0.05

	intensity = 1e11
	macroparticlenumber = 30000

	from LHC import LHC
	n_segments = 1
	machine = LHC(machine_configuration='Injection', n_segments=n_segments, 
					RF_at='end_of_transverse')
					
	bunch   = machine.generate_6D_Gaussian_bunch(
			macroparticlenumber, intensity, epsn_x, epsn_y, sigma_z=sigma_z)
	
	bunch.slice_info = 'unsliced'
	bunch.slice_info = {\
                    'z_bin_center': 25.,\
                    'z_bin_right': 30.,\
                    'z_bin_left':20.}
	

	bufbun = ch.beam_2_buffer(bunch)
	if len(bufbun)>N_buffer_float_size:
		raise ValueError('Buffer is too short!')
	comm.Send(bufbun, dest=1, tag=11)
	
elif myid == 1:
	
	#test None
	comm.Recv(buf_float, source=0, tag=1)
	bnone = ch.buffer_2_beam(buf_float)
	print 'I am 1 and I received', repr(bnone)
	
	comm.Recv(buf_float, source=0, tag=11)
	bunch = ch.buffer_2_beam(buf_float)
	print 'I am 1 and I received the bunch'

if myid<2:
	import time		
	time.sleep(1); comm.Barrier()

	print 'macroparticlenumber', bunch.macroparticlenumber
	time.sleep(1); comm.Barrier()

	print 'particlenumber_per_mp',  bunch.particlenumber_per_mp
	time.sleep(1); comm.Barrier()

	print 'mass', bunch.mass
	time.sleep(1); comm.Barrier()

	print 'charge', bunch.mass
	time.sleep(1); comm.Barrier()

	print 'circumference', bunch.circumference
	time.sleep(1); comm.Barrier()

	print 'gamma', bunch.gamma
	time.sleep(1); comm.Barrier()

	print 'id', bunch.id
	time.sleep(1); comm.Barrier()

	print 'x',  bunch.x
	time.sleep(1); comm.Barrier()

	print 'xp', bunch.xp
	time.sleep(1); comm.Barrier()

	print 'y', bunch.y
	time.sleep(1); comm.Barrier()

	print 'yp', bunch.yp
	time.sleep(1); comm.Barrier()

	print 'z', bunch.z
	time.sleep(1); comm.Barrier()	

	print 'dp', bunch.dp
	time.sleep(1); comm.Barrier()
	
	if not hasattr(bunch, 'slice_info'):
		print "No slice info"
	else:
		print bunch.slice_info


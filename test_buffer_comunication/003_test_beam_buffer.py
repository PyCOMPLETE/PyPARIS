import sys, os
BIN = os.path.expanduser("../../../")
sys.path.append(BIN)

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

N_buffer_float_size = 1000000
buf_float = np.array(N_buffer_float_size*[0.])


# test send
if myid == 0:
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

	bufbun = ch.beam_2_buffer(bunch)
	if len(bufbun)>N_buffer_float_size:
		raise ValueError('Buffer is too short!')
	comm.Send(bufbun, dest=1, tag=11)
	
elif myid == 1:
	comm.Recv(buf_float, source=0, tag=11)
	bunch = ch.buffer_2_beam(buf_float)
	#~ buf = np.array(100*[0])
	#~ 
	#~ list_of_orders_received = ch.buffer_2_list_of_strings(buf)
	print 'I am 1 and I received'
	
comm.Barrier()
	
print bunch.macroparticlenumber
comm.Barrier()

print bunch.particlenumber_per_mp
comm.Barrier()

print bunch.charge
comm.Barrier()

print bunch.mass
comm.Barrier()

print bunch.circumference
comm.Barrier()

print bunch.gamma
comm.Barrier()

print bunch.id
comm.Barrier()

print bunch.x
comm.Barrier()

print bunch.xp
comm.Barrier()

print bunch.y
comm.Barrier()

print bunch.yp
comm.Barrier()

print bunch.z 
comm.Barrier()	

print bunch.dp 
comm.Barrier()
	

	

	


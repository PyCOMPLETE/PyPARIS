import numpy as np
from PyHEADTAIL.particles.particles import Particles


def combine_float_buffers(list_of_buffers):
	N_buffers = len(list_of_buffers)
	len_buffers = np.array(map(lambda seq: float(len(seq)), list_of_buffers))
	return np.concatenate([np.array([float(N_buffers)]), len_buffers]+list_of_buffers)

def split_float_buffers(megabuffer):
	i_mbuf = 0
	
	N_buffers = int(megabuffer[0])
	i_mbuf += 1
	
	len_buffers = megabuffer[i_mbuf:i_mbuf+N_buffers]
	i_mbuf += N_buffers
	
	list_of_buffers = []
	for i_buf in xrange(N_buffers):
		lenbuf = int(len_buffers[i_buf])
		list_of_buffers.append(megabuffer[i_mbuf:i_mbuf+lenbuf])
		i_mbuf += lenbuf
		
	return list_of_buffers
	
	
	


def list_of_strings_2_buffer(strlist):
	data = ''.join(map(lambda s:s+';', strlist))+'\n'
	buf_to_send = np.atleast_1d(np.int_(np.array(map(ord, list(data)))))
	return buf_to_send
	
def buffer_2_list_of_strings(buf):
	str_received = ''.join(map(unichr, list(buf)))
	strlist = map(str, str_received.split('\n')[0].split(';'))[:-1]
	return strlist


def beam_2_buffer(beam):
	
	#print beam
	
	if beam is None:
		buf = np.array([-1.])
	else:	
		if np.array(beam.particlenumber_per_mp).shape != ():
			raise ValueError('particlenumber_per_mp is a vector! Not implemented!')

		
		if not hasattr(beam, 'slice_info'):
			sl_info_buf = np.array([-1., 0., 0., 0.])
		elif beam.slice_info is None:
			sl_info_buf = np.array([-1., 0., 0., 0.])
		elif beam.slice_info == 'unsliced':
			sl_info_buf = np.array([0., 0., 0., 0.])
		else:
			sl_info_buf = np.array([1.,
							beam.slice_info['z_bin_center'],
							beam.slice_info['z_bin_right'],
							beam.slice_info['z_bin_left']])
		
		buf = np.concatenate((
			np.array([float(beam.macroparticlenumber)]),
			np.array([float(beam.particlenumber_per_mp)]), 
			np.array([beam.charge]),
			np.array([beam.mass]),
			np.array([beam.circumference]),
			np.array([beam.gamma]),
			np.atleast_1d(np.float_(beam.id)),
			beam.x, beam.xp, beam.y, beam.yp, beam.z, beam.dp,
			sl_info_buf))
			
	return buf
	
def buffer_2_beam(buf):
	
	if buf[0]<0:
		beam=None
	else:
		i_buf = 0
		
		macroparticlenumber = int(buf[i_buf])
		i_buf += 1
		
		particlenumber_per_mp = buf[i_buf]
		i_buf += 1
		
		charge = buf[i_buf]
		i_buf += 1
		
		mass = buf[i_buf]
		i_buf += 1
		
		circumference = buf[i_buf]
		i_buf += 1
		
		gamma = buf[i_buf]
		i_buf += 1
		
		id_ = np.int_(buf[i_buf:i_buf+macroparticlenumber])
		i_buf += macroparticlenumber

		x =  buf[i_buf:i_buf+macroparticlenumber]
		i_buf += macroparticlenumber
		
		xp =  buf[i_buf:i_buf+macroparticlenumber]
		i_buf += macroparticlenumber
		
		y =  buf[i_buf:i_buf+macroparticlenumber]
		i_buf += macroparticlenumber
		
		yp =  buf[i_buf:i_buf+macroparticlenumber]
		i_buf += macroparticlenumber
		
		z =  buf[i_buf:i_buf+macroparticlenumber]
		i_buf += macroparticlenumber	
		
		dp = buf[i_buf:i_buf+macroparticlenumber]
		i_buf += macroparticlenumber
		
		slice_info_buf = buf[i_buf:i_buf+4]
		i_buf += 4
		
		beam = Particles(macroparticlenumber=macroparticlenumber,
						particlenumber_per_mp=particlenumber_per_mp, charge=charge,
						mass=mass, circumference=circumference, gamma=gamma, 
						coords_n_momenta_dict={\
								'x': np.atleast_1d(x),
								'xp':np.atleast_1d(xp),
								'y':np.atleast_1d(y),
								'yp':np.atleast_1d(yp),	
								'z':np.atleast_1d(z),
								'dp':np.atleast_1d(dp)})
		
		beam.id = np.atleast_1d(id_)
		
		if slice_info_buf[0] < 0.:
			beam.slice_info = None
		elif slice_info_buf[0] == 0.:
			beam.slice_info = 'unsliced'
		else:
			beam.slice_info = {\
                    'z_bin_center':slice_info_buf[1] ,
                    'z_bin_right':slice_info_buf[2],
                    'z_bin_left':slice_info_buf[3]}
	
	return beam

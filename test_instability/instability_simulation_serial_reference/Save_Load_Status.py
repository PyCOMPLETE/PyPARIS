import h5py

import os

def dump_beam_status(beam, filename):
	'''Dump beam status to h5 file'''

	dict_beam_status = {\
	'x':beam.x,
	'xp':beam.xp,
	'y':beam.y,
	'yp':beam.yp,
	'z':beam.z,
	'dp':beam.dp,
	'macroparticlenumber':beam.macroparticlenumber,
	'intensity':beam.intensity,
	'charge':beam.charge,
	'mass':beam.mass,
	'circumference':beam.circumference,
	'gamma':beam.gamma}

	with h5py.File(filename, 'w') as fid:
		for kk in dict_beam_status.keys():
			fid[kk] = dict_beam_status[kk]


def beam_from_h5status(filename):

	import myfilemanager as mfm
	beam_read = mfm.object_with_arrays_and_scalar_from_h5(filename)

	coords_n_momenta_dict = {\
	'x':beam_read.x,
	'xp':beam_read.xp,
	'y':beam_read.y,
	'yp':beam_read.yp,
	'z':beam_read.z,
	'dp':beam_read.dp}
	
	from PyHEADTAIL.particles.generators import ImportDistribution
	beam = ImportDistribution(beam_read.macroparticlenumber, beam_read.intensity, beam_read.charge, beam_read.mass,
					 beam_read.circumference, beam_read.gamma, coords_n_momenta_dict).generate()
	return beam


def dump_ecloud_status(ecloud, filename):
	'''Dump ecloud status to h5 file'''

	dict_ecloud_status = {\
	'init_N_mp': ecloud.init_N_mp,
	'init_x': ecloud.init_x,
	'init_y': ecloud.init_y,
	'init_z': ecloud.init_z,
	'init_vx': ecloud.init_vx,
	'init_vy': ecloud.init_vy,
	'init_vz': ecloud.init_vz,
	'init_nel': ecloud.init_nel}

	with h5py.File(filename, 'w') as fid:
		for kk in dict_ecloud_status.keys():
			fid[kk] = dict_ecloud_status[kk]
			
def reinit_ecloud_from_h5status(filename, ecloud):
	
	print 'Reinitialize ecloud object'

	import myfilemanager as mfm
	ecloud_read = mfm.object_with_arrays_and_scalar_from_h5(filename)
	
	ecloud.init_N_mp = ecloud_read.init_N_mp
	ecloud.init_x = ecloud_read.init_x
	ecloud.init_y = ecloud_read.init_y
	ecloud.init_z = ecloud_read.init_z
	ecloud.init_vx = ecloud_read.init_vx
	ecloud.init_vy = ecloud_read.init_vy
	ecloud.init_vz = ecloud_read.init_vz
	ecloud.init_nel = ecloud_read.init_nel



class SimulationStatus(object):
	def __init__(self,  N_turns_per_run=None, N_turns_target=None, check_for_resubmit=False, jobid=None, queue = '2nd'):
		self.N_turns_target = N_turns_target
		self.N_turns_per_run = N_turns_per_run
		self.check_for_resubmit = check_for_resubmit
		self.jobid = jobid
		self.queue = queue
		
		self.filename = 'simulation_status.sta'
	
	def dump_to_file(self):
		lines = []
		lines.append('present_simulation_part = %d\n'%self.present_simulation_part)
		lines.append('first_turn_part = %d\n'%self.first_turn_part)
		lines.append('last_turn_part = %d\n'%self.last_turn_part)
		lines.append('present_part_done = %s\n'%repr(self.present_part_done))
		lines.append('present_part_running = %s\n'%repr(self.present_part_running))
		
		with open(self.filename, 'wb') as fid:
			fid.writelines(lines)
			
	def load_from_file(self):
		with open(self.filename) as fid:
			exec(fid.read())
		self.present_simulation_part = present_simulation_part
		self.first_turn_part = first_turn_part
		self.last_turn_part = last_turn_part
		self.present_part_done = present_part_done
		self.present_part_running = present_part_running
		
	def print_from_file(self):
		with open(self.filename) as fid:
			print fid.read()
	
	def before_simulation(self):
		self.first_run = False
		try:
			self.load_from_file()
			self.present_simulation_part+=1
			self.first_turn_part += self.N_turns_per_run
			self.last_turn_part += self.N_turns_per_run
		except IOError:
			print 'Simulation Status not found --> initializing simulation'
			self.first_run = True
			self.present_simulation_part = 0
			self.first_turn_part = 0
			self.last_turn_part = self.N_turns_per_run-1
			self.present_part_done = True
			self.present_part_running = False
			
		if not(self.present_part_done) or self.present_part_running:
			raise ValueError('The previous simulation part seems not finished!!!!')
			
		self.present_part_done = False
		self.present_part_running = True
		
		self.dump_to_file()
		
		print 'Starting part:\n\n'
		self.print_from_file()
		print '\n\n'
		
	def after_simulation(self):
		self.load_from_file()
		self.present_part_done = True
		self.present_part_running = False
		self.dump_to_file()
		
		print 'Done part:\n\n'
		self.print_from_file()
		print '\n\n'
		
		if self.check_for_resubmit:
			if self.last_turn_part+1<self.N_turns_target:
				print 'resubmit the job'
				nextpartid = '.%d'%(self.present_simulation_part+1)
				current_sim_folder = os.getcwd()
				command = 'bsub -L /bin/bash -J '+ self.jobid+nextpartid + \
					' -o '+ current_sim_folder+'/STDOUT'+nextpartid + \
					' -e '+ current_sim_folder+'/STDERR'+nextpartid + \
					' -q '+ self.queue +' < '+current_sim_folder+'/job.job\n'
					
				print command
				os.system(command)
				
	def restart_last(self):
		
		self.load_from_file()
		self.N_turns_per_run = 	self.last_turn_part - self.first_turn_part + 1

		self.present_simulation_part-=1
		self.first_turn_part -= self.N_turns_per_run
		self.last_turn_part -= self.N_turns_per_run

		self.present_part_done = True
		self.present_part_running = False
		
		self.dump_to_file()
		
		print 'Restored status:\n\n'
		self.print_from_file()
		print '\n\n'
		
		
		
		
	
					
		


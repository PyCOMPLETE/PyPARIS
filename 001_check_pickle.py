import sys, os
BIN=os.path.expanduser('../')

sys.path.append(BIN)

import numpy as np

N_wkrs = 5

from LHC import LHC
machine = LHC(machine_configuration='Injection', n_segments=29, D_x=10, 
				RF_at='end_of_transverse', use_cython=False)
# We suppose that all the object that cannot be slice parallelized are at the end of the ring
i_end_parallel = len(machine.one_turn_map)-1 #only RF is not parallelizable

N_elements_per_worker = int(np.floor(float(i_end_parallel)/N_wkrs))

print 'N_elements_per_worker', N_elements_per_worker

list_of_machine_parts = []
for ii in xrange(N_wkrs):
	list_of_machine_parts.append(machine.one_turn_map[\
		N_elements_per_worker*ii:N_elements_per_worker*(ii+1)])

part_for_master = list_of_machine_parts[N_elements_per_worker*(ii+1):]

import pickle

obj_to_pickle = list_of_machine_parts[0][0]
del(obj_to_pickle.__dict__)

for attrname in dir(obj_to_pickle):
	member = getattr(obj_to_pickle, attrname)
	try:
		with open('test_pickle.pkl', 'w') as fid:
			pickle.dump({'test':member}, fid)
		print attrname, ' OK'
	except:
		setattr(obj_to_pickle, attrname, None)
		print attrname, ' Bad! Bound to None'
		

#~ with open('test_pickle.pkl', 'w') as fid:
	#~ pickle.dump({'test':obj_to_pickle}, fid)
#~ print 'ALL', ' OK'

for attrname in dir(obj_to_pickle):
	member = getattr(obj_to_pickle, attrname)
	try:
		with open('test_pickle.pkl', 'w') as fid:
			pickle.dump({'test':member}, fid)
		print '2 ', attrname, ' OK'
	except:
		setattr(obj_to_pickle, attrname, None)
		print '2 ', attrname, ' Bad! Bound to None'

	
with open('test_pickle.pkl', 'w') as fid:
	pickle.dump({'test':obj_to_pickle}, fid)
print 'ALL', ' OK'	

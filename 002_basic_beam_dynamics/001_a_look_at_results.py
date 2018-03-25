import sys, os
BIN = os.path.expanduser("../")
sys.path.append(BIN)

import numpy as np

n_files = 3
i_bunch_obs = 1


list_files = ['complete_test/bunch_monitor_ring%03d.h5'%ii for ii in range(n_files)]

import myfilemanager as mfm
dict_data = mfm.bunchh5list_to_dict(list_files)

n_turns = int(np.max(dict_data['i_turn']))

dict_bunch = {kk:np.zeros(n_turns, dtype=np.float64)+np.nan for kk in dict_data.keys()}

for ii in xrange(len(dict_data['i_bunch'])):
	if int(dict_data['i_bunch'][ii]) == int(i_bunch_obs):
		i_turn = int(dict_data['i_turn'][ii])
		for kk in dict_data.keys():
			dict_bunch[kk][i_turn] = dict_data[kk][ii]



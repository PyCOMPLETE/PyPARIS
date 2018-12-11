import sys, os
import numpy as np


sim_folder = '.'
tag = 'noecloud'
n_rings = 4

to_be_saved = [
 'epsn_x',
 'epsn_y',
 'epsn_z',
 'macroparticlenumber',
 'mean_dp',
 'mean_x',
 'mean_xp',
 'mean_y',
 'mean_yp',
 'mean_z',
 'sigma_dp',
 'sigma_x',
 'sigma_y',
 'sigma_z']



list_files = [sim_folder+'/bunch_monitor_ring%03d.h5'%ii for ii in range(n_rings)]

import myfilemanager as mfm
dict_data = mfm.bunchh5list_to_dict(list_files, permissive=True)

print 'Data loaded!'

n_turns = int(np.max(dict_data['i_turn']))+1
n_bunches = int(np.max(dict_data['i_bunch']))+1

list_bunches = []
for i_bunch_obs in range(n_bunches):
    print('Bunch %d/%d'%(i_bunch_obs, n_bunches))
    dict_bunch = {kk:np.zeros(n_turns, dtype=np.float64)+np.nan for kk in dict_data.keys()}
    for ii in xrange(len(dict_data['i_bunch'])):
        if int(dict_data['i_bunch'][ii]) == int(i_bunch_obs):
            i_turn = int(dict_data['i_turn'][ii])
            for kk in dict_data.keys():
                dict_bunch[kk][i_turn] = dict_data[kk][ii]
                
    list_bunches.append(dict_bunch)


dict_matrices = {kk: np.zeros((n_turns, n_bunches)) for kk in to_be_saved}

for i_bunch_obs in range(n_bunches):
    n_turns_this = len(list_bunches[i_bunch_obs]['epsn_x'])
    mask_notnan = ~np.isnan(list_bunches[i_bunch_obs]['macroparticlenumber'])
    
    for kk in to_be_saved:
        dict_matrices[kk][:n_turns_this, i_bunch_obs][mask_notnan] =\
                list_bunches[i_bunch_obs][kk][mask_notnan]


import scipy.io as sio
sio.savemat(tag+'_matrices.mat', dict_matrices, oned_as='row')
    

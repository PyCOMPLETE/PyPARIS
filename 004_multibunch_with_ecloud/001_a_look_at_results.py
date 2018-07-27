import sys, os
BIN = os.path.expanduser("../")
sys.path.append(BIN)

import numpy as np

n_rings = 4



list_files = ['bunch_monitor_ring%03d.h5'%ii for ii in range(n_rings)]

import myfilemanager as mfm
dict_data = mfm.bunchh5list_to_dict(list_files)

n_turns = int(np.max(dict_data['i_turn']))+1
n_bunches = int(np.max(dict_data['i_bunch']))+1

list_bunches = []
for i_bunch_obs in range(n_bunches):
    dict_bunch = {kk:np.zeros(n_turns, dtype=np.float64)+np.nan for kk in dict_data.keys()}
    for ii in xrange(len(dict_data['i_bunch'])):
        if int(dict_data['i_bunch'][ii]) == int(i_bunch_obs):
            i_turn = int(dict_data['i_turn'][ii])
            for kk in dict_data.keys():
                dict_bunch[kk][i_turn] = dict_data[kk][ii]
                
    list_bunches.append(dict_bunch)

import matplotlib.pyplot as plt
plt.close('all')

spect_x = np.fft.rfft(dict_bunch['mean_x'])
spect_y = np.fft.rfft(dict_bunch['mean_y'])
freq_ax = np.fft.rfftfreq(len(dict_bunch['mean_x']))


plt.figure(1)
sp1 = plt.subplot(2,2,1)
sp2 = plt.subplot(2,2,2, sharex=sp1)
for i_bunch_obs in range(n_bunches):
    
    sp1.plot(list_bunches[i_bunch_obs]['mean_x'])
    
    sp2.plot(list_bunches[i_bunch_obs]['mean_y'])

#~ spf1 = plt.subplot(2,2,3)
#~ plt.plot(freq_ax, np.abs(spect_x))

#~ spf2 = plt.subplot(2,2,4, sharex=spf1)
#~ plt.plot(freq_ax, np.abs(spect_y))

plt.figure(2)
sp1 = plt.subplot(2,1,1)
plt.plot(dict_bunch['mean_z'])
sp2 = plt.subplot(2,1,2, sharex=sp1)
plt.plot(dict_bunch['sigma_z'])


plt.show()



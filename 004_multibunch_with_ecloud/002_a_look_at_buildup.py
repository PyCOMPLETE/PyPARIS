import sys, os
BIN = os.path.expanduser("../../")
sys.path.append(BIN)

import argparse
import matplotlib.pyplot as plt
import numpy as np
#from colorsys import hsv_to_rgb
import os
import PyECLOUD.myloadmat_to_obj as mlm
import matplotlib.gridspec as gridspec
import PyECLOUD.mystyle as ms
import PyPARIS.myfilemanager as mfm

plt.close('all')

sim_folder = './'

n_rings = 4
i_bunch_obs = 1

list_files = ['bunch_monitor_ring%03d.h5'%ii for ii in range(n_rings)]

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


myfontsz = 10
ms.mystyle_arial(fontsz=myfontsz)

ob = mlm.myloadmat_to_obj('./cloud_evol_ring0__iter0.mat')   # load dictionary of the current simulation

plt.figure(1)
plt.plot(ob.t/25e-9, ob.Nel_timep)

plt.figure(10)
plt.plot(ob.t/25e-9, ob.lam_t_array)

plt.figure(11)
plt.plot(ob.t/25e-9, ob.cen_density)


plt.figure(2)
plt.pcolormesh(ob.xg_hist, np.arange(ob.nel_hist.shape[0]),  ob.nel_hist)

plt.figure(3)
plt.plot(ob.xg_hist, ob.nel_hist[-1,:])
plt.grid('on')

colorlist = 'b g r c m k orange b'.split()

dict_bunch = list_bunches[i_bunch_obs]

list_clouave = []
plt.figure(100)
for i_iter in xrange(4):
    for i_ring in [0,1,2,3]:
        color = colorlist[i_ring]
        ob = mlm.myloadmat_to_obj('./cloud_evol_ring%d__iter%d.mat'%(i_ring, i_iter))   # load dictionary of the current simulation
        plt.plot(ob.xg_hist, ob.nel_hist[4,:], label='%d'%i_ring, color=color)
        
        list_clouave.append(np.sum(ob.xg_hist*ob.nel_hist[4,:])/np.sum(ob.nel_hist[4,:]))
plt.legend()

plt.figure(101)
plt.plot(list_clouave, label='cloud centroid')
plt.plot(dict_bunch['mean_x'][1:], label ='bunch centroid' )

plt.legend(loc='best')

plt.show()

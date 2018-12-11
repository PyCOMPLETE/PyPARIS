import sys, os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

import myfilemanager as mfm

import mystyle as ms

tag = 'noecloud'
i_bunch = 3

flag_check_damp_time = True
tau_damp_x = 200.
tau_damp_y = 100.

ob = mfm.myloadmat_to_obj(tag+'_matrices.mat')

plt.close('all')

# Plot transverse positions
fig1 = plt.figure(1)
fig1.set_facecolor('w')
ms.mystyle_arial(fontsz=16)

axx = fig1.add_subplot(2,1,1)
axy = fig1.add_subplot(2,1,2, sharex=axx)

axx.plot(ob.mean_x[:, i_bunch])
axy.plot(ob.mean_y[:, i_bunch])

# Plot transverse spectra
fig2 = plt.figure(2)
fig2.set_facecolor('w')

axfx = fig2.add_subplot(2,1,1)
axfy = fig2.add_subplot(2,1,2, sharex=axfx)

spectx = np.abs(np.fft.rfft(ob.mean_x[:, i_bunch]))
specty = np.abs(np.fft.rfft(ob.mean_y[:, i_bunch]))
freq = np.fft.rfftfreq(len(ob.mean_x[:, i_bunch]))

axfx.plot(freq, spectx)
axfy.plot(freq, specty)

if flag_check_damp_time:
    turn_num = np.arange(0, len(ob.mean_x[:, i_bunch]), dtype=np.float)
    axx.plot(ob.mean_x[0, i_bunch]*np.exp(-turn_num/tau_damp_x))
    axy.plot(ob.mean_y[0, i_bunch]*np.exp(-turn_num/tau_damp_y))

for ax in [axx, axy, axfx, axfy]:
    ax.ticklabel_format(style='sci', scilimits=(0,0),axis='y')

for ax in [axx, axy, axfx, axfy]:
    ax.yaxis.set_major_locator(MaxNLocator(5))

for ax in [axx, axy, axfx, axfy]:
    ax.grid(True)

plt.show()

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

flag_check_Qs = True
Q_s = 5.664e-03

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

# Check longitudinal plane
fig3 = plt.figure(3)
fig3.set_facecolor('w')
axz = fig3.add_subplot(2,1,1, sharex=axx)
axfz = fig3.add_subplot(2,1,2)

axz.plot(ob.mean_z[:-10, i_bunch])
spectz = np.abs(np.fft.rfft(ob.mean_z[:-10, i_bunch]))
spectz[0] = 0. # I am non interested in the average
freqz = np.fft.rfftfreq(len(ob.mean_x[:-10, i_bunch]))
axfz.plot(freqz, spectz)
axfz.axvline(x=Q_s)


if flag_check_damp_time:
    turn_num = np.arange(0, len(ob.mean_x[:, i_bunch]), dtype=np.float)
    axx.plot(ob.mean_x[0, i_bunch]*np.exp(-turn_num/tau_damp_x))
    axy.plot(ob.mean_y[0, i_bunch]*np.exp(-turn_num/tau_damp_y))

for ax in [axx, axy, axfx, axfy, axz, axfz]:
    ax.ticklabel_format(style='sci', scilimits=(0,0),axis='y')

for ax in [axx, axy, axfx, axfy, axz, axfz]:
    ax.yaxis.set_major_locator(MaxNLocator(5))

for ax in [axx, axy, axfx, axfy, axz, axfz]:
    ax.grid(True)

plt.show()

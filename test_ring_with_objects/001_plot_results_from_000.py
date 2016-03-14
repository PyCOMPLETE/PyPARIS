import pylab as pl
import myfilemanager as mfm
import numpy as np

ob = mfm.object_with_arrays_and_scalar_from_h5('beam_coord.h5') 

beam_x = ob.beam_x
beam_y = ob.beam_y
beam_z = ob.beam_z
sx = ob.sx
sy = ob.sy 
sz = ob.sz
epsx = ob.epsx
epsy =	ob.epsy
epsz =	ob.epsz

import pylab as plt

plt.figure(2, figsize=(16, 8), tight_layout=True)
plt.subplot(2,3,1)
plt.plot(beam_x)
plt.ylabel('x [m]');plt.xlabel('Turn')
plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
plt.subplot(2,3,2)
plt.plot(beam_y)
plt.ylabel('y [m]');plt.xlabel('Turn')
plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
plt.subplot(2,3,3)
plt.plot(beam_z)
plt.ylabel('z [m]');plt.xlabel('Turn')
plt.gca().ticklabel_format(style='sci', scilimits=(0,0),axis='y')
plt.subplot(2,3,4)
plt.plot(np.fft.rfftfreq(len(beam_x), d=1.), np.abs(np.fft.rfft(beam_x)))
plt.ylabel('Amplitude');plt.xlabel('Qx')
plt.subplot(2,3,5)
plt.plot(np.fft.rfftfreq(len(beam_y), d=1.), np.abs(np.fft.rfft(beam_y)))
plt.ylabel('Amplitude');plt.xlabel('Qy')
plt.subplot(2,3,6)
plt.plot(np.fft.rfftfreq(len(beam_z), d=1.), np.abs(np.fft.rfft(beam_z)))
plt.xlim(0, 0.1)
plt.ylabel('Amplitude');plt.xlabel('Qz')

fig, axes = plt.subplots(3, figsize=(16, 8), tight_layout=True)
twax = [plt.twinx(ax) for ax in axes]
axes[0].plot(sx)
twax[0].plot(epsx, '-g')
axes[0].set_xlabel('Turns')
axes[0].set_ylabel(r'$\sigma_x$')
twax[0].set_ylabel(r'$\varepsilon_y$')
axes[1].plot(sy)
twax[1].plot(epsy, '-g')
axes[1].set_xlabel('Turns')
axes[1].set_ylabel(r'$\sigma_x$')
twax[1].set_ylabel(r'$\varepsilon_y$')
axes[2].plot(sz)
twax[2].plot(epsz, '-g')
axes[2].set_xlabel('Turns')
axes[2].set_ylabel(r'$\sigma_x$')
twax[2].set_ylabel(r'$\varepsilon_y$')
axes[0].grid()
axes[1].grid()
axes[2].grid()
for ax in list(axes)+list(twax): 
	ax.ticklabel_format(useOffset=False, style='sci', scilimits=(0,0),axis='y')
plt.show()	

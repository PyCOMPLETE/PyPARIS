import numpy as np 
#~ import bunchh5_to_obj as bh5o
import myfilemanager as mfm
import mystyle as ms
import pylab as pl
from scipy.constants import c as ccc


pl.close('all')
ob = mfm.bunchh5_to_obj('bunch_evolution.h5')

pl.figure(1)
pl.subplot(2,3,1)
pl.plot(ob.mean_x)
pl.subplot(2,3,4)
spectrum_x = np.abs(np.fft.rfft(ob.mean_x))
pl.semilogy(np.linspace(0, .5, len(spectrum_x)), spectrum_x)


pl.subplot(2,3,2)
pl.plot(ob.mean_y)
pl.subplot(2,3,5)
spectrum_y = np.abs(np.fft.rfft(ob.mean_y))
pl.semilogy(np.linspace(0, .5, len(spectrum_y)), spectrum_y)

pl.subplot(2,3,3)
pl.plot(ob.epsn_x)
pl.subplot(2,3,6)
pl.plot(ob.epsn_y)
pl.show()

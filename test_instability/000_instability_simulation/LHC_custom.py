from PyHEADTAIL.machines.synchrotron import BasicSynchrotron
import numpy as np
from scipy.constants import c, e, m_p

class LHC(BasicSynchrotron):

	def __init__(self, n_segments, machine_configuration):
		
		
		circumference = 26658.8832

		

		if machine_configuration =='HLLHC-injection':
			charge = e
			mass = m_p
			
			alpha_x        = 0. 
			beta_x         = 92.7 
			D_x            = 0. 
			alpha_y        = 0. 
			beta_y         = 93.2 
			D_y            = 0.

			accQ_x        = 62.28
			accQ_y        = 60.31

			Qp_x           = 0
			Qp_y           = 0

			app_x          = 0.0000e-9
			app_y          = 0.0000e-9
			app_xy         = 0

			alpha     	   = 3.4561e-04
			
			h_RF           = 35640
			V_RF           = 8e6
			dphi_RF        = 0.
			
			
			longitudinal_mode = 'non-linear'
			
			p0 = 450.e9 * e /c
			
			p_increment       = 0.
			
		else:
			raise ValueError('ERROR: unknown machine configuration', machine_configuration)

		
		super(LHC, self).__init__(optics_mode='smooth', circumference=circumference, n_segments=n_segments,
             alpha_x=alpha_x, beta_x=beta_x, D_x=D_x, alpha_y=alpha_y, beta_y=beta_y, D_y=D_y,
             accQ_x=accQ_x, accQ_y=accQ_y, Qp_x=Qp_x, Qp_y=Qp_y, app_x=app_x, app_y=app_y, app_xy=app_xy,
             alpha_mom_compaction=alpha, longitudinal_mode=longitudinal_mode,
             h_RF=np.atleast_1d(h_RF), V_RF=np.atleast_1d(V_RF), dphi_RF=np.atleast_1d(dphi_RF), p0=p0, p_increment=p_increment,
             charge=charge, mass=mass, RF_at='end_of_transverse')

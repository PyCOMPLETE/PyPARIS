import sys, os
BIN = os.path.expanduser("../../../")
sys.path.append(BIN)
BIN = os.path.expanduser("../../")
sys.path.append(BIN)


import communication_helpers as ch
import numpy as np
from scipy.constants import c
import share_segments as shs
import slicing_tool as sl

sigma_z_bunch = 10e-2

machine_configuration = 'HLLHC-injection'
n_segments = 2

octupole_knob = 0.0
Qp_x = 5
Qp_y = 5

flag_aperture = False # not tested

enable_transverse_damper = True
dampingrate_x = 50.
dampingrate_y = 50.

class Simulation(object):
    def __init__(self):
        self.N_turns = 10
        self.N_buffer_float_size = 1000000
        self.N_buffer_int_size = 100
        self.N_parellel_rings = 3
        
        self.n_slices_per_bunch = 10
        self.z_cut_slicing = sigma_z_bunch

    def init_all(self):

        from LHC_custom import LHC
        self.machine = LHC(n_segments = n_segments, machine_configuration = machine_configuration,
                        Qp_x=Qp_x, Qp_y=Qp_y,
                        octupole_knob=octupole_knob)
        self.n_non_parallelizable = 1 #RF


        if flag_aperture: # never tested, to be introduced together with coulds
            # setup transverse losses (to "protect" the ecloud)
            import PyHEADTAIL.aperture.aperture as aperture
            apt_xy = aperture.EllipticalApertureXY(x_aper=target_size_internal_grid_sigma*sigma_x, 
                                                   y_aper=target_size_internal_grid_sigma*sigma_y)
            self.machine.one_turn_map.append(apt_xy)
            self.n_non_parallelizable +=1 

        if enable_transverse_damper:
            # setup transverse damper
            from PyHEADTAIL.feedback.transverse_damper import TransverseDamper
            damper = TransverseDamper(dampingrate_x=dampingrate_x, dampingrate_y=dampingrate_y)
            self.machine.one_turn_map.append(damper)
            self.n_non_parallelizable +=1



        
    def init_master(self):
        
        print('Building the beam!')
        
        from scipy.constants import c as clight, e as qe
        from PyHEADTAIL.particles.slicing import UniformBinSlicer
        
        b_spac_s = 25e-9
        non_linear_long_matching = False
        
        bunch_intensity = 1e11
        epsn_x = 2.5e-6
        epsn_y = 3.5e-6
        sigma_z = sigma_z_bunch

        #Filling pattern: here head is left and tail is right
        # filling_pattern = [1., 0., 0., 1., 1., 1., 0.]
        filling_pattern = 5*[1]
        macroparticlenumber = 100000
        min_inten_slice4EC = 1e7
        
        
        import gen_multibunch_beam as gmb
        list_bunches = gmb.gen_matched_multibunch_beam(self.machine, macroparticlenumber, filling_pattern, b_spac_s, 
                bunch_intensity, epsn_x, epsn_y, sigma_z, non_linear_long_matching, min_inten_slice4EC)


        return list_bunches
        
    def treat_piece(self, piece):
        pass

    def slice_bunch_at_start_ring(self, bunch):
        list_slices = sl.slice_a_bunch(bunch, self.z_cut_slicing, self.n_slices_per_bunch)
        return list_slices
        
    def merge_slices_and_perform_bunch_operations_at_end_ring(self, list_slices):
        bunch = sl.merge_slices_into_bunch(list_slices)
        # here perform synchrotron motion
        return bunch

    def piece_to_buffer(self, piece):
        buf = ch.beam_2_buffer(piece)
        return buf

    def buffer_to_piece(self, buf):
        piece = ch.buffer_2_beam(buf)
        return piece




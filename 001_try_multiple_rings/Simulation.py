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

class Simulation(object):
    def __init__(self):
        self.N_turns = 128
        self.N_buffer_float_size = 500000
        self.N_buffer_int_size = 450
        self.N_parellel_rings = 3
        
        self.n_slices_per_bunch = 10
        self.z_cut_slicing = sigma_z_bunch

    def init_all(self):
        from LHC import LHC
        machine = LHC(machine_configuration='Injection', n_segments=43, D_x=0., 
                        RF_at='end_of_transverse')
        self.machine = machine
        
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
        filling_pattern = [1., 0., 0., 1., 1., 1., 0.]
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

    def piece_to_buffer(self, piece):
        buf = ch.beam_2_buffer(piece)
        return buf

    def buffer_to_piece(self, buf):
        piece = ch.buffer_2_beam(buf)
        return piece





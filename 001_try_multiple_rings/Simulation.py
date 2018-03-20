import sys, os
BIN = os.path.expanduser("../../../")
sys.path.append(BIN)
BIN = os.path.expanduser("../../")
sys.path.append(BIN)


import communication_helpers as ch
import numpy as np
from scipy.constants import c
import share_segments as shs


class Simulation(object):
    def __init__(self):
        self.N_turns = 128
        self.N_buffer_float_size = 500000
        self.N_buffer_int_size = 450
        self.N_parellel_rings = 3

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
        
        intensity = 1e11
        epsn_x = 2.5e-6
        epsn_y = 3.5e-6
        sigma_z = 10e-2

        #Filling pattern: here head is left and tail is right
        filling_pattern = [1., 0., 0., 1., 1., 1., 0.]
        macroparticlenumber_track = 100000
        
        machine = self.machine
        
        bucket_length_m = machine.circumference/(machine.longitudinal_map.harmonics[0])
        b_spac_m =  b_spac_s*machine.beta*clight
        b_spac_buckets = np.round(b_spac_m/bucket_length_m)

        if non_linear_long_matching:
            generate_bunch = machine.generate_6D_Gaussian_bunch_matched
        else:
            generate_bunch = machine.generate_6D_Gaussian_bunch

        list_genbunches = []
        for i_slot, inten_slot in enumerate(filling_pattern):
            if inten_slot>0:
                bunch = generate_bunch(macroparticlenumber_track, inten_slot*intensity, epsn_x, epsn_y, sigma_z=sigma_z)
                bunch.z -= b_spac_buckets*bucket_length_m*i_slot
                list_genbunches.append(bunch)

        beam = sum(list_genbunches)

        bucket = machine.longitudinal_map.get_bucket(gamma=machine.gamma, mass=machine.mass, charge=machine.charge)
        # z_beam_center = bucket.z_ufp_separatrix + bucket_length - self.circumference/2.

        # Here the center of the bucket
        bucket.z_sfp

        # I want to re-separate the bunches
        buncher = UniformBinSlicer(n_slices = 0, z_sample_points = np.arange(bucket.z_sfp-len(filling_pattern)*bucket_length_m*b_spac_buckets, 
                                                bucket.z_sfp+bucket_length_m, bucket_length_m*b_spac_buckets))
        buncher_slice_set = beam.get_slices(buncher, statistics=True)
        list_bunches = beam.extract_slices(buncher, include_non_sliced='never')
        
        return list_bunches

    def init_worker(self):
        pass

    def treat_piece(self, piece):
        for ele in self.mypart: 
                ele.track(piece)

    def finalize_turn_on_master(self, pieces_treated):
    

        return orders_to_pass, new_pieces_to_be_treated


    def execute_orders_from_master(self, orders_from_master):
        pass



        
    def finalize_simulation(self):
        pass
        

    def piece_to_buffer(self, piece):
        buf = ch.beam_2_buffer(piece)
        return buf

    def buffer_to_piece(self, buf):
        piece = ch.buffer_2_beam(buf)
        return piece




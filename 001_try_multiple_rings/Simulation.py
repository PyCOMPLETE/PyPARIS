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
        pass
        
    def init_master(self):
        return []

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




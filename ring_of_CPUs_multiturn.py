import numpy as np

import communication_helpers as ch

logfilename = 'pyparislog.txt'
def print2logandstdo(message, mode='a+'):
    print message
    with open(logfilename, mode) as fid:
        fid.writelines([message+'\n'])


class RingOfCPUs_multiturn(object):
    def __init__(self, sim_content, N_pieces_per_transfer=1, force_serial = False, comm=None,
                    N_parellel_rings = 1,
                    N_buffer_float_size = 1000000, N_buffer_int_size = 100,
                    verbose = False):
        
        self.sim_content = sim_content
        self.N_turns = sim_content.N_turns
        
        self.N_pieces_per_transfer = N_pieces_per_transfer
        self.N_buffer_float_size = N_buffer_float_size
        self.N_buffer_int_size = N_buffer_int_size
        self.N_parellel_rings = N_parellel_rings
        
        if hasattr(sim_content, 'N_pieces_per_transfer'):
            self.N_pieces_per_transfer = sim_content.N_pieces_per_transfer
            
        if hasattr(sim_content, 'N_buffer_float_size'):
            self.N_buffer_float_size = sim_content.N_buffer_float_size
            
        if hasattr(sim_content, 'N_buffer_int_size'):
            self.N_buffer_int_size = sim_content.N_buffer_int_size

        if hasattr(sim_content, 'N_parellel_rings'):
            self.N_parellel_rings = sim_content.N_parellel_rings
        
        
        self.sim_content.ring_of_CPUs = self
        
        # choice of the communicator
        if force_serial:
            comm_info = 'Single CPU forced by user.'
            self.comm = SingleCoreComminicator()
        elif comm is not None:
            comm_info = 'Multiprocessing using communicator provided as argument.'
            self.comm = comm
        else:
            comm_info = 'Multiprocessing via MPI.'
            from mpi4py import MPI
            self.comm = MPI.COMM_WORLD
            
        #check if there is only one node
        if self.comm.Get_size()==1:
            #in case it is forced by user it will be rebound but there is no harm in that
            self.comm = SingleCoreComminicator()
            
        # get info on the grid
        self.N_nodes = self.comm.Get_size()
        self.N_wkrs = self.N_nodes-1
        self.master_id = 0
        self.myid = self.comm.Get_rank()
        self.I_am_a_worker = self.myid!=self.master_id
        self.I_am_the_master = not(self.I_am_a_worker)
        
        # Handle multiturn parallelism
        if np.mod(self.N_nodes, self.N_parellel_rings) !=0:
            raise ValueError('Number of note must be a multiple of number of rings!')
            
        self.N_nodes_per_ring = int(float(self.N_nodes)/float(self.N_parellel_rings))
        self.myring = int(np.floor(float(self.myid)/float(self.N_nodes_per_ring)))
        self.myid_in_ring = int(np.mod(float(self.myid),float(self.N_nodes_per_ring)))
        self.I_am_at_start_ring = self.myid_in_ring == 0
        self.I_am_at_end_ring = self.myid_in_ring == (self.N_parellel_rings-1)
        
        if verbose:
            print("I am %d, master=%s, myring=%d, myid_in_ring=%d (%s%s)"%(
                        self.myid, repr(self.I_am_the_master), self.myring, self.myid_in_ring,
                        {True:'start_ring', False:''}[self.I_am_at_start_ring], 
                        {True:'end_ring', False:''}[self.I_am_at_end_ring]))

        # allocate buffers for communication
        self.buf_float = np.zeros(self.N_buffer_float_size, dtype=np.float64)
        self.buf_int = np.array(self.N_buffer_int_size*[0])

        self.sim_content.init_all()
        
        self.comm.Barrier() # only for stdoutp
        
        if self.I_am_the_master:
            print2logandstdo('PyPARIS simulation -- multiturn parallelization')#, mode='w+')
            print2logandstdo(comm_info)
            print2logandstdo('N_cores = %d'%self.N_nodes)
            print2logandstdo('N_pieces_per_transfer = %d'%self.N_pieces_per_transfer)
            print2logandstdo('N_buffer_float_size = %d'%self.N_buffer_float_size)
            print2logandstdo('N_buffer_int_size = %d'%self.N_buffer_int_size)
            print2logandstdo('Multi-ring info:')
            print2logandstdo('N_parellel_rings = %d'%self.N_parellel_rings)
            print2logandstdo('N_nodes_per_ring = %d'%self.N_nodes_per_ring)
            import socket
            import sys
            print2logandstdo('Running on %s'%socket.gethostname())
            print2logandstdo('Interpreter at %s'%sys.executable)			
        
        self.comm.Barrier() # only for stdoutp
        
        if self.I_am_at_start_ring:
            from collections import deque
            self.bunches_to_be_treated = deque([])
        
        if self.I_am_the_master:
            list_bunches = sim_content.init_master()
            self.bunches_to_be_treated.extend(list_bunches)
            
        


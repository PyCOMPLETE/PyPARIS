import numpy as np

import communication_helpers as ch
from collections import deque

logfilename = 'pyparislog.txt'
def print2logandstdo(message, mode='a+'):
    print message
    with open(logfilename, mode) as fid:
        fid.writelines([message+'\n'])
        
verbose = False


class RingOfCPUs_multiturn(object):
    def __init__(self, sim_content, N_pieces_per_transfer=1, force_serial = False, comm=None,
                    N_parellel_rings = 1,
                    N_buffer_float_size = 1000000, N_buffer_int_size = 100,
                    verbose = False):
        
        if N_pieces_per_transfer>1:
            raise ValueError("Not implemented!")

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
        
        self.left = int(np.mod(self.myid-1, self.N_nodes))
        self.right = int(np.mod(self.myid+1, self.N_nodes))

        if self.I_am_at_start_ring:
            self.bunches_to_be_treated = deque([])
            self.slices_to_be_treated = []

        if self.I_am_at_end_ring:
            self.slices_treated = deque([])
        
        if self.I_am_the_master:
            list_bunches = sim_content.init_master()
            self.bunches_to_be_treated.extend(list_bunches)
            
        self.comm.Barrier()

    def run(self):
        
        
        iteration = 0
        list_received_buffers = [self.sim_content.piece_to_buffer(None)]
        while True:

            orders_from_master = []
            
            if self.I_am_at_start_ring:
                
                # If a bunch is received put in the queue
                buffer_received = list_received_buffers[0]
                bunch_received = self.sim_content.buffer_to_piece(buffer_received)
                if bunch_received is not None:
                    self.bunches_to_be_treated.appendleft(bunch_received)

                # If slices_to_be_treated is empty pop a bunch
                if len(self.slices_to_be_treated)==0 and len(self.bunches_to_be_treated)>0:
                    next_bunch = self.bunches_to_be_treated.pop()
                    next_bunch.slice_info['i_turn']+=1
                    self.slices_to_be_treated = self.sim_content.slice_bunch_at_start_ring(next_bunch)
                    
                    if self.myring==0 and self.myid_in_ring == 0:
                        print'Iter%03d - I am %d.%d startin bunch %d/%d turn=%d'%(iteration, self.myring, self.myid_in_ring,
                                        next_bunch.slice_info['i_bunch'], next_bunch.slice_info['N_bunches_tot_beam'], next_bunch.slice_info['i_turn'])
                
                # Pop a slice    
                if len(self.slices_to_be_treated)>0:
                    thisslice = self.slices_to_be_treated.pop()
                else:
                    thisslice = None
                    
                # Treat the slice
                if thisslice is not None:
                    self.sim_content.treat_piece(thisslice)
                self._print_some_info_on_comm(thisslice, iteration, verbose)
                   
                # Slice to buffer
                buf = self.sim_content.piece_to_buffer(thisslice)
            
            elif self.I_am_at_end_ring:
                # Buffer to slice
                recbuf = list_received_buffers[0]
                thisslice = self.sim_content.buffer_to_piece(recbuf)
                
                # Treat the slice
                if thisslice is not None:
                    self.sim_content.treat_piece(thisslice)
                self._print_some_info_on_comm(thisslice, iteration, verbose)

                # Put the slice in slices_treated
                bunch_to_be_sent = None
                if thisslice is not None:
                   self.slices_treated.appendleft(thisslice) 
                   if len(self.slices_treated) == self.slices_treated[0].slice_info['N_slices_tot_bunch']:
                        bunch_to_be_sent = self.sim_content.merge_slices_and_perform_bunch_operations_at_end_ring(self.slices_treated)
                        self.slices_treated = deque([])

                   
                buf = self.sim_content.piece_to_buffer(bunch_to_be_sent)
            
            else:  #Standard node                 
                # Buffer to slice
                recbuf = list_received_buffers[0]
                thisslice = self.sim_content.buffer_to_piece(recbuf)
                
                # Treat the slice
                if thisslice is not None:
                    self.sim_content.treat_piece(thisslice)
                self._print_some_info_on_comm(thisslice, iteration, verbose)

                # Slice to buffer
                buf = self.sim_content.piece_to_buffer(thisslice)
        
                
            list_of_buffers_to_send = [buf]
            sendbuf = ch.combine_float_buffers(list_of_buffers_to_send)
            if len(sendbuf) > self.N_buffer_float_size:
                raise ValueError('Float buffer (%d) is too small!\n %d required.'%(self.N_buffer_float_size, len(sendbuf)))
            self.comm.Sendrecv(sendbuf, dest=self.right, sendtag=self.right, 
                        recvbuf=self.buf_float, source=self.left, recvtag=self.myid)
            list_received_buffers = ch.split_float_buffers(self.buf_float)
            
            # print('Iter%d - I am %d and I received %d'%(iteration, self.myid, int(list_received_buffers[0][0])))
            

            # Handle orders (for now only to stop simulations)
            if self.I_am_the_master:
                # send orders
                buforders = ch.list_of_strings_2_buffer(orders_from_master)
                if len(buforders) > self.N_buffer_int_size:
                    raise ValueError('Int buffer is too small!')
                self.comm.Bcast(buforders, self.master_id)
            else:    
                # receive orders from the master
                self.comm.Bcast(self.buf_int, self.master_id)
                orders_from_master = ch.buffer_2_list_of_strings(self.buf_int)

            # check if simulation has to be ended
            if 'stop' in orders_from_master:
                break


            
            iteration+=1

            # (TEMPORARY!) To stop
            self.comm.Barrier()
            if iteration==100:
                break
            # (TEMPORARY!)
            
    def _print_some_info_on_comm(self, thisslice, iteration, verbose):
        if verbose:
            if thisslice is not None:
                print('Iter%03d - I am %d.%d and I treated slice %d/%d of bunch %d/%d'%(iteration, 
                                                self.myring, self.myid_in_ring,
                                                thisslice.slice_info['i_slice'], thisslice.slice_info['N_slices_tot_bunch'], 
                                                thisslice.slice_info['info_parent_bunch']['i_bunch'], 
                                                thisslice.slice_info['info_parent_bunch']['N_bunches_tot_beam']))
            else:
                print('Iter%03d - I am %d.%d and I treated None'%(iteration, self.myring, self.myid_in_ring))      


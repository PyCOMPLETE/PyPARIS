from PyHEADTAIL.particles.particles import Particles
from PyHEADTAIL.particles.slicing import UniformBinSlicer

import numpy as np


def slice_a_bunch(this_bunch, z_cut, n_slices):

    # Slice bunch if populated
    if this_bunch.slice_info['slice_4_EC']:
        bunch_center = this_bunch.slice_info['z_bin_center']
        this_slicer = UniformBinSlicer(z_cuts=(bunch_center-z_cut, bunch_center+z_cut), n_slices=n_slices)
        this_slices = this_bunch.extract_slices(this_slicer, include_non_sliced='always')
           
        sliced = this_slices[:-1]
        unsliced = this_slices[-1]
        if unsliced.slice_info!='unsliced':
            raise ValueError("Something went wrong")
            
        for ss in sliced:
            ss.slice_info['interact_with_EC'] = True
            
        # Build head and tail slices
        mask_head = unsliced.z>=sliced[-1].slice_info['z_bin_right']
        mask_tail = unsliced.z<=sliced[0].slice_info['z_bin_left']
        
        
        slice_tail = Particles(macroparticlenumber=np.sum(mask_tail),
                            particlenumber_per_mp=unsliced.particlenumber_per_mp, 
                            charge=unsliced.charge,
                            mass=unsliced.mass, circumference=unsliced.circumference, 
                            gamma=unsliced.gamma, 
                            coords_n_momenta_dict={\
                                'x': np.atleast_1d(unsliced.x[mask_tail]),
                                'xp':np.atleast_1d(unsliced.xp[mask_tail]),
                                'y':np.atleast_1d(unsliced.y[mask_tail]),
                                'yp':np.atleast_1d(unsliced.yp[mask_tail]),	
                                'z':np.atleast_1d(unsliced.z[mask_tail]),
                                'dp':np.atleast_1d(unsliced.dp[mask_tail])})
        slice_tail.slice_info={
            'z_bin_center': 0.5*(this_bunch.slice_info['z_bin_left']+sliced[0].slice_info['z_bin_left']),
            'z_bin_left': this_bunch.slice_info['z_bin_left'],
            'z_bin_right': sliced[0].slice_info['z_bin_left'],
            'interact_with_EC': False}
        
        
        slice_head = Particles(macroparticlenumber=np.sum(mask_head),
                            particlenumber_per_mp=unsliced.particlenumber_per_mp, 
                            charge=unsliced.charge,
                            mass=unsliced.mass, circumference=unsliced.circumference, 
                            gamma=unsliced.gamma, 
                            coords_n_momenta_dict={\
                                'x': np.atleast_1d(unsliced.x[mask_head]),
                                'xp':np.atleast_1d(unsliced.xp[mask_head]),
                                'y':np.atleast_1d(unsliced.y[mask_head]),
                                'yp':np.atleast_1d(unsliced.yp[mask_head]),	
                                'z':np.atleast_1d(unsliced.z[mask_head]),
                                'dp':np.atleast_1d(unsliced.dp[mask_head])})
        slice_head.slice_info={
            'z_bin_center': 0.5*(this_bunch.slice_info['z_bin_right']+sliced[-1].slice_info['z_bin_right']),
            'z_bin_left': sliced[-1].slice_info['z_bin_right'],
            'z_bin_right': this_bunch.slice_info['z_bin_right'],
            'interact_with_EC': False}
        
        list_slices_this_bunch = [slice_tail] + sliced + [slice_head]
        
    else:
        list_slices_this_bunch = [this_bunch]
        
    return list_slices_this_bunch

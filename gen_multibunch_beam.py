from scipy.constants import c as clight, e as qe
import numpy as np

from PyHEADTAIL.particles.slicing import UniformBinSlicer

def gen_matched_multibunch_beam(machine, n_macroparticles_per_bunch, filling_pattern, 
        b_spac_s, bunch_intensity, epsn_x, epsn_y, sigma_z, non_linear_long_matching, min_inten_slice4EC):

    bucket_length_m = machine.circumference/(machine.longitudinal_map.harmonics[0])
    b_spac_m =  b_spac_s*machine.beta*clight
    b_spac_buckets = np.round(b_spac_m/bucket_length_m)

    if np.abs(b_spac_buckets*bucket_length_m-b_spac_m)/b_spac_m > 0.03:
        raise ValueError('Bunch spacing is not a multiple of the bucket length!')

    if non_linear_long_matching:
        generate_bunch = machine.generate_6D_Gaussian_bunch_matched
    else:
        generate_bunch = machine.generate_6D_Gaussian_bunch

    list_genbunches = []
    for i_slot, inten_slot in enumerate(filling_pattern):
        if inten_slot>0:
            print('Generating bunch at slot %d/%d'%(i_slot, len(filling_pattern)))
            bunch = generate_bunch(n_macroparticles_per_bunch, inten_slot*bunch_intensity, epsn_x, epsn_y, sigma_z=sigma_z)
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
    # The bunch at position 0 is the tail
    
    # If last bunch is empty remove it
    if (list_bunches[0].intensity<min_inten_slice4EC):
        list_bunches = list_bunches[1:]
    
    # Add further information to bunches
    for i_bb, bb in enumerate(list_bunches[::-1]): # I want bunch 0 at the head of the train
        slice4EC = bb.intensity>min_inten_slice4EC
        bb.slice_info['slice_4_EC'] = slice4EC
        bb.slice_info['interact_with_EC'] = slice4EC
        bb.slice_info['N_bunches_tot_beam'] = len(list_bunches)
        bb.slice_info['i_bunch'] = i_bb
    bb.slice_info['i_turn'] = 0
        

       
    
    return list_bunches

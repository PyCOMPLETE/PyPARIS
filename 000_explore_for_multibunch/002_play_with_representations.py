import numpy as np

a = {
'a': 1.234567890,
'b': 'pippo',
'c': 3}

import pickle
pss = pickle.dumps(a, protocol=2)

# Pad to have a multiple of 8 bytes
s1arr = np.frombuffer(pss, dtype='S1')
ll = len(s1arr)
s1arr_padded = np.concatenate((s1arr, np.zeros(8-ll%8, dtype='S1')))

# Cast to array of floats
f8arr = np.frombuffer(s1arr_padded, dtype='<f8')
message = np.concatenate((np.array([ll], dtype='<f8'),f8arr))


# Trying to go back
llrec = int(message[0])
s1back_padded = np.frombuffer(message[1:].tobytes(), dtype='S1') 
s1back = s1back_padded[:llrec]
pss_rec = s1back.tobytes()

a_rec = pickle.loads(pss_rec)


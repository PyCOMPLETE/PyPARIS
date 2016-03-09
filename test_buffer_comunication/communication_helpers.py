import numpy as np


def list_of_strings_2_buffer(strlist):
	data = ''.join(map(lambda s:s+';', strlist))+'\n'
	buf_to_send = np.int_(np.array(map(ord, list(data))))
	return buf_to_send
	
def buffer_2_list_of_strings(buf):
	str_received = ''.join(map(unichr, list(buf)))
	strlist = map(str, str_received.split('\n')[0].split(';'))[:-1]
	return strlist

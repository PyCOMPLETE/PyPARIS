#!/usr/bin/env python

import numpy as np
import os, sys
import importlib

BIN = os.path.expanduser("./")
sys.path.append(BIN)

if len(sys.argv)!=2:
    raise ValueError('\n\nSyntax must be:\n\t serialexec.py sim_class=module.class\n\n')
if 'sim_class' not in sys.argv[1]:
    raise ValueError('\n\nSyntax must be:\n\t serialexec.py sim_class=module.class\n\n')

sim_module_string = sys.argv[1].split('=')[-1]

sim_module_strings = sim_module_string.split('.')

# if len(sim_module_strings)!=2:
#     raise(ValueError('\n\nsim_class must be given in the form: module.class.\nNested referencing not implemented.\n\n'))
module_name = '.'.join(sim_module_strings[:-1])
class_name = sim_module_strings[-1]

SimModule = importlib.import_module(module_name)
SimClass = getattr(SimModule, class_name)

from PyPARIS.ring_of_CPUs import RingOfCPUs
simulation_content = SimClass()
myCPUring = RingOfCPUs(simulation_content, force_serial=True)
myCPUring.run()
					
	

	

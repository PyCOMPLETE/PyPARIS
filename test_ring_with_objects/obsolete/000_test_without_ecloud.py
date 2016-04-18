import sys, os
BIN = os.path.expanduser("../../")
sys.path.append(BIN)
BIN = os.path.expanduser("../")
sys.path.append(BIN)

from ring_of_CPUs import RingOfCPUs
from Simulation import Simulation
simulation_content = Simulation()

myCPUring = RingOfCPUs(simulation_content, N_pieces_per_transfer=5)

myCPUring.run()

#!/usr/bin/bash

# Run Parallel without MPI
../multiprocexec.py -n 3 sim_class=Simulation.Simulation

# Run Serial
# ../serialexec.py sim_class=Simulation.Simulation

# Run MPI
# mpiexec -n 4 ../withmpi.py sim_class=Simulation.Simulation

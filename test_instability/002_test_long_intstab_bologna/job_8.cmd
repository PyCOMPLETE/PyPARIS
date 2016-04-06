#BSUB -J long
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -N
#BSUB -B
#BSUB -q hpc_inf
#BSUB -a openmpi
#BSUB -n 8
#BSUB -R span[ptile=32]
/usr/share/lsf/9.1/linux2.6-glibc2.3-x86_64/bin/mpirun.lsf env PSM_SHAREDCONTEXTS_MAX=8 python 001_parallel_test.py >> opic.txt 2>> epic.txt

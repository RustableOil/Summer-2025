#! /bin/bash

#SBATCH --account=def-belandl1
#SBATCH --time=0-4:0
#SBATCH --ntasks=64  # num MPI tasks
#SBATCH --mem-per-cpu=256M

for T in 700 800 900 1000 1100; do
    mpirun ./lmp_mpi -in Ni.in -var size 8 -var temp $T -var index 1
done

for T in 700 800 900 1000 1100; do
    mpirun ./lmp_mpi -in NiFe.in -var size 8 -var temp $T -var index 1
done

for T in 700 800 900 1000 1100; do
    mpirun ./lmp_mpi -in NiFeCr.in -var size 8 -var temp $T -var index 1
done

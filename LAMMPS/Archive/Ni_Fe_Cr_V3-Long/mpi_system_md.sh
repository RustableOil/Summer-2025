#! /bin/bash

#SBATCH --account=def-belandl1
#SBATCH --time=0-16:0
#SBATCH --ntasks=64  # num MPI tasks
#SBATCH --mem-per-cpu=16M
#SBATCH --array=1-25

for T in 700 800 900 1000 1100; do
    mpirun ./lmp_mpi -in Ni.in -var size 8 -var temp $T -var index $SLURM_ARRAY_TASK_ID
done

for T in 700 800 900 1000 1100; do
    mpirun ./lmp_mpi -in NiFe.in -var size 8 -var temp $T -var index $SLURM_ARRAY_TASK_ID
done

for T in 700 800 900 1000 1100; do
    mpirun ./lmp_mpi -in NiFeCr.in -var size 8 -var temp $T -var index $SLURM_ARRAY_TASK_ID
done

#! /bin/bash

#SBATCH --account=def-belandl1
#SBATCH --time=2-0:0
#SBATCH --ntasks=64
#SBATCH --mem-per-cpu=256M
#SBATCH --array=1-100

for T in 700 800 900 1000 1100; do
    mpirun -np 64 ./lmp_mpi -in Ni.in -var size 8 -var temp $T -var index $SLURM_ARRAY_TASK_ID
done

for T in 700 800 900 1000 1100; do
    mpirun -np 64 ./lmp_mpi -in NiFe.in -var size 8 -var temp $T -var index $SLURM_ARRAY_TASK_ID
done

for T in 700 800 900 1000 1100; do
    mpirun -np 64 ./lmp_mpi -in NiFeCr.in -var size 8 -var temp $T -var index $SLURM_ARRAY_TASK_ID
done

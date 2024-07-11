#! /bin/bash
#SBATCH --array=1-7680%1000
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=20GB
#SBATCH --job-name=tclean_and_concat
#SBATCH --output=logs/tclean_and_concat_%A_%a.out
#SBATCH --error=logs/tclean_and_concat_%A_%a.err
#SBATCH --time=3:00:00

export OMP_NUM_THREADS=1

source /lustre/aoc/sciops/ssekhar/soft/py38/bin/activate

srun python tclean.py /lustre/aoc/projects/ngvla/archive_ms_v4/ALMA/2019.1.00592.S/ms_v2/uid___A002_Xf0fd41_X5f5a_target.ms --channel_number $SLURM_ARRAY_TASK_ID --imsize 4096 --cell 0.004arcsec --spw 25 --gridder=mosaic --stokes=I --usemask=auto-multithresh --niter=50000 --threshold='2mJy'

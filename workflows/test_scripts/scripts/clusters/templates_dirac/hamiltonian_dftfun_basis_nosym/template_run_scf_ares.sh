#!/bin/bash -l
#SBATCH -J molname_scf
#SBATCH -N 1
#SBATCH --ntasks-per-node=cluster_ntasks
#SBATCH --mem-per-cpu=5GB
#SBATCH --time=cluster_timeh:00:00 
#SBATCH -A plgqctda2-cpu
#SBATCH -p cluster_part
#SBATCH --output="output.out"
#SBATCH --error="error.err"

scratch=$SCRATCH/data_dir_in_scratch
mkdir -p $scratch

# scratch for this calcs:
export data_dir=$PLG_GROUPS_STORAGE/plggqcembed/data_dir_in_scratch
export bin_dir=$data_dir/binfiles
export out_dir=$data_dir/outputs
export plot_dir=$data_dir/plotfiles

mkdir -p $data_dir
mkdir -p $bin_dir
mkdir -p $out_dir
mkdir -p $plot_dir

cd $SLURM_SUBMIT_DIR
srun /bin/hostname

module purge
module use /net/people/plgrid/plggosiao/privatemodules
module load dirac-master-public

mol=molname.xyz
inp_dir=inputs
inp_scf=$inp_dir/scf.inp

echo "#--- Job started at `date`"
pam --scratchfull=$scratch --mw=900 --nw=900 --ag=20 --mpi=$SLURM_NPROCS \
    --inp=$inp_scf --mol=$mol \
    --get="CHECKPOINT.h5=$bin_dir/CHECKPOINT.h5"

echo "#--- Job ended at `date`"

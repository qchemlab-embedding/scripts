#!/bin/bash -l
#SBATCH -J THIS_jobname
#SBATCH -N 1
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=5GB
#SBATCH --time=72:00:00 
#SBATCH -A plgqcembed-cpu
#SBATCH -p plgrid
#SBATCH --output="output.out"
#SBATCH --error="error.err"

data_dir=$PLG_GROUPS_STORAGE/plggqcembed/YOUR_subdirectory/THIS-storage/pyadf_tests/simple
mkdir -p $data_dir

project=simple
cp $project.pyadf   $data_dir
cp coordinates/*    $data_dir

srun /bin/hostname
conda activate /net/pr2/projects/plgrid/plggqcembed/devel/tools/conda_environments/pyadf-main-env/env
config='/net/pr2/projects/plgrid/plggqcembed/devel/tools/pyadf-jobrunner.conf'

cd $data_dir

# this job is run in storage space since ADF can generate large temp files;
# please systematically remove large files from your $HOME and from your $PLG_GROUPS_STORAGE subdirectories!

# to save results add -s flag:
# pyadf -s -c $config $project.pyadf
# otherwise:
pyadf -c $config  $project.pyadf

# you can copy essential outputs back to your $HOME:
cp *out $SLURM_SUBMIT_DIR/

cd $SLURM_SUBMIT_DIR


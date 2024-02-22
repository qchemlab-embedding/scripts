#!/bin/bash -l
#SBATCH -J pyadf_test
#SBATCH -N 1
#SBATCH --ntasks-per-node=8
#SBATCH --mem-per-cpu=5GB
#SBATCH --time=01:00:00 
#SBATCH -A plgqcembed-cpu
#SBATCH -p plgrid-testing
#SBATCH --output="output.out"
#SBATCH --error="error.err"

# adapt this:
scratch=$SCRATCH/gosia-scratch/pyadf-tests/geometry_optimization_ADF
mkdir -p $scratch

data_dir=$PLG_GROUPS_STORAGE/plggqcembed/gosia-storage/pyadf_tests/geometry_optimization_ADF
mkdir -p $data_dir


project=geom
cp $project.pyadf $data_dir
cp -r coordinates $data_dir

# normally, this should not need to be adapted:
srun /bin/hostname

module purge
module use /net/pr2/projects/plgrid/plggqcembed/groupmodules
module load pyadf-master

cd $SLURM_SUBMIT_DIR
config='/net/pr2/projects/plgrid/plggqcembed/devel/tools/pyadf-jobrunner.conf'

# to save results add -s flag:
# pyadf -s --jobrunnerconf $config $project.pyadf
# otherwise (note - execution in storage, since ADF can generate large temp files):
cd $data_dir
pyadf --jobrunnerconf $config $project.pyadf
cp *out    $SLURM_SUBMIT_DIR
cp -r data $SLURM_SUBMIT_DIR
cd $SLURM_SUBMIT_DIR


#!/bin/bash -l
#SBATCH -J pyadf_test
#SBATCH -N 1
#SBATCH --ntasks-per-node=16
#SBATCH --mem-per-cpu=5GB
#SBATCH --time=01:00:00 
#SBATCH -A plgqcembed-cpu
#SBATCH -p plgrid-testing
#SBATCH --output="output.out"
#SBATCH --error="error.err"

# normally, this should not need to be adapted:
srun /bin/hostname
module purge
module use /net/pr2/projects/plgrid/plggqcembed/groupmodules
module load pyadf-devel

# adapt this:
scratch=$SCRATCH/gosia-scratch/pyadf-tests/prp
mkdir -p $scratch
data_dir='/net/pr2/projects/plgrid/plggqcembed/gosia-storage/pyadf/tests/pyadf_scripts/test_usage_response_properties/nmr_shieldings'
mkdir -p $data_dir

# we do calculations from the storage space, as we will also save large numerical grids
home_dir=`pwd`
project=prp_scalarZORA_super_isolated
config='/net/pr2/projects/plgrid/plggqcembed/devel/tools/pyadf-jobrunner.conf'

cp $project.pyadf $data_dir
cp -r coordinates $data_dir

cd $data_dir
pyadf --jobrunnerconf $config $project.pyadf
cp $data_dir/*out $home_dir/
cd $home_dir


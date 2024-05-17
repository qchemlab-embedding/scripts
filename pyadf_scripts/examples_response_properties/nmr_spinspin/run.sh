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


# select one of these to test:
#project=prp_scalarZORA_super
#project=prp_soZORA_super
project=prp_scalarZORA_super_fde

# adapt your data_dir
data_dir=$PLG_GROUPS_STORAGE/plggqcembed/gosia-storage/pyadf_tests/pyadf_scripts/examples_response_properties/nmr_spinspin/$project
mkdir -p $data_dir

# these do not need to be changed
cp $project.pyadf $data_dir
cp coordinates/*  $data_dir

srun /bin/hostname

module load miniconda3/23.5.2-0
eval "$(conda shell.bash hook)"

conda activate /net/pr2/projects/plgrid/plggqcembed/devel/tools/conda_environments/pyadf-devel-nmr-env/env
export PYADFHOME=/net/pr2/projects/plgrid/plggqcembed/devel/pyadf-devel-nmr
config='/net/pr2/projects/plgrid/plggqcembed/devel/tools/pyadf-jobrunner-ADF2021.conf'

cd $data_dir
pyadf -c $config  $project.pyadf
cp *out $SLURM_SUBMIT_DIR/
cd $SLURM_SUBMIT_DIR

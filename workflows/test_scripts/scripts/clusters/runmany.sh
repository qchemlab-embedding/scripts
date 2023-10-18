#!/bin/bash

here=`pwd`
base_dir=$here/jobs/project_name
local_dir=$base_dir/explorations

# ---- adapt -------
mol_names=()
softwares=()
models=()
groups=()
# ------------------


for m in ${mol_names[*]}
  do
  for s in ${softwares[*]}
    do
    for t in ${models[*]}
      do
      for g in ${groups[*]}
        do
          calcdir=$local_dir/$m/$s/$t/$g
          cd $calcdir
          chmod u+x run_*
          sbatch run_prep
          cd $local_dir
        done
      done
    done
  done

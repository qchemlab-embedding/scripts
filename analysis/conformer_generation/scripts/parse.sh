#!/bin/bash

export basedir=`pwd`
mkdir -p $basedir/scratch

python $basedir/scripts/parse.py --inp="$basedir/scratch/m1_h2o_in_allconf.sdf"     --dir="results_starting_from_m1_h2o_in"     --title="m1_h2o_in.xyz"     --prefix="m1_h2o_in_conformers_from_rdkit"
python $basedir/scripts/parse.py --inp="$basedir/scratch/m1_h2o_out_allconf.sdf"    --dir="results_starting_from_m1_h2o_out"    --title="m1_h2o_out.xyz"    --prefix="m1_h2o_out_conformers_from_rdkit"

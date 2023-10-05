#!/bin/bash

export basedir=`pwd`
mkdir -p $basedir/scratch

python $basedir/scripts/conformers_in_rdkit.py --inp="$basedir/coordinates/m1_h2o_in.sdf"      --out="$basedir/scratch/m1_h2o_in_allconf.sdf"     --start="sdf"  --nconf=100 --rmsthr=1.0 --maxiter=700
python $basedir/scripts/conformers_in_rdkit.py --inp="$basedir/coordinates/m1_h2o_out.sdf"     --out="$basedir/scratch/m1_h2o_out_allconf.sdf"    --start="sdf"  --nconf=100 --rmsthr=1.0 --maxiter=700

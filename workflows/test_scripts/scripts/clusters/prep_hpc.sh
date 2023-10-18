#!/bin/bash

#module load python

# -------------------------------------------------------------------
# THIS PART CAN BE MODIFIED
# -------------------------------------------------------------------

# 0. select molecules

moldirs=()


# 1. select model
soft=dirac
method=dft
hamilt=dc
dftfun=b3lyp
basis=dyall.av3z
subdir=super
desc=(density rdg)
ncube=128

# 2. select run type

## test:
#ntasks=4
#timeh=01
#part=plgrid-testing

# standard:
ntasks=8
timeh=72
part=plgrid

## long:
#ntasks=8
#timeh=168
#part=plgrid-long

# -------------------------------------------------------------------
# THIS PART SHOULD NOT NEED ANY MODIFICATIONS
# -------------------------------------------------------------------



# this is the root of git repo
repo=$(builtin cd ../; pwd)
scr=$repo/scripts/clusters
basedir=$repo/tests/explorations
molfile=$(builtin cd coordinates/; echo `ls`)
molname=${molfile%.*}
molcharge=0

cd $basedir
for moldir in "${moldirs[@]}"
do
  cd $moldir
  geomdir=coordinates
  molfile=$(basename $geomdir/*.xyz)
  molname="${molfile%.*}"
  ## dft
  echo "scr: " $scr
  echo "basedir: " $basedir
  echo "moldir: " $moldir
  echo "molfile: " $molfile
  echo "molname: " $molname
  python3 $scr/prepare_hpc.py --basedir $basedir \
         --cluster ares --cluster_ntasks $ntasks --cluster_timeh $timeh --cluster_part $part \
         --mol $molname --charge $molcharge \
         --software $soft --runtype $method \
         --hamiltonians $hamilt \
         --dftfuns $dftfun \
         --basis_sets $basis \
         --subdirs $subdir \
         --functions ${desc[@]} \
         --visgrid_cube $ncube
  cd ../
done
cd ..



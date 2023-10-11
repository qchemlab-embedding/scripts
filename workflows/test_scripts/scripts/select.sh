#!/bin/bash

here=`pwd`
geomdir=$here/coordinates
testdir=$here/explorations

mkdir -p $testdir
cd $testdir

for fullfilename in $geomdir/*
do
  molfile=$(basename $fullfilename)
  mol="${molfile%.*}"
  mkdir -p $mol/coordinates
  cd $mol
  cp $fullfilename coordinates/
  cd ../
done

cd $here

#!/bin/bash

for f in *.xyz
    do
        obabel -ixyz -osdf "${f%.*}".xyz > "${f%.*}".sdf
    done 

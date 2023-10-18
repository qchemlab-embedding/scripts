#!/bin/bash

for f in *.sdf
    do
        obabel -isdf -oxyz "${f%.*}".sdf > "${f%.*}".xyz
    done 

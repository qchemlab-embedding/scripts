#!/usr/bin/env python

import os, sys
import re
from optparse import OptionParser

#-------------------------------------------------------------------------------
def get_conformer(n, lineno, lines, ef):
    energy = re.compile("energy", re.IGNORECASE)
    print(energy)
    ff = open(options.prefix+"_" + str(n) + ".sdf", "w")
    #ff.write("\n")
    i = 0
    for line in lines[lineno:]:
        if "$$$$" in line:
            break
        elif energy.search(line):
            ef.write(str(n) + "\t" + lines[lineno+i+1])
        else:
            ff.write(line)
            i = i + 1
    ff.close()

#-------------------------------------------------------------------------------

parser = OptionParser()

parser.add_option("--inp", 
                  dest="longinp",
                  help="input file with many geometries in sdf format to parse", 
                  metavar="FILE")

parser.add_option("--dir", 
                  dest="resultdir",
                  help="directory to write parsed data (path relative to here)", 
                  metavar="STRING")

parser.add_option("--title",
                  dest="title",
                  help="title comment on top of every geometry on inp file",
                  metavar="STRING")

parser.add_option("--prefix",
                  dest="prefix",
                  help="prefix: the file names with separated conformers will be prefix_i.sdf where i is the  conformer id",
                  metavar="STRING")

(options, args) = parser.parse_args()

print(options)

here = os.getcwd()
rdir = here + "/" + options.resultdir

finp = open(options.longinp, "r")
lines = finp.readlines()
finp.close()

os.makedirs(rdir, exist_ok=True)
os.chdir(rdir)

ef = open("energy.csv", "w")

n = 0
for lineno, line in enumerate(lines):
    if options.title in line:
        get_conformer(n, lineno, lines, ef)
        n = n + 1

ef.close()
os.chdir(here)


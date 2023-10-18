#!/usr/bin/env python 

import sys
import rdkit
from rdkit import Chem
from rdkit.Chem import AllChem

from optparse import OptionParser

parser = OptionParser()

parser.add_option("--inp",
                  dest="inp",
                  help="input file (sdf or smi extensions)",
                  metavar="FILE")

parser.add_option("--out",
                  dest="out",
                  help="output file to write all conformers to",
                  metavar="FILE")

parser.add_option("--start",
                  dest="start",
                  type="string",
                  help="can be: sdf or smi - either generate conformers from the 3D crystal structure or generate starting geometry from smiles)")

parser.add_option("--nconf",
                  dest="nconf",
                  type="int",
                  help="tentative number of conformers (the program will not generate precisely this number)")

parser.add_option("--maxiter",
                  dest="maxiter",
                  type="int",
                  help="maximum number of iterations for MM geometry optimization")

parser.add_option("--rmsthr",
                  dest="rmsthr",
                  type="float",
                  help="RMS limit treshold")

(options, args) = parser.parse_args()


def optimize_confs(confs):
    
    converged = 0
    for conf in confs:
        opt = AllChem.UFFOptimizeMolecule(mol, confId=conf, maxIters=options.maxiter)
        converged+=opt
        
        if opt == -1:
            print("Forcefield could not be setup for conformer %s!!" % (conf,))
        else:
            converged +=opt

    print("%s conformer minimisations failed to converge" % (converged,))
    return confs


def get_mol():
    if options.start == "sdf":
        mols = Chem.SDMolSupplier(options.inp, removeHs = False)
        mol = mols[0] # only one structure on a starting *sdf file
    elif options.start == "smi":
        with open(options.inp, "r") as f:
            smiles = f.readlines()[0].split()[0]
            mol = Chem.AddHs(Chem.MolFromSmiles(smiles))
    return mol


mol = get_mol()
confs = AllChem.EmbedMultipleConfs(mol, numConfs=options.nconf, enforceChirality=True, pruneRmsThresh=options.rmsthr)
allconfs = optimize_confs(confs)


w = Chem.SDWriter(options.out)

for confId in allconfs:
   ff  = AllChem.UFFGetMoleculeForceField(mol, confId = confId)
   ff.Minimize()
   energy_value = ff.CalcEnergy()
   mol.SetProp('ENERGY', '{0:.2f}'.format(energy_value))
   w.write(mol, confId = confId)

w.close()


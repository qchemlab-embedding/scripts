import os
import glob
import py3Dmol
import numpy as np

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import rdBase

#print(rdBase.rdkitVersion)

def align_structures_to_lowest_energy_and_show(moldict, energy_dict, core_smiles):
    """
    align all structures in "moldict" to the one of the lowest energy
    todo (work on the code):
    * separate the alignment step from the visualization
    * modularize/turn into a library of utils
    """
    energy_sorted = sorted(energy_dict.items(), key=lambda x: x[1])
    lowest = energy_sorted[0][0]
    core_lowest = moldict[lowest].GetSubstructMatch(Chem.MolFromSmiles(core_smiles))
    
    for key, mol in moldict.items():
        match_mol_to_core = mol.GetSubstructMatch(Chem.MolFromSmiles(core_smiles))
        AllChem.AlignMol(mol,moldict[lowest],atomMap=list(zip(match_mol_to_core,core_lowest)))
        
    p = py3Dmol.view(width=400,height=400)
    for key, mol in moldict.items(): 
        mb = Chem.MolToMolBlock(mol)
        p.addModel(mb,'sdf')
    p.setStyle({'stick':{'radius':'0.15'}})
    p.setBackgroundColor('0xeeeeee')
    p.zoomTo()
    return p


def align_and_show(moldict, core_smiles, ref_mol):
    """
    align all structures in "moldict" to a reference structure ("ref_mol"), 
    "core_smiles" provides a molecular pattern to prioritize in this alignment ("core_smiles")
    todo (work on the code):
    * separate the alignment step from the visualization
    * modularize/turn into a library of utils
    """ 
    match_ref_to_core = ref_mol.GetSubstructMatch(Chem.MolFromSmiles(core_smiles))
    for key, mol in moldict.items():    
        match_mol_to_core = mol.GetSubstructMatch(Chem.MolFromSmiles(core_smiles))
        AllChem.AlignMol(mol,ref_mol,atomMap=list(zip(match_mol_to_core,match_ref_to_core)))
    
    p = py3Dmol.view(width=400,height=400)
    for key, mol in moldict.items(): 
        mb = Chem.MolToMolBlock(mol)
        p.addModel(mb,'sdf')
    p.setStyle({'stick':{'radius':'0.15'}})
    p.setBackgroundColor('0xeeeeee')
    p.zoomTo()
    return p 




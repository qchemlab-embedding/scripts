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


def from_molfiles_to_moldict(inpfiles, prefix):
    moldict = {}
    for id, inp in enumerate(inpfiles):
        mol = Chem.MolFromMolFile(inp)
        mol = Chem.AddHs(mol)
        name = prefix + str(id)
        moldict[name] = mol
    return moldict


def grep_energies_from_sdf_outputs(files):
    energies = {}
    for inp in files:
        with open(inp,'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                if "M  END" in line:
                    energies[os.path.splitext(os.path.basename(inp))[0]] = float(lines[i+1])
    return energies


def make_similarity_matrix(moldict):
    # similarity_matrix only between macrocycles (h2o not taken into account)
    similarity_matrix = {}
    
    for k_1, m_1 in moldict.items():
        for k_2, m_2 in moldict.items():
            if (k_1, k_2) in similarity_matrix.keys() or (k_2, k_1) in similarity_matrix.keys():
                # do not work on the same conformers
                pass
            else:
                if k_1 != k_2:
                    rms = AllChem.GetBestRMS(m_1,m_2)
                    similarity_matrix[(k_1, k_2)] = rms 
                    
    return similarity_matrix


def find_atoms(moldict):
    O_h2o     = {}
    H_h2o     = {}        
    O_amide   = {}
    H_amide   = {}
    N_amide   = {}
    N_arom    = {}
        
    for k, m in moldict.items():
        Oa  = []
        Hh  = []
        Ha  = []
        Nar = []
        Na  = []
        for atom in m.GetAtoms():
#           remember atom numbering from 0 if you compare with e.g. Avogadro
            # oxygen atoms:
            if atom.GetAtomicNum() == 8:
                if all(x.GetAtomicNum() == 1 for x in atom.GetNeighbors()):
                    O_h2o[k] = atom.GetIdx()
                else:
                    Oa.append(atom.GetIdx())
                    
            # hydrogen atoms:
            if atom.GetAtomicNum() == 1:
                if all(x.GetAtomicNum() == 8 for x in atom.GetNeighbors()):
                    Hh.append(atom.GetIdx())
                elif all(x.GetAtomicNum() == 7 for x in atom.GetNeighbors()):
                    Ha.append(atom.GetIdx())
                    
            # nitrogen atoms:
            if atom.GetAtomicNum() == 7:
                if all(x.GetAtomicNum() == 6 for x in atom.GetNeighbors()):
                    Nar.append(atom.GetIdx())
                else:
                    Na.append(atom.GetIdx())                    
            
            O_amide[k] = Oa
            H_h2o[k]   = Hh
            H_amide[k] = Ha
            N_amide[k] = Na
            N_arom[k]  = Nar
                    
    return O_h2o, O_amide, H_h2o, H_amide, N_amide, N_arom    


def get_distances(moldict, O_h2o, O_amide, H_h2o, H_amide, N_amide, N_arom):
    dist_Oh2o_Hamide = {}
    dist_Hh2o_Narom = {}
    dist_Hh2o_Oamide = {}
    dist_Hh2o_Namide = {}
    
    for k, m in moldict.items():
        dm = Chem.Get3DDistanceMatrix(m)
        
        dist1 = []
        for h_idx in H_amide[k]:
            dist1.append(dm[O_h2o[k],h_idx])
        dist_Oh2o_Hamide[k] = sorted(dist1)
        
        dist2 = []
        dist3 = []
        dist4 = []        
        for h_idx in H_h2o[k]:
            for n1_idx in N_arom[k]:
                dist2.append(dm[n1_idx,h_idx])
            for n2_idx in N_amide[k]:
                dist3.append(dm[n2_idx,h_idx])
            for o_idx in O_amide[k]:
                dist4.append(dm[o_idx,h_idx])                

        dist_Hh2o_Narom[k]  = sorted(dist2)
        dist_Hh2o_Namide[k] = sorted(dist3)
        dist_Hh2o_Oamide[k] = sorted(dist4)            
        
    return dist_Oh2o_Hamide, dist_Hh2o_Narom, dist_Hh2o_Namide, dist_Hh2o_Oamide


def find_duplicates_in_sorted_similarity_matrix_noncovalent(similarity_matrix_sorted,
                                                            energy,
                                                            dist_Oh2o_Hamide,
                                                            dist_Hh2o_Narom,
                                                            dist_Hh2o_Namide,
                                                            dist_Hh2o_Oamide):
    
    similarity_thresh = 1.0 # Angstrom
    energy_thresh     = 5   # kcal/mol
    distance_thresh   = 1.0 # Angstrom
    
    to_be_deleted     = []
    
    for pair in similarity_matrix_sorted:
        if pair[1] < similarity_thresh:
            conf1 = pair[0][0]
            conf2 = pair[0][1]
            # now check minimum and maximum distances:
            if (abs(dist_Oh2o_Hamide[conf1][0]  - dist_Oh2o_Hamide[conf2][0]) < distance_thresh and 
                abs(dist_Oh2o_Hamide[conf1][-1] - dist_Oh2o_Hamide[conf2][-1]) < distance_thresh and
                abs(dist_Hh2o_Narom[conf1][0]   - dist_Hh2o_Narom[conf2][0]) < distance_thresh and 
                abs(dist_Hh2o_Narom[conf1][-1]  - dist_Hh2o_Narom[conf2][-1]) < distance_thresh and
                abs(dist_Hh2o_Namide[conf1][0]  - dist_Hh2o_Namide[conf2][0]) < distance_thresh and 
                abs(dist_Hh2o_Namide[conf1][-1] - dist_Hh2o_Namide[conf2][-1]) < distance_thresh and
                abs(dist_Hh2o_Oamide[conf1][0]  - dist_Hh2o_Oamide[conf2][0]) < distance_thresh and 
                abs(dist_Hh2o_Oamide[conf1][-1] - dist_Hh2o_Oamide[conf2][-1]) < distance_thresh):
                
                
                # finally check energies and remove the one with the higher:
                if abs(energy[conf1] - energy[conf2]) < energy_thresh:
                    if energy[conf1] < energy[conf2]:
                        to_be_deleted.append(conf2)
                    else:
                        to_be_deleted.append(conf1)
            else:
                # similarity_matrix_b_sorted is sorted, so here we would already start looping over 
                # pairs for which rmsd is > threshold 
                # and we do not need to do this, so break
                break

    return to_be_deleted


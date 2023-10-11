#!/usr/bin/env python

import os
import sys
import shutil
import argparse
import subprocess
from pathlib import PurePath, Path
from mendeleev.fetch import fetch_table

assert sys.version_info >= (3, 8)

# -------------------------------------------------------------------
# THIS PART CAN BE MODIFIED
# -------------------------------------------------------------------
# directories and paths
scratch_base='jobs/project-name/explorations'
inp_dirname = 'inputs'
mol_dirname = 'coordinates'
out_dirname = 'outputs'
vis_dirname = 'visgrid_cube'

scalar_field_filename='plot.3d.scalar'

subdirs    = ['super']
scalar_field_dep_on_dfcoef = ['density', 'rdg', 'signl2', 'esp', 'espe', 'espn', 'esprho', 'esperho', 'espnrho']
final_ndim = '128'
runtypes   = ['hf', 'dft', 'cc']

prp_selection = {}
calc_selection = {}

# -------------------------------------------------------------------
here = Path(__file__).parent.absolute()
up = here.parent.absolute()
tmpl_dir_dirac={}
# dft:
tmpl_dir_dirac['dft'] = PurePath.joinpath(here, 'templates_dirac', 'hamiltonian_dftfun_basis_nosym')
# -------------------------------------------------------------------



# -------------------------------------------------------------------
# THIS PART SHOULD NOT NEED ANY MODIFICATIONS
# -------------------------------------------------------------------

def parse_input_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("--basedir")
    parser.add_argument("--mol")
    parser.add_argument("--charge")
    parser.add_argument("--software")
    parser.add_argument("--cluster")
    parser.add_argument("--cluster_ntasks")
    parser.add_argument("--cluster_timeh")
    parser.add_argument("--cluster_part")
    parser.add_argument("--runtype",      choices=runtypes)
    parser.add_argument("--cvalue", type=float)
    parser.add_argument("--hamiltonians", nargs='*')
    parser.add_argument("--dftfuns",      nargs='*')
    parser.add_argument("--basis_sets",   nargs='*')
    parser.add_argument("--subdirs",      nargs='*', choices=subdirs)
    parser.add_argument("--functions",    nargs='*', choices=scalar_field_dep_on_dfcoef)
    parser.add_argument("--visgrid_cube")
    args   = parser.parse_args()
    for k in args.__dict__:
        print(k, args.__dict__[k])
    return args


def modify_lines(g, lines, molname, data_dir_in_scratch, ndim, vis_scfield, plotfilename, \
                 cluster_ntasks=None,cluster_timeh=None,cluster_part=None, \
                 basis=None, hamiltonian=None, dftfun=None, nr_cs=None, charge=None, dfcoef_model=None,cvalue=None):

    patterns={}

    patterns["cluster_ntasks"] = str(cluster_ntasks)
    patterns["cluster_timeh"] = str(cluster_timeh)
    patterns["cluster_part"] = cluster_part

    patterns["molname"] = molname
    patterns["ndim"] = str(ndim)
    patterns["scalar_field_dep_on_dfcoef"] = vis_scfield
    patterns["data_dir_in_scratch"] = data_dir_in_scratch
    patterns["plotfilename"] = plotfilename

    patterns["dfcoef_model"] = dfcoef_model
    patterns["c_val"] = str(cvalue)
    patterns["choice_of_basis"] = basis
    if hamiltonian == 'dc':
        patterns["choice_of_hamiltonian"] = 'remove'
    else:
        patterns["choice_of_hamiltonian"] = hamiltonian
    patterns["choice_of_dftfun"] = dftfun
    patterns["charge_mol"] = str(charge)
    patterns["nr_of_closed_shell"] = str(nr_cs)

    for l in lines:
        for k, v in patterns.items():
            if v:
                l = l.replace(k, v)
        if 'remove' not in l:
            g.write(l)


def modify_run_templates(path, tpl_file, final_file, mol, scratch, ndim, vis_scfield, plotfilename, cluster_ntasks, cluster_timeh, cluster_part, dfcoef_model):
    res_file = final_file
    with open(os.path.join(path, tpl_file), "r") as f:
        lines = f.readlines()
        with open(os.path.join(path, res_file), "w") as g:
            modify_lines(g, lines, mol, scratch, ndim, vis_scfield, plotfilename, \
                        cluster_ntasks, cluster_timeh, cluster_part, dfcoef_model=dfcoef_model)


def modify_inp_templates(path, tpl_file, final_file, mol, ndim, vis_scfield, basis, hamiltonian, dftfun, nr_cs, charge):
    res_file = final_file
    with open(os.path.join(path, tpl_file), "r") as f:
        lines = f.readlines()
        with open(os.path.join(path, res_file), "w") as g:
            modify_lines(g, lines, mol, None, ndim, vis_scfield, None, \
                         None, None, None, \
                         basis, hamiltonian, dftfun, nr_cs, charge)


def prepare_grid_for_fde(tpl_file, res_file, ndim):

    ndim_total = float(ndim)**3

    with open(tpl_file, "r") as f:
        lines = f.readlines()
        with open(res_file, "w") as g:
            g.write(str(int(ndim_total))+'\n')
            for line in lines:
                grid=line.split()
                g.write('{}   {}   {}   0.0 \n'.format(grid[0], grid[1], grid[2]))

def get_closed_shell_el(coor_dir):
    # we are using mendeleev code here
    ptable = fetch_table('elements')
    cols= ['atomic_number', 'symbol'] 

    closed_shell_el = {}
    fmols = []
    for f in Path(coor_dir).rglob('*.xyz'):
        fmols.append(f)
    fmols = list(dict.fromkeys(fmols))
    for fmol in fmols:
        name = os.path.splitext(os.path.basename(fmol))[0]
        nr_electrons = 0
        with open(fmol, "r") as f:
            lines  = f.readlines()
            for line in lines[2:]:
                info = line.strip().split(" ")
                el_this=info[0].strip()
                if el_this.isdigit():
                    atnum = int(el_this)
                else:
                    atnum = ptable.loc[ptable['symbol'].str.contains(el_this,case=False), 'atomic_number'].values[0]
                nr_electrons = nr_electrons+int(atnum)
        closed_shell_el[name] = nr_electrons
    return closed_shell_el

def get_charges(coor_dir):
    charge = {}
    fmols = []
    for f in Path(coor_dir).rglob('*.xyz'):
        fmols.append(f)
    fmols = list(dict.fromkeys(fmols))
    for fmol in fmols:
        name = os.path.splitext(os.path.basename(fmol))[0]
        with open(fmol, "r") as f:
            lines  = f.readlines()
            info   = lines[1].strip().split(";")
            charge[name] = info[0].split("=")[1]
    return charge




# parse options
args=parse_input_options()
explorations_dir=Path(args.basedir)

# make mol directory
mol_dir = Path().resolve()
scratch_specific=mol_dir.name

coor_dir = PurePath.joinpath(mol_dir, mol_dirname)
charge={}
if args.charge:
    charge[args.mol]=args.charge
else:
    charge = get_charges(PurePath.joinpath(up, mol_dirname))
closed_shell_el = get_closed_shell_el(Path(mol_dirname).resolve())

methods = []
if args.runtype == 'dft':
    methods=[dftfun for dftfun in args.dftfuns]
else:
    methods.append(args.runtype)


# make mol subdirectories
for h in args.hamiltonians:
    for d in methods:
        for b in args.basis_sets:
            model = h+'_'+d+'_'+b.replace('.','')
            for t in args.subdirs:
                if str(scratch_specific) == args.mol:
                    scratch_name = scratch_base+'/'+args.mol+'/'+args.software+'/'+model+'/'+t
                else:
                    scratch_name = scratch_base+'/'+str(scratch_specific)+'/'+args.software+'/'+model+'/'+t

                # copy and prepare runscripts
                run_dir = PurePath.joinpath(mol_dir, args.software, model, t)
                shutil.copytree(tmpl_dir_dirac[args.runtype], run_dir, dirs_exist_ok=True, ignore=shutil.ignore_patterns("inprep"))

                dfcoef_model=h+'_hf_'+b.replace('.','')

                r0 = 'template_run_scf_'+args.cluster
                r1 = 'run_scf.sh'
                modify_run_templates(run_dir, r0, r1, args.mol, scratch_name, args.visgrid_cube, None, None, \
                                     args.cluster_ntasks, args.cluster_timeh, args.cluster_part, \
                                     dfcoef_model=dfcoef_model)
                Path(PurePath.joinpath(run_dir, r0)).unlink()

                #Path(PurePath.joinpath(run_dir, r0)).unlink()
                for fl in os.listdir(run_dir):
                    if 'template' in fl:
                        Path(PurePath.joinpath(run_dir, fl)).unlink()

                # copy and prepare inputs
                run_dir = PurePath.joinpath(mol_dir, args.software, model, t)
                inp_dir = PurePath.joinpath(run_dir, inp_dirname)
                if d == 'dft':
                    r0 = 'template_scf.inp'
                    r1 = 'scf.inp'
                print('args.mol ', args.mol)
                print('charge[args.mol] ', charge[args.mol])
                print('closed_shell_el[args.mol] ', closed_shell_el[args.mol])
                modify_inp_templates(inp_dir, r0, r1, args.mol, args.visgrid_cube, None, b, h, d, closed_shell_el[args.mol], charge[args.mol])
                #Path(PurePath.joinpath(inp_dir, r0)).unlink()
                for fl in os.listdir(inp_dir):
                    if 'template' in fl:
                        Path(PurePath.joinpath(inp_dir, fl)).unlink()


                run_dir = PurePath.joinpath(mol_dir, args.software, model, t)
                inp_dir = PurePath.joinpath(run_dir, inp_dirname, vis_dirname)
                r0 = 'template_scalar_field_dep_on_dfcoef.inp'
                for f in args.functions:
                    r1 = f+'_visgrid_cube_'+args.visgrid_cube+'.inp'
                    modify_inp_templates(inp_dir, r0, r1, args.mol, args.visgrid_cube, f, b, h, d, closed_shell_el[args.mol], charge[args.mol])
                #Path(PurePath.joinpath(inp_dir, r0)).unlink()
                for fl in os.listdir(inp_dir):
                    if 'template' in fl:
                        Path(PurePath.joinpath(inp_dir, fl)).unlink()

                # copy geom
                for f in Path( PurePath.joinpath(mol_dir, mol_dirname) ).rglob('*.xyz'):
                    if (os.path.splitext(os.path.basename(f))[0] == args.mol) or (os.path.splitext(os.path.basename(f))[0] == 'geom'):
                        shutil.copy(f, PurePath.joinpath(run_dir, args.mol+'.xyz'))


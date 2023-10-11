#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
from pathlib import Path, PurePath


# -------------------------------------------------------------------
# THIS PART CAN BE MODIFIED
# -------------------------------------------------------------------
data_ndim = sys.argv[1]
final_ndim = sys.argv[2]
data_filename="plot.3d.scalar"
options = {'data_ndim':data_ndim,'final_ndim':final_ndim,'prp_selection':{}, 'calc_selection':{}}


# -------------------------------------------------------------------
# THIS PART SHOULD NOT NEED ANY MODIFICATIONS
# -------------------------------------------------------------------


softwares=[]
methods = []
subdirs = []
functions=[]


class global_data():
    def __init__(self):
        pass

class env():

    def __init__(self, mol_dir_root, 
                 data_dir=None, templates_dir=None, coords_dir=None, grid_dir=None, analysis_dir=None, scratch_dir=None,
                 qc_plotdata_dirname=None, qc_inputs_dirname=None, qc_outputs_dirname=None, qc_binfiles_dirname=None, 
                 options=None):

        self.mol_dir_root  = Path(mol_dir_root)
        self.all_explorations_dir = Path.joinpath(self.mol_dir_root.parent)
        self.templates_dir = Path.joinpath(self.all_explorations_dir.parent, 'scripts_templates') if templates_dir is None else Path(templates_dir)
        self.data_dir      = Path.joinpath(self.mol_dir_root, 'data') if data_dir is None else Path(data_dir)
        self.coords_dir    = Path.joinpath(self.mol_dir_root, 'coordinates') if coords_dir is None else Path(coords_dir)
        self.grid_dir      = Path.joinpath(self.mol_dir_root, 'grids') if grid_dir is None else Path(grid_dir)
        self.analysis_dir  = Path.joinpath(self.mol_dir_root, 'analysis') if analysis_dir is None else Path(analysis_dir)
        self.scratch_dir   = Path.joinpath(self.mol_dir_root, 'scratch') if scratch_dir is None else Path(scratch_dir)

        self.qc_plotdata_dirname = 'plotfiles' if qc_plotdata_dirname is None else qc_plotdata_dirname
        self.qc_inputs_dirname   = 'inputs' if qc_inputs_dirname is None else qc_inputs_dirname
        self.qc_outputs_dirname  = 'outputs' if qc_outputs_dirname is None else qc_outputs_dirname
        self.qc_binfiles_dirname = 'binfiles' if qc_binfiles_dirname is None else qc_binfiles_dirname

        self.options = options

    def prep_env(self):
        pass

    def cleanup(self):

        if (os.getcwd() != self.startdir) and os.path.exists(self.startdir):
            os.chdir(self.startdir)
        if os.path.exists('pyadftempdir'):
            shutil.rmtree('pyadftempdir')


# ===============
# utils functions
# ===============

def add_dir_path(target_path,result=None,level=0,traverse=False):
    #print("in add_dir_path: target_path = ", target_path, type(target_path))
    if result is None:
        result={}
    if not Path(target_path).is_dir():
        #print(target_path, ' directory does not exist here, skipping')
        return None
    for f in target_path.iterdir():
        #print("in add_dir_path: target_path, f = ", target_path,f)
        if f.is_dir():
            if level in result:
                result[level].append(f)
            else:
                result[level] = [f,]
        #    print("in add_dir_path: level, f = ", level,f)
            if traverse:
                add_dir_path(f, result, level+1, True)
    return result

def make_mirror_dirs(root_old, root_new, bottom_dir):
    for p in bottom_dir:
        q=str(p).replace(root_old,root_new)
        Path(q).mkdir(parents=True,exist_ok=True)

def copy_geom(from_dir, to_dirs):
    for f in from_dir.iterdir():
        if f.is_file() and f.suffix == '.xyz':
            for d in to_dirs:
                shutil.copy(f, Path.joinpath(d, 'geom.xyz'))

def copy_data(root_old, root_new, structure):
    for p in structure:
        #if plot_dirname in str(p): 
        if "plotfiles" in str(p): 
            q=str(p).replace(root_old,root_new)
            print("I WILL COPY ", p, " TO ", q)
            shutil.copytree(p, q, dirs_exist_ok=True)

def copy_templates(tpl_list,from_dir, to_dir):
    for f in from_dir.iterdir():
        if f.is_file() and f.name in tpl_list:
            for d in to_dir:
                shutil.copy(f, Path.joinpath(d, f.name.replace('template_','')))

def transform_xyz2csv(fxyz,fcsv=None,a2b=False,b2a=False):
    if fcsv is None:
        fcsv = Path.joinpath(Path(fxyz.parent).resolve(), fxyz.stem+".csv")
    with open(fxyz, "r") as f:
        with open(fcsv, "w") as g:
            if a2b:
                factor = 1.889725989 # from Angstrom to Bohr
                g.write("at,x,y,z [a.u.]\n")
            elif b2a:
                factor = 0.529177249 # from Bohr to Angstrom
                g.write("at,x,y,z [a.u.]\n")
            else:
                factor = 1.0 # xyz files are typically in Angstrom
                g.write("at,x,y,z [A]\n") 
            lines = f.readlines()
            for i, line in enumerate(lines[2:]):
                w = line.strip().split()
                x = float(w[1])*factor
                y = float(w[2])*factor
                z = float(w[3])*factor
                g.write("{0},{1},{2},{3}\n".format(w[0],x,y,z))

def transform_geom(dirs):
    for d in dirs:
        for f in d.iterdir():
            if f.is_file() and f.suffix == '.xyz':
                print("TRANSFORM_GEOM: f = ", f)
                transform_xyz2csv(f,a2b=True)
                #subprocess.call(["transform_xyz2csv.py", f])

def adapt_templates(tpl_list, dirs, patterns):
    for d in dirs:
        for f in d.iterdir():
            if f.match('*.py') or f.match('*inp'):
                #print('MODIFYING: ', f)
                modify_lines(f, patterns)

def modify_lines(tpl, patterns):
    with open(tpl,'r') as f:
        data = f.read()
    for k1, v1 in patterns.items():
        if k1 == tpl.parent:
            for k2,v2 in v1.items():
                if isinstance(v2, dict):
                    for k3,v3 in v2.items():
                        pass
                else:
                    data = data.replace(k2,v2)
    with open(tpl,'w') as f:
        f.write(data)

def def_patterns(allf, typ):
    # get info from path name:
    p={}
    for d in allf:
        #if plot_dirname in str(d):
        if 'plotfiles' in str(d):
            if typ == 'allfun':
                p[d.parents[1]] = {}
            elif typ == 'single':
                p[d] = {}
            elif typ == 'onesoft':
                p[d.parents[3]] = {}
            for f in d.iterdir():
                #df = f.name
                df = data_filename
                q=Path(f).parts
                if typ == 'single':
                    p[d]["qchemfile_single"] = df
                    p[d]["names_single"] = q[-2].split('_')[0]
                    p[d]["ndim"] = q[-2].split('_')[-1]
                    p[d]["final_dim"] = final_ndim
    return p

def modify_templates_all2(dirs, tpl_file, prps):
    for d in dirs:
        allfun=[]
        for p in prps:
            #if plot_dirname in str(p) and str(d) in str(p):
            if "plotfiles" in str(p) and str(d) in str(p):
                q=p.stem
                allfun.append(q)
        for f in d.iterdir():
            #if f.match('*.py') or f.match('*inp'):
            if f.match('*inp'):
                i0 = 0
                with open(f, "r") as ftpl:
                    lines = ftpl.readlines()
                    for iline, line in enumerate(lines):
                        if "start_block" in line:
                            i0 = iline
                with open(f, "w") as ftpl:
                    for iline, line in enumerate(lines[:i0]):
                        ftpl.write(line.replace('final_dim', final_ndim))
                    for prp in allfun:
                        for iline, line in enumerate(lines[i0:]):
                            ftpl.write(line.replace('qchemfile_allfun', '/'.join(['plotfiles', prp, data_filename])).replace('names_allfun', prp.split('_')[0]).replace('ndim',prp.split('_')[-1]))


def modify_templates_all3(dirs, tpl_file, prps):
    for d in dirs:
        allfun=[]
        alldir=[]
        for p in prps:
            if plot_dirname in str(p) and str(d) in str(p):
                q=p.stem
                allfun.append(q)
                alldir.append(p)
        for f in d.iterdir():
            #if f.match('*.py') or f.match('*inp'):
            if f.match('*inp'):
                i0 = 0
                with open(f, "r") as ftpl:
                    lines = ftpl.readlines()
                    for iline, line in enumerate(lines):
                        if "start_block" in line:
                            i0 = iline
                with open(f, "w") as ftpl:
                    for iline, line in enumerate(lines[:i0]):
                        ftpl.write(line.replace('final_dim', final_ndim))
                    for i,prp in enumerate(allfun):
                        k=alldir[i].parts
                        for iline, line in enumerate(lines[i0:]):
                            ftpl.write(line.replace('qchemfile_allfun', '/'.join([str(alldir[i]), data_filename])).replace('names_allfun', k[-4]+'_'+prp.split('_')[0]).replace('ndim',prp.split('_')[-1]))

# -------------------------------------------------------------------

# ===========
# do the work
# ===========

# 1.setup
local_env=env(mol_dir_root=Path.cwd(), options=options)

# 2. get directories with templates
templates=add_dir_path(Path(local_env.templates_dir))

# 3. get lists of directories with data
data=add_dir_path(Path(local_env.data_dir),traverse=True)
print("**** DATA DIR = ", local_env.data_dir)

if data:
    data_softwares, data_methods, data_subdirs, data_functions = [data[i] for i in (0,1,2,4)]
else:
    sys.exit()

# 4. set directories for analysis
analysis=local_env.analysis_dir
print("**** ANALYSIS DIR = ", local_env.analysis_dir)
Path(analysis).mkdir(parents=True,exist_ok=True)
make_mirror_dirs(local_env.data_dir.name,analysis.name,data_functions)
analysis=add_dir_path(Path(analysis),traverse=True)
analysis_softwares, analysis_methods, analysis_subdirs, analysis_functions = [analysis[i] for i in (0,1,2,4)]

# 5. copy data needed for analysis

#   * copy coordinates and transform xyz to csv
copy_geom(local_env.coords_dir, analysis_subdirs)
transform_geom(analysis_subdirs)

#   * plot data
#DONE copy_data(local_env.data_dir.name, local_env.analysis_dir.name, data_functions)

#   * templates
print("**** TEMPLATE DIR = ", local_env.templates_dir)
single_templates = ['template_run_ttkqc_single.py', 'template_ttkqc_start_from_qchem_single.inp']
allfun_templates = ['template_run_ttkqc_allfun.py', 'template_ttkqc_start_allfun.inp']
onesoft_templates = ['template_run_ttkqc_onesoftware.py', 'template_ttkqc_start_onesoftware.inp']

copy_templates(single_templates,Path(local_env.templates_dir), analysis_functions)
copy_templates(allfun_templates,Path(local_env.templates_dir), analysis_subdirs)
#copy_templates(onesoft_templates,Path(local_env.templates_dir), [Path(analysis)])

# 4. adapt templates

single_patterns=def_patterns(analysis_functions, 'single')
adapt_templates(single_templates,analysis_functions,single_patterns)
#
#FIXME:
allfun_patterns=def_patterns(analysis_functions, 'allfun')
modify_templates_all2(analysis_subdirs,allfun_templates,analysis_functions)

#onesoft_patterns=def_patterns(analysis_functions, 'onesoft')
#modify_templates_all3([Path(analysis_dir)],onesoft_templates,analysis_functions)

sys.exit()


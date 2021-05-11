import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
import re
import numpy as np
import itertools
import h5py
from h5writer import _write_basis, _write_scaling_factor, _write_volume
from pathlib import Path
#path = '/home/labb/ENVISIoN/ENVISIoN/envisionpy/hdf5parser/ELK'
#sys.path.insert(0, os.path.expanduser(path))
#from unitcell_parser import unitcell_parser, find_elements, parse_coordinates

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *)+')

def check_directory_elf_elk(vasp_path):
    if Path(vasp_path).joinpath('INFO.OUT').exists() and Path(vasp_path).joinpath('ELF3D.OUT').exists():
        return True
    return False

def parse_lattice(ELK_dir):
    basis = []
    with open(os.path.join(ELK_dir,'INFO.OUT'), "r") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if "Lattice vectors :" in line:
                basis.append([float(n) for n in lines[i+1].split()[:3]])
                basis.append([float(n) for n in lines[i+2].split()[:3]])
                basis.append([float(n) for n in lines[i+3].split()[:3]])
            if "Unit cell volume      :" in line:
                list = line.split()
                scaling_factor = -float(list[-1])
    return scaling_factor ,basis

def parse_vol(ELK_file):
    array = []
    datasize = None
    data_dim = []
    counter = 0
    for line in ELK_file:
        match_float = line_reg_float.match(line)
        if "grid size" in line:
            data_dim_temp = line.split()
            for x in range(len(data_dim_temp)):
                if data_dim_temp[x].isdigit():
                    data_dim += [int(data_dim_temp[x])]
            if data_dim:
                datasize = data_dim[0]*data_dim[1]*data_dim[2]
        elif data_dim and match_float:
            for element in line.split():
                array.append(float(element))
                if len(array) == datasize:
                    return array, data_dim
        else:
            data_dim = None
    return None, None



def parse_elf(h5file, ELK_dir):
    scaling_factor, basis = parse_lattice(ELK_dir)
    _write_basis(h5file, basis)
    _write_scaling_factor(h5file, scaling_factor=1)
    ELK_file = Path(ELK_dir).joinpath('ELF3D.OUT')
    with open(ELK_file, "r+") as f:
        for i in itertools.count():
            array, data_dim = parse_vol(f)
            if not _write_volume(h5file, i, array, data_dim, "ELF"):
                return False
            if not array:
                break
    return True

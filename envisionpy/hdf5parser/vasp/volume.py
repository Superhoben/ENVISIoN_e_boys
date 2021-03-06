#
#  ENVISIoN
#
#  Copyright (c) 2017-2021 Fredrik Segerhammar, Marian Brännvall, Anders Rehult
#  Gabriel Anderberg, Didrik Axén,  Adam Engman, Kristoffer Gubberud Maras,
#  Joakim Stenborg
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#
#  1. Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#  ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#  WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#  ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################################
#
#  Alterations to this file by Anders Rehult, Marian Brännvall, Anton Hjert
#
#  To the extent possible under law, the person who associated CC0
#  with the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.
##################################################################################
#  Alterations to this file by Gabriel Anderberg, Didrik Axén,
#  Adam Engman, Kristoffer Gubberud Maras, Joakim Stenborg
#
#  To the extent possible under law, the person who associated CC0 with
#  the alterations to this file has waived all copyright and related
#  or neighboring rights to the alterations made to this file.
#
#  You should have received a copy of the CC0 legalcode along with
#  this work.  If not, see
#  <http://creativecommons.org/publicdomain/zero/1.0/>.

import os,sys
import inspect
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.expanduser(path_to_current_folder+'/..'))
sys.path.insert(0, os.path.expanduser(path_to_current_folder))
import itertools
import h5py
import re
import numpy as np
from pathlib import Path
from h5writer import _write_volume, _write_basis, _write_scaling_factor
from unitcell import _parse_lattice

line_reg_int = re.compile(r'^( *[+-]?[0-9]+){3} *$')
line_reg_float = re.compile(r'( *[+-]?[0-9]*\.[0-9]+(?:[eE][+-]?[0-9]+)? *)+')

def parse_volume(vasp_file, volume):
	"""Parses volumetric data in a volume file from VASP

	Parameters
	----------
	vasp_file : file object
		file object of volume file

	Returns
	-------
	array : list of float
		list of volumetric data
	data_dim : list of int
		list of dimensions of the data
	"""
	array = []
	datasize = None
	data_dim = None

	for line in vasp_file:
		match_float = line_reg_float.match(line)
		match_int = line_reg_int.match(line)

		if match_int:
			data_dim = ([int(v) for v in line.split()])
			datasize = data_dim[0]*data_dim[1]*data_dim[2]

		elif data_dim and match_float:
			for element in line.split():
				array.append(float(element))
				if len(array) == datasize:
					return array, data_dim
		else:
			data_dim = None
	return None, None

def volume(h5file, hdfgroup, vasp_dir, vasp_file):
	"""
	Reads volume data from  vasp_file, either CHG or ELFCAR,
        and stores it in an HDF-file.

	Parameters
	----------
	h5file : str
		String that asserts which HDF-file to write to
	hdfgroup : str
		String that asserts which group to write to in HDF-file
	vasp_dir : str
		Path to directory containing volume file
	vasp_file : str
		String that asserts which file to open in the directory

	Returns
	-------
	bool
		True if volume file was parsed, False otherwise.
	"""

	if os.path.isfile(h5file):
		with h5py.File(h5file, 'r') as h5:
			if '/{}'.format(hdfgroup) in h5:
					print(vasp_file + ' already parsed. Skipping.')
					return False
	try:
		with open(os.path.join(vasp_dir,'POSCAR'), 'r') as f:
			scaling_factor, basis = _parse_lattice(f)
			_write_basis(h5file, basis)
			_write_scaling_factor(h5file, scaling_factor)
	except FileNotFoundError:
		print("POSCAR file not in directory. Skipping.")
	try:
		with open(os.path.join(vasp_dir, vasp_file), "r") as f:
			for i in itertools.count():
				array, data_dim = parse_volume(f, hdfgroup)
				if not _write_volume(h5file, i, array, data_dim, hdfgroup):
					return False
				if not array:
					break
	except FileNotFoundError:
		print(vasp_file + ' file not in directory. Skipping.')
		return False
	print(vasp_file + ' was parsed successfully.')
	return True




def charge(h5file, vasp_dir):
	"""
	Reads CHG and stores the data in an HDF-file.

	Parameters
	----------
	h5file : str
		String that asserts which HDF-file to write to
	vasp_dir : str
		Path to directory containing volume file

	Returns
	-------
	bool
		True if CHG file was parsed, False otherwise.
	"""
	return volume(h5file, 'CHG', vasp_dir, 'CHG')


def elf(h5file, vasp_dir):
	"""
	Reads ELFCAR and stores the data in an HDF-file.

	Parameters
	----------
	h5file : str
		String that asserts which HDF-file to write to
	vasp_dir : str
		Path to directory containing volume file
	Returns
	-------
	bool
		True if ELFCAR file was parsed, False otherwise.
	"""
	return volume(h5file, 'ELF', vasp_dir, 'ELFCAR')

def check_directory_charge(vasp_path):
	if Path(vasp_path).joinpath('CHG').exists() and Path(vasp_path).joinpath('POSCAR').exists():
		return True
	else:
		return False

def check_directory_elf(vasp_path):
	if Path(vasp_path).joinpath('ELFCAR').exists() and Path(vasp_path).joinpath('POSCAR').exists():
		return True
	else:
		return False

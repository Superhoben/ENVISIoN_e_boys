import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager


#--------VASP-------
#Path to VASP-files and path to where the generated HDF5-file will be located.
VASP_DIR = path_to_current_folder + "/../unit_testing/resources/MD/VASP/Al_300K"
#HDF5_FILE = path_to_current_folder + "/../demo_molecular_dynamics.hdf5"


#--------Premade HDF5-files-------
#Path to a HDF5-file already generated by the molecular_dynamics parser
HDF5_FILE = path_to_current_folder + "/../md_test.hdf5"
#HDF5_FILE = path_to_current_folder + "/../test_md_2punkt0.hdf5"


#parse the VASP-file for molecular dynamics
#envisionpy.hdf5parser.mol_dynamic_parser(HDF5_FILE, VASP_DIR)

#clear any old network
inviwopy.app.network.clear()

#Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("molecular_dynamics")

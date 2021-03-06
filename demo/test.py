import sys, os, inspect
import os, sys, inspect, inviwopy
path_to_current_folder = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(path_to_current_folder + "/../")
import envisionpy
import envisionpy.hdf5parser
from envisionpy.network import VisualisationManager

VASP_DIR = path_to_current_folder + "/../unit_testing/resources/TiPO4_bandstructure"
HDF5_FILE = path_to_current_folder + "/../demo_force2.hdf5"

try:
    os.remove(HDF5_FILE)
except:
    print("Somthing went wrong")

envisionpy.hdf5parser.force_parser(HDF5_FILE, VASP_DIR)

inviwopy.app.network.clear()

# Initialize inviwo network
visManager = VisualisationManager(HDF5_FILE, inviwopy.app)
visManager.start("test")

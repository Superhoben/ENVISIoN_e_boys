import inviwopy
# import inviwopy.glm as glm
import numpy as np
import h5py
from envisionpy.utils.exceptions import *
from .baseNetworks.LinePlotSubnetwork import LinePlotSubnetwork

class Bandstructure(LinePlotSubnetwork):
    '''
    Manages a subnetwork for bandstructure visualisation. 
    Uses a default LinePlotSubnetwork.
    '''
    def __init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos=0, ypos=0):
        LinePlotSubnetwork.__init__(self, inviwoApp, hdf5_path, hdf5_outport, xpos, ypos, False)

        self.set_hdf5_subpath('/Bandstructure/Bands')
        self.set_y_selection_type(2)

        self.set_title("Energy - Fermi energy  [eV]")

    @staticmethod
    def valid_hdf5(hdf5_file):
        return hdf5_file.get('/Bandstructure/Bands') != None



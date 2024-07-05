import os
import argparse
from vtxmpasmeshes.mpas_plots import view_mpas_regional_mesh

# Create ArgumentParser object
parser = argparse.ArgumentParser(description=
                                 'Sensitivity test for varying mesh parameters.')
# Input arguments
parser.add_argument('--filename', type=str, default='circle.grid.nc')
# Parse the command line arguments
args = parser.parse_args()

# Set relevant directories
filename = args.filename

view_mpas_regional_mesh(filename,outfile='resolution_mesh.png')

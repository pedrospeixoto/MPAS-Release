#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to plot scalar fields on regional native MPAS grids regionally

Originally From: Marta Gil Bardaji
Edited: Jan 2024 G.L. Torres Mendonça <guilherme.torresmendonca@ime.usp.br>
"""

import argparse
import os

from dataset_utilities import open_mpas_regional_file
from plot_utilities import plot_mpas_darray
from mpas_plots import view_mpas_regional_mesh

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument(
    "-g", "--grid", type=str, required=True,
    help="Name of an MPAS grid.nc",
)

parser.add_argument(
    "-o", "--outfile", type=str, default=None,
    help="File to save the MPAS plot",
)

args = parser.parse_args()

if not os.path.exists(args.grid):
    raise IOError('File does not exist: ' + args.grid)

view_mpas_regional_mesh(args.grid, outfile=args.outfile)
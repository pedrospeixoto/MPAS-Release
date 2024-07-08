#!/usr/bin/env python

import xarray as xr
from scipy.interpolate import interp1d
import sys
import numpy as np
import matplotlib.pyplot as plt

# Input and output file names
filename = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test2_gtm_simulation/s30_m100.region.static.nc"
ds_static = xr.open_dataset(filename)

# Print value of terrain height for cell 1472 (where tower 13 is located)
print (ds_static["ter"].isel(nCells=1472).values)

# Print value of zgrid at that same cell
filename = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test2_gtm_simulation/cat.nc"
ds_cat = xr.open_dataset(filename)
print (ds_cat["zgrid"].isel(nCells=1472,Time=0).values)

# Print variables of ds2
#print (ds2.variables)
# Check values of latitude and longitude to see if 1472 is indeed the correct value for nCells
print (ds_cat['lonCell'].isel(nCells=1472,Time=0).values*180/np.pi - 360.)
print (ds_cat['latCell'].isel(nCells=1472,Time=0).values*180/np.pi)

# Calculate height of first theta-levels: theta(1) = zgrid(1) + dzw(1)/2 and so on
filename = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test2_gtm_simulation/s30_m100.region.init.nc"
ds_init = xr.open_dataset(filename)
theta_0 = ds_init["zgrid"].isel(nCells=1472,nVertLevelsP1=0).values + 1./ds_init["rdzw"].isel(nVertLevels=0).values/2
theta_1 = ds_init["zgrid"].isel(nCells=1472,nVertLevelsP1=1).values + 1./ds_init["rdzw"].isel(nVertLevels=1).values/2
theta_2 = ds_init["zgrid"].isel(nCells=1472,nVertLevelsP1=2).values + 1./ds_init["rdzw"].isel(nVertLevels=2).values/2
print (theta_0)
print (theta_1)
print (theta_2)
print (ds_init["zgrid"].isel(nCells=1472,nVertLevelsP1=2).values)

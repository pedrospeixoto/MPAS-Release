#!/usr/bin/env python

import xarray as xr
from scipy.interpolate import interp1d
import sys
import numpy as np
import matplotlib.pyplot as plt

# Input and output file names
filename = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test2_gtm_simulation/cat.nc"
outfile = 'height_interp.nc'
#
# Set list of height levels (in m)
#

#
# Set list of fields, each of which must be dimensioned
# by ('Time', 'nCells', 'nVertLevels')
#
field_names = [ 'uReconstructZonal', 'uReconstructMeridional', 'zgrid']
#
# Read fields
#
ds = xr.open_dataset(filename)
ds = ds[field_names]
print (ds)
print (ds.Time)

# Do vertical interpolation
## Height level for which we want the interpolated value
levs_h = [100.]
# Cell corresponding to Perdigao's tower 13
Cells = [1472] 

print(ds['zgrid'].loc[:,Cells[0],0].values)
print(ds['uReconstructZonal'].loc[:,Cells[0],0].values)
print(ds['uReconstructMeridional'].loc[:,Cells[0],0].values)

# Interpolated values
zonal_interp = []
merid_interp = []
wind_speed_interp = []
wind_speed_0 = []

## Loop
for t in ds.Time:
    for cell in Cells:
        y_zonal = interp1d(ds['zgrid'].loc[t,cell,:-1], ds['uReconstructZonal'].loc[t,cell,:],
                         bounds_error=False, fill_value='extrapolate')
        y_merid = interp1d(ds['zgrid'].loc[t,cell,:-1], ds['uReconstructMeridional'].loc[t,cell,:],
                         bounds_error=False, fill_value='extrapolate')
        zonal_interp.append(y_zonal(levs_h[0]))
        merid_interp.append(y_merid(levs_h[0]))
        wind_speed_interp.append(np.sqrt(y_zonal(levs_h[0])*y_zonal(levs_h[0])
                             + y_merid(levs_h[0])*y_merid(levs_h[0])))
        wind_speed_0.append(np.sqrt(ds['uReconstructZonal'].loc[t,cell,0]**2
                            + ds['uReconstructMeridional'].loc[t,cell,0]**2))

plt.figure('zonal')
plt.plot(ds.Time,zonal_interp,label='interp at 100m')
plt.plot(ds.Time,ds['uReconstructZonal'].loc[:,cell,0],label=f"0")
plt.plot(ds.Time,ds['uReconstructZonal'].loc[:,cell,1],label=f"1")
plt.plot(ds.Time,ds['uReconstructZonal'].loc[:,cell,2],label=f"2")
plt.plot(ds.Time,ds['uReconstructZonal'].loc[:,cell,3],label=f"3")
plt.legend()
plt.savefig('zonal.png')

plt.figure('merid')
plt.plot(ds.Time,merid_interp,label='interp at 100m')
plt.plot(ds.Time,ds['uReconstructMeridional'].loc[:,cell,0],label="0")
plt.plot(ds.Time,ds['uReconstructMeridional'].loc[:,cell,1],label="1")
plt.plot(ds.Time,ds['uReconstructMeridional'].loc[:,cell,2],label="2")
plt.plot(ds.Time,ds['uReconstructMeridional'].loc[:,cell,3],label="3")
plt.legend()
plt.savefig('merid.png')

plt.figure('wind_speed')
plt.plot(ds.Time,wind_speed_interp,label='interp')
plt.plot(ds.Time,wind_speed_0,label="original")
plt.legend()
plt.savefig('wind_speed_interp.png')

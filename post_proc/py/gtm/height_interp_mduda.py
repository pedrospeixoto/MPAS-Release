#!/usr/bin/env python

"""
 Vertically interpolate MPAS-Atmosphere fields to a specified set
 of isobaric levels. The interpolation is linear in log-pressur.

 Variables to be set in this script include:
    - levs_hPa : a list of isobaric levels, in hPa
    - field_names : a list of names of fields to be vertically interpolated
                    these fields must be dimensioned by ('Time', 'nCells', 'nVertLevels')
    - fill_val : a value to use in interpolated fields to indicate values below
                 the lowest model layer midpoint or above the highest model layer midpoint

 Modified from isobaric_interp.py by mgduda (https://forum.mmm.ucar.edu/threads/how-to-extract-wind-zonal-meridional-geopotential-height-using-the-convert_mpas-include_field.9147/)
"""


from netCDF4 import Dataset
from scipy.interpolate import interp1d
import sys
import numpy as np


if len(sys.argv) < 2 or len(sys.argv) > 3:
    print('')
    print('Usage: isobaric_interp.py <input filename> [output filename]')
    print('')
    print('       Where <input filename> is the name of an MPAS-Atmosphere netCDF file')
    print('       containing a 3-d pressure field as well as all 3-d fields to be vertically')
    print('       interpolated to isobaric levels, and [output filename] optionally names')
    print('       the output file to be written with vertically interpolated fields.')
    print('')
    print('       If an output filename is not given, interpolated fields will be written')
    print('       to a file named isobaric.nc.')
    print('')
    #exit()

#filename = sys.argv[1]
filename = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test2_gtm_simulation/cat.nc"
if len(sys.argv) == 3:
    outfile = sys.argv[2]
else:
    outfile = 'height_interp.nc'

#
# Set list of height levels (in m)
#
levs_h = [100., 278.90486829, 345.61576659, 434.78884121, 557.58486064,
          725.10354185, 948.35722037, 1238.26625372, 1605.71714561,
          2061.67088025, 2617.14289605, 3283.08158968, 4070.78625209,
          4988.44235771, 5948.17772141, 6905.74497989, 7859.68182817,
          8810.34656767,  9759.05486013, 10707.03207955, 11655.64000729,
          12605.90934701, 13558.45270712, 14513.583648,   15471.38780339,
          16431.77815295, 17394.54310526, 18359.38967871, 19325.98184473,
          20293.97332015, 21263.033979,   22232.8692825,  23203.23253467,
          24173.93025883, 25144.82148219, 26115.81214915, 27086.8462089,
          28057.89510132]#, 29028.94737415]

#
# Set list of fields, each of which must be dimensioned
# by ('Time', 'nCells', 'nVertLevels')
#
field_names = [ 'uReconstructZonal', 'uReconstructMeridional' ]

#
# Set the fill value to be used for points that are below ground
# or above the model top
#
fill_val = -1.0e30

#
# Read 3-d pressure, zonal wind, and meridional wind fields
# on model zeta levels
#
f = Dataset(filename)

nCells = f.dimensions['nCells'].size
nVertLevels = f.dimensions['nVertLevels'].size
nTime = f.dimensions['Time'].size
Cell = [1472] # Cell corresponding to Perdigao's tower 13
zgrid = f.variables['zgrid'][:,:,:-1]
xtime = f.variables['xtime'][:]

# List of fields
fields = []
for field in field_names:
    fields.append(f.variables[field][:])

f.close()

#print (levs_h)
#print (nCells)
#print (nVertLevels)
#print (nTime)
#print (Cell)
print (zgrid)
#print (xtime)
#print (fields)

# Allocate list of output fields
#
interp_fields = []
interp_fieldnames = []
for field in field_names:
    for lev in levs_h:
        interp_fields.append(np.zeros((nCells)))
        interp_fieldnames.append(field+'_'+repr(round(lev))+'m')

print (len(levs_h))
print (len(interp_fields))

# #
# # Create netCDF output file
# #
f = Dataset(outfile, 'w', clobber=False)

f.createDimension('Time', size=nTime)
f.createDimension('nCells', size=nCells)
f.createDimension('nVertLevels',size=nVertLevels)
for field in interp_fieldnames:
    f.createVariable(field, 'f', dimensions=('Time','nCells','nVertLevels'), fill_value=fill_val)


# #
# # Loop over times
# #
for t in range(len(xtime)):

    timestring = xtime[t,0:19].tostring()
    print('Interpolating fields at time '+timestring.decode('utf-8'))

#     #
#     # Vertically interpolate
#     #
    for iCell in range(nCells):

        i = 0
        for field in fields:
            y = interp1d(zgrid[t,iCell,:], field[t,iCell,:],
                         bounds_error=False, fill_value=fill_val)
            for lev in range(len(levs_h)):
                interp_fields[i][iCell] = y(levs_h[lev])
                i = i + 1

#     #
#     # Save interpolated fields
#     #
    for i in range(len(interp_fieldnames)):
        f.variables[interp_fieldnames[i]][t,:] = interp_fields[i][:]

f.close()
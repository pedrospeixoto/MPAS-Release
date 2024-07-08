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
    exit()

filename = sys.argv[1]
if len(sys.argv) == 3:
    outfile = sys.argv[2]
else:
    outfile = 'isobaric.nc'


#
# Set list of isobaric levels (in hPa)
#
levs_hPa = [ 1000.0, 975.0, 950.0, 925.0, 900.0,
              850.0, 800.0, 750.0, 700.0, 650.0,
              600.0, 550.0, 500.0, 450.0, 400.0,
              350.0, 300.0, 250.0, 200.0, 150.0,
              100.0,  70.0,  50.0,  30.0,  20.0,
               10.0 ]


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

pressure = f.variables['pressure'][:]

xtime = f.variables['xtime'][:]

fields = []
for field in field_names:
    fields.append(f.variables[field][:])

f.close()


#
# Convert pressure from Pa to hPa
#
pressure = pressure * 0.01


#
# Compute logarithm of isobaric level values and 3-d pressure field
#
pressure = np.log(pressure)
levs = np.log(levs_hPa)


#
# Allocate list of output fields
#
isobaric_fields = []
isobaric_fieldnames = []
for field in field_names:
    for lev in levs_hPa:
        isobaric_fields.append(np.zeros((nCells)))
        isobaric_fieldnames.append(field+'_'+repr(round(lev))+'hPa')


#
# Create netCDF output file
#
f = Dataset(outfile, 'w', clobber=False)

f.createDimension('Time', size=None)
f.createDimension('nCells', size=nCells)

for field in isobaric_fieldnames:
    f.createVariable(field, 'f', dimensions=('Time','nCells'), fill_value=fill_val)


#
# Loop over times
#
for t in range(len(xtime)):

    timestring = xtime[t,0:19].tostring()
    print('Interpolating fields at time '+timestring.decode('utf-8'))

    #
    # Vertically interpolate
    #
    for iCell in range(nCells):

        i = 0
        for field in fields:
            y = interp1d(pressure[t,iCell,:], field[t,iCell,:],
                         bounds_error=False, fill_value=fill_val)
            for lev in range(len(levs)):
                isobaric_fields[i][iCell] = y(levs[lev])
                i = i + 1


    #
    # Save interpolated fields
    #
    for i in range(len(isobaric_fieldnames)):
        f.variables[isobaric_fieldnames[i]][t,:] = isobaric_fields[i][:]

f.close()

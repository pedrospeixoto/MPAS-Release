#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to concatenate nc files in time domain and calculate wind speed for
a particular point (lon,lat,vertlevel).
"""
import xarray as xr
import numpy as np
import mpas_plot_aux as mplot
import matplotlib.pyplot as plt

def closest_value(arr, x):
    index = np.abs(np.array(arr) - x).argmin()
    return index

def closest_value_2(ds,lon,lat):
    ds['dist_norm'] = np.sqrt((ds['longitude'] - lon)**2 + (ds['latitude'] - lat)**2)
    mask = ds['dist_norm'] == ds['dist_norm'].min()
    #print ('mask:')
    #print (mask)
    #print ('number of matches:')
    #print (mask.sum())
    nCells_index = mask.argmax(dim='nCells')
    #print ("nCells index:")
    #print (nCells_index)
    nCells_value = ds['nCells'].isel(nCells=nCells_index.values.item())
    #print ("nCells value:")
    #print (nCells_value)
    return nCells_value

# Directory containing model output data
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test2_gtm_simulation"
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test4_fig6_with6hspinup_correctingICsLBCs"
data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work"

# Read dataset with concatenated data
ds = xr.open_dataset(f"{data_dir}/cat.nc")
ds = mplot.add_mpas_mesh_variables(ds)

print (ds.zgrid)

# Define point of interest
lat = 39.7136
lon = -7.73
vertlevel = [0,1,2]

#index_lon = closest_value(ds['longitude'].sel(Time=0), lon)
#index_lat = closest_value(ds['latitude'].sel(Time=0), lat)
index_closest  = closest_value_2(ds=ds.sel(Time=0),lon=lon,lat=lat)
print ("nCells:",index_closest)

lon_sel2 = ds['longitude'].sel(Time=0,nCells=index_closest)
lat_sel2 = ds['latitude'].sel(Time=0,nCells=index_closest)
#print (lon_sel2)
#print (lat_sel2)

print (ds['zgrid'].sel(Time=0,nCells=index_closest).values)

# Obtain wind time series for that particular point at lowest vertical level 
# (lowest zgrid= 278.9 m, so height for wind speed will be even higher)
wind_speed = np.zeros((len(vertlevel),len(ds.Time)))
for t in range(len(ds.Time)):
    for l in range(len(vertlevel)):
        wind_speed[l,t] = np.sqrt((ds['uReconstructZonal'].sel(nCells=index_closest,
                                                    nVertLevels=vertlevel[l],
                                                    Time=ds.Time[t]).values)**2
                        +(ds['uReconstructMeridional'].sel(nCells=index_closest,
                                                    nVertLevels=vertlevel[l],
                                                    Time=ds.Time[t]).values)**2)
print (wind_speed)

plt.figure("wind_speed")
plt.plot(ds.Time,wind_speed[0,:],label='theta(0)/tower_height=312m/485m')
plt.plot(ds.Time,wind_speed[1,:],label='theta(1)/tower_height=390m/485m')
plt.plot(ds.Time,wind_speed[2,:],label='theta(1)/tower_height=496m/485m')
plt.xlabel("Time [h]",fontsize=12)
plt.ylabel("Wind Speed [m/s]",fontsize=12)
plt.tick_params(axis='both', which='major', labelsize=12)
plt.xticks(np.arange(min(ds.Time), max(ds.Time)+1,1),
           rotation=45, ha='center')
plt.grid(True)
plt.legend(loc='lower left', bbox_to_anchor=(0., 1.02), borderaxespad=0)
plt.tight_layout()
plt.show()
plt.savefig("windspeed.png")

plt.figure("wind_speed_without_spinup")
plt.plot(ds.Time[0:24],wind_speed[0,6:],label='theta(0)/tower_height=312m/485m')
plt.plot(ds.Time[0:24],wind_speed[1,6:],label='theta(1)/tower_height=390m/485m')
plt.plot(ds.Time[0:24],wind_speed[2,6:],label='theta(2)/tower_height=496m/485m')
plt.xlabel("Time [h]",fontsize=12)
plt.ylabel("Wind Speed [m/s]",fontsize=12)
plt.tick_params(axis='both', which='major', labelsize=12)
plt.xticks(np.arange(min(ds.Time), max(ds.Time)+1,1),
           rotation=45, ha='center')
plt.grid(True)
plt.legend(loc='lower left', bbox_to_anchor=(0., 1.02), borderaxespad=0)
plt.tight_layout()
plt.xlim([0,24])
plt.ylim([0,12])
plt.show()
plt.savefig("windspeed_without_spinup.png")

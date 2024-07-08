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
import cfgrib

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

def closest_value_era5(ds,lon,lat):
    ds['dist_norm'] = np.sqrt((ds['longitude'] - lon)**2 + (ds['latitude'] - lat)**2)
    lon_min = ds['longitude'].where(ds['dist_norm'] == ds['dist_norm'].min()).values
    # Select only that value where lon is not nan
    lon_min = lon_min[~np.isnan(lon_min)]
    lat_min = ds['latitude'].where(ds['dist_norm'] == ds['dist_norm'].min()).values
    # Select only that value where lon is not nan
    lat_min = lat_min[~np.isnan(lat_min)]

    return lon_min,lat_min

def compute_wind_speed(data_dir,lat,lon,vertlevel):

    # Read dataset with concatenated data
    ds = xr.open_dataset(f"{data_dir}/cat.nc")
    ds = mplot.add_mpas_mesh_variables(ds)

    print (ds.zgrid)

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
    return ds.Time, wind_speed

# Define point of interest
lat = 39.7136
lon = -7.73
vertlevel_30km = [1] #[0,1,2]
vertlevel_21km = [2]

def compute_wind_speed_era5(data_dir_u,data_dir_v,lat,lon,vertlevel):
    # see https://stackoverflow.com/questions/67963199/xarray-from-grib-file-to-dataset
    # Import data
    grib_data_u = cfgrib.open_datasets(data_dir_u)[0]
    grib_data_v = cfgrib.open_datasets(data_dir_v)[0]
    # Correct longitude values
    grib_data_u['longitude'] = grib_data_u['longitude'].where(grib_data_u['longitude'] <= 180.0, grib_data_u['longitude'] - 360.0)
    grib_data_v['longitude'] = grib_data_v['longitude'].where(grib_data_v['longitude'] <= 180.0, grib_data_v['longitude'] - 360.0)
    # Find (lon_min,lat_min) that are closest to (lon,lat) given in input
    lon_min_u,lat_min_u = closest_value_era5(ds=grib_data_u,lon=lon,lat=lat)
    lon_min_v,lat_min_v = closest_value_era5(ds=grib_data_v,lon=lon,lat=lat)
    # Check whether the same (lon_min,lat_min) was found for both u and v
    if lon_min_u == lon_min_v:
        if lat_min_u == lat_min_v:
            print ("same (lon,lat) found for u and v in era5 data")
            lat_min = lat_min_u
            lon_min = lon_min_u
        else:
            raise Exception("lat_min_u differs from lat_min_v")
    else:
        raise Exception("lon_min_u differs from lon_min_v")
    print ("lat_min", lat_min)
    print ("lon_min", lon_min)
    # Obtain wind time series
    wind_speed = np.zeros((len(vertlevel),len(grib_data_u.time)))
    for t in range(len(grib_data_u.time)):
        for l in range(len(vertlevel)):
            wind_speed[l,t] = np.sqrt((grib_data_u['u'].sel(longitude=lon_min,
                                                            latitude=lat_min,
                                                        isobaricInhPa=vertlevel[l],
                                                        time=grib_data_u.time[t]).values)**2
                            +(grib_data_v['v'].sel(longitude=lon_min,
                                                            latitude=lat_min,
                                                        isobaricInhPa=vertlevel[l],
                                                        time=grib_data_u.time[t]).values)**2)
    print (wind_speed)
    return grib_data_u.time,wind_speed

# Calculations for ERA5 data
data_dir_u = ("/storage/guilherme_torresmendonca/projeto_nudging_mpas/"
               +"data/raw/ERA5/data_20170403_18h_to_20170405_00h/"
               +"e5.oper.an.pl.128_131_u.ll025uv.2017040300_2017040523_cat.grb")
data_dir_v = ("/storage/guilherme_torresmendonca/projeto_nudging_mpas/"
              +"data/raw/ERA5/data_20170403_18h_to_20170405_00h/"
              +"e5.oper.an.pl.128_132_v.ll025uv.2017040300_2017040523_cat.grb")
vertlevel_era5 = [1000,975.,950.]
t_era5,wind_speed_era5 = compute_wind_speed_era5(data_dir_v=data_dir_v,
                                                 data_dir_u=data_dir_u,
                                                 lat=lat,
                                                 lon=lon,
                                                 vertlevel=vertlevel_era5)
# Directory containing model output data
data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/experiments/test4_fig6_with6hspinup_correctingICsLBCs"
t1,wind_speed_mpas = compute_wind_speed(data_dir,lat,lon,vertlevel_30km)
# Directory containing model output data
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work_same_as_test4_gtm"
#t2,wind_speed_mpas_nudging = compute_wind_speed(data_dir,lat,lon,vertlevel_30km)
# Directory containing model output data
data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/experiments/test_mpas_nudging_hourly_exampleGuilherme"
t3,wind_speed_bueno = compute_wind_speed(data_dir,lat,lon,vertlevel_21km)
# Directory containing model output data
data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/experiments/test5_fig6_withnudging/Apr2017/work_nudg_coeffs_zero"
t4,wind_speed_zero = compute_wind_speed(data_dir,lat,lon,vertlevel_30km)
# Directory containing model output data
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work_v8nudging_corrected_lbcs_generated_again_BUTWRONG2"
data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/experiments/test5_fig6_withnudging/Apr2017/work_v8nudging_meshsimilartobuenos"
t5,wind_speed_v8nudging_mymesh = compute_wind_speed(data_dir,lat,lon,vertlevel_30km)
# Directory containing model output data
data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/experiments/test5_fig6_withnudging/Apr2017/work_v8nudging_myfdda_and_buenomesh_myconfig_corrected_myztop"
t6,wind_speed_v8nudging_buenosmesh = compute_wind_speed(data_dir,lat,lon,vertlevel_30km)


plt.figure("wind_speed_without_spinup")
#plt.plot(t1[0:24],wind_speed_mpas[0,6:-1],linestyle='--',label='v8_no_nudging')
plt.plot(t4[0:24],wind_speed_zero[0,6:],linestyle='--',color='k',
         label='v8_with_nudging, nudg_coeffs=0')
plt.plot(t1[0:24],wind_speed_era5[1,24:48],linestyle='--',
         label='era5, 975 hPa')
plt.plot(t3[1:24],wind_speed_bueno[0,6:],linestyle='--',label='v7_with_nudging (Bueno)')
plt.plot(t6[0:24],wind_speed_v8nudging_buenosmesh[0,6:],label='v8_with_nudging_buenos_mesh')
plt.plot(t5[0:24],wind_speed_v8nudging_mymesh[0,6:],label='v8_with_nudging_mesh_similar_to_buenos')
plt.xlabel("Time [h]",fontsize=12)
plt.ylabel("Wind Speed [m/s]",fontsize=12)
plt.tick_params(axis='both', which='major', labelsize=12)
plt.xticks(np.arange(min(t1), max(t1)+1,1),
           rotation=45, ha='center')
plt.grid(True)
#plt.legend(loc='lower left', bbox_to_anchor=(0., 1.02), borderaxespad=0)
plt.legend(loc='best')
plt.tight_layout()
plt.xlim([0,24])
plt.ylim([0,12])
plt.title("wind speed at theta(1) = 390m; 2017-04-04")
plt.show()
plt.savefig("windspeed_without_spinup_comparison_mymesh_buenosmesh2.png")

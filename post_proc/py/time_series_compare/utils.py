#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import xarray as xr
import numpy as np
import math
import pandas as pd
from geopy.distance import distance
from haversine import haversine

#TODO: utils.py should contain generally useful functions for postprocessing.
#      Therefore, it should live under MPAS-BR/post_proc/py/.

derived_variables = {
    'latCell': ['latitude'],
    'lonCell': ['longitude'],
    'latVertex': ['latitudeVertex'],
    'lonVertex': ['longitudeVertex'],
    'areaCell': ['area', 'resolution'],
}

def add_mpas_mesh_variables(ds, full=True, **kwargs):
    for v in ds.data_vars:
        if v not in derived_variables:
            continue

        newvs = derived_variables[v]

        for newv in newvs:
            if newv in ds:
                #print(newv + ' already here')
                continue

            if 'lat' in v or 'lon' in v:
                ds[newv] = xr.apply_ufunc(np.rad2deg, ds[v])
                ds[newv] = ds[newv].where(ds[newv] <= 180.0, ds[newv] - 360.0)
                ds[newv].attrs['units'] = 'degrees'

            elif newv == 'area':
                radius_circle = ds.attrs.get('sphere_radius', 1.0)
                if radius_circle == 1:
                    # need to correct to earth radius
                    correction_rad_earth = 6371220.0
                else:
                    correction_rad_earth = 1

                ds[newv] = (ds[v] / 10 ** 6) * correction_rad_earth**2
                ds[newv].attrs['units'] = 'km^2 (assuming areaCell in m^2)'
                ds[newv].attrs['long_name'] = 'Area of the cell in km^2'

            elif newv == 'resolution':
                radius_circle = ds.attrs.get('sphere_radius', 1.0)
                if radius_circle == 1.0:
                    #print('need to correct to earth radius!!')
                    correction_rad_earth = 6371220.0
                else:
                    correction_rad_earth = 1

                # km^2 (assuming areaCell in m^2)
                area = (ds[v] / 10 ** 6) * correction_rad_earth**2

                ds[newv] = 2 * (xr.apply_ufunc(np.sqrt, area / math.pi))
                ds[newv].attrs['units'] = 'km'
                ds[newv].attrs['long_name'] = 'Resolution of the cell (approx)'

    return ds

def bash_array_to_list(bash_array):
    return bash_array.split("|")[:-1]

def cs_string_to_list(cs_string):
    return cs_string.split(",")

def create_datetime_range(t0,tf,dt,short_strings='n'):
    '''
    Creates a list of datetime strings between t0 and tf, with 
    time step dt.

    INPUT: t0 (str) - initial datetime in format 'YYYY.mm.dd HH:MM:SS'
           tf (str) - final datetime in format 'YYYY.mm.dd HH:MM:SS'
           dt (str) - time step in seconds

    OUTPUT: datetime_str_list (list) - list of datetime strings
    '''
    t0 = pd.Timestamp(t0)
    tf = pd.Timestamp(tf)
    datetime_range = pd.date_range(start=t0,end=tf,freq=f"{dt}S")
    if short_strings == 'y':
        datetime_str_list = [dt.strftime('%d/%m %Hh') for dt in datetime_range]
    else:
        datetime_str_list = [dt.strftime('%Y-%m-%d_%H.%M.%S') for dt in datetime_range]
    return datetime_str_list

def concat_mpas_output(stream,datetime_list,data_dir,vars_list):
    '''
    Concatenates in time, for variables vars_list,  
    MPAS output files named as follows:

    stream.YYYY.mm.dd_HH.MM.SS

    INPUT: stream (str) - name of the stream
           datetime_list (list) - list of datetime strings in format YYYY.mm.dd_HH.MM.SS
           data_dir (str) - directory where output files are stored
           vars_list (list) - list of variable names (strings)
    
    OUTPUT: cat_file (Xarray dataset) - concatenated dataset
    '''
    # Set variable list to keep in file
    vars_list.extend(['latCell','lonCell','latVertex','lonVertex','areaCell'])
    # Read first file
    filename1 = stream + '.' + datetime_list[0] + '.nc'
    cat_file = xr.open_dataset(f'{data_dir}/{filename1}', engine='netcdf4')[vars_list]
    # Read and concatenate that file to remaining files
    for datetime in datetime_list[1:]:
        filename = stream + '.' + datetime + '.nc'
        ds_temp = xr.open_dataset(f'{data_dir}/{filename}', engine='netcdf4')[vars_list]
        cat_file = xr.concat([cat_file, ds_temp], dim='Time')
    return cat_file

def get_distance_haversine(lats, lons, lat_ref, lon_ref):
    '''
    Using the haversine formula (https://en.wikipedia.org/wiki/Haversine_formula), 
    returns the distance in km of each lat, lon point to (lat_ref,lon_ref).
     
    from Marta G. Badarjí, slightly modified (based on 
    pypi haversine package: https://pypi.org/project/haversine/) 
    by G. Torres Mendonça
    '''

    radius = 6371.0088  # km
    d_lat = np.radians(lats - lat_ref)  # lat distance in radians
    d_lon = np.radians(lons - lon_ref)  # lon distance in radians

    a = (np.sin(d_lat / 2.) * np.sin(d_lat / 2.) +
         np.cos(np.radians(lat_ref)) * np.cos(np.radians(lats)) *
         np.sin(d_lon / 2.) * np.sin(d_lon / 2.))
    c = np.arcsin(np.sqrt(a))
    d = 2 * radius * c

    return d

def closest_value_haversine(ds,lon,lat):
    d = get_distance_haversine(ds['latitude'].values, ds['longitude'].values,
                                            lat_ref=lat, lon_ref=lon)
    ds['distance'] = xr.DataArray(d, dims=['nCells'])
    #print ('distance data array')
    #print (ds[['distance','longitude','latitude']])
    nCells_index = ds['distance'].argmin().item()
    #print ('nCells_index')
    #print (nCells_index)
    #print ('distance min')
    #print (ds['distance'].min())
    #print ('ds[nCells]:')
    #print (ds['nCells'])
    nCells_value = ds['nCells'].isel(nCells=nCells_index)
    distance_value = ds['distance'].isel(nCells=nCells_index)
    return nCells_value, distance_value

def find_nCells_from_latlon(ds,lon,lat,method='haversine',verbose='y'):
    ds = add_mpas_mesh_variables(ds)
    if method == 'haversine':
        index_closest, distance_value  = closest_value_haversine(ds=ds.sel(Time=0),lon=lon,lat=lat)
    else:
        print (f"{method} method not supported.")
        exit (-1)
    if verbose == 'y':
        # Print information on (lon,lat) point
        closest_lon = ds['longitude'].sel(Time=0,nCells=index_closest)
        closest_lat = ds['latitude'].sel(Time=0,nCells=index_closest)
        print ("input (lon,lat):", (lon,lat))
        print ("closest (lon,lat):", (float(closest_lon),float(closest_lat)))
        print ("distance to input point (km):", distance_value.values)
        print ("corresponding nCells value:",index_closest.values)
        print ('max/min lat:', ds['latitude'].values.max(),ds['latitude'].values.min())
        print ('max/min lon:', ds['longitude'].values.max(),ds['longitude'].values.min())
    return index_closest, ds

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to concatenate nc files in time domain
"""
import xarray as xr
import numpy as np

data_dir = ("/storage/guilherme_torresmendonca/projeto_nudging_mpas/"
            +"downloading_ERA5_data/data_20170403_18h_to_20170405_00h")

vars = ['lv_ISBL1','V_GDS0_ISBL','g0_lat_2','g0_lon_3']

# TODO: find all files automatically from initial and final dates
file_list = ['e5.oper.an.pl.128_131_u.ll025uv.2017040300_2017040323.grb',
             'e5.oper.an.pl.128_131_u.ll025uv.2017040400_2017040423.grb',
             'e5.oper.an.pl.128_131_u.ll025uv.2017040500_2017040523.grb']

file_list = [xr.open_dataset(f'{data_dir}/{filename}')[vars] for filename in file_list]

cat_file = xr.concat(file_list,dim="initial_time0_hours")

cat_file.to_netcdf(f"{data_dir}/cat.nc")
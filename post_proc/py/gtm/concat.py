#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to concatenate nc files in time domain
"""
import xarray as xr
import numpy as np

data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test2_gtm_simulation"

initial_hour = 0
final_hour = 23
hour_array = range(initial_hour,final_hour+1)
hour_list = []

for i in range(len(hour_array)):
    if hour_array[i] < 10:
        hour_list.append(f"0{str(hour_array[i])}")
    else:
        hour_list.append(str(hour_array[i]))

name_list = [f"{data_dir}/history.2017-04-04_{h}.00.00.nc" for h in hour_list]
file_list = [xr.open_dataset(name) for name in name_list]

cat_file = xr.concat(file_list,dim="Time")

cat_file.to_netcdf(f"{data_dir}/cat.nc")
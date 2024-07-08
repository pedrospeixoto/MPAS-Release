#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to concatenate nc files in time domain
"""
import xarray as xr
import numpy as np

#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test4_fig6_with6hspinup_correctingICsLBCs"
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work"
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test_mpas_nudging_hourly_exampleGuilherme"
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work_nudg_coeffs_zero"
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work_v8nudging_myfdda_and_buenomesh_myconfig"
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work_v8nudging_myfdda_and_buenomesh_myconfig_corrected_myztop"
#data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work_v8nudging_corrected_lbcs_generated_again_BUTWRONG2_buenosztop"
data_dir = "/storage/guilherme_torresmendonca/projeto_nudging_mpas/test5_fig6_withnudging/Apr2017/work_v8nudging_meshsimilartobuenos"

vars = ['zgrid','uReconstructZonal','uReconstructMeridional','latCell','lonCell']
# TODO: find all files automatically from initial and final dates
file_list =  ['history.2017-04-03_18.00.00.nc',
              'history.2017-04-03_19.00.00.nc',
              'history.2017-04-03_20.00.00.nc',
              'history.2017-04-03_21.00.00.nc',
              'history.2017-04-03_22.00.00.nc',
              'history.2017-04-03_23.00.00.nc',
              'history.2017-04-04_00.00.00.nc',
              'history.2017-04-04_01.00.00.nc',
              'history.2017-04-04_02.00.00.nc',
              'history.2017-04-04_03.00.00.nc',
              'history.2017-04-04_04.00.00.nc',
              'history.2017-04-04_05.00.00.nc',
              'history.2017-04-04_06.00.00.nc',
              'history.2017-04-04_07.00.00.nc',
              'history.2017-04-04_08.00.00.nc',
              'history.2017-04-04_09.00.00.nc',
              'history.2017-04-04_10.00.00.nc',
              'history.2017-04-04_11.00.00.nc',
              'history.2017-04-04_12.00.00.nc',
              'history.2017-04-04_13.00.00.nc',
              'history.2017-04-04_14.00.00.nc',
              'history.2017-04-04_15.00.00.nc',
              'history.2017-04-04_16.00.00.nc',
              'history.2017-04-04_17.00.00.nc',
              'history.2017-04-04_18.00.00.nc',
              'history.2017-04-04_19.00.00.nc',
              'history.2017-04-04_20.00.00.nc',
              'history.2017-04-04_21.00.00.nc',
              'history.2017-04-04_22.00.00.nc',
              'history.2017-04-04_23.00.00.nc']#,
              #'history.2017-04-05_00.00.00.nc']

file_list = [xr.open_dataset(f'{data_dir}/{filename}')[vars] for filename in file_list]

cat_file = xr.concat(file_list,dim="Time")

cat_file.to_netcdf(f"{data_dir}/cat.nc")

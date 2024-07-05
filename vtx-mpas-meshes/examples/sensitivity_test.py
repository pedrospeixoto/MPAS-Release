import os

import pandas as pd

from vtxmpasmeshes.dataset_utilities import open_mpas_regional_file
from vtxmpasmeshes.mesh_generator import full_generation_process, \
    cut_circular_region_beta
from vtxmpasmeshes.mpas_plots import compare_plot_mpas_regional_meshes, \
    view_mpas_regional_mesh, plot_era5_grid, plot_wrf_grid, \
    plot_expected_resolution_rings

from vtxmpasmeshes.plot_utilities import plot_mpas_darray, \
    set_plot_kwargs, add_colorbar, \
    start_cartopy_map_axis, close_plot

import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

DATA_FOLDER = '/home/marta/PycharmProjects/vtx-mpas-meshes/data/' \
              'sensitivity-test-3'

# SITE: perdigao
lat_ref = 39.7136
lon_ref = -7.73

highres = 3
lowres = 20
numlayers = 8

details = {}
grids = []
for margin in [#50,
               #75,
               #100,
               125,
               #150, 250
               ]:
    for size in [#15,
                 #20, 25,
                 30, 35,
                 #50
                 ]:

        name = 'senst_s' + str(size).zfill(2) + '_m' + str(margin).zfill(3)
        folder = DATA_FOLDER + '/' + name + '/'
        basename = folder + name

        global_mesh = basename + '.grid.nc'
        if not os.path.exists(global_mesh):
            os.system('mkdir -p ' + folder)

            # I do a global mesh centered at 0,0 -> to use in MPAS workflow
            full_generation_process(
                global_mesh, 'doughnut',
                redo=False, do_plots=False, do_region=False,
                highresolution=highres, lowresolution=lowres,
                size=size, margin=margin,
                lat_ref=0., lon_ref=0.,
            )

        radius = size+margin
        region_border = radius + (numlayers*lowres)*0.9
        configid = '99' + str(size).zfill(2) + str(margin).zfill(3)
        details[name] = {
            'globalfile': global_mesh,
            'configid': configid,
            'size': size,
            'margin': margin,
            'radius': radius,
            'region_border': region_border,
        }

        with open(DATA_FOLDER + '/config.' + configid + '.txt', 'w') as f:
            f.write('mesh=' + name + '.grid.nc \n')
            f.write('resolution=3' + '\n')
            f.write('inner_size=' + str(size) + '\n')
            f.write('radius=' + str(radius) + '\n')
            f.write('region_border=' + str(region_border) + '\n')
            f.write('num_boundary_layers=8' + '\n')
            f.write('product=raw' + '\n')
            f.write('max_num_domains=2' + '\n')
            f.write('time_integration_order=2' + '\n')
            f.write('two_way_nesting=false' + '\n')
            f.write('stream_list=\'reduced\'' + '\n')
            f.write('final_vars=\'reduced\'' + '\n')
            f.write('levs=\'as_vortex\'' + '\n')

        regional_mesh = DATA_FOLDER + '/' + name + '.region.grid.nc'
        if not os.path.exists(regional_mesh):
            # I do a regional mesh at my location -> with 4 layers
            full_generation_process(
                regional_mesh, 'doughnut',
                redo=False, do_plots=False, do_region=True,
                highresolution=highres, lowresolution=lowres,
                num_boundary_layers=numlayers,
                size=size, margin=margin,
                lat_ref=lat_ref, lon_ref=lon_ref,
            )

        f = DATA_FOLDER + '/' + name + '.mpaswrf_mesh.png'
        if not os.path.isfile(f):
            print('MPAS WRF Plots')
            view_mpas_regional_mesh(regional_mesh,
                                    outfile=f,
                                    do_plot_resolution_rings=True,
                                    do_plot_era5_grid=False,
                                    do_plot_wrf_grid=True,
                                    vname='resolution')

        vname = 'resolution'
        units = 'km'

        ds = open_mpas_regional_file(regional_mesh, full=True)

        myats = ds.attrs

        ax = plt.axes(projection=ccrs.PlateCarree())
        zorder = 2
        ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=zorder)
        ax.stock_img()
        ax.coastlines(resolution='10m', zorder=zorder + 1)

        gl = ax.gridlines(draw_labels=True, alpha=0., linestyle='--',
                          zorder=zorder + 2)
        gl.top_labels = False
        gl.right_labels = False

        plot_kwargs = set_plot_kwargs(ds[vname])
        plot_mpas_darray(ds, vname, ax=ax, title='', lat_ref=0.,
                         lon_ref=0., border_radius=None,
                         **plot_kwargs)
        plot_expected_resolution_rings(ds, ax=ax)
        add_colorbar(ax, label=vname + ' (' + units + ')', **plot_kwargs)
        close_plot(outfile=DATA_FOLDER + '/' + name + '.mpasmesh.png',
                   size_fig=[6, 4])

        ax = plt.axes(projection=ccrs.PlateCarree())
        zorder = 2
        ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=zorder)
        ax.stock_img()
        ax.coastlines(resolution='10m', zorder=zorder + 1)

        gl = ax.gridlines(draw_labels=True, alpha=0., linestyle='--',
                          zorder=zorder + 2)
        gl.top_labels = False
        gl.right_labels = False

        plot_kwargs = set_plot_kwargs(ds[vname])
        plot_mpas_darray(ds, vname, ax=ax, title='', lat_ref=0.,
                         lon_ref=0., border_radius=None,
                         **plot_kwargs)
        plot_expected_resolution_rings(ds, ax=ax)
        plot_wrf_grid(ds, ax=ax)
        add_colorbar(ax, label=vname + ' (' + units + ')', **plot_kwargs)
        close_plot(outfile=DATA_FOLDER + '/' + name + '.mpaswrfmesh.png',
                   size_fig=[6, 4])

        for border_radius in [size + 10, radius, region_border,
                              region_border + 200]:
            ax = plt.axes(projection=ccrs.PlateCarree())
            zorder = 2
            ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=zorder)
            ax.stock_img()
            ax.coastlines(resolution='10m', zorder=zorder + 1)

            gl = ax.gridlines(draw_labels=True, alpha=0., linestyle='--',
                              zorder=zorder + 2)
            gl.top_labels = False
            gl.right_labels = False

            plot_kwargs = set_plot_kwargs(ds[vname].where(ds['cellDistance']
                                                          <= border_radius))
            plot_mpas_darray(ds, vname, ax=ax, title='',
                             border_radius=border_radius,
                             **plot_kwargs)
            plot_expected_resolution_rings(ds, ax=ax)
            plot_wrf_grid(ds, ax=ax)
            add_colorbar(ax, label=vname + ' (' + units + ')', **plot_kwargs)
            ax.set_title(str(int(border_radius)) + 'km zoom', fontsize=14)
            close_plot(outfile=DATA_FOLDER + '/' + name + '.regionmesh.' +
                               str(border_radius) + '.png', size_fig=[6, 4])

        regionalbig_mesh = DATA_FOLDER + '/' + name + '.regionbig.grid.nc'
        if not os.path.exists(regionalbig_mesh):
            cut_circular_region_beta(global_mesh, 2000 * 1000,
                                     regional_grid=regionalbig_mesh,
                                     num_boundary_layers=8,
                                     lat_cen=0., lon_cen=0.)

        ds = open_mpas_regional_file(regionalbig_mesh, full=True,
                                     lat_ref=0., lon_ref=0.)

        ds.attrs = myats
        ds.attrs['vtx-param-lat_ref'] = 0.
        ds.attrs['vtx-param-lon_ref'] = 0.
        print(ds.attrs)

        for border_radius in [size + 10, radius, region_border,
                              500, 1000, 3000, 6000]:
            ax = plt.axes(projection=ccrs.PlateCarree())
            zorder = 2
            ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=zorder)
            ax.stock_img()
            ax.coastlines(resolution='10m', zorder=zorder + 1)

            gl = ax.gridlines(draw_labels=True, alpha=0., linestyle='--',
                              zorder=zorder + 2)
            gl.top_labels = False
            gl.right_labels = False

            plot_kwargs = set_plot_kwargs(ds[vname].where(ds['cellDistance']
                                                          <= border_radius))
            plot_mpas_darray(ds, vname, ax=ax, title='',
                             border_radius=border_radius,
                             **plot_kwargs)
            plot_expected_resolution_rings(ds, ax=ax)
            add_colorbar(ax, label=vname + ' (' + units + ')', **plot_kwargs)
            ax.set_title(str(int(border_radius)) + 'km zoom', fontsize=14)
            close_plot(outfile=DATA_FOLDER + '/' + name + '.mpasmesh.' +
                               str(border_radius) + '.png', size_fig=[6, 4])

        f = DATA_FOLDER + '/' + name + '.resolution_mesh.png'
        if not os.path.isfile(f):
            print('Resolution Plots')
            view_mpas_regional_mesh(regional_mesh, vname='resolution',
                                    outfile=f)

        f = DATA_FOLDER + '/' + name + '.distortion_mesh.png'
        if not os.path.isfile(f):
            print('Distortion Plots')
            view_mpas_regional_mesh(regional_mesh, vname='cellDistortion',
                                    outfile=f, border_radius=size,
                                    cmap='magma')

        print('\n' + '*' * 30)
        print('\nDONE. This is the mesh ' + regional_mesh)
        grids.append(regional_mesh)


info = pd.DataFrame.from_dict(details, orient='index')
print(info)
info.to_csv(DATA_FOLDER + '/info.csv')


kwargs_set = {
    'default': {},
    '150': {'border_radius': 150, 'vmin': 0},
    'inner': {'border_radius': 30, 'vmin': 0},
}

for test, kwargs in kwargs_set.items():

    f = DATA_FOLDER + '/distortion.' + test + '.png'
    if not os.path.isfile(f):
        compare_plot_mpas_regional_meshes(grids,
                                          outfile=f,
                                          suptitle='Meshes comparison: '
                                                   'Distortion',
                                          vname='cellDistortion',
                                          each_title='<NAME>: '
                                                     '<NCELLS> cells',
                                          lat_ref=lat_ref,
                                          lon_ref=lon_ref,
                                          cmap='magma',
                                          **kwargs
                                          )

    f = DATA_FOLDER + '/ratio_al.' + test + '.png'
    if not os.path.isfile(f):
        compare_plot_mpas_regional_meshes(grids,
                                          outfile=f,
                                          suptitle='Meshes comparison: '
                                                   'A/L Ratio',
                                          vname='area_length_ratio',
                                          each_title='<NAME>: '
                                                     '<NCELLS> cells',
                                          lat_ref=lat_ref,
                                          lon_ref=lon_ref,
                                          cmap='magma',
                                          **kwargs
                                          )
kwargs_set = {
    'default': {},
    '200': {'border_radius': 200, 'vmin': 3, 'vmax': 20},
    '50': {'border_radius': 50, 'vmin': 3, 'vmax': 15},
    'inner': {'border_radius': 30, 'vmin': 2.7, 'vmax': 3.3},
}

for test, kwargs in kwargs_set.items():
    f = DATA_FOLDER + '/compare.' + test + '.png'
    if not os.path.isfile(f):
        compare_plot_mpas_regional_meshes(grids,
                                          outfile=f,
                                          suptitle='Meshes comparison',
                                          each_title='<NAME>: '
                                                     '<NCELLS> cells',
                                          lat_ref=lat_ref,
                                          lon_ref=lon_ref,
                                          **kwargs
                                          )

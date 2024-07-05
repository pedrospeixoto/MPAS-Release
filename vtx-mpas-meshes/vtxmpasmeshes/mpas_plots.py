import os

import numpy as np
from shapely.geometry import Polygon
import math

import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.geodesic import Geodesic
from matplotlib.backends.backend_pdf import PdfPages
from geopy.distance import distance

from vtxmpasmeshes.dataset_utilities import open_mpas_regional_file, \
    get_borders_at_distance, mpas_mesh_equivalent_wrf

from vtxmpasmeshes.plot_utilities import plot_latlon_cartopy, \
    plot_mpas_darray, set_plot_kwargs, add_colorbar, \
    start_cartopy_map_axis, close_plot, add_cartopy_details, \
    get_plot_size, get_max_borders


def view_resolution_map(ds, pdfname=None, list_distances=None, **kwargs):
    # ds is a resolution dataset ('distance' and 'resolution' dataset)
    # we plot, for different distances, a

    if list_distances is None:
        list_distances = [1000, 500, 200, 50]

    pdf = None
    if pdfname is not None:
        pdf = PdfPages(pdfname)

    # Region
    # we don't want to plot too much
    region = ds.where(ds['distance'] <= max(list_distances))
    region = region.dropna('lat', how='all').dropna('lon', how='all')

    # Find the center (place at distance zero)
    my_zero = region['distance'].argmin(['lat', 'lon'])
    mylat = int(my_zero['lat'])
    mylon = int(my_zero['lon'])

    # Create a one-dimensional radial array from the center
    axis = region.isel(lat=mylat, lon=range(mylon, region.dims['lon']))
    axis = axis.squeeze(drop=True)
    axis = axis.assign_coords({'distance': axis['distance']})
    axis = axis.swap_dims({'lon': 'distance'})

    # Add several plots to the pdf -> one for each limit distance
    for di in list_distances:
        print('\t .. plotting for distances <= %.0fkm' % di)
        # radial lineplot subplot
        plt.subplot(121)
        axis['resolution'].where(axis['distance'] <= di).plot()
        plt.title('Radial Resolution')

        # map of the area closer than a distance di
        x = region['resolution'].where(region['distance'] <= di)
        x = x.dropna('lat', how='all').dropna('lon', how='all')
        ax = plt.subplot(122, projection=ccrs.PlateCarree())
        add_cartopy_details(ax)
        plot_latlon_cartopy(x, ax=ax, title='Resolution map', **kwargs)

        fig = plt.gcf()
        fig.suptitle('Resolution (km). Distance closer than %.0fkm' % di)
        close_plot(fig, size_fig=[12, 8], pdf=pdf)

    if pdf is not None:
        pdf.close()

    return


def plot_expected_resolution_rings(ds, rings=None, outfile=None, ax=None):

    # if ax=None -> initialize and close the plot
    # if ax not None -> do not initialize nor close
    final = False
    if ax is None:
        final = True
        ax = start_cartopy_map_axis()

    # test that the dataset has the expected attributes
    try:
        lat = ds.attrs['vtx-param-lat_ref']
        lon = ds.attrs['vtx-param-lon_ref']
    except KeyError as e:
        print('The dataset has to be an MPAS mesh created by the '
              'vtx generation flow (attributes vtx-param-)')
        raise e

    # rings of 'expected' limits on the resolution of the mesh
    if rings is None:
        rings = ['size', 'radius', 'border']
    gd = Geodesic()
    for ring in rings:
        rad = ds.attrs['vtx-param-' + ring]
        cp = gd.circle(lon=lon, lat=lat, radius=rad * 1000)
        geom = Polygon(cp)
        ax.add_geometries((geom,), crs=ccrs.PlateCarree(),
                          facecolor='none', edgecolor='black',
                          linewidth=1.5, alpha=0.8)

    # close if needed
    if final:
        close_plot(outfile=outfile)
    return


def plot_era5_grid(ax):
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                      linewidth=1, color='gray', alpha=0.6, linestyle='-')

    gl.top_labels = False
    gl.left_labels = False
    gl.bottom_labels = False
    gl.right_labels = False

    era5_lons = np.arange(-180, 180, 0.25)
    era5_lats = np.arange(-90, 90, 0.25)
    gl.xlocator = mpl.ticker.FixedLocator(era5_lons)
    gl.ylocator = mpl.ticker.FixedLocator(era5_lats)


def plot_wrf_grid(ds, ax=None):
    # test that the dataset has the expected attributes
    try:
        centerlat = ds.attrs['vtx-param-lat_ref']
        centerlon = ds.attrs['vtx-param-lon_ref']
    except KeyError as e:
        print('The dataset has to be an MPAS mesh created by the '
              'vtx generation flow (attributes vtx-param-)')
        raise e

    wrf_details = mpas_mesh_equivalent_wrf(ds)
    num_domains = int(wrf_details['max_domains'])

    colors = ['red', 'green', 'purple', 'orange']
    for domain in range(1, num_domains + 1):

        resol_km = int(wrf_details['d' + str(domain) + 'res'])
        num_cells = int(wrf_details['d' + str(domain) + 'e_wesn']) - 1

        len_grid = distance(kilometers=float(resol_km * num_cells)) / 2

        maxlat = len_grid.destination(point=(centerlat, centerlon),
                                      bearing=0).latitude
        minlat = len_grid.destination(point=(centerlat, centerlon),
                                      bearing=180).latitude
        maxlon = len_grid.destination(point=(centerlat, centerlon),
                                      bearing=90).longitude
        minlon = len_grid.destination(point=(centerlat, centerlon),
                                      bearing=270).longitude

        directions = {'positive': [0, 90], 'negative': [180, 270]}

        for cell in range(math.ceil(num_cells / 2)):

            d = distance(  # cells resolution (max res) times <cell>
                kilometers=float(resol_km * (cell + 1 / 2)))
            for degrees in directions.values():
                vert = d.destination(point=(centerlat, centerlon),
                                     bearing=degrees[0])
                hori = d.destination(point=(centerlat, centerlon),
                                     bearing=degrees[1])

                ax.plot([hori.longitude, hori.longitude], [minlat, maxlat],
                        linewidth=0.8, color=colors[domain - 1])
                ax.plot([minlon, maxlon], [vert.latitude, vert.latitude],
                        linewidth=0.8, color=colors[domain - 1])


def view_mpas_regional_mesh(mpas_grid_file, outfile=None,
                            do_plot_resolution_rings=True,
                            do_plot_era5_grid=False,
                            do_plot_wrf_grid=False,
                            vname='resolution',
                            border_radius=None,
                            **kwargs):

    if vname != 'resolution':
        full = True
    else:
        full = False

    ds = open_mpas_regional_file(mpas_grid_file, full=full)

    units = ds[vname].attrs.get('units', '')
    ncells = str(len(ds[vname].values.flatten()))
    name = os.path.basename(mpas_grid_file)

    # PLOT RESOLUTION

    ax = start_cartopy_map_axis(zorder=2)
    plot_kwargs = set_plot_kwargs(da=ds[vname], **kwargs)

    # --------
    tit = vname + ': ' + name + ' (' + str(ncells) + ')'
    array_plot_kwgs = {**plot_kwargs}
    if 'border_radius' in kwargs:
        if kwargs['border_radius'] is not None:
            array_plot_kwgs['border_radius'] = kwargs['border_radius']

    plot_mpas_darray(ds, vname, ax=ax, title=tit,
                     border_radius=border_radius, **array_plot_kwgs)

    if do_plot_era5_grid:
        plot_era5_grid(ax)
    if do_plot_resolution_rings:
        plot_expected_resolution_rings(ds, ax=ax)
    if do_plot_wrf_grid:
        plot_wrf_grid(ds, ax=ax)
    # --------

    add_colorbar(ax, label=vname + ' (' + units + ')', **plot_kwargs)
    close_plot(outfile=outfile)

    return ds


def compare_plot_mpas_regional_meshes(list_mesh_files, outfile=None,
                                      border_radius=None,
                                      vname='resolution',
                                      do_plot_resolution_rings=True,
                                      do_plot_era5_grid=True,
                                      **kwargs):

    if vname != 'resolution':
        full = True
    else:
        full = False

    names = []
    datasets = []
    for f in list_mesh_files:
        name = os.path.basename(f).replace('.grid.nc', '')
        datasets.append(open_mpas_regional_file(f, full=full))
        names.append(name)

    vars_list = [ds[vname] for ds in datasets]
    plot_kwargs = set_plot_kwargs(list_darrays=vars_list, **kwargs)

    if border_radius is None:
        max_borders = get_max_borders(datasets,
                                      namelat='latitude',
                                      namelon='longitude')
    else:
        # Find the center
        # 1. try the kwargs
        central_lat = kwargs.get('lat_ref', None)
        central_lon = kwargs.get('lon_ref', None)

        for ds in datasets:
            if central_lat is not None and central_lon is not None:
                break
            central_lat = ds.attrs.get('vtx-param-lat_ref', None)
            central_lon = ds.attrs.get('vtx-param-lon_ref', None)
        if central_lon is None or central_lat is None:
            max_borders = get_max_borders(datasets,
                                          namelat='latitude',
                                          namelon='longitude')
        else:
            max_borders = get_borders_at_distance(border_radius,
                                                  centerlat=central_lat,
                                                  centerlon=central_lon,
                                                  )

    nrows, ncols = get_plot_size(len(list_mesh_files))

    fig_size = [5 * ncols, 5 * nrows]
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols+1, figsize=fig_size)
    axs = axs.reshape([nrows, ncols + 1])
    g = mpl.gridspec.GridSpec(nrows=nrows, ncols=ncols+1)

    for m, name in enumerate(names):
        i, j = m // ncols, m % ncols

        each_title = kwargs.get('each_title', '<NAME>')
        ncells = str(datasets[m].dims['nCells'])
        each_title = each_title.replace('<NAME>', name)
        each_title = each_title.replace('<NCELLS>', ncells)

        axs[i, j] = plt.subplot(g[i, j], projection=ccrs.PlateCarree())
        add_cartopy_details(axs[i, j])
        plot_mpas_darray(datasets[m], vname,
                         ax=axs[i, j], **plot_kwargs,
                         title=each_title, borders=max_borders)
        if do_plot_era5_grid:
            plot_era5_grid(axs[i, j])
        if do_plot_resolution_rings:
            plot_expected_resolution_rings(datasets[m], ax=axs[i, j])

    for ax in axs[:, -1]:
        ax.axis('off')

    add_colorbar(axs[:, -1], label=vname + ' (km)', **plot_kwargs)
    suptitle = kwargs.get('suptitle', '')
    if suptitle != '':
        plt.gcf().suptitle(suptitle, fontsize=16)
        plt.subplots_adjust(top=0.9)
    close_plot(outfile=outfile, size_fig=fig_size)


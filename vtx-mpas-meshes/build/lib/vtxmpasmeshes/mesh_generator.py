import os
import time

import xarray as xr
import numpy as np
from scipy.interpolate import interp1d

from mpas_tools.mesh.creation.jigsaw_to_netcdf import jigsaw_to_netcdf
from mpas_tools.mesh.conversion import convert
from mpas_tools.io import write_netcdf

from vtxmpasmeshes.jigsaw_generator import jigsaw_gen_sph_grid
from vtxmpasmeshes.mpas_plots import view_resolution_map, \
    view_mpas_regional_mesh
from vtxmpasmeshes.dataset_utilities import distance_latlon_matrix

PATH_LIMITED_AREA = '/home/marta/PycharmProjects/MPAS-Limited-Area'


def apply_resolution_at_distance(distances, ref_points, ref_resolutions):
    f = interp1d(ref_points, ref_resolutions, bounds_error=False,
                 fill_value='extrapolate')
    resolution = xr.apply_ufunc(f, distances)
    return resolution


def doughnut_variable_resolution(**kwargs):

    # Setting parameters to the defaults if not passed as arguments
    defaults = {'lowresolution': 25,
                'highresolution': 3,
                'size': 40,
                'margin': 100,
                'final_res_dist': 1000}

    for name, default in defaults.items():
        kwag = kwargs.get(name, None)
        if kwag is None:
            kwargs.update({name: default})

    # Inner Circle
    # ------------------------------
    # From distance 0 to <size> -> constant highresolution
    d0, r0 = 0., kwargs['highresolution']
    d1, r1 = kwargs['size'], kwargs['highresolution']

    # 1st Variable Resolution Ring
    # -------------------------------
    # From <size> to <radius> = <size>+<margin> -> linear increase
    # from highresolution to lowresolution
    kwargs['radius'] = kwargs['size'] + kwargs['margin']
    slope = (kwargs['lowresolution'] - kwargs['highresolution']) / kwargs['margin']
    d2, r2 = kwargs['radius'], kwargs['lowresolution']

    # Fixed Low Resolution ring
    # -------------------------------
    # From <radius> until <border>=<radius>+<buffer> -> constant lowresolution
    #  - where the <buffer>=10 * lowresolution
    kwargs['buffer'] = 10 * kwargs['lowresolution']
    kwargs['border'] = kwargs['radius'] + kwargs['buffer']
    d3, r3 = kwargs['border'], kwargs['lowresolution']

    # Crazy increase in cell size ring
    # --------------------------------
    # From <border> to <xmax> -> linear increase with the same <slope>
    # than before until we reach the reoslution <final_res_dist>
    #  - <xmax> can be computed
    deltares = kwargs['final_res_dist'] - kwargs['lowresolution']
    xmax = kwargs['border'] + deltares / slope
    d4, r4 = xmax, kwargs['final_res_dist']
    d5, r5 = 2*xmax, kwargs['final_res_dist']

    # Those are the points I fix
    dists = np.array([d0, d1, d2, d3, d4, d5])
    resol = np.array([r0, r1, r2, r3, r4, r5])

    return dists, resol, kwargs


def variable_resolution_latlonmap(grid, **kwargs):

    print('\n>> Creating a variable resolution map')

    # GRID
    # Create a global lat/lon grid at high resolution

    highresolution = kwargs.get('highresolution', 10.)  # grid size in km
    print('\tResolution in km of lat/lon grid: %.1f' % highresolution)

    dist_degrees = highresolution / 110.

    nlat = int(180. / dist_degrees) + 1
    nlon = int(360. / dist_degrees) + 1

    ds = xr.Dataset(
        coords={
            'lat': np.linspace(-90., 90., nlat),
            'lon': np.linspace(-180., 180., nlon),
        }
    )

    # DISTANCE
    # Compute distance from each point to the reference point

    lat_ref = kwargs.get('lat_ref', None)
    if lat_ref is None:
        lat_ref = 0.
    lon_ref = kwargs.get('lon_ref', None)
    if lon_ref is None:
        lon_ref = 0.
    kwargs.update({'lat_ref': lat_ref, 'lon_ref': lon_ref})

    print('\tComputing the distance to the reference point '
          '(%.2f, %.2f)' % (lat_ref, lon_ref))
    dists = distance_latlon_matrix(ds.coords['lat'], ds.coords['lon'],
                                   lat_ref=lat_ref, lon_ref=lon_ref,
                                   do_tile=True)

    ds['distance'] = xr.DataArray(data=dists, dims=('lat', 'lon'))

    # RESOLUTION
    # Set the resolution value at each point
    print('\tComputing resolutions using technique %s' % grid)

    if grid == 'doughnut':
        dists, resol, kwargs = doughnut_variable_resolution(**kwargs)
        ds['resolution'] = apply_resolution_at_distance(
            ds['distance'], ref_points=dists, ref_resolutions=resol)
    else:
        raise ValueError('!! Grid %s not implemented.' % grid)

    ds.attrs = kwargs

    return ds


def get_mesh_from_resolution(resolution_ds, basename='./mesh'):
    print('\n>> Generating an MPAS mesh')

    # jigsaw
    print('\n\t .- Jigsaw generation')
    mesh_file = jigsaw_gen_sph_grid(resolution_ds['resolution'].values,
                                    resolution_ds['lon'].values,
                                    resolution_ds['lat'].values,
                                    basename=basename)

    # mpas-tools

    print('\n\t .- Jigsaw to netCDF')
    out_file_triangles = basename + '.triangles.nc'
    jigsaw_to_netcdf(msh_filename=mesh_file,
                     output_name=out_file_triangles,
                     on_sphere=True, sphere_radius=1.0)

    print('\n\t .- Convert to MPAS format')
    out_file_mpas = basename + '.grid.nc'
    out_file_graph_info = basename + ".grid.graph.info"
    write_netcdf(
        convert(xr.open_dataset(out_file_triangles),
                dir=os.path.dirname(basename),
                graphInfoFileName=out_file_graph_info),
        out_file_mpas)

    return out_file_mpas, out_file_graph_info


def cut_circular_region(mpas_global_file,
                        region_radius_meters,
                        regional_grid=None,
                        regional_grid_info=None,
                        lat_cen=0., lon_cen=0.,
                        path_create_region=PATH_LIMITED_AREA,
                        ):

    if not os.path.isdir(path_create_region):
        raise IOError('The path to the MPAS-Limited-Area folder is not '
                      'correct. Pass it to the function '
                      'cut_circular_region_beta or define a correct '
                      'default in variable PATH_LIMITED_AREA (in '
                      'mesh_generator.py.')

    print('\n>> Cutting a circular region')
    print('\t centered at %.4f, %.4f' % (lat_cen, lon_cen))
    print('\t with radius %.1fkm' % float(region_radius_meters/1000))

    if region_radius_meters < 5000:
        raise ValueError('Do you want a %.0fm radius region?'
                         'That looks way too small. Maybe you passed '
                         'the radius in km instead as in meters.'
                         % region_radius_meters)

    if not os.path.exists(mpas_global_file):
        raise IOError('Wanted to use the MPAS global file %s but'
                      'it does not seem to exist.' % mpas_global_file)

    os.system('cp ' + mpas_global_file + ' global.grid.nc')

    with open('points.txt', 'w') as f:
        f.write('Name: circle\n')
        f.write('Type: circle\n')
        f.write('Point: %.4f, %.4f\n' % (lat_cen, lon_cen))
        f.write('radius: %.0f\n' % region_radius_meters)

    # If there are regional files we should erase them
    os.system('rm -f circle.grid.nc')
    os.system('rm -f circle.graph.info')

    # Execute create region
    os.system(path_create_region + '/create_region points.txt ' +
              mpas_global_file)

    if not os.path.exists('circle.grid.nc') or \
            not os.path.exists('circle.graph.info'):
        raise AttributeError('The regions were not generated correctly')

    if regional_grid is not None:
        os.system('cp circle.grid.nc ' + regional_grid)

        if regional_grid_info is None:
            regional_grid_info = regional_grid.replace('.nc', '.graph.info')
    else:
        regional_grid = 'circle.grid.nc'

    if regional_grid_info is not None:
        os.system('cp circle.graph.info ' + regional_grid_info)
    else:
        regional_grid_info = 'circle.graph.info'

    return regional_grid, regional_grid_info


def cut_circular_region_beta(mpas_global_file,
                             region_radius_meters,
                             regional_grid=None,
                             regional_grid_info=None,
                             num_boundary_layers=8,
                             lat_cen=0., lon_cen=0.,
                             path_create_region=PATH_LIMITED_AREA,
                             ):

    if not os.path.isdir(path_create_region):
        raise IOError('The path to the MPAS-Limited-Area folder is not '
                      'correct. Pass it to the function '
                      'cut_circular_region_beta or define a correct '
                      'default in variable PATH_LIMITED_AREA (in '
                      'mesh_generator.py.')

    create_region_exec = path_create_region + '/create_region_no_file'
    if not os.path.isfile(create_region_exec):
        raise IOError('Your MPAS-Limited-Area folder does not '
                      'contain the expected executable. Maybe you '
                      'have an old version? ' + create_region_exec)

    print('\n>> Cutting a circular region')
    print('\t centered at %.4f, %.4f' % (lat_cen, lon_cen))
    print('\t with radius %.1fkm' % float(region_radius_meters/1000))

    if region_radius_meters < 5000:
        raise ValueError('Do you want a %.0fm radius region?'
                         'That looks way too small. Maybe you passed '
                         'the radius in km instead as in meters.'
                         % region_radius_meters)

    if not os.path.exists(mpas_global_file):
        raise IOError('Wanted to use the MPAS global file %s but'
                      'it does not seem to exist.' % mpas_global_file)

    # If there are regional files we should erase them
    if regional_grid is None:
        regional_grid = 'circle.grid.nc'
    if regional_grid_info is None:
        regional_grid_info = regional_grid.replace('.nc', '.graph.info')

    os.system('rm -f ' + regional_grid)
    os.system('rm -f ' + regional_grid_info)

    # Execute create region
    os.system(create_region_exec + ' ' + mpas_global_file +
              ' --num_boundary_layers ' + str(num_boundary_layers) +
              ' --oregion ' + regional_grid +
              ' --ograph ' + regional_grid_info +
              ' region.type:circle' +
              ' region.radius:' + str(region_radius_meters) +
              ' region.in_point:' + str(lat_cen) + ',' + str(lon_cen)
              )

    if not os.path.exists(regional_grid) or \
            not os.path.exists(regional_grid_info):
        raise AttributeError('The regions were not generated correctly')

    return regional_grid, regional_grid_info


def full_generation_process(mpas_grid_file, grid, redo=True,
                            do_plots=True, do_region=False, **kwargs):

    if os.path.isfile(mpas_grid_file) and not redo:
        print(' .. already available')
        return

    graph_info_file = mpas_grid_file.replace('.nc', '.graph.info')
    path_save = os.path.dirname(mpas_grid_file)

    os.system('rm -f ' + mpas_grid_file)
    os.system('rm -f ' + graph_info_file)

    start_time = time.time()
    resolution_ds = variable_resolution_latlonmap(grid, **kwargs)
    duration_resolution = time.time() - start_time
    print(' .. finished finding resolution map: %.3fs\n\n' % duration_resolution)

    border = resolution_ds.attrs['border']
    radius = resolution_ds.attrs['radius']
    lat_ref = resolution_ds.attrs['lat_ref']
    lon_ref = resolution_ds.attrs['lon_ref']

    if do_plots:
        print('Plotting')
        start_time = time.time()
        view_resolution_map(resolution_ds,
                            pdfname=path_save + '/resolution.pdf',
                            list_distances=[
                                #1000,
                                500, border, radius])
        duration_plots = time.time() - start_time
        print(' .. finished doing resolution plots: %.3fs\n\n' % duration_plots)

    start_time = time.time()
    tmp_mesh_file, tmp_graph_info = get_mesh_from_resolution(resolution_ds,
                                                             basename='mesh')
    duration_gen = time.time() - start_time
    print(' .. finished generating global mesh: %.3fs\n\n' % duration_gen)

    mpas_grid_file_tmp = mpas_grid_file + '.tmp'
    if do_region:
        start_time = time.time()
        num_boundary_layers = kwargs.get('num_boundary_layers', 8)
        cut_circular_region_beta(tmp_mesh_file, radius*1000,
                                 regional_grid=mpas_grid_file_tmp,
                                 regional_grid_info=graph_info_file,
                                 num_boundary_layers=num_boundary_layers,
                                 lat_cen=lat_ref, lon_cen=lon_ref)
        duration_region = time.time() - start_time
        print(' .. finished cutting region: %.3fs\n\n' % duration_region)

        if not os.path.isfile(mpas_grid_file_tmp) or \
                not os.path.isfile(graph_info_file):
            raise IOError('The file we had to generate was not generated')
    else:
        duration_region = 0.
        os.system('mv ' + tmp_mesh_file + ' ' + mpas_grid_file_tmp)
        os.system('mv ' + tmp_graph_info + ' ' + graph_info_file)

    # Open dataset and update attributes
    mpas_ds = xr.open_dataset(mpas_grid_file_tmp)
    for name, value in resolution_ds.attrs.items():
        mpas_ds.attrs['vtx-param-' + str(name)] = value
    if do_region:
        mpas_ds.attrs['vtx-region-num_boundary_layers'] = num_boundary_layers
        lowres = mpas_ds.attrs['vtx-param-lowresolution']
        region_border = radius + (num_boundary_layers * lowres) * 0.6
        mpas_ds.attrs['vtx-region_border'] = region_border

    # Update the duration of the steps
    durations_process = {
        'resolution': duration_resolution,
        'generation': duration_gen,
        'region': duration_region,
        'total': duration_resolution + duration_gen + duration_region,
    }
    for name, value in durations_process.items():
        mpas_ds.attrs['vtx-duration-' + name] = '%.2f' % value

    print('\n MESH:\n')
    print(mpas_ds)
    mpas_ds.to_netcdf(mpas_grid_file)

    if not os.path.isfile(mpas_grid_file):
        raise IOError('Could not update attributes of file ' +
                      mpas_grid_file_tmp)

    os.system('rm -f ' + mpas_grid_file_tmp)

    if do_plots:
        if do_region:
            print('Resolution Plots')
            view_mpas_regional_mesh(mpas_grid_file,
                                    outfile=path_save + '/resolution_mesh.png')

    return mpas_grid_file, graph_info_file

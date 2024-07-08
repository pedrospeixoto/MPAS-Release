import numpy as np
import xarray as xr
import math
from geopy.distance import distance


derived_variables = {
    'latCell': ['latitude'],
    'lonCell': ['longitude'],
    'latVertex': ['latitudeVertex'],
    'lonVertex': ['longitudeVertex'],
    'areaCell': ['area', 'resolution'],
}


def distance_latlon_matrix(lat, lon, lat_ref=0., lon_ref=0., do_tile=False):
    if do_tile:
        lat = np.tile(lat, (len(lon), 1)).transpose()
        lon = np.tile(lon, (len(lat), 1))

    lon, lat, lon_ref, lat_ref = map(np.radians, [lon, lat, lon_ref, lat_ref])

    newlon = lon_ref - lon
    newlat = lat_ref - lat

    haver_formula = np.sin(newlat / 2.0) ** 2 + np.cos(lat) * \
                    np.cos(lat_ref) * np.sin(newlon / 2.0) ** 2

    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    km = 6367 * dist  # 6367 for distance in KM for miles use 3958
    return km


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
                    #print('need to correct to earth radius!!')
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

    if full:
        ref_point = {}
        for v in ['lat_ref', 'lon_ref']:
            if v in kwargs:
                ref_point[v] = kwargs[v]
        ds = add_distance_to_reference(ds, **ref_point)

        ds = compute_metrics_edge_lengths(ds)
        ds = compute_metrics_triangle_quality(ds)

    return ds


def get_center(lats, lons):
    """
    Given 2 DataArrays of lats, lons, it returns the grid center lat,
    lon.
    :param lats: DataArray of latitudes
    :param lons: DataArray of longitudes
    :return: lat, lon: floats
    """

    lat = float(lats[abs(lats - lats.mean()).argmin()])
    lon = float(lons[abs(lons - lons.mean()).argmin()])

    return lat, lon


def get_distance_to_center(lats, lons,
                           center_lat=None, center_lon=None):
    """
    Using the haversine formula (spherical distance), it returns the
    distance in km of each lat, lon point to the
    central point.
    """
    if center_lat is None or center_lon is None:
        center_lat, center_lon = get_center(lats, lons)

    radius = 6371.  # km
    d_lat = np.radians(lats - center_lat)  # lat distance in radians
    d_lon = np.radians(lons - center_lon)  # lon distance in radians

    a = (np.sin(d_lat / 2.) * np.sin(d_lat / 2.) +
         np.cos(np.radians(center_lat)) * np.cos(np.radians(lats)) *
         np.sin(d_lon / 2.) * np.sin(d_lon / 2.))
    c = 2. * np.arctan2(np.sqrt(a), np.sqrt(1. - a))
    d = radius * c

    return d


def compute_metrics_edge_lengths(ds):
    distances = []

    for i, cell in enumerate(ds['nCells'].values):
        vals = ds['verticesOnCell'].sel(nCells=cell).values

        num_sides = int(ds['nEdgesOnCell'].sel(nCells=cell))
        vals = vals[:num_sides] - 1
        lats = ds['latitudeVertex'].values[vals]
        lons = ds['longitudeVertex'].values[vals]
        lat_ref = lats[-1]
        lon_ref = lons[-1]

        my_cell_dists = []
        for i in range(ds.dims['maxEdges']):
            if i >= num_sides:
                my_cell_dists.append(np.nan)
                continue
            d = distance_latlon_matrix(lats[i], lons[i],
                                       lat_ref=lat_ref,
                                       lon_ref=lon_ref, do_tile=False)

            my_cell_dists.append(d)
            lat_ref, lon_ref = lats[i], lons[i]
        distances.append(my_cell_dists)

    ds['edgesLength'] = xr.DataArray(data=distances,
                                     dims=('nCells', 'maxEdges'))
    ds['edgesLength'].attrs = {
        'name': 'Length of edges',
        'units': 'km',
        'long_name': 'Haversine distance between adjacent vertices of a cell.'
    }

    ds['mean_edgesLength'] = ds['edgesLength'].mean(dim='maxEdges')
    ds['mean_edgesLength'].attrs = {
        'name': 'Mean edge length',
        'units': 'km',
        'long_name': 'Mean edge length of a cell.'
    }

    ds['min_edgesLength'] = ds['edgesLength'].min(dim='maxEdges')
    ds['min_edgesLength'].attrs = {
        'name': 'Minimum edge length',
        'units': 'km',
        'long_name': 'Minimum edge length of a cell.'
    }

    ds['max_edgesLength'] = ds['edgesLength'].max(dim='maxEdges')
    ds['max_edgesLength'].attrs = {
        'name': 'Maximum edge',
        'units': 'km',
        'long_name': 'Maximum edge length of a cell.'
    }

    ds['rmse_edgesLength'] = xr.apply_ufunc(np.sqrt,
                                            (ds['edgesLength'] ** 2).mean(
                                                dim='maxEdges'))
    ds['rmse_edgesLength'].attrs = {
        'name': 'Rmse edge length',
        'units': 'km',
        'long_name': 'Root mean squared edge length.'
    }

    ds['ration_edgesLength'] = ds['min_edgesLength'] / ds['max_edgesLength']
    ds['ration_edgesLength'].attrs = {
        'name': 'Ratio of edge lengths',
        'units': '',
        'long_name': 'Ratio between minimum and maximum edge lengths '
                     'of a cell.'
    }

    ds['cellDistortion'] = xr.apply_ufunc(np.sqrt, (
                (ds['edgesLength'] - ds['rmse_edgesLength']) ** 2).mean(
        dim='maxEdges')) / ds['rmse_edgesLength']
    ds['cellDistortion'].attrs = {
        'name': 'Cell Distortion',
        'units': '',
        'long_name': 'Cell Distortion: Haversine distance between adjacent '
                     'vertices of a cell. '
                     'https://pedrosp.ime.usp.br/papers/PeixotoBarros2013.pdf'
    }
    return ds


def add_distance_to_reference(ds, **kwargs):
    lat_ref = kwargs.get('lat_ref', ds.attrs.get('vtx-param-lat_ref', None))
    lon_ref = kwargs.get('lon_ref', ds.attrs.get('vtx-param-lon_ref', None))

    if lat_ref is None or lon_ref is None:
        print('WARNING Not enough info to add distance to center')
        return ds

    d = get_distance_to_center(ds['latitude'].values, ds['longitude'].values,
                               center_lat=lat_ref, center_lon=lon_ref)

    ds['cellDistance'] = xr.DataArray(data=d, dims=('nCells'))
    ds['cellDistance'].attrs = {
        'name': 'Distance to ref. point',
        'units': 'km',
        'long_name': 'Distance from cell center to reference point'
    }
    return ds


def open_mpas_regional_file(file, **kwargs):
    ds = xr.open_dataset(file)
    ds = add_mpas_mesh_variables(ds, **kwargs)
    return ds


def compute_metrics_triangle_quality(ds):
    distances = []
    circ_radius = []
    area_triangles = []
    for vertex in ds['nVertices']:
        vals = ds['cellsOnVertex'].sel(nVertices=vertex).values

        if 0 in vals:
            distances.append([np.nan, np.nan, np.nan])
            circ_radius.append(np.nan)
            area_triangles.append(np.nan)
            continue

        vals = vals - 1
        lats = ds['latitude'].sel(nCells=vals).values
        lons = ds['longitude'].sel(nCells=vals).values

        lat_ref = lats[-1]
        lon_ref = lons[-1]

        dis = []
        for i in range(3):
            d = distance_latlon_matrix(lats[i], lons[i],
                                       lat_ref=lat_ref,
                                       lon_ref=lon_ref, do_tile=False)
            dis.append(d)
            lat_ref, lon_ref = lats[i], lons[i]

        # abc / np.sqrt( ( a + b + c ) ( b + c − a ) ( c + a − b ) ( a + b − c ) )
        radius_ball = dis[0] * dis[1] * dis[2] / np.sqrt(
            (dis[0] + dis[1] + dis[2]) * (-dis[0] + dis[1] + dis[2]) * (
                        dis[0] - dis[1] + dis[2]) * (dis[0] + dis[1] - dis[2]))
        circ_radius.append(radius_ball)

        # sqrt(p ( p − a ) ( p − b ) ( p − c )) where p is half-perimeter
        p = (dis[0] + dis[1] + dis[2]) / 2
        area = np.sqrt(p * (p - dis[0]) * (p - dis[1]) * (p - dis[2]))
        area_triangles.append(area)

        distances.append(dis)

    ds['tsideLength'] = xr.DataArray(data=distances,
                                     dims=('nVertices', 'vertexDegree'))
    ds['tsideLength'].attrs = {
        'name': 'Length of sides for a triangle',
        'units': 'km',
        'long_name': 'Haversine distance between adjacent vertices of triangles (center '
                     'cells that surround a vertex).'
    }

    ds['mean_tsideLength'] = ds['tsideLength'].mean(dim='vertexDegree')
    ds['edgesLength'].attrs = {
        'name': 'Mean side length',
        'units': 'km',
        'long_name': 'Mean side length of a triangle.'
    }

    ds['min_tsideLength'] = ds['tsideLength'].min(dim='vertexDegree')
    ds['min_tsideLength'].attrs = {
        'name': 'Minimum side length',
        'units': 'km',
        'long_name': 'Minimum side length of a triangle.'
    }

    ds['max_tsideLength'] = ds['tsideLength'].max(dim='vertexDegree')
    ds['max_tsideLength'].attrs = {
        'name': 'Maximum side length',
        'units': 'km',
        'long_name': 'Maximum side length of a triangle.'
    }

    ds['rmse_tsideLength'] = xr.apply_ufunc(np.sqrt,
                                            (ds['tsideLength'] ** 2).mean(
                                                dim='vertexDegree'))
    ds['rmse_tsideLength'].attrs = {
        'name': 'Rmse side length',
        'units': 'km',
        'long_name': 'Root mean squared side length.'
    }

    ds['ratio_tsideLength'] = ds['min_tsideLength'] / ds['max_tsideLength']
    ds['ratio_tsideLength'].attrs = {
        'name': 'Ratio of side lengths',
        'units': 'km',
        'long_name': 'Ratio between minimum and maximum side lengths of a triangle.'
    }

    ds['triangleDistortion'] = xr.apply_ufunc(np.sqrt, (
                (ds['tsideLength'] - ds['rmse_tsideLength']) ** 2).mean(
        dim='vertexDegree')) / ds['rmse_tsideLength']
    ds['triangleDistortion'].attrs = {
        'name': 'Triangle Distortion',
        'units': 'km',
        'long_name': 'Triangle Distortion: computed from the distance between cell centers surrounding a vertex.'
    }

    # Circumscribing circle radius :
    ds['circums_radius'] = xr.DataArray(data=circ_radius, dims=('nVertices'))
    ds['circums_radius'].attrs = {
        'name': 'Radius of the circumscribing circle',
        'units': 'km',
        'long_name': 'Radius of the circumscribing circle of a triangle.'
    }

    # https://gmd.copernicus.org/articles/10/2117/2017/gmd-10-2117-2017.pdf
    # definition 2 (radius-edge ratio)
    ds['radius_edge_ratio'] = ds['circums_radius'] / ds['min_tsideLength']
    ds['circums_radius'].attrs = {
        'name': 'Radius-edge ratio',
        'units': '',
        'long_name': 'The radius-edge ratio is a measure of element shape quality: circums_radius/min_tsideLength'
    }

    # Area triangle:
    # Definition 3 (area–length ratio)
    ds['area_triangle'] = xr.DataArray(data=area_triangles, dims=('nVertices'))
    ds['area_triangle'].attrs = {
        'name': 'Area of a triangle',
        'units': 'km',
        'long_name': 'Area of a triangle (from latlon distances).'
    }

    ds['area_length_ratio'] = 4 * np.sqrt(3) / 3 * ds['area_triangle'] / (
                ds['rmse_tsideLength'] ** 2)
    ds['area_length_ratio'].attrs = {
        'name': 'Area-length ratio',
        'units': 'km',
        'long_name': 'Area-length ratio: 4sqrt(3)/3  area/(rmse_tsideLength)**2'
    }

    return ds


def get_borders_at_distance(distance_km, centerlat=0., centerlon=0.):
    len_grid = distance(kilometers=distance_km)

    maxlat = len_grid.destination(point=(centerlat, centerlon),
                                  bearing=0).latitude
    minlat = len_grid.destination(point=(centerlat, centerlon),
                                  bearing=180).latitude
    maxlon = len_grid.destination(point=(centerlat, centerlon),
                                  bearing=90).longitude
    minlon = len_grid.destination(point=(centerlat, centerlon),
                                  bearing=270).longitude

    return minlon, maxlon, minlat, maxlat


def find_min_number_wrf_cells(distance_km=None, resolution_km=None,
                              previous_domain_cells=0,
                              margin_cells_each_side=9,
                              force_buffer=False):

    if distance_km is not None and resolution_km is not None:
        min_num_cells = int(distance_km / resolution_km)
        # print('   - distance: %f' % distance_km)
        # print('   - resolution_km: %f' % resolution_km)
        # print('   - minimum number: %f' % min_num_cells)
    else:
        min_num_cells = 1

    # num wrf cells has to be odd and multiple of 3.
    # it also has to be >= 27 and > previous domain num cells / 3 + 18

    if previous_domain_cells > 0:
        # print('  - previous_domain_cells: %f' % previous_domain_cells)
        at_least = int(previous_domain_cells / 3 + 2*margin_cells_each_side)
        min_num_cells = max(min_num_cells, at_least)

    if force_buffer:
        smallest_grid = int(2 * margin_cells_each_side)
        min_num_cells = max(min_num_cells, smallest_grid)

    while not min_num_cells % 2 != 0 or not min_num_cells % 3 == 0:
        min_num_cells += 1

    return min_num_cells


def equivalent_wrf_domains(resolutions, diameters,
                           max_domains=2, silent=False):

    if len(resolutions) != len(diameters):
        raise AttributeError('Resolutions and diameters list should '
                             'be same length')

    highresolution = int(resolutions[0])
    if resolutions[-1] is None:
        num_domains = len(resolutions)
        resol_nests = [int(highresolution * 3 ** i) for i in
                       range(max_domains)]
    else:
        lowresolution = int(resolutions[-1])

        # Find resolution outer domain
        options = [int(highresolution * 3 ** i) for i in range(max_domains)]
        # find the option closest to lowresolution
        dists = [abs(lowresolution - option) for option in options]
        mindist = np.argmin(dists)
        resol_nests = options[:(mindist + 1)]
        num_domains = len(resol_nests)

    domains_def = {
        'max_domains': str(num_domains),
    }

    num_cells = {}
    for nest in range(num_domains):
        # nest = 0 is the highest resolution / smaller domain
        # but nest = 0 means highest domain = num_domains
        # The outer nest is domain = 1 and nest = num_domains - 1
        domain = num_domains - nest

        # Resolution
        domains_def['d' + str(domain) + 'res'] = str(resol_nests[nest])

        # Number of cells
        if nest == 0:
            prev_num_cells = 0
        else:
            prev_num_cells = num_cells[nest - 1]

        diameter = diameters[nest]
        if diameter is None:
            wrf_cells = find_min_number_wrf_cells(
                previous_domain_cells=prev_num_cells,
                margin_cells_each_side=9)
        else:
            wrf_cells = find_min_number_wrf_cells(
                distance_km=diameter, resolution_km=resol_nests[nest],
                previous_domain_cells=prev_num_cells)
        num_cells[nest] = wrf_cells

        domains_def['d' + str(domain) + 'e_wesn'] = \
            str(wrf_cells + 1)

        if not silent:
            print('\nNested n', nest, ' / Domain d', domain)
            print('\tResolution:', resol_nests[nest], 'km')
            print('\t' + str(wrf_cells) + 'x' + str(wrf_cells),
                  'WRF cells of', resol_nests[nest], 'km resolution.')

    for domain in range(1, num_domains + 1):
        nest = num_domains - domain

        if domain == 1:
            if not silent:
                print('Lowest Resolution domain')
            dij = 1
        else:
            if not silent:
                print('Inner domain')
            # quantes celes del domini superior (domain-1) ocupa?
            upper_cells_total = num_cells[nest + 1] - 1
            upper_cells_covered = (num_cells[nest] - 1) / 3
            dij = int(((upper_cells_total - upper_cells_covered) / 2) + 1)

        # Starting ij
        domains_def['d' + str(domain) + 'dij'] = str(dij)

    return domains_def


def mpas_mesh_equivalent_wrf(ds, **kwargs):
    highresolution = kwargs.get('highresolution',
                                ds.attrs.get('vtx-param-highresolution',
                                             None))
    size = kwargs.get('size', ds.attrs.get('vtx-param-size', None))
    lowresolution = kwargs.get('lowresolution',
                                ds.attrs.get('vtx-param-lowresolution',
                                             None))
    regborder = kwargs.get('region_border', ds.attrs.get('vtx-region_border',
                                                         None))

    if size is not None:
        innerdiam = 2.*size
    else:
        innerdiam = None

    if regborder is not None:
        outerdiam = 2.*regborder
    else:
        outerdiam = None

    if highresolution >= 3.:
        ewrf = equivalent_wrf_domains([highresolution, lowresolution],
                                      [innerdiam, outerdiam], silent=True)
    else:
        ewrf = equivalent_wrf_domains([highresolution, None, None],
                                      [innerdiam, None, outerdiam],
                                      max_domains=3,
                                      silent=True)

    return ewrf


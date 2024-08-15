#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to plot sclar fields on native MPAS grids

Originally From: ??
Edited: Danilo  <danilo.oceano@gmail.com>  in 2023
Last edited: Nov 2023 by P. Peixoto (ppeixoto@usp.br)
Last edited: Nov 2023 by F.A.V.B. Alves (fbalves@usp.br)
Last edited: Aug 2024 by P. Peixoto (ppeixoto@usp.br)

"""

import math
import os

import xarray as xr
import numpy as np

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.collections as mplcollections
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.cm as cm
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from geopy.distance import distance

import argparse

import pickle as pkle

import matplotlib.collections as mplcollections
import matplotlib.patches as patches
import matplotlib.path as path
import matplotlib.cm as cm
import cartopy.crs as ccrs
from netCDF4 import Dataset

from tqdm import tqdm

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


def open_mpas_file(file, **kwargs):

    ds = xr.open_dataset(file)

    ds = add_mpas_mesh_variables(ds, **kwargs)

    return ds

def start_cartopy_map_axis(zorder=1, proj='lonlat'):

    if proj=='lonlat':
        plot_crs = ccrs.PlateCarree()
    elif proj=='mollweide':
        plot_crs = ccrs.Mollweide()
    elif proj=='orthographic':
        plot_crs = ccrs.Orthographic(central_longitude=-50.0, central_latitude=0.0, globe=None)
    else:
        plot_crs = ccrs.Robinson()
    
    fig = plt.figure(figsize=(8, 8), constrained_layout=True,facecolor='black')
    ax = fig.add_subplot(projection=plot_crs, frameon=False)
    ax.set_facecolor("black")

    #ax = plt.axes(projection=plot_crs)  # projection type
    
    add_cartopy_details(ax, zorder=zorder)

    return ax

def add_cartopy_details(ax, zorder=1):

    #Country boarders
    #ax.add_feature(cfeature.BORDERS, linestyle=':', zorder=zorder, linewidth=0.1)

    #Coastlines
    #ax.coastlines(resolution='10m', zorder=zorder+1, linewidth=0.1)

    #img = plt.imread("BlueMarble_2005_SAm_09_4096.png")
    img = plt.imread("0000.jpg")
    ax.imshow(img, transform=ccrs.PlateCarree())
    
    # Reference gridlines
    #gl = ax.gridlines(draw_labels=True, alpha=0.5, linestyle='--',
    #                  zorder=zorder+2, linewidth=0.5)
    #gl.top_labels = False
    #gl.right_labels = False
    
def set_plot_kwargs(da=None, clip=False, list_darrays=None, **kwargs):
    plot_kwargs = {k: v for k, v in kwargs.items()
                   if k in ['cmap', 'vmin', 'vmax']
                   and v is not None}
    
    if 'cmap' not in plot_kwargs:
        plot_kwargs['cmap'] = 'Spectral'

    vmin = plot_kwargs.get('vmin', None)
    if vmin is None:
        if da is not None:
            vmin,_ = get_vim_vmax(da,clip)   
            #vmin = np.min(da)
        elif list_darrays is not None:
            vmin = np.min([v.min() for v in list_darrays if v is not None])

    if vmin is not None:
        plot_kwargs['vmin'] = vmin

    vmax = plot_kwargs.get('vmax', None)
    if vmax is None:
        if da is not None:
            _,vmax = get_vim_vmax(da,clip)   
            #vmax = np.max(da)
        elif list_darrays is not None:
            vmax = np.max([v.max() for v in list_darrays if v is not None])

    if vmax is not None:
        plot_kwargs['vmax'] = vmax

    return plot_kwargs

def get_vim_vmax(da,clip=False):
    #Returns good vmin and vmax values to plot da field

    truemaxval = da.max().values
    trueminval = da.min().values

    # Use same range for negative and positive values (zero will always have the same color)
    if (trueminval <= 0) and (truemaxval > 0):
        if truemaxval > abs(trueminval):
            slice = da.values[ da.values > 0]
        else:
            slice = -da.values[ da.values <= 0]
        sigma = np.std(slice)
        m = np.mean(slice)
        if clip:
            maxval = min(truemaxval,m+4*sigma)
        else:
            maxval = truemaxval
        minval = -maxval
 
    # Clip values at mean + 4*std so we still get good color resolution if the solution has a small number of very large numbers
    elif (truemaxval >= 0):
        minval = trueminval
        sigma = np.std(da.values)
        m = np.mean(da.values)
        if clip:
            maxval = min(truemaxval,m+4*sigma)
        else:
            maxval = truemaxval
    else:
        maxval = truemaxval
        sigma = np.std(da.values)
        m = np.mean(da.values)
        if clip:
            minval = max(trueminval,m-4*sigma)
        else:
            minval = trueminval

    return minval, maxval

def get_mpas_patches(mesh, type="cell", msh_file="grid.nc", pickleFile=None):

    nCells = len(mesh.dimensions['nCells'])
    nVertices = len(mesh.dimensions['nVertices'])
    nEdgesOnCell = mesh.variables['nEdgesOnCell']
    verticesOnCell = mesh.variables['verticesOnCell']
    cellsOnVertex = mesh.variables['cellsOnVertex']

    base_name = os.path.splitext(msh_file)[0]

    if (type=="triangle" or type=="dual"):
        patches_filename = base_name + '.tri.pat'
        nPat = nVertices
    else:
        patches_filename = base_name + '.cell.pat'
        nPat = nCells

    if pickleFile:
        pickle_fname = pickleFile
    else:
        pickle_fname = patches_filename

    mesh_patches = [None] * nPat

    print("Patches file:", pickle_fname)

    if(os.path.isfile(pickle_fname)):
        pickled_patches = open(pickle_fname,'rb')
        patch_collection = pkle.load(pickled_patches)
        pickled_patches.close()
        print("Pickle file (", pickle_fname, ") loaded succesfully")
        return patch_collection

    print("\nCreating patches...")
    print("If this is a large mesh, then this proccess will take a while...")

    for i in tqdm(range(nPat)):
        # For each cell/triangle, get the latitude and longitude points of its vertices
        # and make a patch of that point vertices

        if (type=="triangle" or type=="dual"):
            vertices = cellsOnVertex[i,:]
            vertices = np.append(vertices, vertices[0:1]) #Close the loop
            vertices -= 1 # The indexing needs to start in zero, not 1. (??)
            vert_lats = mesh.variables['latCell'][vertices]* (180 / np.pi)
            vert_lons = mesh.variables['lonCell'][vertices]* (180 / np.pi)
        else:
            vertices = verticesOnCell[i,:nEdgesOnCell[i]]
            vertices = np.append(vertices, vertices[0:1]) #Close the loop
            vertices -= 1 # The indexing needs to start in zero, not 1.
            vert_lats = mesh.variables['latVertex'][vertices]* (180 / np.pi)
            vert_lons = mesh.variables['lonVertex'][vertices]* (180 / np.pi)

        # Normalize longitude
        diff = np.copy(vert_lons)
        vert_lons[diff > 180.0] = vert_lons[diff > 180.] - 360.
        vert_lons[diff < -180.0] = vert_lons[diff < -180.] + 360.

        coords = np.vstack((vert_lons, vert_lats))

        cell_path = np.ones(vertices.shape) * path.Path.LINETO
        cell_path[0] = path.Path.MOVETO
        cell_path[-1] = path.Path.CLOSEPOLY
        cell_patch = path.Path(coords.T,
                            codes=cell_path,
                            closed=True,
                            readonly=True)

        mesh_patches[i] = patches.PathPatch(cell_patch)

    print("\n")

    # Create patch collection
    patch_collection = mplcollections.PatchCollection(mesh_patches, transform=ccrs.Geodetic())

    # Pickle the patch collection
    pickle_file = open(pickle_fname, 'wb')
    pkle.dump(patch_collection, pickle_file)
    pickle_file.close()

    print("\nCreated a patch file for mesh: ", pickle_file)
    return patch_collection

def plot_scalar_mpas(mesh, da, ds, ax, plotEdge=True, file='grid.nc', **plot_kwargs):
    # da: specific xarray to be plotted (time/level filtered)
    # ds: general xarray with grid structure, require for grid propreties
    # plotEdge: wether the cell edge should be visible or not. For high-resolution grids figure looks better if plotEdge=False

    if 'nCells' in da.dims: #Plot on Voronoi cells
        cell_type = "cell"

    elif 'nVertices' in da.dims: #Plot on Triangles
        cell_type = "dual"

    patch_collection = get_mpas_patches(mesh, type=cell_type, msh_file=file, pickleFile=None)

    cm = mpl.colormaps['Spectral']

    print("Creating colormap for variable")
    norm_val = mpl.colors.Normalize(vmin=plot_kwargs['vmin'], vmax=plot_kwargs['vmax'], clip=True)(da.values)
    colors = cm(norm_val)

    if plotEdge:
        edgecolor = 'lightgray'
        lw = 0.5
    else:
        edgecolor = None   
        lw = None

    patch_collection.set_linewidths(lw)
    patch_collection.set_linestyle("-")
    patch_collection.set_edgecolors(edgecolor)
    #patch_collection.set_facecolors(colors)
    patch_collection.set_facecolors("None")
    patch_collection.set_snap(None)

    # Now apply the patch_collection to our axis (ie plot it)
    print("Plotting variable")
    ax.add_collection(patch_collection)
    
    return

def add_colorbar(axs, fig=None, label=None, **plot_kwargs):
    if fig is None:
        fig = plt.gcf()

    try:
        x = axs[0, 0]
    except:
        try:
            x = axs[0]
            n = len(axs)
        except:
            axs = np.array([axs]).reshape([1, 1])
        else:
            axs = axs.reshape([n, 1])

    cbar = fig.colorbar(
        mpl.cm.ScalarMappable(
            norm=mpl.colors.Normalize(vmin=plot_kwargs['vmin'],
                                      vmax=plot_kwargs['vmax'], clip=True),
            cmap=plot_kwargs['cmap']),
        ax=axs[:, :], shrink=0.6)
    cbar.ax.locator_params(nbins=10)
    if label is not None:
        cbar.set_label(label)

    return

def close_plot(fig=None, size_fig=None, pdf=None, outfile=None,
               force_show=False):

    if size_fig is None:
        size_fig = [8, 8]

    if fig is None:
        fig = plt.gcf()
    fig.set_size_inches(size_fig)
    

    if outfile is not None:
        plt.savefig(outfile, dpi=800, transparent=True) 

    if pdf is not None:
        pdf.savefig(fig, dpi=800)

    if (outfile is None and pdf is None) or force_show:
        plt.show()

    plt.close()


def plot_mpas_darray(mesh, ds, vname, time=None, level=None, ax=None, outfile=None, title=None, plotEdge=True, clip=False, **kwargs):
    
    ## plot_mpas_darray
    da = ds[vname]
    
    if 'Time' in da.dims:
        print()    
        if time not in da['Time'].values:
            print("Proposed time slice not available:", time," Timesteps:", da['Time'].values)
            print("  Setting time slice to zero.")
            time = 0
        else:
            print('Selecting time slice '+ str(time) + '.')

        da = da.isel({'Time': time})      

    
    if 'nVertLevels' in da.dims:
        print()    
        if level not in da['nVertLevels'].values:
            print("Proposed vertical level slice not available.", level," Levels:", da['nVertLevels'].values)
            print("  Setting level to zero.")
            level = 0
        else:
            print('Selecting vertical level '+ str(time) + '.')

        da = da.isel({'nVertLevels': level})      
    print("\n Data to be plotted")    
    print(da)
    print()

    #ax.set_extent([-180.0, 180,-90.0, 90.0], crs=ccrs.PlateCarree())
    
    plot_kwargs = set_plot_kwargs(da=da, clip=clip, **kwargs)
    
    if 'nCells' in da.dims or 'nVertices' in da.dims: #Plot on Voronoi or dual cells
        plot_scalar_mpas(mesh, da, ds, ax, plotEdge, **plot_kwargs)
    else: # TO DO: Implement ploting edge quantities
        print('WARNING  Impossible to plot!')

    if title == None:
        title = vname

    ax.set_global()
    
    #ax.set_title(title)
    
    #add_colorbar(ax, label=vname + ' (' + da.attrs.get('units', '') + ')', **plot_kwargs)

    return 

def view_mpas_mesh(mpas_grid_file, outfile=None,
                            vname='resolution',
                            time=None,
                            level=None,
                            plotEdge=True,
                            clip=False,
                            proj='lonlat',
                            **kwargs):
    mesh = Dataset(os.path.join(mpas_grid_file), 'r') 
    ds = open_mpas_file(mpas_grid_file)

    if vname not in ds.data_vars:
        print('Unplottable Data Array ' + vname)
        print('Available variables:', list(ds.keys()))
        return

    units = ds[vname].attrs.get('units', '')
    ncells = str(len(ds[vname].values.flatten()))
    name = os.path.basename(mpas_grid_file)
    print(vname, units, ncells, name, ds[vname])

    ax = start_cartopy_map_axis(zorder=2,proj=proj)

    tit = vname + ': ' + name + ' (' + str(ncells) + ')'
    if time is not None:
        tit = tit + " Timestep="+str(time)
    if level is not None:
        tit = tit + " Level="+str(level)
                
    plot_mpas_darray(mesh, ds, vname, time=time, level=level, ax=ax, title=tit, plotEdge=plotEdge,clip=clip)
    
    close_plot(outfile=outfile)
        
    
if __name__ == "__main__":
    
    derived_variables = {
        'latCell': ['latitude'],
        'lonCell': ['longitude'],
        'latVertex': ['latitudeVertex'],
        'lonVertex': ['longitudeVertex'],
        'areaCell': ['area', 'resolution'],
    }
    
    parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument(
        "-f", "--infile", type=str, required=True,
        help="Name of an MPAS grid or data file (.nc)",
    )
    
    parser.add_argument(
        "-o", "--outfile", type=str, default=None,
        help="File to save the MPAS plot",
    )
    parser.add_argument(
        "-v", "--var", type=str, default='resolution',
        help="Variable to be plotted",
    )

    parser.add_argument(
        "-l", "--level", type=int, default=None,
        help="Vertical level",
    )

    parser.add_argument(
        "-t", "--time", type=int, default=None,
        help="Time step",
    )

    parser.add_argument(
        "-g", "--grid", type=str, default='yes',
        help="Draw grid edges: yes or no",
    )

    parser.add_argument(
        "-c", "--clip", type=str, default='no',
        help="Clip values grater than (expected_val + 4*std): yes or no",
    )

    parser.add_argument(
        "-p", "--projection", type=str, default='lonlat',
        help="Globe projection to use: 'lonlat', 'robinson' or 'mollweide'",
    )

    args = parser.parse_args()

    if not os.path.exists(args.infile):
        raise IOError('File does not exist: ' + args.infile)

    if args.grid in ['no', 'No', 'N', 'n']:
        plotEdge=False
    else:
        plotEdge=True

    if args.clip in ['yes', 'Yes', 'Y', 'y']:
        clip=True
    else:
        clip=False

    if args.projection in ['robinson', 'rob', 'Robinson', 'Rob']:
        proj='robinson'
    elif args.projection in ['moll', 'Moll', 'mollweide', 'Mollweide', 'mol', 'Mol']:
        proj='mollweide'
    elif args.projection in ['Orthographic', 'Ortho', 'ortho', 'orthographic']:
        proj='orthographic'
    else:
        proj='lonlat'

    view_mpas_mesh(args.infile, outfile=args.outfile, time=args.time, level=args.level, vname=args.var, plotEdge=plotEdge,clip=clip,proj=proj)
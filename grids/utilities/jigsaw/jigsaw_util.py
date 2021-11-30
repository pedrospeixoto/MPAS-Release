#!/usr/bin/env python
#
#  Basic script to creat spherical grids for MPAS-Atmosphere
#  by Pedro S. Peixoto Dec 2021 <ppeixoto@usp.br>
#
#  Based on 
#  http://mpas-dev.github.io/MPAS-Tools/stable/mesh_creation.html#spherical-meshes
#  and Jigsaw scripts: https://github.com/dengwirda/jigsaw-python/tree/master/tests
#  
# Pre-requisites:
# 0) Install the conda enviroment MPAS-Tools
# 1) Get the requirements https://github.com/pedrospeixoto/MPAS-Tools/blob/master/conda_package/dev-spec.txt
# 2) Create enviroment
#     $ conda config --add channels conda-forge
#     $ conda create --name mpas-tools --file dev-spec.txt 
# 3) Install the mpas-tools pack
#     $ conda install mpas_tools
# 4) Use it with $ conda activate mpas-tools
# 5) If necessary, install jigsawpy https://github.com/dengwirda/jigsaw-geo-python/
 
import numpy as np
import argparse
import os
import numpy as np
import subprocess

#from mpas_tools.ocean import build_spherical_mesh
from scipy import interpolate

import jigsawpy as jig



def jigsaw_gen_sph_grid(cellWidth, x, y, earth_radius=6371.0e3,
    basename="mesh", ):

    """
    A function for building a jigsaw spherical mesh
    Parameters
    ----------
    cellWidth : ndarray
        The size of each cell in the resulting mesh as a function of space
    x, y : ndarray
        The x and y coordinates of each point in the cellWidth array (lon and
        lat for spherical mesh)
    on_sphere : logical, optional
        Whether this mesh is spherical or planar
    earth_radius : float, optional
        Earth radius in meters
    """
    # Authors
    # -------
    #by P. Peixoto in Dec 2021
    # based on MPAS-Tools file from Mark Petersen, Phillip Wolfram, Xylar Asay-Davis 

    
    # setup files for JIGSAW
    opts = jig.jigsaw_jig_t()
    opts.geom_file = basename+'.msh'
    opts.jcfg_file = basename+'.jig'
    opts.mesh_file = basename+'-MESH.msh'
    opts.hfun_file = basename+'-HFUN.msh'
    on_sphere=True

    # save HFUN data to file
    hmat = jig.jigsaw_msh_t()
    
    hmat.mshID = 'ELLIPSOID-GRID'
    hmat.xgrid = np.radians(x)
    hmat.ygrid = np.radians(y)
    hmat.value = cellWidth
    jig.savemsh(opts.hfun_file, hmat)

    # define JIGSAW geometry
    geom = jig.jigsaw_msh_t()
    geom.mshID = 'ELLIPSOID-MESH'
    geom.radii = earth_radius*1e-3*np.ones(3, float)
    jig.savemsh(opts.geom_file, geom)

    # build mesh via JIGSAW!
    opts.hfun_scal = 'absolute'
    opts.hfun_hmax = float("inf")
    opts.hfun_hmin = 0.0
    opts.mesh_dims = +2  # 2-dim. simplexes
    opts.optm_qlim = 0.9375
    opts.verbosity = +1
    jig.savejig(opts.jcfg_file, opts)
    
    #Call jigsaw
    process = subprocess.call(['jigsaw', opts.jcfg_file])


    

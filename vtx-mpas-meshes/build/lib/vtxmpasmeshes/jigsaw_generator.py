#  Marta Gil Bardaji, Vortex, marta.gil@vortexfdc.com
#  May 2022

#  Simplification of the script
#  https://github.com/pedrospeixoto/MPAS-PXT/blob/master/grids/utilities/jigsaw/jigsaw_util.py
#  by Pedro S. Peixoto Dec 2021 <ppeixoto@usp.br>
#
#  which is itself based on
#  http://mpas-dev.github.io/MPAS-Tools/stable/mesh_creation.html#spherical-meshes
#  and Jigsaw scripts:
#  https://github.com/dengwirda/jigsaw-python/tree/master/tests


import numpy as np
import jigsawpy as jig
import subprocess


def jigsaw_gen_sph_grid(cellWidth, x, y, earth_radius=6371.0e3,
                        basename="mesh"):
    """
    A function for building a jigsaw spherical mesh

    Parameters
    ----------
    cellWidth : ndarray
        The size of each cell in the resulting mesh as a function of space
    x, y : ndarray
        The x and y coordinates of each point in the cellWidth array
        (lon and lat for spherical mesh)
    earth_radius : float, optional
        Earth radius in meters
    basename : str
        folder + '/' + name of the different files the function saves

    """
    # Authors
    # -------
    # by P. Peixoto in Dec 2021
    # based on MPAS-Tools from Mark Petersen, Phillip Wolfram, Xylar Asay-Davis

    # setup files for JIGSAW
    opts = jig.jigsaw_jig_t()
    opts.geom_file = basename + '.msh'
    opts.jcfg_file = basename + '.jig'
    opts.mesh_file = basename + '-MESH.msh'
    opts.hfun_file = basename + '-HFUN.msh'

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
    geom.radii = earth_radius * 1e-3 * np.ones(3, float)
    jig.savemsh(opts.geom_file, geom)

    # build mesh via JIGSAW!
    opts.hfun_scal = 'absolute'
    opts.hfun_hmax = float("inf")
    opts.hfun_hmin = 0.0
    opts.mesh_dims = +2  # 2-dim. simplexes
    # MARTA CHANGES
    opts.mesh_iter = 500000
        # %   OPTS.MESH_ITER - {default=+INF} max. number of mesh ref-
        # %       inement iterations. Set ITER=N to see progress after
        # %       N iterations.
    opts.optm_qlim = 0.9375
        # %   OPTS.OPTM_QLIM - {default=0.9375} threshold on mesh cost
        # %       function above which gradient-based optimisation is
        # %       attempted.
    opts.optm_qtol = 1.0e-7
        # %   OPTS.OPTM_QTOL - {default=1.E-04} tolerance on mesh cost
        # %       function for convergence. Iteration on a given node
        # %       is terminated if adjacent element cost-functions are
        # %       improved by less than QTOL.

    opts.optm_iter = 5000
        # %   OPTS.OPTM_ITER - {default=16} max. number of mesh optim-
        # %       isation iterations. Set ITER=N to see progress after
        # %       N iterations.

    # new opts
    # %   OPTS.MESH_OFF2 - {default=0.90} radius-edge ratio target
    # %       for insertion of "shape"-type offcentres for 2-tria
    # %       elements. When refining an element II, offcentres
    # %       are positioned to form a new "frontal" element JJ
    # %       that satisfies JRAD <= OFF2.
    opts.mesh_off2 = 0.97

    # -----------------
    opts.verbosity = +1
    jig.savejig(opts.jcfg_file, opts)

    # Call jigsaw
    subprocess.call(['jigsaw', opts.jcfg_file])

    return opts.mesh_file

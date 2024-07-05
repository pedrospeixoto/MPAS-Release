# vtx-mpas-meshes
Creation and analysis of MPAS-WRF meshes by Vortex


Work under progress.
Example of regional mesh:
![example_mesh.png](example_mesh.png)

Created by Marta Gil Bardají. 
Contact email: marta.gil@vortexfdc.com

## Installation Guide

To obtain a local copy of the code, clone this github repository [meshes]. Note that you need permission to do so.

    $ git clone git@github.com:marta-gil/vtx-mpas-meshes.git

The necessary conda environment can be created using the ``environment.yml`` file present in the **vtx-mpas-meshes** repository cloned from github:

    $ conda env create -n <envname> -f <path-to-environment.yml-file>

The conda environment contains:
* mpas-tools & jigsaw for mesh creation
* xarray, geopy, cartopy for mesh visualization
* packages for documentation
* jupyter notebook

The environment should be activated to run the scripts in this repository.

    $ conda activate <envname>

Then you can install the scripts of this repository by installing the `vtxmpasmeshes` source files using the `setup.py` file.

    (<envname>) $ pyhton setup.py install

To be able to run the Jupyter Notebooks, add the environment to ipykernel:

    (<envname>) $ python -m ipykernel install --user --name=<envname>

and a successful message similar to this should appear:

    Installed kernelspec <envname> in /home/<username>/.local/share/jupyter/kernels/<envname>

[meshes]: https://github.com/marta-gil/vtx-mpas-meshes.git

## Mesh generation

Creates global and regional MPAS meshes based on global latlon resolution maps. The focus is on symmetric resolutions that are highest at a certain area of the planet and decrease radially.

![example_resolution.png](example_resolution.png)

Based on https://github.com/pedrospeixoto/MPAS-PXT/blob/master/grids/utilities/jigsaw/spherical_grid.py by Pedro S. Peixoto  ppeixoto@usp.br.

It uses:
* MPAS-Tools http://mpas-dev.github.io/MPAS-Tools/stable/mesh_creation.html#spherical-meshes
* jigsaw: https://github.com/dengwirda/jigsaw-python/tree/master/tests








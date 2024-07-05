import os
import pandas as pd
from vtxmpasmeshes.mesh_generator import full_generation_process_gtm
import argparse

# Create ArgumentParser object
parser = argparse.ArgumentParser(description=
                                 'Sensitivity test for varying mesh parameters.')
# Input arguments
parser.add_argument('--mpas_br_dir', type=str, help='directory containing MPAS-BR/')
parser.add_argument('--meshes_dir', type=str, help='directory for saving meshes')
parser.add_argument('--limited_area_dir', type=str, help='directory of MPAS-Limited-Area')
parser.add_argument('--N', type=str, default='2', help='number of partitions')
parser.add_argument('--lon', type=float, help='longitude for mesh center')
parser.add_argument('--lat', type=float, help='latitude for mesh center')
parser.add_argument('--inner_radius', type=float, help='inner radius (s)')
parser.add_argument('--outer_radius', type=float, help='outer radius (s+m)')
parser.add_argument('--n_layers', type=int, default=8, help='number of external layers')
parser.add_argument('--high_res', type=float, help='minimum grid-distance')
parser.add_argument('--low_res', type=float, help='maximum grid-distance')
parser.add_argument('--do_regional', type=str, default='y', 
                    help='flag for building regional (y) or global (n) mesh')
parser.add_argument('--grid_type', type=str, default='doughnut', 
                    help='type of grid to be constructed')


# Parse the command line arguments
args = parser.parse_args()

# Set relevant directories
DATA_DIR = args.mpas_br_dir+'/vtx-mpas-meshes/data'
PATH_LIMITED_AREA = args.limited_area_dir

# Lon,lat of mesh center
lon_ref = args.lon
lat_ref = args.lat

# Parameters
# These parameters define the changing in the resolution. Varying the distance
# from the center of mesh d, we define the expected grid spacing S as follows (see Bardaji, 2022):
## 0 < d < size --> S = highres
## size < d < size + margin --> S = highres + lambda*(d-size)
## size + margin < d < alpha (not defined here) --> S = lowres
## alpha < d < beta (not defined here) --> S = lowres + lambda*(d-(size+margin))
size = args.inner_radius # s in the paper
highres = args.high_res # cgs in the paper
margin = args.outer_radius - args.inner_radius # m in the paper
lowres = args.low_res # mgs in the paper
numlayers = args.n_layers # layers outside requested nominal radius
grid_type = args.grid_type # type of grid to be constructed

# Set main filename
name = (f"lat_{round(lat_ref)}_lon_{round(lon_ref)}_oradius_{round(args.outer_radius)}_iradius_{round(size)}"+
        f"_margin_{round(margin)}_hres_{round(highres)}_lres_{round(lowres)}") # 's' + str(size).zfill(2) + '_m' + str(margin).zfill(3)
radius = size+margin
region_border = radius + (numlayers*lowres)#*0.9

# Set specific filenames
regional_mesh = DATA_DIR + '/' + name + '.region.grid.nc'
regional_mesh_info = DATA_DIR + '/' + name + '.region.grid.graph.info'
regional_mesh_plots = DATA_DIR + '/resolution*'

# Run main script
if not os.path.exists(regional_mesh):
    # Create a regional mesh at the desired location -> with 4 layers (?)
    print ('creating regional mesh centered at chosen location')
    full_generation_process_gtm(
        regional_mesh, grid_type,
        redo=False, do_plots=True, do_region=args.do_regional,
        highresolution=highres, lowresolution=lowres,
        num_boundary_layers=numlayers,
        size=size, margin=margin,
        lat_ref=lat_ref, lon_ref=lon_ref,
        path_limited_area=PATH_LIMITED_AREA
    )
else:
    print("Mesh already exists -- nothing to be done.")

# Save final output files
OUTPUT_DIR = args.meshes_dir + f'/{name}.region'
if not os.path.exists(OUTPUT_DIR):
    os.system(f'mkdir {OUTPUT_DIR}')
os.system(f'mv {regional_mesh} {regional_mesh_info} {regional_mesh_plots} {OUTPUT_DIR}')

# Create block decomposition file
print ('N:',args.N)
os.system(f'gpmetis -minconn -contig -niter=200 {OUTPUT_DIR}/{name}.region.grid.graph.info {args.N}')

# Remove temporary output files
os.system(f'rm {DATA_DIR}/*.nc')
os.system(f'rm -r {args.meshes_dir}/mesh* {args.meshes_dir}/tmp* points.txt')
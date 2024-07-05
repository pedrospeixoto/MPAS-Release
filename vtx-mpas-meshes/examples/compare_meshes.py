import argparse
import os

from vtxmpasmeshes.mpas_plots import compare_plot_mpas_regional_meshes

parser = argparse.ArgumentParser(
    description=__doc__,
    formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument('-gs', '--grids', default=[],
                    help='names of the grids',
                    type=lambda s: [item for item in s.split(',')]
                    )

parser.add_argument(
    "-b", "--border", default=None, type=float,
    help="Plot the area of this radius around the central point (km).",
)

parser.add_argument(
    "-vmin", "--vmin", default=None, type=float,
    help="Minimum resolution color (km).",
)

parser.add_argument(
    "-vmax", "--vmax", default=None, type=float,
    help="Maximum resolution color (km).",
)

parser.add_argument(
    "-cmap", "--cmap", default=None, type=str,
    help="Color palette.",
)

parser.add_argument(
    "-o", "--outfile", type=str, default=None,
    help="File to save the MPAS plots",
)

# -e do draw era5 grid
parser.add_argument(
    "-e", "--era5", action="store_true",
    help="overlay era5 grid.",
)

args = parser.parse_args()

DATA_FOLDER = '/home/marta/PycharmProjects/vtx-mpas-meshes/data'

grids = []
for g in args.grids:
    grid = DATA_FOLDER + '/' + g + '/' + g + '.grid.nc'
    if not os.path.exists(grid):
        raise IOError('File does not exist: ' + grid)
    grids.append(grid)

compare_plot_mpas_regional_meshes(grids,
                                  outfile=args.outfile,
                                  suptitle='Meshes comparison',
                                  each_title='<NAME>: <NCELLS> cells',
                                  border_radius=args.border,
                                  vmin=args.vmin,
                                  vmax=args.vmax,
                                  cmap=args.cmap)

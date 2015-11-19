#!/bin/bash

# open tunnel to server in a separate terminal
# ssh -CYttg -L 30001:localhost:30001 pedrosp@ime.usp.br ssh -CYtt -L 30001:localhost:22 pedrosp@arachne

# rsync data
#x1.163842/  x1.2562/  x1.2621442/	x1.40962/  x1.655362/  x4.163842/
rsync -av -e "ssh -p 30001"  x1.2562/  pedrosp@localhost:/var/tmp/pedrosp/grids/mpas/x1.2562/ --progress
rsync -av -e "ssh -p 30001"  x1.10242/  pedrosp@localhost:/var/tmp/pedrosp/grids/mpas/x1.10242/ --progress
rsync -av -e "ssh -p 30001"  x1.40962/  pedrosp@localhost:/var/tmp/pedrosp/grids/mpas/x1.40962/ --progress
rsync -av -e "ssh -p 30001"  x1.163842/  pedrosp@localhost:/var/tmp/pedrosp/grids/mpas/x1.163842/ --progress
rsync -av -e "ssh -p 30001"  x1.655362/  pedrosp@localhost:/var/tmp/pedrosp/grids/mpas/x1.655362/ --progress
rsync -av -e "ssh -p 30001"  x4.163842/  pedrosp@localhost:/var/tmp/pedrosp/grids/mpas/x4.163842/ --progress
rsync -av -e "ssh -p 30001"  x4.535554/  pedrosp@localhost:/var/tmp/pedrosp/grids/mpas/x4.535554/ --progress



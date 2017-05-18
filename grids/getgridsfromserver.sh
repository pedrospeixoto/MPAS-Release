#!/bin/bash

# get grids stored in CFD01
#rsync -avu pedrosp@cfd01.ime.usp.br:/var/tmp/pedrosp/Work/Programas/MPAS/MPAS-PXT/grids/ --progress .

#Get grids from web server
wget --recursive --no-parent --no-clobber --convert-links --cut-dirs=3 --no-host-directories http://www.ime.usp.br/~pedrosp/grids/mpas/
rm index.* robots.txt
find . -type f -name 'index.html*' -delete

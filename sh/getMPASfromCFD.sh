#!/bin/bash

# Get MPAS 4
rsync -avu pedrosp@cfd01.ime.usp.br:/var/tmp/pedrosp/Work/Programas/MPAS/Repos/MPAS-Release-master.zip --progress .

# Get jw_test templates
rsync -avu pedrosp@cfd01.ime.usp.br:/var/tmp/pedrosp/Work/Programas/MPAS/Repos/jw_baroclinic_wave_pxt.tar.bz2 --progress .
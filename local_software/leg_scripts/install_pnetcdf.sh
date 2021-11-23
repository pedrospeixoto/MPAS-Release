#! /bin/bash

source ./install_helpers.sh ""

export CC=$SERIAL_CC
export CXX=$SERIAL_CXX
export F77=$SERIAL_F77
export FC=$SERIAL_FC
export MPICC=$MPI_CC
export MPICXX=$MPI_CXX
export MPIF77=$MPI_F77
export MPIF90=$MPI_FC
export F90=$SERIAL_FC
export FFLAGS="-fallow-argument-mismatch"
export FCFLAGS="-fallow-argument-mismatch"

PKG_NAME="PNETCDF"
PKG_INSTALLED_FILE="$SWEET_LOCAL_SOFTWARE_DST_DIR/bin/pnetcdf"
PKG_URL_SRC="https://www2.mmm.ucar.edu/people/duda/files/mpas/sources/pnetcdf-1.11.2.tar.gz"

config_setup

config_package $@

config_configure 

config_make_default_install

config_success

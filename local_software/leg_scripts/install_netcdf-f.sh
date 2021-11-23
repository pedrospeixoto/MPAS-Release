#! /bin/bash

source ./install_helpers.sh ""

PKG_NAME="NETCDF-F"
PKG_INSTALLED_FILE="$SWEET_LOCAL_SOFTWARE_DST_DIR/bin/netcdf-f"
PKG_URL_SRC="https://www2.mmm.ucar.edu/people/duda/files/mpas/sources/netcdf-fortran-4.4.5.tar.gz"


export CPPFLAGS="-I${SWEET_LOCAL_SOFTWARE_DST_DIR}/include"
export LDFLAGS="-L${SWEET_LOCAL_SOFTWARE_DST_DIR}/lib"
export LIBS="-lhdf5_hl -lhdf5 -lz -ldl"
export CC=$MPI_CC
export FC=$MPI_FC
export F77=$MPI_F77
export LIBS="-lnetcdf ${LIBS}"
export FFLAGS="-fallow-argument-mismatch"
export FCFLAGS="-fallow-argument-mismatch"

config_setup

config_package $@

config_configure --enable-parallel-tests --disable-shared

config_make_default_install

config_success

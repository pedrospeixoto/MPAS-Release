#! /bin/bash

source ./install_helpers.sh ""

PKG_NAME="NETCFD-C"
PKG_INSTALLED_FILE="$SWEET_LOCAL_SOFTWARE_DST_DIR/bin/netcdf-c"
PKG_URL_SRC="https://www2.mmm.ucar.edu/people/duda/files/mpas/sources/netcdf-c-4.7.0.tar.gz"


export FC=$F90
export FCFLAGS=$F90FLAGS
export CPPFLAGS="-I${SWEET_LOCAL_SOFTWARE_DST_DIR}/include"
export LDFLAGS="-L${SWEET_LOCAL_SOFTWARE_DST_DIR}/lib"
export LIBS="-lhdf5_hl -lhdf5 -lz -ldl"
export CC=$MPI_CC

config_setup

config_package $@

config_configure --disable-dap --enable-netcdf4 --enable-pnetcdf --enable-cdf5 --enable-parallel-tests --disable-shared

config_make_default_install

config_success

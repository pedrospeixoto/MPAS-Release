#! /bin/bash

source ./install_helpers.sh ""

export FC=$MPI_FC
export CC=$MPI_CC
export CXX=$MPI_CXX

PKG_NAME="HDF5"
PKG_INSTALLED_FILE="$SWEET_LOCAL_SOFTWARE_DST_DIR/bin/hdf5"
PKG_URL_SRC="https://www2.mmm.ucar.edu/people/duda/files/mpas/sources/hdf5-1.10.5.tar.bz2"

config_setup

config_package $@

config_configure --enable-parallel --with-zlib=${SWEET_LOCAL_SOFTWARE_DST_DIR} --disable-shared

config_make_default_install

config_success

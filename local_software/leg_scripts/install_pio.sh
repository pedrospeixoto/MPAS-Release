#! /bin/bash

source ./install_helpers.sh ""

PKG_NAME="PIO"
PKG_INSTALLED_FILE="$SWEET_LOCAL_SOFTWARE_DST_DIR/bin/pio"
#PKG_URL_SRC="https://www2.mmm.ucar.edu/people/duda/files/mpas/sources/netcdf-c-4.7.0.tar.gz"

cd local_src
git clone https://github.com/NCAR/ParallelIO
cd ParallelIO
git checkout -b pio-2.4.4 pio2_4_4
export PIOSRC=`pwd`
cd ..
mkdir pio
cd pio
export CC=$MPI_CC
export FC=$MPI_FC
cmake -DNetCDF_C_PATH=$NETCDF -DNetCDF_Fortran_PATH=$NETCDF -DPnetCDF_PATH=$PNETCDF -DHDF5_PATH=$NETCDF -DCMAKE_INSTALL_PREFIX=$LIBBASE -DPIO_USE_MALLOC=ON -DCMAKE_VERBOSE_MAKEFILE=1 -DPIO_ENABLE_TIMING=OFF $PIOSRC
make
#make check
make install
cd ..


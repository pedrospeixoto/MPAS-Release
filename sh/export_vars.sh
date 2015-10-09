#!/bin/bash

BASEDIR=/scratch/pd300/MPASprogs
SOURCEDIR=${BASEDIR}/sources

#clear all modules
module purge
#module load openmpi-x86_64
#module load openmpi-gcc-4.8.2/1.6.5 
module load gcc/4.8.2 
export FC=gfortran
export F77=gfortran
export F90=grortran
export CC=gcc
export MPIFC=mpif90
export MPIF90=mpif90
#not sure about this!!
export MPIF77=mpif77
export MPICC=mpicc

#MPI stuff
export MPI_PATH=${BASEDIR}/openmpi
export LD_LIBRARY_PATH=${MPI_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${MPI_PATH}/bin:$PATH

#NETCDF and PIO
export NETCDF_PATH=${BASEDIR}/netcdf
export PNETCDF_PATH=${BASEDIR}/pnetcdf
export PIO_PATH=${BASEDIR}/pio

export NETCDF=$NETCDF_PATH
export PNETCDF=$PNETCDF_PATH
export PIO=$PIO_PATH

#LIBs and PATHS
export LD_LIBRARY_PATH=${NETCDF_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${NETCDF_PATH}/bin:$PATH
export LD_LIBRARY_PATH=${PNETCDF_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${PNETCDF_PATH}/bin:$PATH
export LD_LIBRARY_PATH=${PIO_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${PIO_PATH}/bin:$PATH


#cmake
export PATH=${BASEDIR}/bin:$PATH

# METIS
export PATH=${BASEDIR}/metis-5.1.0/build/Linux-x86_64/programs:$PATH







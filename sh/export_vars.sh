#!/bin/bash

export BASEDIR=/scratch/pd300/MPASprogs
#export BASEDIR=/scratch/pedrosp

export MPI_PATH=${BASEDIR}/openmpi
export NETCDF_PATH=${BASEDIR}/netcdf
export PNETCDF_PATH=${BASEDIR}/pnetcdf
export PIO_PATH=${BASEDIR}/pio
export METIS_PATH=${BASEDIR}/metis

#clear all modules
module purge

#For ?
#module load openmpi-x86_64
#module load openmpi-gcc-4.8.2/1.6.5 

#For emps-snadbach
module load gcc/4.8.2 

#For lince
#module load openmpi/1.8.3-intel 
module load openmpi/1.10.1-intel

#export FC=ifort
#export F77=ifort
#export F90=ifort
#export CC=icc
export FC=gfortran
export F77=gfortran
export F90=grortran
export CC=gcc
export MPIFC=mpif90
export MPIF90=mpif90
export MPIF77=mpif77
export MPICC=mpicc

#MPI 
export LD_LIBRARY_PATH=${MPI_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${MPI_PATH}/bin:$PATH

#NETCDF and PIO
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

#cmake - needed for metis
#export PATH=${BASEDIR}/bin:$PATH

# METIS - use as: gpmetis graph.info N
export PATH=${BASEDIR}/metis-5.1.0/build/Linux-x86_64/programs:$PATH
#export LD_LIBRARY_PATH=${METIS_PATH}/lib:$LD_LIBRARY_PATH
#export PATH=${METIS_PATH}/bin:$PATH

#NCAR GRAPHICS NCL
export NCL_PATH=${BASEDIR}/ncl
export PATH=${NCL_PATH}/bin:$PATH
export LD_LIBRARY_PATH=${NCL_PATH}/lib:$LD_LIBRARY_PATH
export NCARG_ROOT=${NCL_PATH}


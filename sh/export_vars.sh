#!/bin/bash
# Last modif Peixoto Nov 2015
# Comment what you don't need 

#Lince
export BASEDIR=/scratch/pedrosp

#MAC cluster
export BASEDIR=/scratch/pr63so/di25coq

#CFD
export BASEDIR=/var/tmp/pedrosp/MPAS

#Laptop
export BASEDIR=/opt

export SOURCEDIR=${BASEDIR}/sources
export MPI_PATH=${BASEDIR}/openmpi
export NETCDF_PATH=${BASEDIR}/netcdf
export PNETCDF_PATH=${BASEDIR}/pnetcdf
export PIO_PATH=${BASEDIR}/pio
export METIS_PATH=${BASEDIR}/metis


#clear all modules
#module purge

#module load openmpi-x86_64
#module load openmpi-gcc-4.8.2/1.6.5 


#For lince
#module load openmpi/1.8.3-intel 
module load openmpi/1.10.1-intel

#For MAC cluster
module load netcdf/mpi/4.3
module load pnetcdf/1.6
export NETCDF_PATH=${NETCDF_BASE}
export PNETCDF_PATH=${PNETCDF_BASE}
export PIO_PATH=${BASEDIR}/pio


#For gnu
module load gcc/4.8.2 
export FC=gfortran
export F77=gfortran
export F90=grortran
export CC=gcc

#For intel
export FC=ifort
export F77=ifort
export F90=ifort
export CC=icc

#MPI
export MPIFC=mpif90
export MPIF90=mpif90
export MPIF77=mpif77
export MPICC=mpicc

#For MPAS
export NETCDF=$NETCDF_PATH
export PNETCDF=$PNETCDF_PATH
export PIO=$PIO_PATH


export LD_LIBRARY_PATH=${MPI_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${MPI_PATH}/bin:$PATH

export LD_LIBRARY_PATH=${NETCDF_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${NETCDF_PATH}/bin:$PATH

export LD_LIBRARY_PATH=${PNETCDF_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${PNETCDF_PATH}/bin:$PATH

export LD_LIBRARY_PATH=${PIO_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${PIO_PATH}/bin:$PATH

export LD_LIBRARY_PATH=${METIS_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${METIS_PATH}/bin:$PATH

export NCL_PATH=${BASEDIR}/ncl
export PATH=${NCL_PATH}/bin:$PATH
export LD_LIBRARY_PATH=${NCL_PATH}/lib:$LD_LIBRARY_PATH
export NCARG_ROOT=${NCL_PATH}









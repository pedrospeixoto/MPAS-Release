#!/bin/bash
# Last modif Peixoto Nov 2015
# Comment what you don't need 

#Lince
export BASEDIR=/scratch/pedrosp

#MAC cluster
export BASEDIR=/scratch/pr63so/di25coq

#CFD
#export BASEDIR=/var/tmp/pedrosp/MPAS

#Laptop
export BASEDIR=/opt

cd $BASEDIR
mkdir sources
export SOURCEDIR=${BASEDIR}/sources
export MPI_PATH=${BASEDIR}/openmpi
export NETCDF_PATH=${BASEDIR}/netcdf
export PNETCDF_PATH=${BASEDIR}/pnetcdf
export PIO_PATH=${BASEDIR}/pio
export METIS_PATH=${BASEDIR}/metis


#clear all modules
module purge

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


test -n "$1" && exit 0


cd $SOURCEDIR
#GET SOURCES
if ! [ -f ${SOURCEDIR}/openmpi-1.6.5.tar.gz ]; then
	wget http://www.open-mpi.org/software/ompi/v1.6/downloads/openmpi-1.6.5.tar.gz
fi
if ! [ -f ${SOURCEDIR}/parallel-netcdf-1.3.1.tar.gz ]; then
	wget http://ftp.mcs.anl.gov/pub/parallel-netcdf/parallel-netcdf-1.3.1.tar.gz
fi
if ! [ -f ${SOURCEDIR}/netcdf-4.1.3.tar.gz ]; then
	wget http://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-4.1.3.tar.gz
fi
if ! [ -d ${SOURCEDIR}/pio1_6_7 ]; then
	svn export http://parallelio.googlecode.com/svn/trunk_tags/pio1_6_7/
	
fi
if ! [ -f ${SOURCEDIR}/metis-5.1.0.tar.gz ]; then
	wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
fi

if ! [ -f ${SOURCEDIR}/pio.zip ]; then
	wget https://github.com/NCAR/ParallelIO/archive/master.zip
	mv master.zip pio.zip
fi

#OPENMPI # not needed if module loaded
cd $BASEDIR
tar xvf ${SOURCEDIR}/openmpi-1.6.5.tar.gz
cd openmpi-1.6.5
./configure --prefix=${MPI_PATH}
#./configure --prefix=${MPI_PATH} CXX=icpc
make
make install
export LD_LIBRARY_PATH=${MPI_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${MPI_PATH}/bin:$PATH

#NETCDF
cd $BASEDIR
tar xvf ${SOURCEDIR}/netcdf-4.1.3.tar.gz
cd netcdf-4.1.3
./configure --prefix=${NETCDF_PATH} --disable-dap --disable-netcdf-4 --disable-cxx --disable-shared --enable-fortran
make all check
make install
export LD_LIBRARY_PATH=${NETCDF_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${NETCDF_PATH}/bin:$PATH

#PNETCDF
cd $BASEDIR
tar xvf ${SOURCEDIR}/parallel-netcdf-1.3.1.tar.gz
cd parallel-netcdf-1.3.1
./configure --prefix=${PNETCDF_PATH}
make 
make install
export LD_LIBRARY_PATH=${PNETCDF_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${PNETCDF_PATH}/bin:$PATH

#PIO
cd $BASEDIR
cp -a ${SOURCEDIR}/pio1_6_7 .
cd pio1_6_7/pio
./configure --prefix=${PIO_PATH}
make 
make install
export LD_LIBRARY_PATH=${PIO_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${PIO_PATH}/bin:$PATH

#PIO from git
cd $BASEDIR
unzip ${SOURCEDIR}/pio.zip
cd ParallelIO-master
CC=mpicc FC=mpif90 cmake -DNetCDF_PATH=${NETCDF_PATH} -DPnetCDF_PATH=${PNETCDF_PATH} -DCMAKE_INSTALL_PREFIX:PATH=${PIO_PATH} .
make
make install



#METIS
cd $BASEDIR
tar xvf ${SOURCEDIR}/metis-5.1.0.tar.gz
cd metis-5.1.0
make config prefix=${METIS_PATH}
make install
export LD_LIBRARY_PATH=${METIS_PATH}/lib:$LD_LIBRARY_PATH
export PATH=${METIS_PATH}/bin:$PATH

#MPAS 
cd $BASEDIR
wget https://github.com/pedrospeixoto/MPAS-PXT/archive/master.zip
mv master.zip MPAS-PXT.zip
unzip xvf MPAS-PXT.zip
mv MPAS-PXT-master MPAS-PXT

# Grids
cd MPAS-PXT
cd grids
#rsync -avu pedrosp@ime.usp.br:www/grids/mpas/ .
wget -b --recursive --no-parent --no-clobber --convert-links --cut-dirs=3 --no-host-directories http://www.ime.usp.br/~pedrosp/grids/mpas/
rm index.* robots.txt
find . -type f -name 'index.html*' -delete
cd ..


#Compile
#make gfortran CORE=init_atmosphere

#run
#mpirun -np 4 ./init_atmosphere_model


# NCL - outputs
cd MPAS-PXT
cd sh
. wget-ncl.sh
cd $BASEDIR
mkdir ncl
mv ncl_ncarg* ncl/
cd ncl
tar xvf ncl_ncarg-6.2.1.Linux_Debian7.6_x86_64_nodap_gcc472.tar.gz
export NCL_PATH=${BASEDIR}/ncl
export PATH=${NCL_PATH}/bin:$PATH
export LD_LIBRARY_PATH=${NCL_PATH}/lib:$LD_LIBRARY_PATH
export NCARG_ROOT=${NCL_PATH}









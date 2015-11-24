#! /bin/bash

#
# This is a template to set up environment variables correctly
#


SCRIPTDIR="`pwd`/local_software"

if [ ! -d "$SCRIPTDIR" ]; then
        echo
	echo "********************************************************"
        echo "ERROR: Execute this script only from the root directory"
        echo "   source local_software/env_vars.sh"
	echo "********************************************************"
        echo
	return
fi

export PATH="$SCRIPTDIR/local/bin:$PATH"
export PKG_CONFIG_PATH="$SCRIPTDIR/local/lib/pkgconfig:$PKG_CONFIG_PATH"

export LD_LIBRARY_PATH="$SCRIPTDIR/local/lib:$LD_LIBRARY_PATH"
export LD_LIBRARY_PATH="$SCRIPTDIR/local/lib64:$LD_LIBRARY_PATH"

export DYLD_LIBRARY_PATH="$SCRIPTDIR/local/lib:$LD_LIBRARY_PATH"
export DYLD_LIBRARY_PATH="$SCRIPTDIR/local/lib64:$LD_LIBRARY_PATH"



export INSTDIR="$SCRIPTDIR/local"


export NETCDF_PATH=${INSTDIR}
export NETCDF=${INSTDIR}
export PNETCDF_PATH=${INSTDIR}
export PIO_PATH=${INSTDIR}

# FOR MPAS
export NETCDF=$NETCDF_PATH
export PNETCDF=$PNETCDF_PATH
export PIO=$PIO_PATH

host=`hostname`
if [[ $host == mac* ]]; then
	echo "DETECTED MAC CLUSTER (AMD), LOADING STUFF"

	source /etc/profile.d/modules.sh

	module unload intel
	module unload mpi.intel
	module load gcc/4.8
	module load mpi.intel/5.1_gcc
	module load binutils

	# setup compile stuff
	#For GNU
	export FC=gfortran
	export F77=gfortran
	export F90=grortran
	export CC=gcc

	#For Intel - gnarg
	#export FC=ifort
	#export F77=ifort
	#export F90=ifort
	#export CC=icc

	#MPI
	export MPIFC=mpif90
	export MPIF90=mpif90
	export MPIF77=mpif77
	export MPICC=mpicc
else
	echo "********************************************************"
	echo "****************** ENVIRONMENT UNKNOWN *****************"
	echo "********************************************************"
	return
fi



echo "Environment variables loaded"

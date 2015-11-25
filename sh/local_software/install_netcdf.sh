#! /bin/bash

. config.sh


echo "*** NETCDF ***"
if [ "`uname -s`" != "Linux" ]; then
        echo "This script only supports Linux systems"
else
        if [ ! -e "$DST_DIR/lib/libnetcdf.so" ]; then
                SRC_LINK="http://www.unidata.ucar.edu/downloads/netcdf/ftp/netcdf-4.1.3.tar.gz"
                FILENAME="`basename $SRC_LINK`"
                BASENAME="netcdf-4.1.3"

                cd "$SRC_DIR"

                if [ ! -e "$FILENAME" ]; then
			echo "Getting $SRC_LINK"
                        curl "$SRC_LINK" -o "$FILENAME" || exit 1
                fi
		echo "Extracting $FILENAME"
                tar xzf "$FILENAME"
                cd "$BASENAME"

                # update configure scripts
                #sh autogen.sh
                #sed -i -- 's/EXTRA_CFLAGS="$EXTRA_CFLAGS -fpascal-strings"//' ./configure
                ./configure --prefix=${DST_DIR} --disable-dap --disable-netcdf-4 --disable-cxx --disable-shared --enable-fortran || exit 1
		make all check || exit 1
                make install || exit 1

                echo "DONE"

        fi
fi


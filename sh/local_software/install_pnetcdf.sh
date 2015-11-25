#! /bin/bash

. config.sh


echo "*** NETCDF ***"
if [ "`uname -s`" != "Linux" ]; then
        echo "This script only supports Linux systems"
else
        if [ ! -e "$DST_DIR/lib/libpnetcdf.so" ]; then
                SRC_LINK="http://ftp.mcs.anl.gov/pub/parallel-netcdf/parallel-netcdf-1.3.1.tar.gz"
                FILENAME="`basename $SRC_LINK`"
                BASENAME="parallel-netcdf-1.3.1"

                cd "$SRC_DIR"

                if [ ! -e "$FILENAME" ]; then
			echo "Getting $SRC_LINK"
                        curl "$SRC_LINK" -o "$FILENAME" || exit 1
                fi

		echo "Extracting $FILENAME"
                tar xzf "$FILENAME"
                cd "$BASENAME"

                ./configure --prefix=${DST_DIR} || exit 1
		make || exit 1
		make install || exit 1

                echo "DONE"

        fi
fi


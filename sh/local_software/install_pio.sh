#! /bin/bash

. config.sh


echo "*** PIO ***"
if [ "`uname -s`" != "Linux" ]; then
        echo "This script only supports Linux systems"
else
        if [ ! -e "$DST_DIR/lib/libpio.so" ]; then
                SRC_LINK="https://github.com/NCAR/ParallelIO/archive/pio1_6_7.zip"
                FILENAME="`basename $SRC_LINK`"
                BASENAME="pio1_6_7.zip"
                
		# On the Blue gene Rice the wget has no zip extention
		
                cd "$SRC_DIR"

                if [ ! -e "$FILENAME" ]; then
			echo "Getting $SRC_LINK"
                        wget "$SRC_LINK" || exit 1
                fi

		echo "Extracting $FILENAME"
		unzip "$FILENAME"
		mv ParallelIO-pio1_6_7 pio1_6_7 || exit 1
                cd pio1_6_7/pio || exit 1

                ./configure --prefix=${DST_DIR} || exit 1

		# INTEL HACK for MAC CLUSTER
		if [ "mac-login-amd" == "`hostname`" ]; then
			echo "************************************ HACK FOR MAC ********************************"
			sed -i -- 's/-I\/lrz\/sys\/intel\/impi\/5.1.1.109\/include64//' ./Makefile.conf
		fi

		make all || exit 1
                make install || exit 1

                echo "DONE"

        fi
fi


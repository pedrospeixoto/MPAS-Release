#! /bin/bash

source ./install_helpers.sh ""

PKG_NAME="ZLIB"
PKG_INSTALLED_FILE="$SWEET_LOCAL_SOFTWARE_DST_DIR/bin/zlib"
PKG_URL_SRC="https://www2.mmm.ucar.edu/people/duda/files/mpas/sources/zlib-1.2.11.tar.gz"

config_setup

config_package $@

config_configure --static

config_make_default_install

config_success

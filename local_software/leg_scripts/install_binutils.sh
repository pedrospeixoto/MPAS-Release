#! /bin/bash

#
# Required for Travis CI
#

source ./install_helpers.sh ""

#echo_error "ERROR: There are some issues if installing binutils such as 'configure: error: memset not found in libc' if configuring libpng\nTherefore, we disable this right here"

# Name of package
PKG_NAME="binutils"

# Path to one file of installed package to test for existing installation
PKG_INSTALLED_FILE="$SWEET_LOCAL_SOFTWARE_DST_DIR/bin/as"

# URL to source code to fetch it
PKG_URL_SRC="binutils-2.34.tar.xz"

config_setup

config_package $@

config_configure_make_default_install

config_success

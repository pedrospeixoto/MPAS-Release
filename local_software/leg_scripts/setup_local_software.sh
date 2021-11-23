#! /bin/bash

#
# Install default software packages for the currently loaded
# platform ${MULE_PLATFORM_ID}
#
# This information is available in
#	"${MULE_LOCAL_PLATFORM_DIR}/local_software_default.sh"
#


source ./install_helpers.sh "" || exit 1

if [ ! -e "$MULE_LOCAL_PLATFORM_DIR" ]; then
	echo_error ""
	echo_error "MULE LOCAL Platform directory '${MULE_LOCAL_PLATFORM_DIR}' not found"
	echo_error ""
	exit 1
fi

LOCAL_SOFTWARE_PLATFORM="${MULE_LOCAL_PLATFORM_DIR}/local_software_default.sh"
if [ ! -e "$LOCAL_SOFTWARE_PLATFORM" ]; then
	echo_error ""
	echo_error "ERROR: File '${LOCAL_SOFTWARE_PLATFORM}' not found"
	echo_error ""
	exit
fi


# Packages to install
PKGS=()
source "$LOCAL_SOFTWARE_PLATFORM"


echo_info "Installing packages: ${PKGS[@]}"

for D in "${PKGS[@]}"; do
	./$D || exit 1

	# Make sure that the python environment is loaded if installing python
	source "$MULE_SOFTWARE_ROOT/local_software/local/python_venv_anaconda/bin/activate" 2>/dev/null
	hash -r
done

echo_success_hline
echo_success "All software installed"
echo_success_hline


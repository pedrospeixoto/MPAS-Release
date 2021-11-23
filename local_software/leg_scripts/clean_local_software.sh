#! /bin/bash

source ./install_helpers.sh "" || exit 1

echo_info "Cleaning up"

DIRS="local local_src"
for d in $DIRS; do
	C="rm -rf ${d}"
	echo_info " + Executing '${C}'"

	${C}
done

echo_success "Done"


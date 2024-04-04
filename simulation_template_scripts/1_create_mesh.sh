#!/bin/bash

# !!!!! Requires vtx-mpas-meshes: https://github.com/marta-gil/vtx-mpas-meshes !!!!!

# Activate conda vtx_env environment
CONDA_PATH="$(conda info --root)"
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate vtx_env

# Select parameters from input_file.txt
echo "Reading input parameters:"
while IFS="=" read -r name value; do
    if [[ ! "$name" =~ ^\# ]]; then
	declare -r $name=$value
        echo $name":" $value
    fi	
done < input_file.txt

# Run script
cd $vtx_mpas_meshes_dir
python3 create_regional_mesh.py --vtx_mpas_meshes_dir $vtx_mpas_meshes_dir --exp_dir $exp_dir --meshes_dir $meshes_dir --N $N --lon $lon --lat $lat --inner_radius $inner_radius --outer_radius $outer_radius --high_res $high_res --low_res $low_res --do_regional $do_regional 

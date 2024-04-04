#!/bin/bash

# Select parameters from input_file.txt
echo "Reading input parameters:"
while IFS="=" read -r name value; do
    if [[ ! "$name" =~ ^\# ]]; then
        declare -r $name=$value
        echo $name":" $value
    fi
done < input_file.txt

exp_gen_dir=${exp_dir}

# Set sensitivity parameter values
iradius_min=5
iradius_max=125
iradius_step=10

source utils.sh
iradius_range=($(create_x_range $iradius_min $iradius_max $iradius_step))

# Preparation: create directories and copy simulation scripts
for iradius in "${iradius_range[@]}"; do
    echo "$iradius"
    
    lat_round=$(printf "%.0f" "$lat")
    lon_round=$(printf "%.0f" "$lon")
    oradius_round=$(printf "%.0f" "$outer_radius")
    iradius_round=$(printf "%.0f" "$iradius")
    margin=$((outer_radius - iradius))
    margin_round=$(printf "%.0f" "$margin")
    hres_round=$(printf "%.0f" "$high_res")
    lres_round=$(printf "%.0f" "$low_res")
    dir_name=lat_${lat_round}_lon_${lon_round}_oradius_${oradius_round}_iradius_${iradius_round}_margin_${margin_round}_hres_${hres_round}_lres_${lres_round} 
    
    if [ ! -d $dir_name ]; then
        mkdir $dir_name
    fi
    cd $dir_name
    cp ${simulation_template_scripts_dir}/* .
    rm input_file.txt
    cp ../input_file.txt .
    modify_param_value input_file.txt inner_radius $iradius
    modify_param_value input_file.txt exp_dir $(pwd)

    cd $exp_gen_dir || exit 1
done

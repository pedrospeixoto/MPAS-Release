#!/bin/bash

# Activate conda vtx_env environment
CONDA_PATH="$(conda info --root)"
source "$CONDA_PATH/etc/profile.d/conda.sh"
conda activate mpas-tools

# Select parameters from input_file.txt
echo "Reading input parameters:"
while IFS="=" read -r name value; do
    if [[ ! "$name" =~ ^\# ]]; then
	declare -r $name=$value
        echo $name":" $value
    fi	
done < input_file.txt

# Create array of dates and hours to loop through files
source utils.sh
datetime_array=($(create_datetime_dot_range $date1 $time1 $date2 $time2 $dt_files))
# Adjust array format
datetime_array_final=$(printf "%s|" "${datetime_array[@]}")

# Select variables for concat file
vars_array=('zgrid' 'uReconstructZonal' 'uReconstructMeridional' 'latCell' 'lonCell')
# Adjust array format
vars_array_final=$(printf "%s|" "${vars_array[@]}")

# Select stream
stream='history'

# Input data dir
data_dir=${exp_dir}/output

echo $datetime_array_final

# Run script
cd $py_scripts_dir
python3 concat.py --data_dir $data_dir --vars_array "${vars_array_final}" --datetime_array "${datetime_array_final}" --stream $stream

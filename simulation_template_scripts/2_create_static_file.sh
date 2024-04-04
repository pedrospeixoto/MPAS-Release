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

# Following tutorial https://www2.mmm.ucar.edu/projects/mpas/tutorial/Boulder2019/index.html

# Create static file directory
cd $static_files_dir
mkdir $file_name
cd $file_name

# Link mesh file
ln -s ${meshes_dir}/${file_name}/${file_name}.grid.nc grid.nc
ln -s ${meshes_dir}/${file_name}/${file_name}.grid.graph.info.part.${N} info.part.${N}

# Link init_atmosphere_model
ln -s ${mpas_dir}/init_atmosphere_model .

# Create streams file
if [ -f "streams.init_atmosphere" ]; then
    rm -f streams.init_atmosphere
fi
cat << EOF  > streams.init_atmosphere
<streams>
<immutable_stream name="input"
                  type="input"
                  filename_template="grid.nc"
                  input_interval="initial_only" />

<immutable_stream name="output"
                  type="output"
                  filename_template="static.nc"
                  clobber_mode="overwrite"
                  output_interval="initial_only" />
</streams>
EOF

# Create namelist file
if [ -f "namelist.init_atmosphere" ]; then
    rm -f namelist.init_atmosphere
fi
cat << EOF  > namelist.init_atmosphere
&nhyd_model
    config_init_case       = 7
/
&data_sources
    config_geog_data_path = '${geog_data_dir}'
   config_landuse_data = 'MODIFIED_IGBP_MODIS_NOAH'
    config_topo_data = 'GMTED2010'
    config_vegfrac_data = 'MODIS'
    config_albedo_data = 'MODIS'
    config_maxsnowalbedo_data = 'MODIS'
    config_supersample_factor = 3
/
&preproc_stages
    config_static_interp = true
    config_native_gwd_static = true
    config_vertical_grid = false
    config_met_interp    = false
    config_input_sst     = false
    config_frac_seaice   = false
/
&decomposition
    config_block_decomp_file_prefix = '${file_name}.grid.graph.info.part.'
/
EOF

# Run init_atmosphere_model
nohup mpirun -n 2 ./init_atmosphere_model &

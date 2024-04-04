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

echo "Creating output directory"

output_dir=$exp_dir/output
if [ ! -d $output_dir ]; then
    mkdir $output_dir
fi

cd $output_dir

#-----------------------------------------------------------------------
# Build streams.init_atmosphere I/O configuration file
#-----------------------------------------------------------------------

echo "Building streams.init_atmosphere"

if [ -f streams.init_atmosphere ]; then
    rm -f streams.init_atmosphere
fi

cat << EOF  > streams.init_atmosphere
<streams>
<immutable_stream name="input"
                  type="input"
                  filename_template="init.nc"
                  input_interval="initial_only" />

<immutable_stream name="output"
                  type="output"
                  filename_template="foo.nc"
                  clobber_mode="overwrite"
                  output_interval="initial_only" />

<immutable_stream name="lbc"
                  type="output"
                  filename_template="lbc.\$Y-\$M-\$D_\$h.\$m.\$s.nc"
                  filename_interval="output_interval"
                  packages="lbcs"
                  clobber_mode="overwrite"
                  output_interval="${lbcs_interval}" />
</streams>
EOF

#
# Copy in MPAS init_atmosphere executable.
#

echo "Copying init_atmosphere executable"

ln -s ${mpas_dir}/init_atmosphere_model .

#
# Link to the meteorological target data intermediate files
#

echo "Linking intermediate files"
# TODO: link only files between date1_h1 and date2_h2
ln -s ${intermediate_input_data_dir}/FILE* .
#ln -s $MET_DIR/GEO* .
#ln -s $MET_DIR/LSM* .
 
#
# Link to all block decomposition files
#

echo "Linking block decomposition file"

ln -s ${meshes_dir}/${file_name}/${file_name}.grid.graph.info.part.${N} info.part.${N}

#-----------------------------------------------------------------------
# Build namelist.init_atmosphere
#-----------------------------------------------------------------------

echo "Building namelist.init_atmosphere"

if [ -f namelist.init_atmosphere ]; then
    rm namelist.init_atmosphere
fi

cat << EOF  > namelist.init_atmosphere
&nhyd_model
    config_init_case       = 9
    config_theta_adv_order = 3
    config_start_time      = '${date1}_${time1}'
    config_stop_time       = '${date2}_${time2}'
    config_coef_3rd_order = 0.25
    config_hcm_staggering = false
/
&dimensions
    config_nvertlevels   = ${nvertlevels}
    config_nsoillevels   = 4
    config_nfglevels     = 38
    config_nfgsoillevels = 4
/
&data_sources
    config_geog_data_path = '${geog_data_dir}'
    config_met_prefix = 'FILE'
    config_sfc_prefix = 'FILE'
    config_fg_interval = ${lbcs_interval}
    config_landuse_data = 'MODIFIED_IGBP_MODIS_NOAH'
    config_topo_data = 'GMTED2010'
    config_vegfrac_data = 'MODIS'
    config_albedo_data = 'MODIS'
    config_maxsnowalbedo_data = 'MODIS'
    config_supersample_factor = 3
    config_use_spechumd = false
/
&vertical_grid
    config_ztop = ${ztop}
    config_nsmterrain = 1
    config_smooth_surfaces = true
    config_dzmin = 0.3
    config_nsm = 30
    config_tc_vertical_grid = true
    config_blend_bdy_terrain = false
/
&interpolation_control
    config_extrap_airtemp = 'linear'
/
&preproc_stages
    config_static_interp = .false.
    config_native_gwd_static = .false.
    config_vertical_grid = .true.
    config_met_interp    = .true.
    config_input_sst     = .false.
    config_frac_seaice   = .true.
/
&io
    config_pio_num_iotasks = 0
    config_pio_stride = 1
/
&decomposition
    config_block_decomp_file_prefix = 'info.part.'
/
EOF

#
# Run executable
#
echo "Running init_atmosphere_model"
date '+Started MPAS init_atmosphere at %m/%d/%y %H:%M:%S'
nohup mpirun -n $N ./init_atmosphere_model
date '+Completed MPAS init_atmosphere at %m/%d/%y %H:%M:%S%n'

#
# Store streams and namelist files
#
mv streams.init_atmosphere streams_lbcs.init_atmosphere
mv namelist.init_atmosphere namelist_lbcs.init_atmosphere

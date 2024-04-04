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

echo "Building streams.atmosphere"

if [ -f streams.atmosphere ]; then
    rm -f streams.atmosphere
fi

cat << EOF  > streams.atmosphere
<streams>
<immutable_stream name="input"
                  type="input"
                  filename_template="init.nc"
                  input_interval="initial_only" />

<immutable_stream name="restart"
                  type="input;output"
                  filename_template="restart.\$Y-\$M-\$D_\$h.\$m.\$s.nc"
                  input_interval="initial_only"
                  #clobber_mode="overwrite"
                  output_interval="$restart_output_interval" />

<immutable_stream name="fdda"
                  type="input"
                  io_type="netcdf4"
                  filename_template="fdda.nc"
                  input_interval="$fdda_output_interval" />

<stream name="output"
        type="output"
        filename_template="history.\$Y-\$M-\$D_\$h.\$m.\$s.nc"
        #clobber_mode="overwrite"
        output_interval="$history_output_interval" >
	<file name="stream_list.atmosphere.output"/>
</stream>

<stream name="diagnostics"
        type="output"
        filename_template="diag.\$Y-\$M-\$D_\$h.\$m.\$s.nc"
        #clobber_mode="overwrite"
        output_interval="$diag_output_interval" >
	<file name="stream_list.atmosphere.diagnostics"/>
</stream>

<stream name="surface"
        type="input"
        filename_template="x1.40962.sfc_update.nc"
        filename_interval="none"
        input_interval="$sfc_interval" >

	<file name="stream_list.atmosphere.surface"/>
</stream>

<immutable_stream name="iau"
                  type="input"
                  filename_template="x1.40962.AmB.\$Y-\$M-\$D_\$h.\$m.\$s.nc"
                  filename_interval="none"
                  packages="iau"
                  input_interval="initial_only" />

<immutable_stream name="lbc_in"
                  type="input"
                  filename_template="lbc.\$Y-\$M-\$D_\$h.\$m.\$s.nc"
                  filename_interval="input_interval"
                  packages="limited_area"
                  input_interval="$lbcs_interval" />

</streams>
EOF

#
# Copy in MPAS init_atmosphere executable.
#

echo "Copying atmosphere executable"

ln -s ${mpas_dir}/atmosphere_model .

#
# Copy in physics files
#

echo "Copying physics files"

ln -s ${mpas_dir}/src/core_atmosphere/physics/physics_wrf/files/* .

#
# Copy in stream_list.atmosphere* files 
#

echo "Copying stream_list.atmosphere* files"

cp ${config_files_dir}/stream_list.atmosphere.* .

#
# Link to all block decomposition files
#

echo "Linking block decomposition file"

ln -s ${meshes_dir}/${file_name}/${file_name}.grid.graph.info.part.${N} info.part.${N}

#-----------------------------------------------------------------------
# Build namelist.init_atmosphere
#-----------------------------------------------------------------------

echo "Building namelist.atmosphere"

if [ -f namelist.atmosphere ]; then
    rm namelist.atmosphere
fi

cat << EOF  > namelist.atmosphere
&nhyd_model
    config_time_integration_order = 2
    config_dt = $config_dt
    config_start_time = '${date1}_${time1}'
    config_run_duration = $config_run_duration
    config_split_dynamics_transport = true
    config_number_of_sub_steps = 2
    config_dynamics_split_steps = 3
    config_h_mom_eddy_visc2 = 0.0
    config_h_mom_eddy_visc4 = 0.0
    config_v_mom_eddy_visc2 = 0.0
    config_h_theta_eddy_visc2 = 0.0
    config_h_theta_eddy_visc4 = 0.0
    config_v_theta_eddy_visc2 = 0.0
    config_horiz_mixing = '2d_smagorinsky'
    config_len_disp = $config_len_disp
    config_visc4_2dsmag = 0.05
    config_w_adv_order = 3
    config_theta_adv_order = 3
    config_scalar_adv_order = 3
    config_u_vadv_order = 3
    config_w_vadv_order = 3
    config_theta_vadv_order = 3
    config_scalar_vadv_order = 3
    config_scalar_advection = true
    config_positive_definite = false
    config_monotonic = true
    config_coef_3rd_order = 0.25
    config_epssm = 0.1
    config_smdiv = 0.1
/
&damping
    config_zd = 22000.0
    config_xnutr = 0.2
/
&limited_area
    config_apply_lbcs = $config_apply_lbcs
/
&io
    config_pio_num_iotasks = 0
    config_pio_stride = 1
/
&decomposition
    config_block_decomp_file_prefix = 's30_m200.region.grid.graph.info.part'
/
&restart
    config_do_restart = $config_do_restart
/
&printout
    config_print_global_minmax_vel = true
    config_print_detailed_minmax_vel = false
/
&IAU
    config_IAU_option = 'off'
    config_IAU_window_length_s = 21600.
/
&physics
    config_sst_update = $config_sst_update
    config_sstdiurn_update = $config_sstdiurn_update
    config_deepsoiltemp_update = $config_deepsoiltemp_update
    config_radtlw_interval = '$config_radtlw_interval'
    config_radtsw_interval = '$config_radtsw_interval'
    config_bucket_update = '$config_bucket_update'
    config_physics_suite = '$config_physics_suite'
    config_microp_scheme = '$config_microp_scheme'
    config_gwdo_scheme = '$config_gwdo_scheme'
    config_fdda_scheme = '$config_fdda_scheme'
    config_fdda_t = $config_fdda_t
    config_fdda_q = $config_fdda_q
    config_fdda_uv = $config_fdda_uv
    config_fdda_t_coef = $config_fdda_t_coef
    config_fdda_q_coef = $config_fdda_q_coef
    config_fdda_uv_coef = $config_fdda_uv_coef
    config_fdda_t_in_pbl = $config_fdda_t_in_pbl
    config_fdda_q_in_pbl = $config_fdda_q_in_pbl
    config_fdda_uv_in_pbl = $config_fdda_uv_in_pbl
    config_fdda_t_min_layer = $config_fdda_t_min_layer
    config_fdda_q_min_layer = $config_fdda_q_min_layer
    config_fdda_uv_min_layer = $config_fdda_uv_min_layer
/
&soundings
    config_sounding_interval = 'none'
/
EOF

#
# Run executable
#
echo "Running atmosphere_model"
date '+Started MPAS atmosphere at %m/%d/%y %H:%M:%S'
nohup mpirun -n $N ./atmosphere_model &
date '+Completed MPAS atmosphere at %m/%d/%y %H:%M:%S%n'

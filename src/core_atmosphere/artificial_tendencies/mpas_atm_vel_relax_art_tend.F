module mpas_atm_vel_relax_art_tend

    use mpas_derived_types, only : MPAS_pool_type, MPAS_clock_type, MPAS_LOG_ERR, MPAS_LOG_CRIT
    use mpas_kind_types, only : RKIND, R8KIND, StrKIND
    use mpas_log, only : mpas_log_write
    use mpas_pool_routines

    type (MPAS_pool_type), pointer :: mesh
    type (MPAS_pool_type), pointer :: state
    type (MPAS_pool_type), pointer :: diag

    type (MPAS_clock_type), pointer :: clock
    
    real(RKIND), dimension(:), pointer :: areaCell
    integer, pointer :: nCellsSolve

    logical :: lmean_init = .false.
    real(RKIND), pointer :: time_scale

    real(RKIND), dimension(:), pointer :: u_init, v_init! Mean horizontal velocity profile at different height levels
    real(RKIND), allocatable, dimension(:) :: mean_u, mean_v, mpi_local_mean_u, mpi_local_mean_v! current mean velocity profile at different height levels

    real(RKIND) :: total_cell_area

    public :: velocity_relaxation_setup, &
              velocity_relaxation_compute, &
              velocity_relaxation_cleanup

    private

    contains
    
    !-----------------------------------------------------------------------
    !  routine velocity_relaxation_setup
    !
    !> \brief Initialize velocity field relaxation artificial tendency
    !> \author Felipe A. V. de Bragança Alves
    !> \date   27 August 2024
    !> \details
    !>  Initialize velocity field relaxation artificial tendency
    !
    !-----------------------------------------------------------------------
    subroutine velocity_relaxation_setup(stream_mgr, configs, structs, clock, dminfo)

        use mpas_derived_types, only : MPAS_streamManager_type, MPAS_pool_type, MPAS_clock_type, dm_info
        use mpas_dmpar, only: mpas_dmpar_sum_real

        implicit none

        type (MPAS_streamManager_type), target, intent(inout) :: stream_mgr
        type (MPAS_pool_type), pointer :: configs
        type (MPAS_pool_type), pointer :: structs
        type (MPAS_clock_type), pointer :: clock
        type (dm_info), intent(in) :: dminfo

        character(len=StrKIND), pointer :: config_velocity_relaxation
        real(RKIND) :: local_area_sum
        integer, pointer :: nVertLevels


        call mpas_pool_get_subpool(structs, 'mesh', mesh)
        call mpas_pool_get_subpool(structs, 'state', state)
        call mpas_pool_get_subpool(structs, 'diag', diag)

        call mpas_pool_get_array(mesh, 'areaCell', areaCell)
        call mpas_pool_get_dimension(mesh, 'nCellsSolve', nCellsSolve)

        call mpas_pool_get_config(configs, 'config_velocity_relaxation', config_velocity_relaxation)

        if (config_velocity_relaxation == 'mean_init') then
            !Force the horizontal mean velocity to the same as in the initial condition through a relaxation term: (U_init-U_current)/time_scale

            !set global flag
            lmean_init = .true.

            !Set time_scale module variable
            call mpas_pool_get_config(configs, 'config_velocity_relaxation_time_scale', time_scale)

            !precompute total horizontal cell area
            local_area_sum = sum(areaCell(1:nCellsSolve))
            call mpas_dmpar_sum_real(dminfo, local_area_sum, total_cell_area)

            call mpas_pool_get_array(mesh, 'u_init', u_init)
            call mpas_pool_get_array(mesh, 'v_init', v_init)

            call mpas_pool_get_dimension(mesh, 'nVertLevels', nVertLevels)

            allocate(mean_u(nVertLevels))
            allocate(mean_v(nVertLevels))

        endif

    end subroutine velocity_relaxation_setup


end module

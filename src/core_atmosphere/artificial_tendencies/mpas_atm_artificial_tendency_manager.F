! Copyright (c) 2016,  Los Alamos National Security, LLC (LANS)
! and the University Corporation for Atmospheric Research (UCAR).
!
! Unless noted otherwise source code is licensed under the BSD license.
! Additional copyright and license information can be found in the LICENSE file
! distributed with this code, or at http://mpas-dev.github.com/license.html
!
module mpas_atm_artificial_tendency_manager

    private

    public :: mpas_atm_artificial_tend_setup, &
              mpas_atm_artificial_tend_compute, &
              mpas_atm_artificial_tend_cleanup

    contains


    !-----------------------------------------------------------------------
    !  routine MPAS_atm_artificial_tend_setup
    !
    !> \brief Initialize the artificial tendency manager and all artificial tendencies
    !> \author Felipe A. V. de Bragança Alves
    !> \date   21 August 2024
    !> \details
    !>  Initialize the artificial tendency manager and all artificial tendencies
    !
    !-----------------------------------------------------------------------
    subroutine mpas_atm_artificial_tend_setup(stream_mgr, configs, structs, clock, dminfo)

        use mpas_derived_types, only : MPAS_streamManager_type, MPAS_pool_type, MPAS_clock_type, dm_info
        use mpas_atm_vel_relax_art_tend, only: velocity_relaxation_setup

        implicit none

        type (MPAS_streamManager_type), target, intent(inout) :: stream_mgr
        type (MPAS_pool_type), pointer :: configs
        type (MPAS_pool_type), pointer :: structs
        type (MPAS_clock_type), pointer :: clock
        type (dm_info), intent(in) :: dminfo

        call velocity_relaxation_setup(stream_mgr, configs, structs, clock, dminfo)


    end subroutine mpas_atm_artificial_tend_setup

    !-----------------------------------------------------------------------
    !  routine MPAS_atm_artificial_tend_compute
    !
    !> \brief Compute artificial tendencies before they are added to dyn_tend
    !> \author Felipe A. V. de Bragança Alves
    !> \date   21 August 2024
    !> \details
    !>  MPAS_atm_artificial_tend_compute.
    !
    !-----------------------------------------------------------------------
    subroutine mpas_atm_artificial_tend_compute()

        implicit none

    end subroutine mpas_atm_artificial_tend_compute


    !-----------------------------------------------------------------------
    !  routine MPAS_atm_artificial_tend_cleanup
    !
    !> \brief Finalizes artificial tendency manager and all artificial tendencies.
    !> \author Felipe A. V. de Bragança Alves
    !> \date   21 August 2024
    !> \details
    !>  Finalizes artificial tendency manager and all artificial tendencies.
    !
    !-----------------------------------------------------------------------
    subroutine mpas_atm_artificial_tend_cleanup()

        implicit none

    end subroutine mpas_atm_artificial_tend_cleanup

end module mpas_atm_artificial_tendency_manager

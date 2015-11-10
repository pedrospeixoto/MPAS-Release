!***********************************************************************
!
!  mpas_consistent
!
!> \brief   MPAS  module with routines for consistent scheme
!> \author  Pedro Peixoto
!> \date    Oct/15
!> \details
!> This module provides routines for performing the consistent scheme methods of Peixoto JCP 2015
!
!-----------------------------------------------------------------------
module mpas_consistent

  use mpas_derived_types
  use mpas_pool_routines
  use mpas_configure
  use mpas_constants
  use mpas_vector_operations

  implicit none

  private

  public :: mpas_init_barycentric_coefs, &
            mpas_initialize_vectors_general, &
            mpas_perot_reconstruct

  interface mpas_perot_reconstruct
     module procedure mpas_reconstruct_1d
     module procedure mpas_reconstruct_2d
  end interface

  contains

!***********************************************************************
!
!  routine mpas_reconstruct_2d
!
!> \brief   2d MPAS Vector reconstruction routine
!> \author  Xylar Asay-Davis, Todd Ringler
!> \date    03/28/13
!> \details
!>  Purpose: reconstruct vector field at cell centers based on radial basis functions
!>  Input: grid meta data and vector component data residing at cell edges
!>  Output: reconstructed vector field (measured in X,Y,Z) located at cell centers
!-----------------------------------------------------------------------
  subroutine mpas_reconstruct_2d(meshPool, u, uReconstructX, uReconstructY, uReconstructZ, uReconstructZonal, uReconstructMeridional)!{{{

    implicit none

    type (mpas_pool_type), intent(in) :: meshPool !< Input: Mesh information
    real (kind=RKIND), dimension(:,:), intent(in) :: u !< Input: Velocity field on edges
    real (kind=RKIND), dimension(:,:), intent(out) :: uReconstructX !< Output: X Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:,:), intent(out) :: uReconstructY !< Output: Y Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:,:), intent(out) :: uReconstructZ !< Output: Z Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:,:), intent(out) :: uReconstructZonal !< Output: Zonal Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:,:), intent(out) :: uReconstructMeridional !< Output: Meridional Component of velocity reconstructed to cell centers

    !   temporary arrays needed in the compute procedure
    integer, pointer :: nCellsSolve
    integer, dimension(:,:), pointer :: edgesOnCell
    integer, dimension(:), pointer :: nEdgesOnCell
    integer :: iCell,iEdge, i
    real(kind=RKIND), dimension(:), pointer :: latCell, lonCell

    real (kind=RKIND), dimension(:,:,:), pointer :: coeffs_reconstruct

    logical, pointer :: on_a_sphere

    real (kind=RKIND) :: clat, slat, clon, slon


    ! stored arrays used during compute procedure
    call mpas_pool_get_array(meshPool, 'coeffs_reconstruct', coeffs_reconstruct)

    ! temporary variables
    call mpas_pool_get_array(meshPool, 'nEdgesOnCell', nEdgesOnCell)
    call mpas_pool_get_array(meshPool, 'edgesOnCell', edgesOnCell)
    call mpas_pool_get_dimension(meshPool, 'nCellsSolve', nCellsSolve)

    call mpas_pool_get_array(meshPool, 'latCell', latCell)
    call mpas_pool_get_array(meshPool, 'lonCell', lonCell)

    call mpas_pool_get_config(meshPool, 'on_a_sphere', on_a_sphere)

    ! init the intent(out)
    uReconstructX = 0.0
    uReconstructY = 0.0
    uReconstructZ = 0.0

    ! loop over cell centers
    do iCell = 1, nCellsSolve
      ! a more efficient reconstruction where rbf_values*matrix_reconstruct has been precomputed
      ! in coeffs_reconstruct
      do i=1,nEdgesOnCell(iCell)
        iEdge = edgesOnCell(i,iCell)
        uReconstructX(:,iCell) = uReconstructX(:,iCell) &
          + coeffs_reconstruct(1,i,iCell) * u(:,iEdge)
        uReconstructY(:,iCell) = uReconstructY(:,iCell) &
          + coeffs_reconstruct(2,i,iCell) * u(:,iEdge)
        uReconstructZ(:,iCell) = uReconstructZ(:,iCell) &
          + coeffs_reconstruct(3,i,iCell) * u(:,iEdge)

      enddo
    enddo   ! iCell

    if (on_a_sphere) then
      do iCell = 1, nCellsSolve
        clat = cos(latCell(iCell))
        slat = sin(latCell(iCell))
        clon = cos(lonCell(iCell))
        slon = sin(lonCell(iCell))
        uReconstructZonal(:,iCell) = -uReconstructX(:,iCell)*slon + uReconstructY(:,iCell)*clon
        uReconstructMeridional(:,iCell) = -(uReconstructX(:,iCell)*clon &
          + uReconstructY(:,iCell)*slon)*slat &
          + uReconstructZ(:,iCell)*clat
      end do
    else
      uReconstructZonal = uReconstructX
      uReconstructMeridional = uReconstructY
    end if

  end subroutine mpas_reconstruct_2d!}}}


!***********************************************************************
!
!  routine mpas_reconstruct_1d
!
!> \brief   1d MPAS Vector reconstruction routine
!> \author  Xylar Asay-Davis, Todd Ringler, Matt Hoffman
!> \date    03/28/13
!> \details
!>  Purpose: reconstruct vector field at cell centers based on radial basis functions
!>  Input: grid meta data and vector component data residing at cell edges
!>  Output: reconstructed vector field (measured in X,Y,Z) located at cell centers
!-----------------------------------------------------------------------
  subroutine mpas_reconstruct_1d(meshPool, u, uReconstructX, uReconstructY, uReconstructZ, uReconstructZonal, uReconstructMeridional)!{{{

    implicit none

    type (mpas_pool_type), intent(in) :: meshPool !< Input: Mesh information
    real (kind=RKIND), dimension(:), intent(in) :: u !< Input: Velocity field on edges
    real (kind=RKIND), dimension(:), intent(out) :: uReconstructX !< Output: X Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:), intent(out) :: uReconstructY !< Output: Y Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:), intent(out) :: uReconstructZ !< Output: Z Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:), intent(out) :: uReconstructZonal !< Output: Zonal Component of velocity reconstructed to cell centers
    real (kind=RKIND), dimension(:), intent(out) :: uReconstructMeridional !< Output: Meridional Component of velocity reconstructed to cell centers

    !   temporary arrays needed in the compute procedure
    integer, pointer :: nCellsSolve
    integer, dimension(:,:), pointer :: edgesOnCell
    integer, dimension(:), pointer :: nEdgesOnCell
    integer :: iCell,iEdge, i
    real(kind=RKIND), dimension(:), pointer :: latCell, lonCell

    real (kind=RKIND), dimension(:,:,:), pointer :: coeffs_reconstruct

    logical, pointer :: on_a_sphere

    real (kind=RKIND) :: clat, slat, clon, slon


    ! stored arrays used during compute procedure
    call mpas_pool_get_array(meshPool, 'coeffs_reconstruct', coeffs_reconstruct)

    ! temporary variables
    call mpas_pool_get_array(meshPool, 'nEdgesOnCell', nEdgesOnCell)
    call mpas_pool_get_array(meshPool, 'edgesOnCell', edgesOnCell)
    call mpas_pool_get_dimension(meshPool, 'nCellsSolve', nCellsSolve)

    call mpas_pool_get_array(meshPool, 'latCell', latCell)
    call mpas_pool_get_array(meshPool, 'lonCell', lonCell)

    call mpas_pool_get_config(meshPool, 'on_a_sphere', on_a_sphere)

    ! init the intent(out)
    uReconstructX = 0.0
    uReconstructY = 0.0
    uReconstructZ = 0.0

    ! loop over cell centers
    do iCell = 1, nCellsSolve
      ! a more efficient reconstruction where rbf_values*matrix_reconstruct has been precomputed
      ! in coeffs_reconstruct
      do i=1,nEdgesOnCell(iCell)
        iEdge = edgesOnCell(i,iCell)
        uReconstructX(iCell) = uReconstructX(iCell) &
          + coeffs_reconstruct(1,i,iCell) * u(iEdge)
        uReconstructY(iCell) = uReconstructY(iCell) &
          + coeffs_reconstruct(2,i,iCell) * u(iEdge)
        uReconstructZ(iCell) = uReconstructZ(iCell) &
          + coeffs_reconstruct(3,i,iCell) * u(iEdge)

      enddo
    enddo   ! iCell

    if (on_a_sphere) then
      do iCell = 1, nCellsSolve
        clat = cos(latCell(iCell))
        slat = sin(latCell(iCell))
        clon = cos(lonCell(iCell))
        slon = sin(lonCell(iCell))
        uReconstructZonal(iCell) = -uReconstructX(iCell)*slon + uReconstructY(iCell)*clon
        uReconstructMeridional(iCell) = -(uReconstructX(iCell)*clon &
          + uReconstructY(iCell)*slon)*slat &
          + uReconstructZ(iCell)*clat
      end do
    else
      uReconstructZonal = uReconstructX
      uReconstructMeridional = uReconstructY
    end if

  end subroutine mpas_reconstruct_1d!}}}

!***********************************************************************
!
!  routine mpas_initialize_vectors_general
!
!> \brief   MPAS initialization routine for vector
!> \author  Pedro Peixoto
!> \date    Nov/2015
!> \details
!> This routine computes geometric fields that will be potentially useful for calling
!> the interpolation routines. It is general in the sense that it allows correct calculation when
!> the grid is HCm (velocities given at the midpoint of Voronoi edges)
!>
!> Input: the mesh
!> Output:
!>      edgeNormalVectors - the unit vector normal to the edge and tangent to the sphere
!>      cellTangentPlane - 2 orthogonal unit vectors in the tangent plane of each cell
!>                         The first unit vector is chosen to point toward the center of the first
!>                         edge on the cell.
!>      localVerticalUnitVectors - the unit normal vector of the tangent plane at the center
!>                         of each cell
!-----------------------------------------------------------------------
  subroutine mpas_initialize_vectors_general(meshPool)!{{{

    implicit none

    type (mpas_pool_type), intent(in) :: meshPool  !< Input: Mesh information

    integer :: iEdge, iCell, cell1, cell2
    integer, pointer :: nCells, nEdges
    integer, dimension(:,:), pointer :: cellsOnEdge, verticesOnEdge, edgesOnCell
    real(kind=RKIND), dimension(:), pointer :: xCell, yCell, zCell, xEdge, yEdge, zEdge
    real(kind=RKIND), dimension(:,:), pointer :: localVerticalUnitVectors, edgeNormalVectors
    real(kind=RKIND), dimension(:,:,:), pointer :: cellTangentPlane
    real(kind=RKIND), dimension(3) :: xHatPlane, yHatPlane, rHat
    real(kind=RKIND) :: normalDotRHat
    logical, pointer :: on_a_sphere

    call mpas_pool_get_config(meshPool, 'on_a_sphere', on_a_sphere)

    call mpas_pool_get_array(meshPool, 'xCell', xCell)
    call mpas_pool_get_array(meshPool, 'yCell', yCell)
    call mpas_pool_get_array(meshPool, 'zCell', zCell)
    call mpas_pool_get_array(meshPool, 'xEdge', xEdge)
    call mpas_pool_get_array(meshPool, 'yEdge', yEdge)
    call mpas_pool_get_array(meshPool, 'zEdge', zEdge)
    call mpas_pool_get_array(meshPool, 'cellsOnEdge', cellsOnEdge)
    call mpas_pool_get_array(meshPool, 'verticesOnEdge', verticesOnEdge)
    call mpas_pool_get_array(meshPool, 'edgesOnCell', edgesOnCell)

    call mpas_pool_get_dimension(meshPool, 'nCells', nCells)
    call mpas_pool_get_dimension(meshPool, 'nEdges', nEdges)

    call mpas_pool_get_array(meshPool, 'localVerticalUnitVectors', localVerticalUnitVectors)
    call mpas_pool_get_array(meshPool, 'edgeNormalVectors', edgeNormalVectors)
    call mpas_pool_get_array(meshPool, 'cellTangentPlane', cellTangentPlane)

    ! init arrays
    edgeNormalVectors = 0
    localVerticalUnitVectors = 0

    ! loop over all cells to be solved on this block
    do iCell = 1, nCells
      if (on_a_sphere) then
        localVerticalUnitVectors(1,iCell) = xCell(iCell)
        localVerticalUnitVectors(2,iCell) = yCell(iCell)
        localVerticalUnitVectors(3,iCell) = zCell(iCell)
        call mpas_unit_vec_in_r3(localVerticalUnitVectors(:,iCell))
      else ! on a plane
        localVerticalUnitVectors(:,iCell) = (/ 0., 0., 1. /)
      end if
    end do

    ! Initialize normal unit vectors at each edge
    ! These vectors point from cell to cell.
    ! At boundaries, one cell does not exist, so it points from cell to edge.
    do iEdge = 1,nEdges
      cell1 = cellsOnEdge(1,iEdge)
      cell2 = cellsOnEdge(2,iEdge)

      if (cell1 == nCells+1) then ! this is a boundary edge
        ! the normal points from the cell location to the edge location
        edgeNormalVectors(1,iEdge) = xEdge(iEdge) - xCell(cell2)
        edgeNormalVectors(2,iEdge) = yEdge(iEdge) - yCell(cell2)
        edgeNormalVectors(3,iEdge) = zEdge(iEdge) - zCell(cell2)

      elseif (cell2 == nCells+1) then ! this is a boundary edge
        ! the normal points from the cell location to the edge location
        edgeNormalVectors(1,iEdge) = xEdge(iEdge) - xCell(cell1)
        edgeNormalVectors(2,iEdge) = yEdge(iEdge) - yCell(cell1)
        edgeNormalVectors(3,iEdge) = zEdge(iEdge) - zCell(cell1)

      else ! this is not a boundary cell
        ! the normal points from the cell 1 to cell2
        ! mrp problem: on periodic domains, vectors on edges of domain point the wrong way.
        edgeNormalVectors(1,iEdge) = xCell(cell2) - xCell(cell1)
        edgeNormalVectors(2,iEdge) = yCell(cell2) - yCell(cell1)
        edgeNormalVectors(3,iEdge) = zCell(cell2) - zCell(cell1)

      endif
      call mpas_unit_vec_in_r3(edgeNormalVectors(:,iEdge))
    end do

    do iCell=1,nCells
      iEdge = edgesOnCell(1,iCell)
      ! xHat and yHat are a local basis in the plane of the horizontal cell
      ! we arbitrarily choose xHat to point toward the first edge
      rHat = localVerticalUnitVectors(:,iCell)
      normalDotRHat = sum(edgeNormalVectors(:,iEdge)*rHat)
      xHatPlane = edgeNormalVectors(:,iEdge) - normalDotRHat*rHat
      call mpas_unit_vec_in_r3(xHatPlane)

      call mpas_cross_product_in_r3(rHat, xHatPlane, yHatPlane)
      call mpas_unit_vec_in_r3(yHatPlane) ! just to be sure...
      cellTangentPlane(:,1,iCell) = xHatPlane
      cellTangentPlane(:,2,iCell) = yHatPlane
    end do

  end subroutine mpas_initialize_vectors_general!}}}

!***********************************************************************
!
!  routine mpas_init_barycentric_coefs
!
!> \brief   MPAS Calculate barycentric coordinate coefficients for
!>           scalar interpolation to edge midpoints
!> \author  Pedro Peixoto
!> \date    Oct 2015
!> \details
!>  Purpose: pre-compute coefficients for linear interpolation
!>  Input: grid meta data
!>  Output: grid % coeffs_bary_interp - coefficients
!-----------------------------------------------------------------------
  subroutine mpas_init_barycentric_coefs(mesh)!{{{

    implicit none

    type (mpas_pool_type), intent(in) :: &
         mesh         !< Input: Mesh information

    ! temporary arrays needed in the (to be constructed) init procedure
    integer :: i, iCell, iCell1, iCell2, iEdge, iVertex, iVertex1, iVertex2
    integer, pointer:: nEdges
    real (kind=RKIND), dimension(:), pointer :: xCell, yCell, zCell
    real (kind=RKIND), dimension(:), pointer :: xEdge, yEdge, zEdge
    real (kind=RKIND), dimension(:), pointer :: xVertex, yVertex, zVertex
    integer, dimension(:,:), pointer :: cellsOnEdge, cellsOnVertex, verticesOnEdge, edgesOnCell, edgesOnEdge, edgesOnVertex
    integer, dimension(:), pointer :: indexToEdgeID
    real (kind=RKIND) :: xTrEdgeMidpoint, yTrEdgeMidpoint, zTrEdgeMidpoint, ptNorm, distTrEdgeMidToVertex1, distTrEdgeMidToVertex2
	logical, pointer :: on_a_sphere
	real (kind=RKIND), pointer :: sphere_radius
	real (kind=RKIND), dimension(:), pointer :: dvEdge, dcEdge
	real (kind=RKIND), dimension(1:3) :: p1, p2, p3, p, bary_coord

    !========================================================
    ! temporary variables needed for init procedure
    !========================================================
    call mpas_pool_get_dimension(mesh, 'nEdges', nEdges)
    call mpas_pool_get_array(mesh, 'xCell', xCell)
    call mpas_pool_get_array(mesh, 'yCell', yCell)
    call mpas_pool_get_array(mesh, 'zCell', zCell)
    call mpas_pool_get_array(mesh, 'xEdge', xEdge)
    call mpas_pool_get_array(mesh, 'yEdge', yEdge)
    call mpas_pool_get_array(mesh, 'zEdge', zEdge)
    call mpas_pool_get_array(mesh, 'xVertex', xVertex)
    call mpas_pool_get_array(mesh, 'yVertex', yVertex)
    call mpas_pool_get_array(mesh, 'zVertex', zVertex)
    call mpas_pool_get_array(mesh, 'cellsOnEdge', cellsOnEdge)
    call mpas_pool_get_array(mesh, 'cellsOnVertex', cellsOnVertex)
    call mpas_pool_get_array(mesh, 'verticesOnEdge', verticesOnEdge)
	call mpas_pool_get_array(mesh, 'dcEdge', dcEdge)
	call mpas_pool_get_array(mesh, 'dvEdge', dvEdge)
    call mpas_pool_get_config(mesh, 'on_a_sphere', on_a_sphere)
    call mpas_pool_get_config(mesh, 'sphere_radius', sphere_radius)
	call mpas_pool_get_array(mesh, 'indexToEdgeID', indexToEdgeID)

    !do iEdge = 1, nEdges
	!	print*, iEdge, indexToEdgeID(iEdge), verticesOnEdge(:, iEdge)
	!end do
   do iEdge = 1, nEdges
       iCell1 = cellsOnEdge(1,iEdge)
       iCell2 = cellsOnEdge(2,iEdge)
       iVertex1 = verticesOnEdge(1,iEdge)
       iVertex2 = verticesOnEdge(2,iEdge)
		!print*, iEdge, iCell1, iCell2, iVertex1, iVertex2

		!Calculate midpoint of the triangle edge (the one that intersects the Voronoi cell edges
		! There is no need to divide by 2 (average) because it is going to be nromalized anyway
		xTrEdgeMidpoint=xCell(iCell1)+xCell(iCell2)
		yTrEdgeMidpoint=yCell(iCell1)+yCell(iCell2)
		zTrEdgeMidpoint=zCell(iCell1)+zCell(iCell2)
	    ptNorm= xTrEdgeMidpoint**2+yTrEdgeMidpoint**2+ zTrEdgeMidpoint**2
		ptNorm=sqrt(ptNorm)
		xTrEdgeMidpoint=sphere_radius*xTrEdgeMidpoint/ptNorm
		yTrEdgeMidpoint=sphere_radius*yTrEdgeMidpoint/ptNorm
		zTrEdgeMidpoint=sphere_radius*zTrEdgeMidpoint/ptNorm
		!print*, xTrEdgeMidpoint, yTrEdgeMidpoint, zTrEdgeMidpoint
		!print*, xEdge(iEdge), yEdge(iEdge), zEdge(iEdge)
		distTrEdgeMidToVertex1=arc_length(xTrEdgeMidpoint, yTrEdgeMidpoint, zTrEdgeMidpoint, &
			xVertex(iVertex1),yVertex(iVertex1), zVertex(iVertex1))
	    distTrEdgeMidToVertex2=arc_length(xTrEdgeMidpoint, yTrEdgeMidpoint, zTrEdgeMidpoint, &
			xVertex(iVertex2),yVertex(iVertex2), zVertex(iVertex2))
		!print*, distTrEdgeMidToVertex1, distTrEdgeMidToVertex2, distTrEdgeMidToVertex1+distTrEdgeMidToVertex2, &
		!	dvEdge(iEdge), dcEdge(iEdge)
        !Case 1: TrEdgeMid closer to v1 ==> Edge midpoint belongs to triangle v2
		!  v1----------TrEdgeMid--------Mid-----------------------------v2
		!Case 2: TrEdgeMid closer to v2 ==> Edge midpoint belongs to triangle v1
		!  v1---------------------------Mid-----TrEdgeMid---------------v2
	    if(distTrEdgeMidToVertex1<distTrEdgeMidToVertex2)then
	    	iVertex=iVertex2
	    else
	    	iVertex=iVertex1
	    end if
	    !Edge Point to have scalars interpolated to
		p(1)=xEdge(iEdge)
		p(2)=yEdge(iEdge)
		p(3)=zEdge(iEdge)
		!Vertices of the triangle (cell nodes) tha contain the Edge Midpoint
		p1(1)=xCell(cellsOnVertex(1,iVertex))
		p1(2)=yCell(cellsOnVertex(1,iVertex))
		p1(3)=zCell(cellsOnVertex(1,iVertex))
		p2(1)=xCell(cellsOnVertex(2,iVertex))
		p2(2)=yCell(cellsOnVertex(2,iVertex))
		p2(3)=zCell(cellsOnVertex(2,iVertex))
		p3(1)=xCell(cellsOnVertex(3,iVertex))
		p3(2)=yCell(cellsOnVertex(3,iVertex))
		p3(3)=zCell(cellsOnVertex(3,iVertex))
		bary_coord=bar_coord(p, p1, p2, p3)
	    !print*, iEdge, indexToEdgeID(iEdge), iVertex
	    !print*, cellsOnVertex(:,iVertex)
	    !print*, bary_coord(:)
	    !print*
    end do

  end subroutine mpas_init_barycentric_coefs!}}}


   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   ! FUNCTION ARC_LENGTH
   !
   ! Returns the length of the great circle arc from A=(ax, ay, az) to
   !    B=(bx, by, bz). It is assumed that both A and B lie on the surface of the
   !    same sphere centered at the origin.
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   real (kind=RKIND) function arc_length(ax, ay, az, bx, by, bz)

      implicit none

      real (kind=RKIND), intent(in) :: ax, ay, az, bx, by, bz

      real (kind=RKIND) :: r, c
      real (kind=RKIND) :: cx, cy, cz

      cx = bx - ax
      cy = by - ay
      cz = bz - az

!      r = ax*ax + ay*ay + az*az
!      c = cx*cx + cy*cy + cz*cz
!
!      arc_length = sqrt(r) * acos(1.0 - c/(2.0*r))

      r = sqrt(ax*ax + ay*ay + az*az)
      c = sqrt(cx*cx + cy*cy + cz*cz)
!      arc_length = sqrt(r) * 2.0 * asin(c/(2.0*r))
      arc_length = r * 2.0 * asin(c/(2.0*r))

   end function arc_length


 function bar_coord(p, p1, p2, p3)
    !----------------------------------------------------------
    ! BARYCENTRIC COORDINATES given 3 points on the sphere
    !
    ! Given a point in cartesian coords and 3 points (p1, p2, p3)
    ! that form a triangle, and are given in the counter-clockwise
    ! ordering, returns the barycentric coords
    !   of the point.
    !
    !   The barycentric coordinates refer to the planar triangle
    !--------------------------------------------------------------
    !Point inside triangle tr and triangle vertices
    real (RKIND), intent(in), dimension(1:3) :: p
    real (RKIND), intent(in), dimension(1:3) :: p1
    real (RKIND), intent(in), dimension(1:3) :: p2
    real (RKIND), intent(in), dimension(1:3) :: p3

    !Barycentric coordinates
    real (RKIND):: bar_coord(1:3)
    real (RKIND):: b(1:3)

    ! 2* Area of the triangle
    real (RKIND):: area

    b(1)=(det(p,p2,p3))
    b(2)=(det(p,p3,p1))
    b(3)=(det(p,p1,p2))
    area=sum(b(1:3)) !abs(det(p1,p2,p3))

    bar_coord=b/area

    return
  end function bar_coord

   function det(p1, p2, p3)
    !-----------------------------------------------------------------------
    !  DET
    !
    !  Returns the determinant of the matrix made of the 3 points p1, p2, p3
    !   as columns
    !-----------------------------------------------------------------------
    real (RKIND), intent(in) :: p1(1:3)
    real (RKIND), intent(in) :: p2(1:3)
    real (RKIND), intent(in) :: p3(1:3)
    real (RKIND):: det

    det=dot_product(cross_product(p1,p2),p3)

    return
  end function det

  function cross_product(a,b)
    !-----------------------------------------------------------------------
    !  CROSS_PRODUCT
    !
    !  Returns the right-handed vector cross product of two 3-vectors:
    !				C = A x B.
    !-----------------------------------------------------------------------
    implicit none

    real (RKIND), intent(in):: a(1:3)
    real (RKIND), intent(in):: b(1:3)
    real (RKIND):: cross_product(1:3)

    cross_product(1) = a(2)*b(3) - a(3)*b(2)
    cross_product(2) = a(3)*b(1) - a(1)*b(3)
    cross_product(3) = a(1)*b(2) - a(2)*b(1)

    return
  end function cross_product

end module mpas_consistent


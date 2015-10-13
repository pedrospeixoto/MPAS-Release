! Copyright (c) 2013,  Los Alamos National Security, LLC (LANS)
! and the University Corporation for Atmospheric Research (UCAR).
!
! Unless noted otherwise source code is licensed under the BSD license.
! Additional copyright and license information can be found in the LICENSE file
! distributed with this code, or at http://mpas-dev.github.com/license.html
!
!***********************************************************************
!
!  mpas_barycentric_interpolation
!
!> \brief   MPAS Barycentric interpolation  module
!> \author  Pedro Peixoto
!> \date    Oct/15
!> \details
!> This module provides routines for performing linear barycentric interpolations
!
!-----------------------------------------------------------------------
module mpas_barycentric_interpolation

  use mpas_derived_types
  use mpas_pool_routines
  use mpas_configure
  use mpas_constants


  implicit none

  public :: mpas_init_barycentric_coefs


  contains

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
	    print*, iEdge, indexToEdgeID(iEdge), iVertex
	    print*, cellsOnVertex(:,iVertex)
	    print*, bary_coord(:)
	    print*
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

end module mpas_barycentric_interpolation


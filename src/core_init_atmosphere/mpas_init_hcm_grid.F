	
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       mpas_init_hcm_grid
!       
!       > \brief   Initialize grid for HCm positioning (See Peixoto JCP 2015)
!       > \author  Pedro S. Peixoto
!       > \date    10/28/15
!       > \details
!       > Overwrites the edge position to be relative to
!       > the midpoint of the Voronoi cell edges instead of the Triangle edges.
!       
!-----------------------------------------------------------------------
	module mpas_init_hcm_grid

	use mpas_derived_types
	use mpas_pool_routines
	use mpas_configure
	use mpas_constants

	implicit none
	private
  save
	public :: convert_grid_to_hcm

	contains

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       convert_grid_to_hcm
!
!       > \brief   convert grid to hcm staggering - See Peixoto 2015
!       > \author  Pedro S. Peixoto
!       > \date    10/28/15
!       > \details
!       > Overwrites the edge position to be relative to
!       > the midpoint of the Voronoi cell edges instead of the Triangle edges.
!
!-----------------------------------------------------------------------
	subroutine convert_grid_to_hcm(meshPool)

	implicit none
  	type (mpas_pool_type), intent(in) :: meshPool

	integer, pointer :: nCells, nVertices, nEdges

	real(kind=RKIND) :: pii, omega

	integer :: i

	real (kind=RKIND), dimension(:), pointer :: xCell, yCell, zCell, latCell, lonCell
	real (kind=RKIND), dimension(:), pointer :: xVertex, yVertex, zVertex, latVertex, lonVertex
	real (kind=RKIND), dimension(:), pointer :: xEdge, yEdge, zEdge, latEdge, lonEdge, angleEdge, fEdge, fVertex
	integer, dimension(:,:), pointer :: verticesOnEdge

	integer, dimension(2) :: onEdgeStart                   
	integer, dimension(2) :: onEdgeCount

	real (kind=RKIND) :: original_latitude_radians, original_longitude_radians, new_latitude_radians, new_longitude_radians
	real (kind=RKIND) :: thetaLat, thetaLon, thetaBirdsEye
	real (kind=RKIND) :: x0LongitudeAtEquator, y0LongitudeAtEquator, z0LongitudeAtEquator
	real (kind=RKIND) :: uCrossProduct, vCrossProduct, wCrossProduct
	real (kind=RKIND) :: xNew, yNew, zNew

	real (kind=RKIND) :: v
	real (kind=RKIND) :: ax, ay, az
	real (kind=RKIND) :: bx, by, bz
	real (kind=RKIND) :: cx, cy, cz

	character (len=3) :: HCm="HCm"

	pii = 2.*asin(1.0)
  	omega = 2.0*pii / 86400.0

	call mpas_pool_get_dimension(meshPool, 'nCells', nCells)
	call mpas_pool_get_dimension(meshPool, 'nEdges', nEdges)
	call mpas_pool_get_dimension(meshPool, 'nVertices', nVertices)

	call mpas_pool_get_array(meshPool, 'xCell', xCell)
	call mpas_pool_get_array(meshPool, 'yCell', yCell)
	call mpas_pool_get_array(meshPool, 'zCell', zCell)
	call mpas_pool_get_array(meshPool, 'latCell', latCell)
	call mpas_pool_get_array(meshPool, 'lonCell', lonCell)

	call mpas_pool_get_array(meshPool, 'xVertex', xVertex)
	call mpas_pool_get_array(meshPool, 'yVertex', yVertex)
	call mpas_pool_get_array(meshPool, 'zVertex', zVertex)
	call mpas_pool_get_array(meshPool, 'latVertex', latVertex)
	call mpas_pool_get_array(meshPool, 'lonVertex', lonVertex)
	call mpas_pool_get_array(meshPool, 'fVertex', fVertex)

	call mpas_pool_get_array(meshPool, 'xEdge', xEdge)
	call mpas_pool_get_array(meshPool, 'yEdge', yEdge)
	call mpas_pool_get_array(meshPool, 'zEdge', zEdge)
	call mpas_pool_get_array(meshPool, 'latEdge', latEdge)
	call mpas_pool_get_array(meshPool, 'lonEdge', lonEdge)
	call mpas_pool_get_array(meshPool, 'angleEdge', angleEdge)
	call mpas_pool_get_array(meshPool, 'fEdge', fEdge)

	call mpas_pool_get_array(meshPool, 'verticesOnEdge', verticesOnEdge)

	data onEdgeStart /1, 1/
	onEdgeCount(1) = 2
	onEdgeCount(2) = nEdges

	write(0,*) " Converting grid to HCm staggering" ! (config_hcm_staggering=", config_hcm_staggering, ")"
	
	do i=1,nEdges

!       First vertex coordinates
	   ax = xVertex(verticesOnEdge(1,i))
	   ay = yVertex(verticesOnEdge(1,i))
	   az = zVertex(verticesOnEdge(1,i))

!       Second vertex coordinates
	   cx = xVertex(verticesOnEdge(2,i))
	   cy = yVertex(verticesOnEdge(2,i))
	   cz = zVertex(verticesOnEdge(2,i))

!       Voronoi edge midpoint - cartesian line
!       temporary use bx, by, bz
	   bx = (ax+cx)/2.0
	   by = (ay+cy)/2.0
	   bz = (az+cz)/2.0

!       Normalize to sphere
	   v = sqrt(bx**2.0 + by**2.0 + bz**2.0)
	   xEdge(i) = bx / v
	   yEdge(i) = by / v
	   zEdge(i) = bz / v

!       Convert to lat lon
	   call convert_xl(xEdge(i), yEdge(i), zEdge(i), latEdge(i), lonEdge(i))

!       compute new angle edge
	   bx = -cos(lonEdge(i))*sin(latEdge(i)) + ax
	   by = -sin(lonEdge(i))*sin(latEdge(i)) + ay
	   bz =  cos(latEdge(i))                 + az
	   
	   v = sqrt(bx**2.0 + by**2.0 + bz**2.0)
	   bx = bx / v
	   by = by / v
	   bz = bz / v

!       Compute angle between AB and AC lines
	   angleEdge(i) = sphere_angle(ax, ay, az, bx, by, bz, cx, cy, cz)

	   fEdge(i)=2*omega*sin(latEdge(i))

	end do

	end subroutine convert_grid_to_hcm


	!Convert degree to radians
	real function degreesToRadians(degAngle)

	implicit none

	real(kind=RKIND) :: degAngle

		degreesToRadians = degAngle * 2 * pii / 360

	end function degreesToRadians


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       SUBROUTINE CONVERT_XL
!       
!       Convert (x, y, z) to a (lat, lon) location on a sphere with
!       radius sqrt(x^2 + y^2 + z^2).
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	subroutine convert_xl(x, y, z, lat, lon)
	
	implicit none
	
	real (kind=RKIND), intent(in) :: x, y, z
	real (kind=RKIND), intent(out) :: lat, lon
	
	real (kind=RKIND) :: dl, clat
	real (kind=RKIND) :: eps
	parameter (eps=1.e-10)
	
	dl = sqrt(x*x + y*y + z*z)
	lat = asin(z/dl)
	
!       check for being close to either pole
	
	if (abs(x) > eps) then
	   
	   if (abs(y) > eps) then
	      
	      lon = atan(abs(y/x))
	      
	      if ((x <= 0.) .and. (y >= 0.)) then
		 lon = pii-lon
	      else if ((x <= 0.) .and. (y < 0.)) then
		 lon = lon+pii
	      else if ((x >= 0.) .and. (y <= 0.)) then
		 lon = 2*pii-lon
	      end if
	      
	   else			! we're either on longitude 0 or 180
	      
	      if (x > 0) then
		 lon = 0.
	      else
		 lon = pii
	      end if
	      
	   end if
	   
	else if (abs(y) > eps) then
	   
	   if (y > 0) then
	      lon = pii/2.
	   else
	      lon = 3.*pii/2.
	   end if
	   
	else			! we are at a pole
	   
	   lon = 0.
	   
	end if

	end subroutine convert_xl


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       SUBROUTINE CONVERT_LX
!       
!       Convert (lat,lon) to an (x, y, z) location on a sphere with specified radius.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	subroutine convert_lx(x, y, z, radius, lat, lon)

	implicit none

	real (kind=RKIND), intent(in) :: radius, lat, lon
	real (kind=RKIND), intent(out) :: x, y, z

	z = radius * sin(lat)
	x = radius * cos(lon) * cos(lat)
	y = radius * sin(lon) * cos(lat)

	end subroutine convert_lx


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       FUNCTION SPHERE_ANGLE
!       
!       Computes the angle between arcs AB and AC, given points A, B, and C
!       Equation numbers w.r.t. http://mathworld.wolfram.com/SphericalTrigonometry.html
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	real function sphere_angle(ax, ay, az, bx, by, bz, cx, cy, cz)

	implicit none

	real (kind=RKIND), intent(in) :: ax, ay, az, bx, by, bz, cx, cy, cz

	real (kind=RKIND) :: a, b, c ! Side lengths of spherical triangle ABC

	real (kind=RKIND) :: ABx, ABy, ABz ! The components of the vector AB
	real (kind=RKIND) :: mAB ! The magnitude of AB
	real (kind=RKIND) :: ACx, ACy, ACz ! The components of the vector AC
	real (kind=RKIND) :: mAC ! The magnitude of AC

	real (kind=RKIND) :: Dx	! The i-components of the cross product AB x AC
	real (kind=RKIND) :: Dy	! The j-components of the cross product AB x AC
	real (kind=RKIND) :: Dz	! The k-components of the cross product AB x AC

	real (kind=RKIND) :: s	! Semiperimeter of the triangle
	real (kind=RKIND) :: sin_angle

	a = acos(max(min(bx*cx + by*cy + bz*cz,1.0_RKIND),-1.0_RKIND)) ! Eqn. (3)
	b = acos(max(min(ax*cx + ay*cy + az*cz,1.0_RKIND),-1.0_RKIND)) ! Eqn. (2)
	c = acos(max(min(ax*bx + ay*by + az*bz,1.0_RKIND),-1.0_RKIND)) ! Eqn. (1)

	ABx = bx - ax
	ABy = by - ay
	ABz = bz - az

	ACx = cx - ax
	ACy = cy - ay
	ACz = cz - az

	Dx =   (ABy * ACz) - (ABz * ACy)
	Dy = -((ABx * ACz) - (ABz * ACx))
	Dz =   (ABx * ACy) - (ABy * ACx)

	s = 0.5*(a + b + c)
!       sin_angle = sqrt((sin(s-b)*sin(s-c))/(sin(b)*sin(c)))   ! Eqn. (28)
	sin_angle = sqrt(min(1.0_RKIND,max(0.0_RKIND,(sin(s-b)*sin(s-c))/(sin(b)*sin(c))))) ! Eqn. (28)

	if ((Dx*ax + Dy*ay + Dz*az) >= 0.0) then
	   sphere_angle =  2.0 * asin(max(min(sin_angle,1.0_RKIND),-1.0_RKIND))
	else
	   sphere_angle = -2.0 * asin(max(min(sin_angle,1.0_RKIND),-1.0_RKIND))
	end if

	end function sphere_angle
	



!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
!       SUBROUTINE CROSS_PRODUCT
!       
!       Computes C = A x B
!       
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
	subroutine cross_product(Ax, Ay, Az, &
	Bx, By, Bz, &
	Cx, Cy, Cz)

	real (kind=RKIND), intent(in)  :: Ax, Ay, Az
	real (kind=RKIND), intent(in)  :: Bx, By, Bz
	real (kind=RKIND), intent(out) :: Cx, Cy, Cz

	Cx = (Ay * Bz) - (Az * By)
	Cy = (Az * Bx) - (Ax * Bz)
	Cz = (Ax * By) - (Ay * Bx)

	end subroutine cross_product                                 

	end module mpas_init_hcm_grid

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_csm.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/contributed.ncl"

begin

  ;
  ; The (lat,lon) the plot is to be centered over
  ;
  cenLat   = 0.0
  cenLon   = 0.0

  ;
  ; Projection to use for plot
  ;
;  projection = "Orthographic"
  projection = "CylindricalEquidistant"
; projection="Mercator"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;


  r2d = 57.2957795             ; radians to degrees

  wks = gsn_open_wks("pdf","surface_p")
  wks2 = gsn_open_wks("pdf","surface_slp")
  wks3 = gsn_open_wks("pdf","850hpa_vor")
  wks4 = gsn_open_wks("pdf","850hpa_temp")
  wks5 = gsn_open_wks("pdf","slp_pert")

  f = addfile("output.nc","r")

  lonCell   = f->lonCell(:) * r2d
  latCell   = f->latCell(:) * r2d
  lonVertex = f->lonVertex(:) * r2d
  latVertex = f->latVertex(:) * r2d
  lonEdge = f->lonEdge(:) * r2d
  latEdge = f->latEdge(:) * r2d
  verticesOnCell = f->verticesOnCell(:,:)
  alpha = f->angleEdge(:)
  cf1 = f->cf1
  cf2 = f->cf2
  cf3 = f->cf3


  res                      = True
  res@gsnMaximize          = True
  res@gsnSpreadColors      = True

  res@sfXArray             = lonCell
  res@sfYArray             = latCell
  ;res@sfXArray             = lonEdge
  ;res@sfYArray             = latEdge

  res@cnFillOn             = True
  res@cnFillMode           = "AreaFill"
;  res@cnLevelSpacingF      =  10.0
  res@cnInfoLabelOn        = True
;  res@cnLevelSelectionMode = "ManualLevels"
;  res@cnMinLevelValF       =  999. 
;  res@cnMaxLevelValF       = 101.
;  res@cnLevelSpacingF      =    0.25 
  res@cnLinesOn            = True
  res@cnLineLabelsOn       = True
  res@cnInfoLabelOn        = True
  res@cnInfoLabelFontHeightF = 0.007

;  res@lbLabelBarOn         = True
;  res@lbLabelAutoStride    = True
;  res@lbBoxLinesOn         = False

  res@mpProjection      = projection
  res@mpDataBaseVersion = "MediumRes"
;  res@mpGridAndLimbDrawOrder = "PreDraw"
;  res@mpGridLineColor   = "Background"
;  res@mpGridAndLimbOn   = True
  res@mpCenterLatF      = cenLat
  res@mpCenterLonF      = cenLon
  res@mpOutlineOn       = False
  res@mpFillOn          = False
  res@mpPerimOn         = False
  res@gsnFrame          = False
  res@mpMinLatF         = -90.

  res@gsnContourNegLineDashPattern = 1
  ;res@cnLineDashPattern = 0

; Info for vorticity plot
 resvor                      = True
  resvor@gsnMaximize          = True
  resvor@gsnSpreadColors      = True

  resvor@sfXArray             = lonVertex
  resvor@sfYArray             = latVertex

  resvor@cnFillOn             = True
  resvor@cnFillMode           = "AreaFill"
;  resvor@cnLevelSpacingF      =  10.0
  resvor@cnInfoLabelOn        = True
;  res@cnLevelSelectionMode = "ManualLevels"
;  res@cnMinLevelValF       =  940. 
;  res@cnMaxLevelValF       = 1024.
;  res@cnLevelSpacingF      =    4. 
  resvor@cnLinesOn            = True
  resvor@cnLineLabelsOn       = True
  resvor@cnInfoLabelOn        = True
  resvor@cnInfoLabelFontHeightF = 0.007

  resvor@mpProjection      = projection
  resvor@mpDataBaseVersion = "MediumRes"
;  res@mpGridAndLimbDrawOrder = "PreDraw"
;  res@mpGridLineColor   = "Background"
;  res@mpGridAndLimbOn   = True
  resvor@mpCenterLatF      = cenLat
  resvor@mpCenterLonF      = cenLon
  resvor@mpOutlineOn       = False
  resvor@mpFillOn          = False
  resvor@mpPerimOn         = False
  resvor@gsnFrame          = False
  resvor@mpMinLatF         = 0.
  resvor@gsnContourNegLineDashPattern = 1
  ;resvor@cnLineDashPattern = 0
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  
  ;========================
  ; get list of all files and open as "one big file"
  ;========================                             
     all_files = systemfunc ("ls diag*.nc")
     fall      = addfiles (all_files, "r")   ; note the "s" of addfile
  ;========================
  ; choose how files are combined and read in variable across files
  ;========================  
     ListSetType (fall, "cat") 
     slp    = fall[:]->mslp 
     vor850 = fall[:]->vorticity_850hPa
     temp850 = fall[:]->temperature_850hPa                    
     printVarSummary(vor850)
     printVarSummary(temp850)
     
  nTime = 9
  do iTime =0, nTime
  DAY = iTime

  res@gsnLeftString     = ":F21:P:B::F21:sfc:N: at day " + DAY + " "
  res@gsnLeftStringFontHeightF = 0.012
  res@gsnRightString    = " "
  res@gsnRightStringFontHeightF = 0.01

  ;There are two option for surface pressure
  ;option1 -> using coefficient cf1, cf2, cf3
  ;h0= (f->pressure_p(iTime,:,0) + f->pressure_base(iTime,:,0))/100.
  ;h1= (f->pressure_p(iTime,:,1) + f->pressure_base(iTime,:,1))/100.
  ;h2= (f->pressure_p(iTime,:,2) + f->pressure_base(iTime,:,2))/100.
  ;h = (cf1*h0 + cf2*h1 + cf3*h2)
  h0= (f->pressure(iTime,:,0))/100.
  h1= (f->pressure(iTime,:,1))/100.
  h2= (f->pressure(iTime,:,2))/100.
  h = (cf1*h0 + cf2*h1 + cf3*h2)

  ;option2 -> using simple extrapolation 
  ;rdzw = f->rdzw(:)
  ;p = f->pressure(iTime,:,1)
  
  ;rho=f->rho(iTime,:,:)
  ;qv = f->qv(iTime,:,:) 
  ;h = (p + 0.5/rdzw(0)*9.80616*(1.25*rho(:,0) - .25*rho(:,1)))/100. ;for dry!!!
  w_c = f->w(iTime,:,7)
  sp=slp(iTime,:)/100
  v850=vor850(iTime,:)
  t850=temp850(iTime,:)
  slp_p=slp(iTime,:)-slp(0,:)
  maxsp=max(h)
  minsp=min(h)
  print(maxsp)
  print(minsp)
  
  ;printVarSummary(sp)
  ;h = (p + 0.5/rdzw(0)*9.80616*(1.25*rho(:,0)*(1.+qv(:,0)) - .25*rho(:,1)*(1.+qv(:,1))))/100. ;for moist!!!

  fld = h

  map = gsn_csm_contour_map(wks,fld,res)
  ;mapsp = gsn_csm_contour_map(wks2,sp,res)
  mapvor850 = gsn_csm_contour_map(wks3,v850,resvor)
  ;mapt850 = gsn_csm_contour_map(wks4,t850,res)
  ;mapspp = gsn_csm_contour_map(wks5,slp_p,res)
  frame(wks)
  frame(wks2)
  frame(wks3)
  frame(wks4)
  frame(wks5)
    
  end do

end


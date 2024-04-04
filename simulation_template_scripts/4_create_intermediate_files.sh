#!/bin/bash
# Based on degrib_exe.sh from Fernandez et al, 2023, "Model for Prediction Across Scales-Atmosphere (MPAS-A) on INPE’s
# EGEON System - User’s Guide", Technical Report
#

# !!!!! Requires WPS !!!!!

# Select parameters from input_file.txt
echo "Reading input parameters:"
while IFS="=" read -r name value; do
    if [[ ! "$name" =~ ^\# ]]; then
        declare -r $name=$value
        echo $name":" $value
    fi
done < input_file.txt

# Go to WPS directory
cd $wps_dir

# Invariant variables 
#
# Land-Sea Mask
#
echo "Land-Sea Mask"
rm -f namelist.wps
sed -e "s,#LABELINITIAL#,1979-01-01_00:00:00,g;s,#LABELEND#,1979-01-01_00:00:00,g;s,#PREFIX#,$data_name/LSM,g" \
${wps_dir}/namelist.wps.TEMPLATE > ./namelist.wps
rm -f GRIBFILE.AAA
./link_grib.csh ${raw_input_data_dir}/e5.oper.invariant.128_172_lsm.ll025sc.1979010100_1979010100.grb
./ungrib.exe
mv ungrib.log ungrib.lsm.log
# #
# # SOILGHT
# #
echo "Soil Height"
rm -f namelist.wps
sed -e "s,#LABELINITIAL#,1979-01-01_00:00:00,g;s,#LABELEND#,1979-01-01_00:00:00,g;s,#PREFIX#,$data_name/GEO,g" \
${wps_dir}/namelist.wps.TEMPLATE > ./namelist.wps
rm -f GRIBFILE.AAA
./link_grib.csh ${raw_input_data_dir}/e5.oper.invariant.128_129_z.ll025sc.1979010100_1979010100.grb
./ungrib.exe
mv ungrib.log ungrib.geo.log
# #
# # Now, surface and upper air atmospheric variables
# #
echo "Surface and upper air atmospheric variables"
rm -f namelist.wps
sed -e "s,#LABELINITIAL#,${date1}_${time1},g;s,#LABELEND#,${date2}_${time2},g;s,#PREFIX#,$data_name/FILE,g" ${wps_dir}/namelist.wps.TEMPLATE > ./namelist.wps
rm -f GRIBFILE.*
./link_grib.csh ${raw_input_data_dir}/e5.oper.an.*.grb
./ungrib.exe
mv ungrib.log ungrib.${date1}_${time1}_${date2}_${time2}.log

echo "concatenate file for initial conditions:"

# Create array of dates and hours to loop through files
source ${exp_dir}/utils.sh
date_array=($(create_datehour_range $date1 $time1 $date2 $time2 $dt_files))

# Loop through date and hours
for DATE in "${date_array[@]}"; do
    FILENAME="FILE:${DATE}"
    echo "concatenating ${FILENAME} with invariant fields:"
    cat ${intermediate_input_data_dir}/${FILENAME} ${intermediate_input_data_dir}/LSM\:1979-01-01_00 > ${intermediate_input_data_dir}/FILE_CAT_LSM:${DATE}
    cat ${intermediate_input_data_dir}/FILE_CAT_LSM:${DATE} ${intermediate_input_data_dir}/GEO\:1979-01-01_00 > ${intermediate_input_data_dir}/FILE_CAT_LSM_GEO:${DATE}
    mv ${intermediate_input_data_dir}/FILE_CAT_LSM_GEO:${DATE} ${intermediate_input_data_dir}/${FILENAME}
    echo "done."
done

rm -f ${intermediate_input_data_dir}/FILE_CAT_LSM:* GRIBFILE.*

echo "####################################"
echo "#         Ungrib completed         #"
echo "####################################"

# # clean up and remove links

# mv ungrib.*.log ${EXPDIR}/logs
# mv ungrib.log ${EXPDIR}/logs/ungrib.2021-01-01_00:00:00.log
# mv Timing.degrib ${EXPDIR}/logs
# mv namelist.wps degrib_exe.sh ${EXPDIR}/scripts
# rm -f link_grib.csh
# cd ..
# ln -sf wpsprd/FILE3\:2021-01-01_00 .
# find ${EXPDIR}/wpsprd -maxdepth 1 -type l -exec rm -f {} \;
# echo "End of degrib Job"
# exit 0

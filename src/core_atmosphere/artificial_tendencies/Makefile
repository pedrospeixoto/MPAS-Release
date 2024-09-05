.SUFFIXES: .F .o

#
# Add new artificial tendencies modules to ARTIFICIAL_TENDENCY_MODULES
#
ARTIFICIAL_TENDENCY_MODULES = \
	mpas_atm_vel_relax_art_tend.o \


mpas_atm_vel_relax_art_tend.o:


################### Generally no need to modify below here ###################

mpas_atm_artificial_tendency_manager.o: $(ARTIFICIAL_TENDENCY_MODULES)

mpas_atm_art_tend_todynamics.o: mpas_atm_artificial_tendency_manager.o

OBJS = mpas_atm_artificial_tendency_manager.o mpas_atm_art_tend_todynamics.o

all: $(ARTIFICIAL_TENDENCY_MODULES) $(OBJS)

clean:
	$(RM) *.o *.mod *.f90
	@# Some Intel compilers generate *.i files; clean them up, too
	$(RM) *.i

.F.o:
	$(RM) $@ $*.mod
ifeq "$(GEN_F90)" "true"
	$(CPP) $(CPPFLAGS) $(PHYSICS) $(CPPINCLUDES) $< > $*.f90
	$(FC) $(FFLAGS) -c $*.f90 $(FCINCLUDES) -I../../framework -I../../operators -I../dynamics -I../physics -I../physics/physics_wrf -I../../external/esmf_time_f90
else
	$(FC) $(CPPFLAGS) $(PHYSICS) $(FFLAGS) -c $*.F $(CPPINCLUDES) $(FCINCLUDES) -I../../framework -I../../operators -I../dynamics -I../physics -I../physics/physics_wrf -I../../external/esmf_time_f90
endif

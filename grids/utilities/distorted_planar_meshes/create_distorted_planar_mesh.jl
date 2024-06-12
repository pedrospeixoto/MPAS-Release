#!/usr/bin/env julia

import Pkg

Pkg.offline()

Pkg.activate("mpas",shared=true)

if !isfile(joinpath(DEPOT_PATH[1],"environments","mpas","Project.toml"))
    Pkg.offline(false)
    @info "It seems the 'mpas' shared environment for julia was not set up yet.\nThis script will now try to download its own separate version of several packages to work properly. This includes NetCDF and all its dependencies, and the julia Makie plotting library.\nThis is done only once and may take a while.\nIf you wish to continue, please press 'enter', otherwise press ctrl+C to cancel"
    ans = readline()
    Pkg.add(["NCDatasets","GLMakie","CondaPkg","ArgParse"])
    Pkg.add(url="https://github.com/favba/TensorsLite.jl.git",rev="pin")
    Pkg.add(url="https://github.com/favba/ImmutableVectors.jl.git",rev="pin")
    Pkg.add(url="https://github.com/favba/TensorsLiteGeometry.jl.git",rev="pin")
    Pkg.add(url="https://github.com/favba/VoronoiMeshDataStruct.jl.git",rev="pin")
    Pkg.add(url="https://github.com/favba/VoronoiOperators.jl.git",rev="pin")
    Pkg.add(url="https://github.com/favba/MPASTools.jl.git",rev="pin")

    import CondaPkg
    CondaPkg.add("mpas_tools",channel="conda-forge")

    Pkg.precompile()
end

using MPASTools

create_distorted_planar_mesh_main(ARGS)

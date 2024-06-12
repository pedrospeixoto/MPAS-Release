#!/usr/bin/env julia
import Pkg

Pkg.offline()
Pkg.activate("mpas",shared=true)

using TensorsLite
using TensorsLiteGeometry
using NCDatasets
import GLMakie as plt
using VoronoiMeshDataStruct

function plot_periodic_mesh_cells(filename::AbstractString)
    mesh = NCDataset(filename) do f; VoronoiMesh(f);end
    xp = mesh.attributes[:x_period]::Float64
    yp = mesh.attributes[:y_period]::Float64
    #dc = mesh.attributes[:dc]::Float64
    dc = mesh.dcEdge[1]
    limits = (-dc/2,xp+dc,0.0,yp+dc)


    edges, ghost_edges = create_cell_linesegments(mesh)

    fig = plt.Figure()
    ax = plt.Axis(fig[1,1],aspect=plt.DataAspect(),limits=limits,title=filename*" Cells", xgridvisible=false, ygridvisible=false)

    plt.linesegments!(ax,edges[1],edges[2],color=:deepskyblue3,linestyle=:solid)
    plt.linesegments!(ax,ghost_edges[1],ghost_edges[2],color=:deepskyblue3,linestyle=:dash)
    plt.scatter!(ax,mesh.xCell,mesh.yCell,color=:deepskyblue3)

    wait(display(fig))
end

plot_periodic_mesh_cells(ARGS[1])

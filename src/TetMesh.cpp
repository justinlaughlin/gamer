/*
 * ***************************************************************************
 * This file is part of the GAMer software.
 * Copyright (C) 2016-2018
 * by Christopher Lee, John Moody, Rommie Amaro, J. Andrew McCammon,
 *    and Michael Holst
 *
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 *
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
 *
 * ***************************************************************************
 */

#include <array>
#include <algorithm>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iomanip>
#include <map>
#include <ostream>
#include <set>
#include <strstream>
#include <string>
#include <vector>

#include <libraries/casc/casc>

#include "TetMesh.h"

std::unique_ptr<TetMesh> makeTetMesh(
        const std::vector<SurfaceMesh*> &surfmeshes,
        std::string tetgen_params){

    // Create new tetmesh object
    std::unique_ptr<TetMesh> tetmesh(new TetMesh);

    size_t nVertices = 0, nFaces = 0, nRegions = 0, nHoles = 0;
    int i = 0;
    for (auto &surfmesh : surfmeshes){
        size_t nverts = surfmesh->template size<1>();
        size_t nfaces = surfmesh->template size<3>();

        if(nverts == 0 || nfaces == 0){
            std::stringstream ss;
            ss << "SurfaceMesh " << i << " contains no data."
                      << " Cannot tetrahedralize nothing.";
            throw std::runtime_error(ss.str());
        }

        auto metadata = *surfmesh->get_simplex_up();


        // TODO: (10) Use a more rigorous check of closedness
        if(hasHole(*surfmesh)){
            std::stringstream ss;
            ss << "SurfaceMesh " << i << " is not closed. Cannot tetrahedralize non-manifold objects.";
            throw std::runtime_error(ss.str());
        }

        metadata.ishole ? ++nHoles : ++nRegions;

        nVertices += nverts;
        nFaces += nfaces;
        ++i;
    }

    if (nRegions < 1){
        std::cerr << "Error(makeTetMesh): Expected at least one non-hole SurfaceMesh." << std::endl;
        throw std::runtime_error("No non-hole Surface Meshes found. makeTetMesh expects at least one non-hole SurfaceMesh");
    }

    std::cout << "Number of vertices: " << nVertices << std::endl;
    std::cout << "Number of Faces: " << nFaces << std::endl;
    std::cout << "Number of Regions: " << nRegions << std::endl;
    std::cout << "Number of Holes: " << nHoles << std::endl;

    tetgenio in, out;

    tetgenio::facet *f;
    tetgenio::polygon *p;

    // Allocate memory for tetgenio object arrays
    in.numberofpoints   = nVertices;
    in.pointlist        = new REAL[nVertices * 3];

    in.numberoffacets   = nFaces;
    in.facetlist        = new tetgenio::facet[nFaces];
    in.facetmarkerlist  = new int[nFaces];

    in.numberofregions  = nRegions;
    in.regionlist       = new REAL[nRegions * 5];

    if (nHoles > 0){
        in.numberofholes    = nHoles;
        in.holelist         = new REAL[nHoles * 3];
    }

    // Reset counters
    nFaces = nRegions = nHoles = 0;
    typename TetMesh::KeyType cnt = 0;

    for (auto &surfmesh : surfmeshes){
        std::map<typename TetMesh::KeyType, typename TetMesh::KeyType> sigma;

        // Assign vertex information
        for(const auto vertexID : surfmesh->template get_level_id<1>())
        {
            sigma[surfmesh->get_name(vertexID)[0]] = cnt;

            auto vertex = *vertexID;
            auto idx = cnt*3;
            in.pointlist[idx] = vertex[0];
            in.pointlist[idx+1] = vertex[1];
            in.pointlist[idx+2] = vertex[2];

            ++cnt;
        }

        // Assign face information
        for (const auto faceID : surfmesh->template get_level_id<3>()){
            auto w = surfmesh->get_name(faceID);

            f                       = &in.facetlist[nFaces];
            f->holelist             = (REAL *)NULL;
            f->numberofholes        = 0;
            f->numberofpolygons     = 1;

            f->polygonlist          = new tetgenio::polygon[f->numberofpolygons];
            p                       = &f->polygonlist[0];
            p->numberofvertices     = 3;
            p->vertexlist           = new int[p->numberofvertices];
            p->vertexlist[0]        = sigma[w[0]];
            p->vertexlist[1]        = sigma[w[1]];
            p->vertexlist[2]        = sigma[w[2]];

            in.facetmarkerlist[nFaces] = (*faceID).marker == -1? 0 : (*faceID).marker;
            ++nFaces;
        }

        auto metadata = *surfmesh->get_simplex_up();

        // TODO: (25) Improve region point picking strategy
        // Pick a point inside the region
        auto faceID = *surfmesh->template get_level_id<3>().begin();
        Vector normal = getNormal(*surfmesh, faceID);
        normal /= std::sqrt(normal|normal);

        auto fname = surfmesh->get_name(faceID);
        auto a = *surfmesh->get_simplex_up({fname[0]});
        auto b = *surfmesh->get_simplex_up({fname[1]});
        auto c = *surfmesh->get_simplex_up({fname[2]});

        Vector d = a-b;
        double weight = std::sqrt(d|d);

        // flip normal and scale by weight
        normal *= weight;
        Vector regionPoint = (a+b+c)/3 - normal;

        std::cout << "Region point: " << regionPoint << std::endl;

        if(metadata.ishole){
            auto idx            = nHoles*3;
            in.holelist[idx]    = regionPoint[0];
            in.holelist[idx+1]  = regionPoint[1];
            in.holelist[idx+2]  = regionPoint[2];
            ++nHoles;
        }
        else
        {
            auto idx                = nRegions*5;
            in.regionlist[idx]      = regionPoint[0];
            in.regionlist[idx+1]    = regionPoint[1];
            in.regionlist[idx+2]    = regionPoint[2];
            in.regionlist[idx+3]    = metadata.marker;
            // std::cout << "Region marker: " << metadata.marker << std::endl;

            if(metadata.useVolumeConstraint){
                in.regionlist[idx+4]    = metadata.volumeConstraint;
            }
            else{
                in.regionlist[idx+4]    = -1;
            }
            ++nRegions;
        }
    } // endif for surfmesh :surfmeshes

    // Add boundary marker on each node
    in.pointmarkerlist = new int[in.numberofpoints];
    for (int i = 0; i < in.numberofpoints; ++i){
        in.pointmarkerlist[i] = 1;
    }

    // Casting away const is an evil thing to do, however, tetgen has not yet
    // conformed...
    // auto plc = const_cast<char*>("plc");
    // in.save_nodes(plc);
    // in.save_poly(plc);

    // Call TetGen
    try{
        tetrahedralize(tetgen_params.c_str(), &in, &out, NULL);
    }
    catch (int e){
        switch(e){
        case 1:
            throw std::runtime_error("Tetgen: Out of memory");
        case 2:
            throw std::runtime_error("Tetgen: internal error");
        case 3:
            throw std::runtime_error("Tetgen: A self intersection was detected. Program stopped. Hint: use -d option to detect all self-intersections");
        case 4:
            throw std::runtime_error("Tetgen: A very small input feature size was detected.");
        case 5:
            throw std::runtime_error("Tetgen: Two very close input facets were detected");
        case 10:
            throw std::runtime_error("Tetgen: An input error was detected");
        }
    }
    // auto result = const_cast<char*>("result");
    // out.save_nodes(result);
    // out.save_elements(result);
    // out.save_faces(result);
    return tetgenioToTetMesh(out);
}

std::unique_ptr<TetMesh> tetgenioToTetMesh(tetgenio &tetio){
    std::unique_ptr<TetMesh> mesh(new TetMesh);

    if (tetio.mesh_dim == 2){
        throw std::runtime_error("tetgenioToTetMesh expects a tetrahedral tetgenio. Found surface instead.");
    }

    auto &metadata = *mesh->get_simplex_up();

    // Check for higher order cells
    const bool higher_order = tetio.numberofcorners == 10;

    metadata.higher_order = higher_order;

    std::set<int> vertices;

    // std::cout << "Number of tetrahedron attributes: " << tetio.numberoftetrahedronattributes
    //     << std::endl;

    // Copy over tetrahedron data
    // std::cout << "Copying over tetrahedron data..." << std::endl;
    for (int i = 0; i < tetio.numberoftetrahedra; ++i){
        // Set marker
        int marker = 0;

        if(tetio.numberoftetrahedronattributes > 0)
            marker = (int) tetio.tetrahedronattributelist[i * tetio.numberoftetrahedronattributes];

        // Get vertex id's
        int *ptr = &tetio.tetrahedronlist[i*tetio.numberofcorners];

        vertices.insert({ptr[0], ptr[1], ptr[2], ptr[3]});

        // TODO: (0) Do we need to set the orientation?
        // std::cout << casc::to_string(std::array<int,4>({ptr[0], ptr[1], ptr[2], ptr[3]})) << std::endl;
        mesh->insert<4>({ptr[0], ptr[1], ptr[2], ptr[3]},
                tetmesh::Cell(0, marker));
    }

    // std::cout << "Number of vertices: " << mesh->size<1>() << std::endl;
    // std::cout << "Number of edges: " << mesh->size<2>() << std::endl;
    // std::cout << "Number of faces: " << mesh->size<3>() << std::endl;
    // std::cout << "Number of tetrahedra: " << mesh->size<4>() << std::endl;

    // Copy over vertex data
    // std::cout << "Copying over vertex data..." << std::endl;
    for (auto i : vertices){
        double *ptr = &tetio.pointlist[i*3];
        auto vertex = mesh->get_simplex_up({i});
        if (vertex != nullptr){
            auto &vdata = *vertex;
            // std::cout << casc::to_string(std::array<double,3>({ptr[0],ptr[1],ptr[2]})) << std::endl;
            vdata = tetmesh::TetVertex(ptr[0], ptr[1], ptr[2], tetio.pointmarkerlist[i], false);
        }
    }

    for (auto &fdata : mesh->get_level<3>()){
        fdata.marker = 0;   // Initialize markers
    }

    // Go over faces and copy over marker information
    // std::cout << "Copying over face data..." << std::endl;
    for (int i = 0; i < tetio.numberoftrifaces; ++i){
    	int *ptr = &tetio.trifacelist[i*3];
        auto face = mesh->get_simplex_up({ptr[0], ptr[1], ptr[2]});
        if (face != nullptr){
            auto &fdata = *face;
            fdata.marker = tetio.trifacemarkerlist[i];
        }
    }

    // Copy over edge markers
    // std::cout << "Copying over edge data..."  << std::endl;
    for (int i = 0; i < tetio.numberofedges; ++i){
        int *ptr = &tetio.edgelist[i*2];

        auto edgeID = mesh->get_simplex_up({ptr[0], ptr[1]});
        if(edgeID != nullptr){
            auto &edata = *edgeID;
            edata.marker = tetio.edgemarkerlist[i];

            if (higher_order){
                double *pos = &tetio.pointlist[tetio.o2edgelist[i]*3];
                edata.position = Vector({pos[0], pos[1], pos[2]});
            }
        }
    }
    compute_orientation(*mesh);
    return mesh;
}

void writeVTK(const std::string& filename, const TetMesh &mesh){
    std::ofstream fout(filename);
    if(!fout.is_open())
    {
        std::cerr   << "File '" << filename
                    << "' could not be writen to." << std::endl;
        exit(1);
    }

    fout << "# vtk DataFile Version 2.0\n"
         << "Unstructured Grid\n"
         << "ASCII\n"  // BINARY
         << "DATASET UNSTRUCTURED_GRID\n";

    std::map<typename TetMesh::KeyType,typename TetMesh::KeyType> sigma;
    typename TetMesh::KeyType cnt = 0;

    // Output vertices
    fout << "POINTS " << mesh.size<1>() << " double" << std::endl;
    for (auto vertexID : mesh.get_level_id<1>()){
        sigma[mesh.get_name(vertexID)[0]] = cnt++;
        auto vertex = *vertexID;
        fout    << std::setprecision(17) << vertex[0] << " "
                << vertex[1] << " "
                << vertex[2] << "\n";
    }
    fout << "\n";

    bool orientationError = false;

    fout << "CELLS " << mesh.size<4>() << " " << mesh.size<4>()*(4+1) << "\n";
    for (auto cellID : mesh.get_level_id<4>()){
        auto w = mesh.get_name(cellID);
        auto orientation = (*cellID).orientation;

        if (orientation == 1){
            fout << "4 " << std::setw(4) << sigma[w[3]] << " "
                         << std::setw(4) << sigma[w[1]] << " "
                         << std::setw(4) << sigma[w[2]] << " "
                         << std::setw(4) << sigma[w[0]] << "\n";
        }
        else if(orientation == -1){
            fout << "4 " << std::setw(4) << sigma[w[0]] << " "
                         << std::setw(4) << sigma[w[1]] << " "
                         << std::setw(4) << sigma[w[2]] << " "
                         << std::setw(4) << sigma[w[3]] << "\n";
        }
        else{
            orientationError = true;
            fout << "4 " << std::setw(4) << sigma[w[0]] << " "
                         << std::setw(4) << sigma[w[1]] << " "
                         << std::setw(4) << sigma[w[2]] << " "
                         << std::setw(4) << sigma[w[3]] << "\n";
        }
    }
    fout << "\n";

    fout << "CELL_TYPES " << mesh.size<4>() << "\n";
    for (int i = 0; i < mesh.size<4>(); ++i){
        fout << "10\n";
    }
    fout << "\n";

    fout << "CELL_DATA " << mesh.size<4>() << "\n";
    fout << "SCALARS cell_scalars int 1\n";
    fout << "LOOKUP_TABLE default\n";
    // This should output in the same order...
    for (auto cell : mesh.get_level<4>()){
        fout << cell.marker << "\n";
    }
    fout << "\n";

    if(orientationError){
        std::cerr << "WARNING(writeVTK): The orientation of one or more faces "
                  << "is not defined. Did you run compute_orientation()?"
                  << std::endl;
    }
    fout.close();
}

void writeOFF(const std::string& filename, const TetMesh &mesh){
    std::ofstream fout(filename);
    if(!fout.is_open())
    {
        std::cerr   << "File '" << filename
                    << "' could not be writen to." << std::endl;
        exit(1);
    }

    fout << "OFF\n";
    fout << mesh.size<1>() << " "
         << mesh.size<4>() << " "
         << mesh.size<2>() << "\n";

    std::map<typename TetMesh::KeyType,typename TetMesh::KeyType> sigma;
    typename TetMesh::KeyType cnt = 0;

    fout.precision(10);
    for(const auto vertexID : mesh.get_level_id<1>()){
        sigma[mesh.get_name(vertexID)[0]] = cnt++;
        auto vertex = *vertexID;

        fout    << vertex[0] << " "
                << vertex[1] << " "
                << vertex[2] << " "
                << "\n";
    }

    bool orientationError = false;

    for (auto cellID : mesh.get_level_id<4>()){
        auto w = mesh.get_name(cellID);
        auto orientation = (*cellID).orientation;

        if (orientation == 1){
            fout << "4 " << std::setw(4) << sigma[w[3]] << " "
                         << std::setw(4) << sigma[w[1]] << " "
                         << std::setw(4) << sigma[w[2]] << " "
                         << std::setw(4) << sigma[w[0]] << "\n";
        }
        else if(orientation == -1){
            fout << "4 " << std::setw(4) << sigma[w[0]] << " "
                         << std::setw(4) << sigma[w[1]] << " "
                         << std::setw(4) << sigma[w[2]] << " "
                         << std::setw(4) << sigma[w[3]] << "\n";
        }
        else{
            orientationError = true;
            fout << "4 " << std::setw(4) << sigma[w[0]] << " "
                         << std::setw(4) << sigma[w[1]] << " "
                         << std::setw(4) << sigma[w[2]] << " "
                         << std::setw(4) << sigma[w[3]] << "\n";
        }
    }

    if(orientationError){
        std::cerr << "WARNING(writeOFF): The orientation of one or more cells "
                  << "is not defined. Did you run compute_orientation()?"
                  << std::endl;
    }
    fout.close();
}

void writeDolfin(const std::string &filename, const TetMesh &mesh){

    if((*mesh.get_simplex_up()).higher_order == true){
        std::cerr   << "Dolfin output does not support higher order mesh..." << std::endl;
        exit(1);
    }

    std::ofstream fout(filename);
    if(!fout.is_open())
    {
        std::cerr   << "File '" << filename
                    << "' could not be writen to." << std::endl;
        exit(1);
    }

    fout    << "<?xml version=\"1.0\"?>\n"
            << "<dolfin xmlns:dolfin=\"http://fenicsproject.org\">\n"
            << "  <mesh celltype=\"tetrahedron\" dim=\"3\">\n"
            << "    <vertices size=\"" << mesh.size<1>() <<  "\">\n";

    std::map<typename TetMesh::KeyType,typename TetMesh::KeyType> sigma;
    size_t cnt = 0;

    // Print out Vertices
    // std::cout << "Printing Vertices" << std::endl;
    fout.precision(6);
    for(const auto vertexID : mesh.get_level_id<1>()){
        size_t idx = cnt;
        sigma[mesh.get_name(vertexID)[0]] = cnt++;
        auto vertex = *vertexID;

        fout    << "      <vertex index=\"" << idx << "\" "
                << "x=\"" << vertex[0] << "\" "
                << "y=\"" << vertex[1] << "\" "
                << "z=\"" << vertex[2] << "\" />\n";
    }
    fout    << "    </vertices>\n";


    // Print out Tetrahedra
    // std::cout << "Printing Tetrahedra" << std::endl;
    cnt = 0;
    std::vector<std::array<std::size_t, 3> > faceMarkerList;
    std::vector<std::array<std::size_t, 2> > cellMarkerList;

    fout    << "    <cells size=\"" << mesh.size<4>() << "\">\n";
    for (const auto tetID :  mesh.get_level_id<4>()){
        std::size_t idx = cnt++;
        auto tetName = mesh.get_name(tetID);
        fout    << "      <tetrahedron index=\"" << idx << "\" "
                << "v0=\"" << sigma[tetName[0]] << "\" "
                << "v1=\"" << sigma[tetName[1]] << "\" "
                << "v2=\"" << sigma[tetName[2]] << "\" "
                << "v3=\"" << sigma[tetName[3]] << "\" />\n";
        // std::cout << casc::to_string(tetName) << std::endl;

        // First face = vertices 2,3,4
        // Second face = vertices 1,3,4 etc...
        for (std::size_t i = 0; i < 4; ++i){
            auto faceID = mesh.get_simplex_down(tetID, tetName[i]);
            std::size_t mark = (*faceID).marker;
            // std::cout << casc::to_string(mesh.get_name(faceID)) << " " << i << std::endl;
            if(mark != 0) faceMarkerList.push_back({idx, i, mark});
        }
        cellMarkerList.push_back({idx, static_cast<std::size_t>((*tetID).marker)});
    }
    fout << "    </cells>\n";
    fout << "    <domains>\n";

    fout << "      <mesh_value_collection name=\"m\" type=\"uint\" dim=\"2\" size=\"" << faceMarkerList.size() << "\">\n";
    for (const auto marker : faceMarkerList){
        fout    << "        <value cell_index=\"" << marker[0] << "\" "
                << " local_entity=\"" << marker[1] << "\" "
                << " value=\"" << marker[2] << "\" />\n";
    }

    fout << "      </mesh_value_collection>\n";
    fout << "      <mesh_value_collection name=\"m\" type=\"uint\" dim=\"3\" size=\"" << mesh.size<4>() << "\">\n";

    for (const auto marker : cellMarkerList){
        fout    << "        <value cell_index=\"" << marker[0] << "\" "
                << " local_entity=\"0\" "
                << " value=\"" << marker[1] << "\" />\n";
    }
    fout << "      </mesh_value_collection>\n";
    fout << "    </domains>\n";
    fout << "  </mesh>\n";
    fout << "</dolfin>\n";

    fout.close();
}

void writeTriangle(const std::string &filename, const TetMesh &mesh){
    std::ofstream fout(filename + ".node");
    if(!fout.is_open())
    {
        std::cerr   << "File '" << filename + ".node"
                    << "' could not be writen to." << std::endl;
        exit(1);
    }

    std::map<typename TetMesh::KeyType,typename TetMesh::KeyType> sigma;
    size_t cnt = 1;

    // Print out Vertices
    // std::cout << "Printing Vertices" << std::endl;
    // nVertices, dimension, nattributes, nmarkers
    fout << mesh.size<1>() << " 3 " << " 0 " << " 1\n";

    fout.precision(6);
    for(const auto vertexID : mesh.get_level_id<1>()){
        size_t idx = cnt;
        sigma[mesh.get_name(vertexID)[0]] = cnt++;
        auto vertex = *vertexID;

        fout    << idx << " "
                << vertex[0] << " "
                << vertex[1] << " "
                << vertex[2] << " "
                << (*vertexID).marker << "\n";
    }
    fout.close(); // Close .node file


    // Open file filename.ele
    std::ofstream foutEle(filename + ".ele");
    if (!foutEle.is_open())
    {
        std::cerr   << "File '" << filename + ".ele"
                    << "' could not be writen to." << std::endl;
        exit(1);
    }

    // nTetrahedra, nodes per tet, nAttributes
    foutEle << mesh.size<4>() << " 4 1\n";
    cnt = 1;
    for (const auto tetID :  mesh.get_level_id<4>()){
        std::size_t idx = cnt++;
        auto tetName = mesh.get_name(tetID);
        foutEle << idx << " "
                << sigma[tetName[0]] << " "
                << sigma[tetName[1]] << " "
                << sigma[tetName[2]] << " "
                << sigma[tetName[3]] << " "
                << (*tetID).marker << "\n";
    }
    foutEle.close(); // Close .ele file
}

void smoothMesh(TetMesh &mesh){
    std::set<TetMesh::SimplexID<1>> vertexIDs;

    for (auto faceID : mesh.get_level_id<3>()){
        if(mesh.up(faceID).size() == 1){
            auto bdryVertices = mesh.down(mesh.down(faceID)); // Set of vertices
            vertexIDs.insert(bdryVertices.begin(), bdryVertices.end());
        }
    }

    for (auto vID :  mesh.get_level_id<1>()){
        if (vertexIDs.find(vID) == vertexIDs.end()){
            std::set<TetMesh::SimplexID<1>> nbhd;
            neighbors_up(mesh, vID, std::inserter(nbhd, nbhd.end()));

            Vector barycenter;
            for(auto nbor : nbhd){
                barycenter += *nbor;
            }
            barycenter /= nbhd.size();
            auto& pos  = *vID;
            pos = barycenter;
        }
    }
}




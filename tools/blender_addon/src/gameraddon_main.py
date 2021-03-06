# ***************************************************************************
# This file is part of the GAMer software.
# Copyright (C) 2016-2018
# by Christopher Lee, Tom Bartol, John Moody, Rommie Amaro, J. Andrew McCammon,
#    and Michael Holst

# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
# ***************************************************************************

import bpy
from bpy.props import (BoolProperty, CollectionProperty, EnumProperty,
        FloatProperty, FloatVectorProperty, IntProperty, IntVectorProperty,
        PointerProperty, StringProperty, BoolVectorProperty)
from bpy.app.handlers import persistent

from gamer_addon.surfacemesh_ops import SurfaceMeshImprovementProperties

from gamer_addon.versions import (checkVersion, getGamerVersion)

from gamer_addon.meshstats import MeshQualityReportProperties

from gamer_addon.tetrahedralization import GAMerTetrahedralizationPropertyGroup

from gamer_addon.util import UNSETID


# python imports
import sys

# we use per module class registration/unregistration
def register():
    bpy.utils.register_module(__name__)

def unregister():
    bpy.utils.unregister_module(__name__)

@persistent
def gamer_load_post(dummy):
    """
    Initialize GAMer addon...
    """
    scene = bpy.context.scene
    if not scene.gamer.initialized:
        # print('Initializing GAMer Properties')
        scene.gamer.init_properties()
    else:
        # GAMer was previously initialized check version
        checkVersion()
        return

    mats = bpy.data.materials
    if 'bnd_unset_mat' not in mats:
        # if bnd_unset_mat is not defined, then create it
        bnd_unset_mat = bpy.data.materials.new('bnd_unset_mat')
        bnd_unset_mat.use_fake_user = True
        bnd_unset_mat.gamer.boundary_id = UNSETID


class GAMerAddonProperties(bpy.types.PropertyGroup):
    initialized = BoolProperty(name="GAMer Initialized", default=False)
    gamer_version = StringProperty(name="GAMer Version", default="0")
    boundary_id_counter = IntProperty(name="GAMer Boundary id Counter")
    versionerror = IntProperty(name="Version mismatch", default=0)

    surfmesh_procs = PointerProperty(
            type=SurfaceMeshImprovementProperties,
            name="GAMer Surface Mesh Improvement")

    mesh_quality_properties = PointerProperty(
            type=MeshQualityReportProperties,
            name="GAMer Mesh Quality Reporting"        )

    tet_group = PointerProperty(
            type=GAMerTetrahedralizationPropertyGroup,
            name="GAMer Tetrahedralization")

    def allocate_boundary_id ( self ):
        self.boundary_id_counter += 1
        return self.boundary_id_counter

    def init_properties ( self ):
        self.gamer_version = str(getGamerVersion())
        self.boundary_id_counter = 0 # Start counting at 0

        if 'bnd_unset_mat' not in bpy.data.materials:
            bnd_unset_mat = bpy.data.materials.new('bnd_unset_mat')
            bnd_unset_mat.use_fake_user = True
            bnd_unset_mat.gamer.boundary_id = UNSETID
            self.initialized = True

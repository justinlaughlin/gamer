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
import sys
import re
from ast import literal_eval

class GAMER_OT_prompt_update(bpy.types.Operator):
    bl_idname = "gamer.prompt_update"
    bl_label = "Warn to update GAMer addon"
    bl_options = {'BLOCKING', 'INTERNAL'}

    def execute(self, context):
        self.report({'WARNING'},
            "Blendfile was generated with a newer version of GAMer.")
        return {'FINISHED'}

class GAMER_OT_prompt_old_version(bpy.types.Operator):
    bl_idname = "gamer.prompt_old_version"
    bl_label = "Warn that GAMer cannot convert file automatically"
    bl_options = {'BLOCKING', 'INTERNAL'}

    def execute(self, context):
        self.report({'WARNING'},
            "Blendfile was generated with a version that does not support automatic conversion.")
        return {'FINISHED'}

class GAMER_OT_update_to_2_0_1_from_v_0_1(bpy.types.Operator):
    bl_idname = "gamer.update_to_2_0_1_from_v_0_1"
    bl_label = "Update from v0.1 to v2.0.1"
    bl_description = "Update GAMer version to 2.0.1 from v0.1"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        for obj in context.scene.objects:
            bpy.context.scene.objects.active = obj
            if obj.type == 'MESH':
                obj.gamer.remove_all_boundaries(context)
                for key, bdry in obj['boundaries'].items():
                    obj.gamer.add_boundary(context)
                    newBdry = obj.gamer.boundary_list[obj.gamer.active_bnd_index]

                    newBdry.boundary_name = key
                    newBdry.marker = bdry['marker']

                    # Deselect all
                    bpy.ops.object.mode_set(mode='EDIT')
                    bpy.ops.mesh.select_all(action='DESELECT')
                    bpy.ops.object.mode_set(mode='OBJECT')

                    # Select faces of interest
                    for faces in bdry['faces'].values():
                        for i in faces:
                            obj.data.polygons[i].select = True
                    bpy.ops.object.mode_set(mode='EDIT')

                    newBdry.assign_boundary_faces(context)
            del obj['boundaries']
            if 'id_counter' in obj.gamer:
                del obj.gamer['id_counter']
            if 'include' in obj.gamer:
                del obj.gamer['include']
            context.scene.gamer.gamer_version = "(2,0,1)"
            checkVersion()
        return {'FINISHED'}

def getGamerVersion():
    return sys.modules['gamer_addon'].bl_info.get('version', (-1, -1, -1))

def checkVersion():
    """
    Check the version
    """
    scene = bpy.context.scene
    print("Blendfile contains GAMer v%s metadata"%(scene.gamer.gamer_version))

    fileVer = scene.gamer.gamer_version
    isTupleStr = re.compile('\(.*\)')
    if isTupleStr.match(fileVer):
        fileVer = literal_eval(fileVer)
    else:
        fileVer = tuple(fileVer.split('.'))

    currVer = getGamerVersion()
    scene.gamer.versionerror = compare_version(fileVer, currVer)

    if scene.gamer.versionerror == -1:
        # Update from 2.0.0 to current
        if compare_version(fileVer, (2,0,0)) == 0:
            print("Metadata version is out of date.",
                    "Migrating from v(2, 0, 0) to v%s"%(str(currVer)))
            for obj in bpy.data.objects:
                if obj.type == 'MESH':
                    # Migrate name to boundary_name
                    for bdry in obj.gamer.boundary_list:
                        bdry.boundary_name = bdry.name
                        bdry.name = str(bdry.boundary_id)
                        if 'boundaries' in obj.keys():
                            del obj['boundaries']
            scene.gamer.gamer_version = str(currVer)
            scene.gamer.versionerror = 0
        else:
            bpy.ops.gamer.prompt_old_version()
    elif scene.gamer.versionerror == 1:
        bpy.ops.gamer.prompt_update()


## VERSION UTILITY FUNCTIONS
def cmp(a, b):
    """
    Compare a and b. Returns -1 if b > a, 1 if a > b, or 0 if a == b
    """
    return (a > b) - (a < b)

def compare_version(v1, v2):
    """
    Compare version tuples

    Return 1:  v1 >  v2
    Return 0:  v1 == v2
    Return -1: v1 <  v2
    """
    return cmp(*zip(*map(lambda x,y:(x or 0, y or 0),
            map(int, v1), map(int, v2))))

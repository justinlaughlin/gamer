# operations to smoothen ER meshes with very tight geometries

# Note, edge flipping can be problematic on these geometries so we might want to set the tolerance higher
# In void selectFlipEdges() [SurfaceMesh.h] I changed the edge flip criterion to 1.001 rather than 1.01:
# edgeFlipCriterion = 1.001

# open up a terminal and type
# blender -b --python-console
# i.e. start blender, don't show the GUI [background], run a python console

##############################
# import modules
import bpy, bmesh # standard blender python modules
import sys # we need to add the path of gamer to our path
sys.path.insert(0, '/home/justin/.config/blender/2.79/scripts/addons/') # tell python where the gamer addon is located
import gamer_addon as g # import gamer module
#sys.path.insert(0, '/home/justin/gitrepos/forks/gamer/tests/justin/') # tell python where the cli_pygamer.py file is located
#import cli_pygamer as cg # some functions that do common tasks

##############################
# Functions

def deleteAllObj():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    print("All objects deleted.")
    getObjects(printOut=True)

def importObj(objPath):
    importedObj = bpy.ops.import_scene.obj(filepath=objPath)
    objName = getObjects()[0]
    #obj = bpy.context.selected_objects[0]
    obj = bpy.data.objects[objName]
    obj.select = True
    print('\nSuccessful import of obj file...!')
    getVertices(obj,printVertices=True)
    return obj # bpy.context.active_object

def getObjects(printOut=False):
    objList = bpy.data.objects.keys()
    if printOut:
        print('All objects in workspace:')
        print(objList)
    return objList

def getVertices(obj,printVertices=False):
    # tell us some information about the object
    if obj.mode == 'EDIT':
        # this works only in edit mode,
        bm = bmesh.from_edit_mesh(obj.data)
        verts = [vert.co for vert in bm.verts]
    else:
        # this works only in object mode,
        verts = [vert.co for vert in obj.data.vertices]
    if printVertices:
        print('Object \"%s\" has %d vertices' % (obj.name, len(verts)))
    return(verts)

def changeGAMerSettings(smooth_iter=10,dense_iter=5,dense_rate=1.2):
    # settings
    bpy.context.scene.gamer.surfmesh_procs.smooth_iter = 10
    bpy.context.scene.gamer.surfmesh_procs.dense_iter = 5
    bpy.context.scene.gamer.surfmesh_procs.dense_rate = 1.2
    print('GAMer settings changed:')
    print('smooth_iter=%d\ndense_iter=%d\ndense_rate=%f' % (smooth_iter,dense_iter,dense_rate))

def initializeMesh():
    """
    Standard procedures to ensure mesh is ready for GAMer operations
    (assuming it is manifold, and watertight)
    """
    # set to edit mode and select all
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    # necessary steps before cleaning mesh
    # Make all normal vectors point outwards
    bpy.ops.mesh.normals_make_consistent(inside=False)
    # delete degenerate vertices/edges/faces
    bpy.ops.mesh.dissolve_degenerate()
    # make sure everything is triangulated
    bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
    print('Mesh initialized (edit mode, all selected, degenerates dissolved, consistent normals)')

def sub_div(obj,niter):

    print('Beginning subdivision...')
    getVertices(obj,printVertices=True)
    for i in range(niter):
        bpy.ops.mesh.subdivide()
    print('Mesh subdivided %d times' % (niter,(niter*4)))
    print('Subdivision finished...')
    getVertices(obj,printVertices=True)



def smooth_tris(niter):
    for i in range(niter):
        bpy.ops.gamer.smooth()
        bpy.ops.mesh.select_all(action='SELECT')
        print('GAMer smooth_tris complete (iteration %d of %d)'%(i, niter))

def normal_smooth(niter):
    for i in range(niter):
        bpy.ops.gamer.normal_smooth()
        bpy.ops.mesh.select_all(action='SELECT')
        print('GAMer normal_smooth complete (iteration %d of %d)'%(i, niter))


def coarsen(niter):
    for i in range(niter):
        bpy.ops.gamer.coarse_dense()
        bpy.ops.mesh.select_all(action='SELECT')
        print('GAMer coarsen complete (iteration %d of %d)'%(i, niter))


def del_non_manifold(niter):
    """very experimental"""
    for i in range(niter):
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.delete(type='FACE')
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.select_more()
        bpy.ops.mesh.delete(type='VERT')
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.delete(type='FACE')
        # fill and triangulate
        bpy.ops.mesh.select_non_manifold()
        bpy.ops.mesh.edge_face_add()
        bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
        bpy.ops.mesh.select_all(action='DESELECT')


########
# import the object
# BTW
# ...this can be looped over many objects to make life easier... for example if each ER mesh is stored as ER0.obj, ER1.obj, etc. in the directory "basePath"
# you could write, 
# basePath = '/home/justin/Team Drives/justinl.now@gmail.com/Rangamani Lab Drive/Justin/proj1_(FEniCS_spine_geometry)/main/mesh/justin-debugging/'
# objPaths = [basePath + 'ER' + number + '.obj' for number in range(N)] # generates a list with the base path prepended to the specific object name.
# for objPath in objPaths:

objPath = '/home/justin/Team Drives/justinl.now@gmail.com/Rangamani Lab Drive/Justin/proj1_(FEniCS_spine_geometry)/main/mesh/justin-debugging/singleER.obj'
deleteAllObj() # clear out workspace
obj = importObj(objPath)

changeGAMerSettings(smooth_iter=10,dense_iter=5,dense_rate=1.2)
initializeMesh()


# subdivide
sub_div(obj,2)
smooth_tris(15)
#### make sure this part is successful or it will start normal smoothing & creating intersecting faces
normal_smooth(2)
coarsen(5)
smooth_tris(5)
normal_smooth(1)
smooth_tris(2)





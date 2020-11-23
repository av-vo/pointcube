import bpy
import numpy as np
from PIL import Image
import math
import random


def draw_point(x, z, s, y_max, name):
    """Draw a point primitive.
    
    Parameters
    ----------
    x, z : int, coordinates of the point
    s : float, point size
    y_max : int, extrusion depth
    name : str, name assigned to the point to distinguish the cube face (i.e. 'front', 'side', 'top') the point belongs to
    """
    bpy.ops.mesh.primitive_circle_add(vertices=8, radius=s, fill_type='NGON', enter_editmode=False, align='WORLD', location=(x, random.randint(0, y_max), z), scale=(1, 1, 1))
    so = bpy.context.active_object
    so.rotation_euler[0] = math.radians(90)
    so.name = name

def img2points(name, img_path, num_stacks, y_max = 20, invert = False, point_size = .5, point_size_cutoff = .0):
    """Convert a raster image to a point cloud.
    
    Parameters
    ----------
    name : str, name of the cube face (i.e. 'front', 'side', 'top') that the image maps to
    img_path : path to the input image
    num_stacks : number of points along the z axis
    y_max : int, extrusion depth
    invert : bool, invert the mapping from pixel value to point size
    point_size : float, scaling factor for point size
    point_size_cutoff : float, points will not be drawn if smaller than this size
    """
    
    img = Image.open(img_path, 'r')
    width, height = img.size
    pxl = list(img.getdata())
    pxl = np.array(pxl).reshape((height, width))

    v_min = np.min(img)
    v_max = np.max(img)

    cell_size = math.floor(height/num_stacks)

    xIdx_max = width // cell_size + 1
    yIdx_max = height // cell_size + 1
    arr = np.zeros((xIdx_max, yIdx_max))

    for x in range(0, width, cell_size):
        xIdx = x // cell_size
        for z in range(0, height, cell_size):
            zIdx = num_stacks - z // cell_size
            size = pxl[z][x] if invert else 255 - pxl[z][x]
            size = size / (v_max - v_min) * point_size
            if size < point_size_cutoff :
                continue
            arr[xIdx][zIdx] = size
            draw_point(xIdx, zIdx, size, y_max, name)
            
    merge(name)
            
def merge(name):
    """Merge points belonging to a single cube side (i.e. front, side, top)
    
    Parameters
    ----------
    name : str, name of the cube face (i.e. 'front', 'side', 'top') 
    """
    obs = []
    for ob in bpy.context.scene.objects:
        if name in ob.name:
            obs.append(ob)

    ctx = bpy.context.copy()

    ctx['active_object'] = obs[0]
    ctx['selected_editable_objects'] = obs
    bpy.ops.object.join(ctx)
    
def rotate():
    """Rotate the point clouds
    
    """
    for ob in bpy.context.scene.objects:
        if ob.name == 'side':
            ob.rotation_euler[2] += math.radians(90)
        elif ob.name == 'top':
            ob.rotation_euler[0] -= math.radians(90)

img2points('front', 'input-images/front_.png', 20, invert = True)
img2points('side', 'input-images/side_.png', 20)
img2points('top', 'input-images/top_.png', 20)
rotate()
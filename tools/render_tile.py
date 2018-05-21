# render_tile.py - render tiles at all offsets via Blender
# Usage:
#   blender tile.blend -b -P render_tile.py
import bpy
from mathutils import Vector

camera = bpy.data.objects[0]

def set_output_path(path):
    bpy.data.scenes['Scene'].render.filepath = path
    
def reset_camera():
    global camera
    camera.delta_location = Vector((0.0, 0.0, 0.0))

def translate_camera(vec):
    global camera
    camera.delta_location += vec

for x in range(-2, 3):
    for y in range(-2, 2):
        if (x, y) == (0, 1):
            continue
        reset_camera()
        translate_camera(Vector((x * 2, y * 2, 0.0)))
        set_output_path('ren_%d_%d.png' % (x, y))
        bpy.ops.render.render(write_still=True)

reset_camera()

# render_tile.py - render tiles at all offsets via Blender
# Usage:
#   blender tile.blend -b -P render_tile.py
import bpy
import os
from mathutils import Vector
import tempfile

camera = bpy.data.objects[0]

def set_output_path(path):
    bpy.data.scenes['Scene'].render.filepath = path
    
def reset_camera():
    global camera
    camera.delta_location = Vector((0.0, 0.0, 0.0))

def translate_camera(vec):
    global camera
    camera.delta_location += vec

def load_image(path):
    try:
        return bpy.data.images.load(path)
    except:
        raise NameError('could not load image %s' % path)

bpy.context.scene.use_nodes = False
render = bpy.context.scene.render
render.resolution_x = 160
render.resolution_y = 160

images = {}
files = []
for x in range(-3, 4):
    for y in range(-2, 2):
        # Skip this position if it is right on top of
        # the player's location.
        if (x, y) == (0, 1):
            continue
        
        # Reserve a temporary file to hold the render.
        f = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        f.close()
        
        # Render the scene from this position.
        reset_camera()
        translate_camera(Vector((x * 2, y * 2, 0.0)))
        set_output_path(f.name)
        bpy.ops.render.render(write_still=True)
        
        # Load the rendered image.
        loaded_image = load_image(f.name)
        
        # Store the file.
        files.append(f)
        
        # Store the image.
        images[(x, y)] = loaded_image

# Set up the nodes system.
bpy.context.scene.use_nodes = True

# Create the background image.
bpy.ops.image.new(name='bg', width=640, height=640,
                  color=(0.0, 0.0, 0.0, 0.0), alpha=True)

# Set up the nodes.
tree = bpy.context.scene.node_tree
links = tree.links

for node in tree.nodes:
    tree.nodes.remove(node)

bg_node = tree.nodes.new(type='CompositorNodeImage')
bg_node.image = bpy.data.images['bg']

current_source = bg_node

for pos, image in images.items():
    x, y = pos
    image_node = tree.nodes.new(type='CompositorNodeImage')
    image_node.image = image
    translate_node = tree.nodes.new(type='CompositorNodeTranslate')
    translate_node.inputs[1].default_value = 80 + 160 - (abs(x) * 160) # X
    translate_node.inputs[2].default_value = 320 - 80 + (-(y + 2) * 160) # Y
    links.new(image_node.outputs[0], translate_node.inputs[0])
    alpha_over_node = tree.nodes.new(type='CompositorNodeAlphaOver')
    links.new(current_source.outputs[0], alpha_over_node.inputs[1])
    links.new(translate_node.outputs[0], alpha_over_node.inputs[2])
    current_source = alpha_over_node

comp_node = tree.nodes.new(type='CompositorNodeComposite')
links.new(current_source.outputs[0], comp_node.inputs[0])


# Render the final image.
print('Rendering image...')
set_output_path('out.png')
render.resolution_x = 640
render.resolution_y = 640
bpy.ops.render.render(write_still=True)

# Delete all the temporary files.
for f in files:
    os.unlink(f.name)

# Move the camera to its original location.
reset_camera()

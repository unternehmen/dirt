import sys
import os
import pygame
from pygame.locals import *
import OpenGL
from OpenGL.GL import *


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
FPS = 24
SHADER_DIR = 'shaders'


def update():
    """Update the game state."""
    pass


def draw(glsl_program, attributes):
    """Draw the contents of the game window."""
    glClear(GL_COLOR_BUFFER_BIT)
    glUseProgram(glsl_program)
    vertices = [ 0.0,  0.8,
                -0.8, -0.8,
                 0.8, -0.8]
    glEnableVertexAttribArray(attributes['coord2d'])
    glVertexAttribPointer(attributes['coord2d'], # attribute
                          2,                     # number of elements
                          GL_FLOAT,              # the type of each element
                          GL_FALSE,              # take values as is
                          0,                     # no data in between
                          vertices)              # pointer to the C array
    glDrawArrays(GL_TRIANGLES, 0, 3)
    glDisableVertexAttribArray(attributes['coord2d'])

def _die(text):
    print(text, file=sys.stderr)
    sys.exit(1)


def _load_shader(name, kind):
    full_path = os.path.join(SHADER_DIR, name)

    with open(full_path, 'r') as f:
        source = ''.join(f.readlines())

    shader = glCreateShader(kind);
    glShaderSource(shader, source)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS, None) != GL_TRUE:
        _die('error: could not compile ' + full_path)

    return shader

def _get_attr_location(glsl_program, name):
    attr = glGetAttribLocation(glsl_program, name)
    if attr == -1:
        _die('error: could not bind attribute ' + name)
    return attr

if __name__ == '__main__':
    # Initialize Pygame.
    pygame.init()

    # Open the game window.
    pygame.display.set_mode(SCREEN_SIZE, OPENGL | DOUBLEBUF)

    # Set up OpenGL.
    if not glInitGl21VERSION():
        _die('error: OpenGL 2.1 must be supported')
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Load the shaders.
    vert_shader = _load_shader('vertex.v.glsl', GL_VERTEX_SHADER)
    frag_shader = _load_shader('fragment.f.glsl', GL_FRAGMENT_SHADER)
    glsl_program = glCreateProgram()
    glAttachShader(glsl_program, vert_shader)
    glAttachShader(glsl_program, frag_shader)
    glLinkProgram(glsl_program)
    if glGetProgramiv(glsl_program, GL_LINK_STATUS, None) != GL_TRUE:
        _die('error: could not link shader glsl_program')
    attributes = {
        'coord2d': _get_attr_location(glsl_program, 'coord2d')
    }

    # Set up the game state.
    clock = pygame.time.Clock()

    # Main loop
    while True:
        # Check for user input.
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)

        update()
        draw(glsl_program, attributes)

        # Flip the display.
        pygame.display.flip()

        # Delay until the next frame.
        clock.tick(FPS)

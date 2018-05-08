import sys
import pygame
from pygame.locals import *
import OpenGL
from OpenGL.GL import *


SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT
FPS = 24


def update():
    """Update the game state."""
    pass


def draw():
    """Draw the contents of the game window."""
    glClear(GL_COLOR_BUFFER_BIT)


if __name__ == '__main__':
    # Initialize Pygame.
    pygame.init()

    # Open the game window.
    pygame.display.set_mode(SCREEN_SIZE, OPENGL | DOUBLEBUF)

    # Set up OpenGL.
    if not glInitGl21VERSION():
        print('error: OpenGL 2.1 must be supported', file=sys.stderr)
        sys.exit(1)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    # Set up the game state.
    clock = pygame.time.Clock()

    # Main loop
    while True:
        # Check for user input.
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)

        update()
        draw()

        # Flip the display.
        pygame.display.flip()

        # Delay until the next frame.
        clock.tick(FPS)

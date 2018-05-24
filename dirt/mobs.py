from .utils import load_image

def render(world, x, y, render_proc):
    """Draw any mobs at (x, y) in the world from player's POV.

    :param world: the world containing the mobs
    :param x: the x position
    :param y: the y position
    :param render_proc: the procedure to use for drawing the mob
    """
    for mob in world.mobs:
        if (mob.x, mob.y) == (x, y):
            render_proc(mob.image)

class Mob(object):
    def __init__(self, name='', image_path='', start_x=0, start_y=0):
        self.name = name
        self.image = load_image(image_path)
        self.x = start_x
        self.y = start_y

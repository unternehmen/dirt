import math
import pygame
from pkg_resources import resource_stream

def draw_text(font, text, color, window, x, y):
    "Draw TEXT in FONT with COLOR onto WINDOW at (X, Y)."
    cursor = 0

    for line in text.split('\n'):
        surf = font.render(line, True, color)
        window.blit(surf, (x, y + cursor))
        cursor += font.get_linesize()

def game_time_to_string(time):
    hour = math.floor(time / 60)
    indicator = ''

    if hour >= 12:
        indicator = 'PM'

        hour -= 12
    else:
        indicator = 'AM'

    if hour == 0:
        hour = 12

    return str(hour) + ":" + ("%02d" % (time % 60, )) + ' ' + indicator

def get_resource_stream(path):
    """
    Return a stream to the contents of a named resource.
    
    :param path: the path to the resource
    :returns: a file-like stream to the resource
    """
    return resource_stream('dirt', path)
    
def load_image(path):
    return pygame.image.load(get_resource_stream(path), path)
    
def load_sound(path):
    return pygame.mixer.Sound(file=get_resource_stream(path))

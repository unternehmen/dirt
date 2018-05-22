import os
import math
import pygame
import appdirs
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
    # Resources in the ~/.local/share/dirt or AppData folder should shadow
    # the packaged resources.
    appname = 'dirt'
    appauthor = None
    
    f = None
    try:
        full_path = os.path.join(appdirs.user_data_dir(appname, appauthor), path)
        f = open(full_path, 'rb')
        return f
    except FileNotFoundError:
        pass
    
    # Not in the local one... How about system-wide?
    try:
        full_path = os.path.join(appdirs.site_data_dir(appname, appauthor), path)
        f = open(full_path, 'rb')
        return f
    except FileNotFoundError:
        pass
    
    # It wasn't found in the user's directories,
    # so we just use the packaged resource.
    return resource_stream('dirt', path)
    
def load_image(path):
    with get_resource_stream(path) as f:
        return pygame.image.load(f, path)
    
def load_sound(path):
    with get_resource_stream(path) as f:
        return pygame.mixer.Sound(file=f)

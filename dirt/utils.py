import os
import math
import pygame
import appdirs
from pkg_resources import resource_stream

# Given to methods in the appdirs module
_APPNAME = 'dirt'
_APPAUTHOR = None

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
    global _APPNAME, _APPAUTHOR
    
    # Resources in the ~/.local/share/dirt or AppData folder should shadow
    # the packaged resources.
    f = None
    try:
        full_path = os.path.join(appdirs.user_data_dir(_APPNAME, _APPAUTHOR), path)
        f = open(full_path, 'rb')
        return f
    except FileNotFoundError:
        pass
    
    # Not in the local one... How about system-wide?
    try:
        full_path = os.path.join(appdirs.site_data_dir(_APPNAME, _APPAUTHOR), path)
        f = open(full_path, 'rb')
        return f
    except FileNotFoundError:
        pass
    
    # It wasn't found in the user's directories,
    # so we just use the packaged resource.
    return resource_stream('dirt', path)

def get_user_resource_path(path):
    """
    Returns the full path of a resource appended to the user's application
    data directory. For Linux users, this would be in ~/.local/share/dirt.
    :param str path: the path to the resource
    :returns: the path to the resource appended to the appdata directory
    :rtype: str
    """
    global _APPNAME, _APPAUTHOR
    return os.path.join(appdirs.user_data_dir(_APPNAME, _APPAUTHOR), path)

def ensure_user_resource_path_exists():
    """
    Create the application data directory for dirt if it doesn't exist.
    """
    datadir = os.path.join(appdirs.user_data_dir(_APPNAME, _APPAUTHOR), 'data')
    if not os.path.exists(datadir):
        os.makedirs(datadir)

def load_image(path):
    with get_resource_stream(path) as f:
        return pygame.image.load(f, path)
    
def load_sound(path):
    with get_resource_stream(path) as f:
        return pygame.mixer.Sound(file=f)

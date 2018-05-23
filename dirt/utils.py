import os
import math
import pygame
import appdirs
from pkg_resources import resource_stream, resource_exists

# Given to methods in the appdirs module
_APPNAME = 'dirt'
_APPAUTHOR = None

# This array is used by the image/sound/etc loading functions
_mods = []

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
    if resource_exists('dirt', path):
        return resource_stream('dirt', path)
    
    # Couldn't find it :/
    return None
    
def register_mod(mod_name):
    global _mods
    _mods = [mod_name] + _mods

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

def get_mod_resource(path):
    for mod_name in _mods:
        p = os.path.join('mods', mod_name, path)
        print(p)
        res = get_resource_stream(p)
        if res is not None:
            return res
    
    # Couldn't find the resource...
    raise Exception('Couldn\'t find the mod resource: %s' % path)

def load_image(path):
    with get_mod_resource(path) as f:
        return pygame.image.load(f, path)
    
def load_sound(path):
    with get_mod_resource(path) as f:
        return pygame.mixer.Sound(file=f)

import pygame
import os
import json
from .utils import get_resource_stream, get_user_resource_path, get_mod_resource
from .mobs import Mob

class World(object):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []
        self.bgm_path = 'magictown.ogg'
        self.day_sky_prefix = 'day'
        self.night_sky_prefix = 'sky'
        self.mobs = []

    def at(self, x, y):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError('Tried to access tile (%d, %d) in %dx%d map' % (x, y, self.width, self.height))
        return self.tiles[y*self.width + x]

    def set_at(self, x, y, num):
        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            raise ValueError('Tried to access tile (%d, %d) in %dx%d map' % (x, y, self.width, self.height))
        self.tiles[y*self.width + x] = num

    def newmap(self, width, height):
        self.width = width
        self.height = height
        self.tiles = [0] * width * height

    def load(self, filename):
        with get_mod_resource(filename) as f:
            j = json.loads(f.read().decode('utf-8'))

        self.width = j['width']
        self.height = j['height']
        self.tiles = j['tiles']
        self.bgm_path = j['bgm']
        self.day_sky_prefix = j['day_sky_prefix']
        self.night_sky_prefix = j['night_sky_prefix']

        if 'mobs' in j:
            for mobdef in j['mobs']:
                self.mobs.append(Mob(**mobdef))

        # Play the world's music.
        pygame.mixer.music.load(get_mod_resource(os.path.join('data', self.bgm_path)))
        pygame.mixer.music.play(loops=-1)

    def save(self, filename):
        j = {
            'width': self.width,
            'height': self.height,
            'bgm': self.bgm_path,
            'day_sky_prefix': self.day_sky_prefix,
            'night_sky_prefix': self.night_sky_prefix,
            'tiles': self.tiles
        }
        
        f = open(get_user_resource_path(filename), 'w')
        json.dump(j, f)
        f.close()

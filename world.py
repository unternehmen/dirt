import pygame
import os
import json

class World(object):
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tiles = []

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
        f = open(filename, 'r')
        j = json.load(f)
        f.close()

        self.width = j['width']
        self.height = j['height']
        self.tiles = j['tiles']
        self.bgm_path = j['bgm']

        # Play the world's music.
        pygame.mixer.music.load(os.path.join('data', self.bgm_path))
        pygame.mixer.music.play(loops=-1)

    def save(self, filename):
        j = {
            'width': self.width,
            'height': self.height,
            'bgm': self.bgm_path,
            'tiles': self.tiles
        }
        
        f = open(filename, 'w')
        json.dump(j, f)
        f.close()

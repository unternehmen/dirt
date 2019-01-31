import os.path
import math
import json
from .utils import get_resource_stream, get_user_resource_path, get_mod_resource

def sanitize_map_name(name):
    return ''.join([ch for ch in name if ch.isalnum() or ch == '_'])

class Chunk(object):
    WIDTH_IN_TILES = 18
    HEIGHT_IN_TILES = 18

    def __init__(self):
        self.map_name = None
        self.column = 0
        self.row = 0

        self.mob_inits = None

        self.tiles = None

    def _contains_local(self, loc_x, loc_y):
        return loc_x >= 0 and loc_y >= 0 and loc_x < Chunk.WIDTH_IN_TILES and loc_y < Chunk.HEIGHT_IN_TILES

    def _world_to_local_coords(self, x, y):
        loc_x = x - self.column * Chunk.WIDTH_IN_TILES
        loc_y = y - self.row * Chunk.HEIGHT_IN_TILES
        return (loc_x, loc_y)

    def try_load(self, map_name, x, y):
        # Sanitize map_name
        map_name = sanitize_map_name(map_name)

        # Get the column and row of the desired chunk
        chunk_column = int(math.floor(float(x) / Chunk.WIDTH_IN_TILES))
        chunk_row = int(math.floor(float(y) / Chunk.HEIGHT_IN_TILES))

        # Construct the chunk's filename
        filename = '%s_%d_%d.json' % (map_name, chunk_column, chunk_row)

        self.map_name = map_name
        self.column = chunk_column
        self.row = chunk_row
        #self.mob_inits = j['mob_inits']

        print('Loading %s... ' % filename, end='')

        # Load!
        try:
            with get_mod_resource(os.path.join('data', filename)) as f:
                j = json.loads(f.read().decode('utf-8'))
        except Exception:
            # Could be anything really...
            # TODO: Make get_mod_resource throw a specific exception
            self.tiles = [0] * Chunk.WIDTH_IN_TILES * Chunk.HEIGHT_IN_TILES
            print('Failed. Using zero chunk')
            return False

        self.tiles = j['floor_tiles']

        print('Succeeded.')
        return True

    def at(self, x, y):
        loc_x, loc_y = self._world_to_local_coords(x, y)
        return self.tiles[loc_y*Chunk.WIDTH_IN_TILES + loc_x]

    def contains(self, x, y):
        loc_x, loc_y = self._world_to_local_coords(x, y)
        return self._contains_local(loc_x, loc_y)

class ChunkedWorld(object):
    '''Chunk-based map object.'''
    def __init__(self):
        self.recent_chunks = []

    def _set_most_recent_chunk(self, chunk):
        try:
            self.recent_chunks.remove(chunk)
        except ValueError:
            pass
        self.recent_chunks.insert(0, chunk)

    def get_or_load_chunk_for(self, map_name, x, y):
        for chunk in self.recent_chunks:
            if chunk.map_name == map_name and chunk.contains(x, y):
                self._set_most_recent_chunk(chunk)
                return chunk

        chunk = Chunk()
        chunk.try_load(map_name, x, y)
        self._set_most_recent_chunk(chunk)

        # Prune old chunks
        while len(self.recent_chunks) > 5:
            self.recent_chunks.pop()
        return chunk

    def at(self, map_name, x, y):
        chunk = self.get_or_load_chunk_for(map_name, x, y)
        if chunk is not None:
            return chunk.at(x, y)

        return None


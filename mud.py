import pygame
from pygame import *

SCREEN_WIDTH = 512
SCREEN_HEIGHT = 480
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)


SOUTH = 0
WEST  = 1
NORTH = 2
EAST  = 3
NUM_DIRECTIONS = 4


def direction_as_vector(direction):
    if direction == SOUTH:
        return 0, 1
    elif direction == WEST:
        return -1, 0
    elif direction == NORTH:
        return 0, -1
    elif direction == EAST:
        return 1, 0
    else:
        raise ValueError('invalid direction')


class KeyState:
    def __init__(self):
        self.current_keystate = pygame.key.get_pressed()
        self.old_keystate = self.current_keystate

    def update(self):
        self.old_keystate = self.current_keystate
        self.current_keystate = pygame.key.get_pressed()

    def is_key_down(self, key):
        return self.current_keystate[key]

    def is_key_pressed(self, key):
        return self.current_keystate[key] and not self.old_keystate[key]


class Player:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.facing = SOUTH

class Game:
    STAGE = [
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        1, 0, 0, 1, 0, 0, 0, 0, 0, 1,
        1, 0, 0, 1, 0, 1, 0, 1, 0, 1,
        1, 0, 1, 1, 0, 1, 0, 0, 0, 1,
        1, 0, 1, 0, 0, 1, 1, 1, 0, 1,
        1, 0, 1, 0, 0, 0, 1, 0, 0, 1,
        1, 0, 1, 1, 1, 0, 1, 0, 1, 1,
        1, 0, 0, 0, 1, 0, 1, 0, 0, 1,
        1, 0, 1, 0, 0, 0, 0, 0, 0, 1,
        1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
    ]
    STAGE_WIDTH = 10
    STAGE_HEIGHT = 10

    def __init__(self):
        self._player = Player()
        self._player.x = 1
        self._player.y = 1
        self._player.facing = SOUTH
        self._states = {
            'title': {
                'on_update': self._title_update,
                'on_draw': self._title_draw
            },
            'travel': {
                'on_update': self._travel_update,
                'on_draw': self._travel_draw
            },
            'battle': {
                'on_update': self._battle_update,
                'on_draw': self._battle_draw
            }
        }
        self._state = 'title'

    def update(self):
        self._states[self._state]['on_update']()

    def draw(self):
        self._states[self._state]['on_draw']()

    def _tile_at(self, x, y):
        return Game.STAGE[y * Game.STAGE_WIDTH + x]

    def _title_update(self):
        if keystate.is_key_pressed(K_SPACE):
            self._state = 'travel'

    def _title_draw(self):
        pass

    def _travel_update(self):
        if keystate.is_key_pressed(K_UP):
            vec = direction_as_vector(self._player.facing)
            self._player.x += vec[0]
            self._player.y += vec[1]
        elif keystate.is_key_pressed(K_DOWN):
            vec = direction_as_vector(self._player.facing)
            self._player.x -= vec[0]
            self._player.y -= vec[1]
        elif keystate.is_key_pressed(K_LEFT):
            self._player.facing = (self._player.facing - 1) \
                                  % NUM_DIRECTIONS
        elif keystate.is_key_pressed(K_RIGHT):
            self._player.facing = (self._player.facing + 1) \
                                  % NUM_DIRECTIONS

    def _travel_draw(self):
        self._render_stage()

    def _battle_update(self):
        pass

    def _battle_draw(self):
        self._render_stage()

    def _render_stage(self):
        distance_vec = direction_as_vector(self._player.facing)
        strafe_vec = -distance_vec[1], distance_vec[0]

        for distance in range(3, -1, -1):
            for berth in range(0, 4):
                if berth == 0:
                    strafes = (0,)
                else:
                    strafes = berth, -berth

                for strafe in strafes:
                    if distance == 1 and abs(strafe) > 2:
                        continue

                    if distance == 0 and abs(strafe) > 1:
                        continue

                    x = self._player.x \
                        + (distance_vec[0] * distance) \
                        + (strafe_vec[0] * strafe)
                    y = self._player.y \
                        + (distance_vec[1] * distance) \
                        + (strafe_vec[1] * strafe)

                    if x < 0 or x >= Game.STAGE_WIDTH \
                       or y < 0 or y >= Game.STAGE_HEIGHT:
                        continue

                    tile = self._tile_at(x, y)
                    
                    if tile == 0:
                        color = (0, 255, 0)
                    elif tile == 1:
                        color = (255, 0, 0)

                    render_surface.fill(color, (x * 16, y * 16, 16, 16))


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
render_surface = pygame.Surface((256, 240), 0, screen)
clock = pygame.time.Clock()
keystate = KeyState()
game = Game()

quitted = False
while not quitted:
    for event in pygame.event.get():
        if event.type == QUIT:
            quitted = True

    keystate.update()
    game.update()
    render_surface.fill((0, 0, 0))
    game.draw()

    pygame.transform.scale(render_surface, SCREEN_SIZE, screen)
    pygame.display.flip()
    clock.tick(60)

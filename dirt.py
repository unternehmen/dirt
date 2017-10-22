#!/usr/bin/env python3
# dirt.py - a low fantasy adventure game set in Maya

import sys, pygame, math, random
from collections import namedtuple
from pygame.locals import *
from dialogmanager import DialogManager, Say, Choose, BigMessage
from world import World
from monsters.rat import Rat
from monsters.jyesula import Jyesula
from monsters.proselytizer import Proselytizer
from monsters.guard import Guard
from utils import draw_text, game_time_to_string

# Developer privileges / Allow backtick (`) console.
dev_enabled = True
dev_console_lines = [
    'Welcome to JAULD OS v1.2',
    'Type HELP for instructions.',
    'Press backtick (`) to return to the game.'
]
dev_console_input = ''

def dev_console_print(s):
    '''Prints something to the dev console.'''
    global dev_console_lines
    
    lines = s.split('\n')
    dev_console_lines += lines

    # Erase old lines
    if len(dev_console_lines) > 14:
        dev_console_lines = dev_console_lines[-14:]

# We use this dictionary to get text from user input
key_chars = {
    pygame.K_a: 'a',
    pygame.K_b: 'b',
    pygame.K_c: 'c',
    pygame.K_d: 'd',
    pygame.K_e: 'e',
    pygame.K_f: 'f',
    pygame.K_g: 'g',
    pygame.K_h: 'h',
    pygame.K_i: 'i',
    pygame.K_j: 'j',
    pygame.K_k: 'k',
    pygame.K_l: 'l',
    pygame.K_m: 'm',
    pygame.K_n: 'n',
    pygame.K_o: 'o',
    pygame.K_p: 'p',
    pygame.K_q: 'q',
    pygame.K_r: 'r',
    pygame.K_s: 's',
    pygame.K_t: 't',
    pygame.K_u: 'u',
    pygame.K_v: 'v',
    pygame.K_w: 'w',
    pygame.K_x: 'x',
    pygame.K_y: 'y',
    pygame.K_z: 'z',
    pygame.K_0: '0',
    pygame.K_1: '1',
    pygame.K_2: '2',
    pygame.K_3: '3',
    pygame.K_4: '4',
    pygame.K_5: '5',
    pygame.K_6: '6',
    pygame.K_7: '7',
    pygame.K_8: '8',
    pygame.K_9: '9',
    pygame.K_SPACE: ' ',
}

# Map editor
dev_map_editor_pan_x = 0
dev_map_editor_pan_y = 0

# Modes that the program can be in.
MODE_GAME           = 0
MODE_DEV_CONSOLE    = 1
MODE_DEV_MAP_EDITOR = 2
current_mode = MODE_GAME

# Cardinal directions
NORTH    = 0
EAST     = 1
SOUTH    = 2
WEST     = 3
NUM_DIRS = 4

# Define the different kinds of tile.
TileKind = namedtuple('TileKind', 'is_solid img')
tile_kinds = {
    0: TileKind(is_solid=False, img=None),
    1: TileKind(is_solid=True, img="data/wall_plain.png"),
    2: TileKind(is_solid=True, img="data/door_plain.png"),
    3: TileKind(is_solid=True, img="data/column_plain.png"),
    4: TileKind(is_solid=False, img="data/grass_plain.png"),
    5: TileKind(is_solid=False, img="data/floor_bloody.png"),
    6: TileKind(is_solid=True, img="data/spikes.png"),
    7: TileKind(is_solid=False, img="data/floor_glass.png")
}

class Game(object):
    """A Game stores information which needs to be everywhere."""
    def __init__(self):
        """Create a new Game object."""
        # The current minute of the in-game day.
        self.time = 60 * 5

font = None

class Player:
    def __init__(self, x, y):
        self.health = 3
        self.max_health = 3
        self.money = 3
        self.facing = SOUTH
        self.opponent = None
        self.in_menu = False
        self.time_passed = False
        self.x = x
        self.y = y

    def stop_time(self):
        """
        Make time considered to be "not passed".

        This must happen after time passes (when the user walks,
        attacks, etc.) so that time does not endlessly keep passing.
        """
        self.time_passed = False

    def pass_time(self):
        """
        Make time considered to be "passed".

        This has many effects:

        * The game clock advances by one minute.
        * Enemies re-engage the player if they are in battle.
        * A random encounter might happen.
        """
        self.time_passed = True

    def time_has_passed(self):
        'Return whether time is considered to be "passed".'
        return self.time_passed

    def take_damage(self, amount):
        "Make the player take an AMOUNT of damage."
        self.health = max(0, self.health - amount)

    def gain_money(self, amount):
        "Make the player gain an AMOUNT of money."
        self.money += amount

    def lose_money(self, amount):
        "Make the player lose an AMOUNT of money."
        self.money = max(0, self.money - amount)

    def is_dead(self):
        "Return whether the player is dead."
        return self.health <= 0

    def leave_battle(self):
        "Make the player leave the current battle."
        self.opponent = None

    def leave_menu(self):
        "Make the player leave the current menu."
        self.in_menu = False

    def is_in_battle(self):
        "Return whether the player is in a battle."
        return self.opponent is not None

    def is_in_menu(self):
        "Return whether the player is in a menu."
        return self.in_menu

    def enter_battle(self, opponent):
        "Make the player enter battle."
        self.opponent = opponent

    def enter_menu(self):
        "Make the player enter the menu."
        self.in_menu = True

    def attack(self, enemy):
        "Make the player attack an enemy."
        enemy.take_damage(1)

    def get_opponent(self):
        "Return the player's opponent."
        return self.opponent


def dir_as_offset(direction):
    if direction == NORTH:
        return 0, -1
    elif direction == EAST:
        return 1, 0
    elif direction == SOUTH:
        return 0, 1
    elif direction == WEST:
        return -1, 0

def dialog_action_throne_room():
    while True:
        result = yield Choose('Bow', 'Beg', 'Talk about...', 'Depart')

        if result == 0:
            yield Say('You are\nlearning\nmanners\nI see.')
        elif result == 1:
            yield Say('You have\nalways been\nfine without\nmoney')
            yield Say('Why do you\nneed it\nnow?')
        elif result == 2:
            while True:
                result = yield Choose('Lettre', 'Cold Garden',
                                      'Day and night', 'Nevermind')

                if result == 0:
                    yield Say('It seems that\ndanger is\nafoot.  Jauld,\nfix it.')
                elif result == 1:
                    yield Say('If you find\nmy ring,\nI can return\nto C.G.')
                    yield Say('But I cannot\ntake you\nwith me.')
                elif result == 2:
                    yield Say('The sun goes\ndown quite\nsuddenly,\nyes.')
                elif result == 3:
                    break
        elif result == 3:
            break


def dialog_action_ghost():
    while True:
        result = yield Choose('Squint', 'Shiver', 'Depart')

        if result == 0:
            yield Say('... ooo...')
        elif result == 1:
            yield Say('... woo...')
        elif result == 2:
            break

def dialog_action_tavern(player):
    if player.money > 1:
        player.health = player.max_health
        player.money -= 2
        yield BigMessage('You went in and had a drink.')
    else:
        yield BigMessage('You can\'t afford an ale.')

def dialog_action_read_lettre():
    yield BigMessage("""Dear Jyesula,

May the Stars be on our Side.  If this
Lettre has fallen into the wrong Hands,
we may all be doomed.

Jyesula, your People are dying.
Only you can stop the Sick Drake
from putrifying our Realm.

We beg you set out at once.
The Town of Anstre awaits its fate.

-Mayor of Anstre""")

def dialog_action_its_locked():
    yield BigMessage('It\'s locked.')

def dialog_action_guard_blocks_you():
    yield BigMessage('A guard does not let you through.')

def draw_world(window, x, y, facing, world, tile_kinds, tile_images):
    farness_vec = 0
    strafe_vec = 0

    farness_vec = dir_as_offset(facing)
    strafe_vec = [-farness_vec[1], -farness_vec[0]]

    if farness_vec[0] == 1:
        strafe_vec[1] *= -1
    elif farness_vec[0] == -1:
        strafe_vec[1] *= -1

    strafe_vec = tuple(strafe_vec)

    for farness in range(3, -1, -1):
        for berth in range(-3, 1):
            sides = []

            if berth == 0:
                sides = [0]
            else:
                sides = [berth, -berth]

            for strafe in sides:
                if farness == 1 and abs(strafe) > 2:
                    continue

                if farness == 0 and abs(strafe) > 1:
                    continue

                # Locate the selected tile in the world.
                pos_x = x + \
                        (farness_vec[0] * farness) + \
                        (strafe_vec[0] * strafe)
                pos_y = y + \
                        (farness_vec[1] * farness) + \
                        (strafe_vec[1] * strafe)

                # If the tile is off-world, refuse to draw it.
                if pos_x < 0 or pos_x >= world.width or \
                   pos_y < 0 or pos_y >= world.height:
                    continue

                tile = world.at(pos_x, pos_y)
                tile_img = tile_kinds[tile].img

                if tile_img == None:
                    continue

                surf = None

                # Determine which part of the tile image to draw.
                clip_x = 0

                if strafe <= 0:
                    surf = tile_images[tile_img].regular
                    clip_x = 480 + (160 * strafe)
                else:
                    surf = tile_images[tile_img].flipped
                    clip_x = 160 * strafe

                clip_y = 480 - (160 * farness)

                # Draw the tile.
                window.blit(surf, (0, 0),
                            (clip_x, clip_y, 160, 160))

                if strafe == 0:
                    break


if __name__ == '__main__':
    # Initialize Pygame.
    pygame.init()
    pygame.font.init()

    # Load the font.
    font = pygame.font.Font(None, 20)

    # Open the window.
    # For fullscreen:
    #window = pygame.display.set_mode((320, 240), FULLSCREEN)
    window = pygame.display.set_mode((320, 240))

    # Load sprites.
    jauld_img = pygame.image.load('data/jauld.png')
    proselytizer_img = pygame.image.load('data/proselytizer.png')
    heart_full_img = pygame.image.load('data/heart_full.png')
    heart_half_img = pygame.image.load('data/heart_half.png')
    heart_empty_img = pygame.image.load('data/heart_empty.png')
    money_one = pygame.image.load('data/money_one.png')
    money_two = pygame.image.load('data/money_two.png')
    money_three = pygame.image.load('data/money_three.png')
    money_four = pygame.image.load('data/money_four.png')
    money_five = pygame.image.load('data/money_five.png')
    money_ten = pygame.image.load('data/money_ten.png')
    money_sixteen = pygame.image.load('data/money_sixteen.png')
    money_thirtytwo = pygame.image.load('data/money_thirtytwo.png')
    wall_plain_img = pygame.image.load('data/wall_plain.png')
    wall_plain_flipped_img = pygame.transform.flip(wall_plain_img,
                                                   True,
                                                   False)
    door_plain_img = pygame.image.load('data/door_plain.png')
    door_plain_flipped_img = pygame.transform.flip(door_plain_img,
                                                   True,
                                                   False)
    night_throne_img = pygame.image.load('data/night_throne.png')
    day_throne_img = pygame.image.load('data/day_throne.png')
    ghost_img = pygame.image.load('data/ghost.png')
    spike_sound = pygame.mixer.Sound('data/blow.wav')

    # Load sky images
    night_sky = [
        pygame.image.load('data/sky_north.png'),
        pygame.image.load('data/sky_east.png'),
        pygame.image.load('data/sky_south.png'),
        pygame.image.load('data/sky_west.png')
    ]

    day_sky = [
        pygame.image.load('data/day_north.png'),
        pygame.image.load('data/day_east.png'),
        pygame.image.load('data/day_south.png'),
        pygame.image.load('data/day_west.png')
    ]

    skybox = list(night_sky) # We'll use the night sky first

    # Load images for all tiles.
    TileImage = namedtuple('TileImage', 'regular flipped')
    tile_images = {}
    for kind in tile_kinds.values():
        if kind.img is not None:
            regular = pygame.image.load(kind.img)
            flipped = pygame.transform.flip(regular, True, False)
            tile_images[kind.img] = \
              TileImage(regular=regular,
                        flipped=flipped)

    # Set up the player.
    player = Player(12, 16)

    # Set up the menu.
    selection = 0

    # Set up overall game variables.
    denominations = {
        1: money_one,
        2: money_two,
        3: money_three,
        4: money_four,
        5: money_five,
        10: money_ten,
        16: money_sixteen,
        32: money_thirtytwo
    }
    day_length = 60 * 24
    game = Game()
    world = World()
    world.load('data/castle.json')

    # Set up and play the music.
    pygame.mixer.music.load('data/magic-town.ogg')
    pygame.mixer.music.play(loops=-1)

    # new DialogManager system
    dialog_manager = DialogManager()
    dialog_manager.start(dialog_action_read_lettre)

    clock = pygame.time.Clock()

    # Loop until the user quits.
    done = False
    while not done:
        if current_mode == MODE_GAME:
            # Update the state of the dialog.
            dialog_manager.update()

            # Clear the screen.
            window.fill((255, 255, 255))

            # Draw the sky.
            if skybox[player.facing] is not None:
                window.blit(skybox[player.facing], (0, 0), (0, 0, 160, 89))

            # Draw the world.
            draw_world(window,
                       player.x, player.y, player.facing,
                       world,
                       tile_kinds, tile_images)

            # Draw the enemy if we are in battle.
            if player.is_in_battle():
                player.get_opponent().draw(window)

            # Draw the border around the world.
            window.fill((0, 0, 0), (160, 0, 1, 160))
            window.fill((0, 0, 0), (0, 160, 160, 1))

            # Draw the player's avatar.
            window.blit(jauld_img, (170, 10))

            # Draw the player's money.
            coins = []
            left = player.money

            for denom in reversed(sorted(denominations.keys())):
                while denom <= left:
                    coins += [denom]
                    left -= denom

            cursor = 300
            for coin in coins:
                window.blit(denominations[coin], (cursor, 10))
                cursor -= 6

            # Draw the player's health.
            for i in range(0, player.max_health):
                if player.health - i <= 0:
                    # Draw an empty heart.
                    window.blit(heart_empty_img, (190 + (i * 20), 10))
                elif player.health - i == 0.5:
                    # Draw a half heart.
                    window.blit(heart_half_img, (190 + (i * 20), 10))
                else:
                    # Draw a full heart.
                    window.blit(heart_full_img, (190 + (i * 20), 10))

            # Draw the time of day.
            msg = font.render("Game time: " +
                              game_time_to_string(game.time),
                              True, (0, 0, 0))
            window.blit(msg, (170, 44))

            # Draw the menu if the menu is active.
            if player.is_in_menu():
                cursor = 165
                i = 0

                for choice in player.get_opponent().get_options(player):
                    text_surf = font.render(choice, True, (0, 0, 0))
                    window.blit(text_surf, (10, cursor))

                    if selection == i:
                        # Draw a box next to the selected option.
                        window.fill((0, 0, 0), (3, cursor + 5, 4, 4))

                    cursor += 18
                    i += 1


            # Draw the dialog if it is active.
            if dialog_manager.is_active():
                dialog_manager.draw(window, font)
            
            # Update the window.
            pygame.display.flip()

            # React to user input.
            for event in pygame.event.get():
                if event.type == QUIT:
                    # Quit the game.
                    done = True
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        # Quit the game.
                        done = True
                    elif event.key == K_BACKQUOTE:
                        if dev_enabled:
                            current_mode = MODE_DEV_CONSOLE
                    elif player.is_in_menu() and player.is_in_battle():
                        # Handle battle menu navigation and choosing.
                        enemy = player.get_opponent()

                        if selection >= len(enemy.get_options(player)):
                            selection = len(enemy.get_options(player)) - 1

                        if event.key == K_UP:
                            if selection > 0:
                                selection -= 1
                        elif event.key == K_DOWN:
                            if selection < len(enemy.get_options(player)) - 1:
                                selection += 1
                        elif event.key == K_RETURN:
                            # Select the current menu item.
                            enemy.suffer(player,
                                         enemy.get_options(player)[selection])
                    else:
                        if dialog_manager.is_active():
                            dialog_manager.key_pressed(event.key)
                        else:
                            # Handle player movement.
                            if event.key == K_RETURN and player.is_in_battle():
                                player.enter_menu()
                            elif event.key == K_RIGHT:
                                # Turn the player right.
                                player.facing = (player.facing + 1) % NUM_DIRS
                            elif event.key == K_LEFT:
                                # Turn the player left.
                                player.facing = (player.facing - 1) % NUM_DIRS
                            elif event.key == K_UP:
                                # Attempt to move the player forward.
                                offset = dir_as_offset(player.facing)
                                if not tile_kinds[world.at(player.x + offset[0],
                                                  player.y + offset[1])].is_solid:
                                    player.x += offset[0]
                                    player.y += offset[1]
                                    player.pass_time()

                                    if player.is_in_battle():
                                        player.get_opponent().follow(player)
                                else:
                                    target = (player.x + offset[0],
                                              player.y + offset[1])
                                    if target == (14, 18):
                                        dialog_manager.start(dialog_action_tavern, player)
                                    elif target == (12, 29):
                                        # Enter the throne room of Jyesula.
                                        if game.time < 60 * 6 or game.time >= 60 * 19:
                                            backdrop = night_throne_img
                                        else:
                                            backdrop = day_throne_img

                                        dialog_manager.start(dialog_action_throne_room, backdrop)
                                    elif target == (10, 16):
                                        # Enter the ghost room.
                                        dialog_manager.start(dialog_action_ghost, ghost_img)
                                    elif target == (12, 15):
                                        dialog_manager.start(dialog_action_guard_blocks_you)
                                    elif world.at(*target) == 2:
                                        dialog_manager.start(dialog_action_its_locked)
                            elif event.key == K_DOWN:
                                # Attempt to move the player backward.
                                offset = dir_as_offset(player.facing)
                                if not tile_kinds[world.at(player.x - offset[0],
                                                           player.y - offset[1])].is_solid:
                                    player.x -= offset[0]
                                    player.y -= offset[1]
                                    player.pass_time()

                                    if player.is_in_battle():
                                        player.get_opponent().follow(player)

            # If the enemy died, end the battle.
            if player.is_in_battle() and player.get_opponent().is_dead():
                player.get_opponent().reward(player)
                player.leave_menu()
                player.leave_battle()
                enemy = None

            if player.time_has_passed():
                player.stop_time()

                game.time = (game.time + 1) % day_length

                # Update the sky
                if game.time < 60 * 6 or game.time >= 60 * 19:
                    skybox = list(night_sky)
                else:
                    skybox = list(day_sky)

                # If the player is in battle, let the enemy attack
                # and summon the menu.
                if player.is_in_battle():
                    player.get_opponent().engage(player)

                # Start a random encounter, randomly.
                if (not player.is_in_battle()
                        and world.at(player.x, player.y) != 5
                        and random.randint(0, 30) == 0):
                    index = random.randint(0,3)

                    if index == 0:
                        player.enter_battle(Rat())
                    elif index == 1:
                        player.enter_battle(Proselytizer())
                    elif index == 2:
                        player.enter_battle(Jyesula())
                    else:
                        player.enter_battle(Guard())

                    player.enter_menu()

            # If the player is in battle, tick the enemy.
            if player.is_in_battle():
                player.get_opponent().tick()

            # End the game if the user has died.
            if player.is_dead():
                done = True
        elif current_mode == MODE_DEV_CONSOLE:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    done = True
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_BACKQUOTE:
                        # Switch back to game mode
                        current_mode = MODE_GAME
                    elif e.key == pygame.K_ESCAPE:
                        done = True
                    elif e.key == pygame.K_BACKSPACE:
                        # Erase the last character
                        if len(dev_console_input) >= 1:
                            dev_console_input = dev_console_input[0:-1]
                    elif e.key == pygame.K_RETURN:
                        # Submit a command
                        cmd = dev_console_input.strip().lower()
                        
                        if cmd == 'help':
                            dev_console_print('The following commands are available:')
                            dev_console_print('  HELP')
                            dev_console_print('  EDITMAP')
                            dev_console_print('Press backtick(`) to return to the game.')
                        elif cmd == 'editmap':
                            current_mode = MODE_DEV_MAP_EDITOR
                            dev_map_editor_pan_x = 0
                            dev_map_editor_pan_y = 0
                            dev_console_print('Started map editor.')
                        else:
                            dev_console_print('Bzzzrt! Type HELP for instructions.')

                        dev_console_input = ''
                    elif e.key in key_chars:
                        # Append a new character
                        ch = key_chars[e.key]
                        if e.mod & pygame.KMOD_SHIFT:
                            ch = ch.upper()
                        dev_console_input += ch

            window.fill((0, 0, 0))
            
            # Draw the output of previous commands
            for i in range(len(dev_console_lines)):
                line = dev_console_lines[-1 - i]
                draw_text(font, line, (255, 255, 255), window, 0, window.get_height() - (i+2) * font.get_linesize())

            # Draw the command that is being typed in
            draw_text(font, dev_console_input + '|', (255, 255, 255), window, 0, window.get_height() - font.get_linesize())
            
            pygame.display.flip()
        elif current_mode == MODE_DEV_MAP_EDITOR:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    done = True
                elif e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        done = True
                    elif e.key == pygame.K_BACKQUOTE:
                        current_mode = MODE_GAME
                    elif e.key == pygame.K_UP:
                        dev_map_editor_pan_y -= 1
                    elif e.key == pygame.K_RIGHT:
                        dev_map_editor_pan_x += 1
                    elif e.key == pygame.K_DOWN:
                        dev_map_editor_pan_y += 1
                    elif e.key == pygame.K_LEFT:
                        dev_map_editor_pan_x -= 1
                    elif e.key in key_chars:
                        ch = key_chars[e.key]
                        if ch in '01234567':
                            tile_x = player.x - dev_map_editor_pan_x
                            tile_y = player.y - dev_map_editor_pan_y
                            world.set_at(tile_x, tile_y, int(ch))
            
            window.fill((0, 0, 0))
            
            for y in range(-6, 6):
                tile_y = y + player.y - dev_map_editor_pan_y
                for x in range(-6, 6):
                    tile_x = x + player.x - dev_map_editor_pan_x
                    if tile_x >= 0 and tile_x < world.width and tile_y >= 0 and tile_y < world.height:
                        tile = world.at(tile_x, tile_y)

                        color = (255, 255, 255)
                        if tile_x == player.x and tile_y == player.y:
                            color = (255, 0, 0)

                        if x == 0 and y == 0:
                            draw_text(font, '(  )', (0, 50, 255), window, 16*6 - 16*x - 5, 16*6 - 16*y)
                        draw_text(font, str(tile), color, window, 16*6 - 16*x, 16*6 - 16*y)

            pygame.display.flip()

        # Delay until the next frame.
        clock.tick(40)


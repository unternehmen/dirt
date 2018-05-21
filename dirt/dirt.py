#!/usr/bin/env python3
# dirt.py - a low fantasy adventure game set in Maya
import sys, pygame, math, random, os, itertools
from collections import namedtuple
from pygame.locals import *
from .dialogmanager import DialogManager, Say, Choose, BigMessage
from .world import World
from .monsters import Rat, Jyesula, Proselytizer, Guard
import dirt.convlib as convlib
from dirt.utils import draw_text, game_time_to_string, get_resource_stream, load_image, load_sound

# Developer privileges / Allow backtick (`) console.
allow_edit = False
edit_mode_chosen_tile = 3
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

allowed_console_chars = \
  'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789./ '

# Modes that the program can be in.
MODE_GAME        = 0
MODE_DEV_CONSOLE = 1
current_mode = MODE_GAME

# Cardinal directions
NORTH    = 0
EAST     = 1
SOUTH    = 2
WEST     = 3
NUM_DIRS = 4

# Define the different kinds of tile.
# Fields:
#   substrate - what tile's image should be drawn under this (or None)
#   is_beneath - whether the tile should be draw under other tiles
#   is_solid - whether the player can walk through this tile
#   img - the path to the tile's image
TileKind = namedtuple('TileKind', 'substrate is_beneath is_solid img')
tile_kinds = {
    0: TileKind(substrate=None, is_beneath=True, is_solid=False, img='data/plain_floor.png'),
    1: TileKind(substrate=None, is_beneath=False, is_solid=True, img="data/wall_plain.png"),
    2: TileKind(substrate=None, is_beneath=False, is_solid=True, img="data/door_fancy.png"),
    3: TileKind(substrate=0, is_beneath=False, is_solid=True, img="data/column_plain.png"),
    4: TileKind(substrate=None, is_beneath=False, is_solid=False, img="data/grass_plain.png"),
    5: TileKind(substrate=None, is_beneath=True, is_solid=False, img="data/floor_bloody.png"),
    6: TileKind(substrate=4, is_beneath=False, is_solid=True, img="data/spikes.png"),
    7: TileKind(substrate=None, is_beneath=True, is_solid=False, img="data/floor_glass.png")
}

class Game(object):
    """A Game stores information which needs to be everywhere."""
    def __init__(self):
        """Create a new Game object."""
        # The current minute of the in-game day.
        self.time = 60 * 5

font = None
player = None

class Player:
    def __init__(self, x, y):
        self.health = 3
        self.max_health = 3
        self.money = 3
        self.facing = SOUTH
        self.opponent = None
        self.in_menu = False
        self.conversation = None
        self.in_conversation = False
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

    def is_in_conversation(self):
        "Return whether the player is in a new-style conversation."
        return self.in_conversation
    
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
    global player
    while True:
        result = yield Choose('Bow', 'Ask for money', 'Talk', 'Depart')
        if result == 0:
            yield Say('You are\nlearning\nmanners\nI see.')
        elif result == 1:
            yield Say('You have\nalways been\nfine without\nmoney')
            yield Say('Why do you\nneed it\nnow?')
        elif result == 2:
            player.in_conversation = True
            player.conversation = convlib.jyesula
            player.conversation.run_begin_funcs(player, circumstances='throneroom')
        else:
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

def dialog_action_tavern():
    global player

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

def draw_single_tile(win, forward, right, tile_kinds, tile_images, tile_kind_id, beneathness):
    tile = tile_kinds[tile_kind_id]
    
    if beneathness and tile.substrate is not None:
        if tile.substrate is not None:
            draw_single_tile(win, forward, right, tile_kinds, tile_images, tile.substrate, True)
    elif beneathness == tile.is_beneath:
        # Just focus on drawing the tile itself.
        clip_y = 480 - 160 * forward
        clip_x = 0
        flip = False

        if right == 0:
            clip_w = 160
        else:
            clip_w = 80
        
        if right <= 0:
            screen_x_offset = 0
            clip_x = 480 + 160 * right
        else:
            screen_x_offset = 80
            clip_x = 480 - 160 * right + 80
            flip = True

        win.blit(tile_images[tile.img].regular,
                 (screen_x_offset, 0),
                 (clip_x, clip_y, clip_w, 160))

def draw_world_with_beneathness(win, x, y, facing, world, tile_kinds, tile_images, beneathness):
    angle = 0
    if facing == NORTH:
        angle = math.pi/2
    elif facing == WEST:
        angle = math.pi
    elif facing == SOUTH:
        angle = 3*math.pi/2
    
    sa = math.sin(angle)
    ca = math.cos(angle)
    for forward in range(3, -1, -1):
        for right in itertools.chain(range(-3, 0), range(3, -1, -1)):
            pos_x = x + int(round(forward*ca + right*sa))
            pos_y = y + int(round(-forward*sa + right*ca))
            
            if pos_x >= 0 and pos_x < world.width and \
               pos_y >= 0 and pos_y < world.height:
                tile = world.at(pos_x, pos_y)
                draw_single_tile(win, forward, right, tile_kinds, tile_images, tile, beneathness)

def draw_world(window, x, y, facing, world, tile_kinds, tile_images):
    draw_world_with_beneathness(window, x, y, facing, world, tile_kinds, tile_images, True)
    draw_world_with_beneathness(window, x, y, facing, world, tile_kinds, tile_images, False)

def load_skybox(prefix):
    path_prefix = 'data/' + prefix
    return [
        load_image(path_prefix + '_north.png'),
        load_image(path_prefix + '_east.png'),
        load_image(path_prefix + '_south.png'),
        load_image(path_prefix + '_west.png')
    ]

def main():
    global current_mode, allow_edit, player

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
    jauld_img = load_image('data/jauld.png')
    proselytizer_img = load_image('data/proselytizer.png')
    heart_full_img = load_image('data/heart_full.png')
    heart_half_img = load_image('data/heart_half.png')
    heart_empty_img = load_image('data/heart_empty.png')
    money_one = load_image('data/money_one.png')
    money_two = load_image('data/money_two.png')
    money_three = load_image('data/money_three.png')
    money_four = load_image('data/money_four.png')
    money_five = load_image('data/money_five.png')
    money_ten = load_image('data/money_ten.png')
    money_sixteen = load_image('data/money_sixteen.png')
    money_thirtytwo = load_image('data/money_thirtytwo.png')
    ui_frame_img = load_image('data/ui_frame.png')
    plain_floor_img = load_image('data/plain_floor.png')
    wall_plain_img = load_image('data/wall_plain.png')
    wall_plain_flipped_img = pygame.transform.flip(wall_plain_img,
                                                   True,
                                                   False)
    night_throne_img = load_image('data/night_throne.png')
    day_throne_img = load_image('data/day_throne.png')
    ghost_img = load_image('data/ghost.png')
    spike_sound = load_sound('data/blow.wav')

    # Load images for all tiles.
    TileImage = namedtuple('TileImage', 'regular flipped')
    tile_images = {}
    for kind in tile_kinds.values():
        if kind.img is not None:
            regular = load_image(kind.img)
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
    
    conversation_input = ''

    # Load sky images
    night_sky = load_skybox(world.night_sky_prefix)
    day_sky = load_skybox(world.day_sky_prefix)

    skybox = night_sky # We'll use the night sky first
    
    # new DialogManager system
    dialog_manager = DialogManager()
    dialog_manager.start(dialog_action_read_lettre)

    clock = pygame.time.Clock()
    frame_counter = 0

    # Loop until the user quits.
    done = False
    while not done:
        frame_counter += 1
        
        if current_mode == MODE_GAME:
            # Update the state of the dialog.
            dialog_manager.update()

            # Clear the screen.
            window.fill((255, 255, 255))

            # Draw the sky.
            if skybox[player.facing] is not None:
                window.blit(skybox[player.facing], (0, 0))# (0, 0, 160, 89))

            # Draw the world.
            draw_world(window,
                       player.x, player.y, player.facing,
                       world,
                       tile_kinds, tile_images)
                       
            # If we in edit mode, then make flashing tile ahead
            if allow_edit and frame_counter % 7 < 3:
                draw_single_tile(window, 1, 0, tile_kinds, tile_images, edit_mode_chosen_tile, True)
                draw_single_tile(window, 1, 0, tile_kinds, tile_images, edit_mode_chosen_tile, False)

            # Draw the enemy if we are in battle.
            if player.is_in_battle():
                player.get_opponent().draw(window)

            # Draw the border around the world.
            window.blit(ui_frame_img, (0, 0))

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
            
            # Draw the dialog if it is active.
            if dialog_manager.is_active():
                dialog_manager.draw(window, font, draw_choices=(not player.in_conversation))
            
            if (player.conversation is not None and not player.is_in_menu() and not dialog_manager.is_active()) or player.in_conversation:
                log = player.conversation.log
                lines = []
                for entry in log:
                    lines += str(entry).split('\n')
                if player.in_conversation:
                    # Draw black background for conversation
                    window.fill((0, 0, 0), (0, 240 - 5 * font.get_linesize(), 320, 5 * font.get_linesize()))
                    for i in range(0, min(len(lines), 4)):
                        color = (255, 255, 255)
                        line = lines[-i - 1]
                        if line.startswith('Jyesula:'):
                            color = (255, 0, 0)
                        draw_text(font, line, color, window, 0, 240 - (2+i) * font.get_linesize())
                    draw_text(font, 'Talk>' + conversation_input + '|', (255, 255, 255), window, 0, 240 - font.get_linesize())
                else:
                    for i in range(0, min(len(lines), 4)):
                        draw_text(font, lines[-1 - i], (128, 128, 128), window, 0, 240 - (1+i) * font.get_linesize())

            # Draw the menu if the menu is active.
            elif not player.in_conversation and player.is_in_menu():
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
                    elif allow_edit:
                        if event.key == K_p:
                            # Edit tile ahead
                            ox, oy = dir_as_offset(player.facing)
                            tx, ty = player.x + ox, player.y + oy
                            world.set_at(tx, ty, edit_mode_chosen_tile)
                        elif event.key == K_h:
                            edit_mode_chosen_tile = edit_mode_chosen_tile - 1
                            if edit_mode_chosen_tile < 0:
                                edit_mode_chosen_tile += len(tile_kinds)
                        elif event.key == K_t:
                            edit_mode_chosen_tile = edit_mode_chosen_tile + 1
                            if edit_mode_chosen_tile >= len(tile_kinds):
                                edit_mode_chosen_tile -= len(tile_kinds)
                    elif player.in_conversation:
                        if event.key == K_RETURN:
                            player.conversation.feed_player_msg(conversation_input, player)
                            conversation_input = u''
                        elif event.key == pygame.K_BACKSPACE:
                            # Erase the last character
                            if len(conversation_input) >= 1:
                                conversation_input = conversation_input[0:-1]
                        elif event.unicode in allowed_console_chars:
                            ch = event.unicode
                            if event.mod & KMOD_SHIFT:
                                ch = ch.upper()
                            conversation_input += ch
                    elif dialog_manager.is_active():
                            dialog_manager.key_pressed(event.key)
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
                            if player.x + offset[0] >= 0 and \
                               player.x + offset[0] < world.width and \
                               player.y + offset[1] >= 0 and \
                               player.y + offset[1] < world.height:
                                if allow_edit or not tile_kinds[world.at(player.x + offset[0],
                                                          player.y + offset[1])].is_solid:
                                    player.x += offset[0]
                                    player.y += offset[1]
                                    if not allow_edit:
                                        player.pass_time()

                                    if player.is_in_battle():
                                        player.get_opponent().follow(player)
                                else:
                                    target = (player.x + offset[0],
                                              player.y + offset[1])
                                    if target == (14, 18):
                                        dialog_manager.start(dialog_action_tavern)
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
                            if allow_edit or not tile_kinds[world.at(player.x - offset[0],
                                                       player.y - offset[1])].is_solid:
                                player.x -= offset[0]
                                player.y -= offset[1]
                                if not allow_edit:
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
                    skybox = night_sky
                else:
                    skybox = day_sky

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
                        args = cmd.split()

                        if len(args) >= 1:
                            if args[0] == 'help' or args[0] == '?':
                                dev_console_print('The following commands are available:')
                                dev_console_print('  NEWMAP <width> <height>')
                                dev_console_print('  LOADMAP <filename>')
                                dev_console_print('  ALLOWEDIT')
                                dev_console_print('  DISALLOWEDIT')
                                dev_console_print('  SAVEMAP <filename>')
                                dev_console_print('  SETMUSIC <filename>')
                                dev_console_print('    (relative to ./data/)')
                                dev_console_print('  TELEPORT <x> <y>')
                                dev_console_print('  SETDAYSKY <prefix>')
                                dev_console_print('  SETNIGHTSKY <prefix>')
                                dev_console_print('Press backtick(`) to return to the game.')
                            elif args[0] == 'allowedit':
                                allow_edit = True
                            elif args[0] == 'disallowedit':
                                allow_edit = False
                            elif args[0] == 'newmap':
                                if len(args) == 3:
                                    width = int(args[1])
                                    height = int(args[2])
                                    world.newmap(width, height)
                                    dev_console_print('New map created (size %dx%d)' % (width, height))
                                else:
                                    dev_console_print('usage: newmap <width> <height>')
                            elif args[0] == 'savemap':
                                if len(args) == 2:
                                    world.save(args[1])
                                    dev_console_print('Saved to %s' % args[1])
                                else:
                                    dev_console_print('usage: savemap <filename>')
                            elif args[0] == 'loadmap':
                                if len(args) == 2:
                                    world.load(args[1])
                                    day_sky[0:4] = load_skybox(world.day_sky_prefix)
                                    night_sky[0:4] = load_skybox(world.night_sky_prefix)
                                    dev_console_print('Loaded map %s' % args[1])
                                else:
                                    dev_console_print('usage: loadmap <filename>')
                            elif args[0] == 'teleport':
                                if len(args) == 3:
                                    x = int(args[1])
                                    y = int(args[2])
                                    player.x = x
                                    player.y = y
                                    dev_console_print('Teleported to (%d, %d)' % (x, y))
                                else:
                                    dev_console_print('usage: teleport <x> <y>')
                            elif args[0] == 'setmusic':
                                if len(args) == 2:
                                    path = args[1]
                                    world.bgm_path = path
                                    pygame.mixer.music.load(os.path.join('data', path))
                                    pygame.mixer.music.play(loops=-1)
                                else:
                                    dev_console_print('usage: setmusic <path>')
                            elif args[0] == 'setdaysky':
                                if len(args) == 2:
                                    prefix = args[1]
                                    world.day_sky_prefix = prefix
                                    day_sky.clear()
                                    day_sky.extend(load_skybox(prefix))
                                    dev_console_print('Updated day sky!')
                                else:
                                    dev_console_print('usage: setdaysky <prefix>')
                            elif args[0] == 'setnightsky':
                                if len(args) == 2:
                                    prefix = args[1]
                                    world.night_sky_prefix = prefix
                                    night_sky.clear()
                                    night_sky.extend(load_skybox(prefix))
                                    dev_console_print('Updated night sky!')
                                else:
                                    dev_console_print('usage: setnightsky <prefix>')
                            else:
                                dev_console_print('Bzzzrt! Type HELP for instructions.')

                        dev_console_input = ''
                    elif e.unicode in allowed_console_chars:
                        # Append a new character
                        ch = e.unicode
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
        
        # Delay until the next frame.
        clock.tick(40)


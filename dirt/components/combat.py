import pygame
from dirt.utils import load_sound

class CombatComponent:
    blow_fx = None

    def __init__(self, health=0, power=0):
        self.health = health
        self.power = power
        self.ignore_hooks = []
        self.attack_hooks = []
        self.death_hooks = []
        self.surrendered = False
        self.turn_skipped = False

        if CombatComponent.blow_fx is None:
            CombatComponent.blow_fx = \
              load_sound('data/blow.wav')

    def add_ignore_hook(self, proc):
        self.ignore_hooks += [proc] + self.ignore_hooks

    def add_attack_hook(self, proc):
        self.attack_hooks = [proc] + self.attack_hooks

    def add_death_hook(self, proc):
        self.death_hooks = [proc] + self.death_hooks

    def run_ignore_hooks(self, player):
        for hook in self.ignore_hooks:
            hook(player)

    def run_attack_hooks(self, player):
        for hook in self.attack_hooks:
            hook(player)

    def run_death_hooks(self, player):
        for hook in self.death_hooks:
            hook(player)

    def take_turn(self, player):
        if self.turn_skipped:
            self.turn_skipped = False
            return

        player.take_damage(self.power)
        CombatComponent.blow_fx.play()

    def skip_turn(self):
        self.turn_skipped = True

    def handle_option(self, option, player):
        if option == 'Attack':
            self.run_attack_hooks(player)

            player.attack(self)

            if self.is_dead():
                self.run_death_hooks(player)
            else:
                self.take_turn(player)

            player.pass_time()

            return True
        elif option == 'Ignore':
            self.run_ignore_hooks(player)

            player.leave_menu()

            return True
        else:
            return False

    def add_options(self, array):
        array.insert(0, 'Attack')
        array.append('Ignore')

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)

    def surrender(self):
        self.surrendered = True

    def is_dead(self):
        return self.health <= 0

    def is_done(self):
        return self.surrendered or self.is_dead()

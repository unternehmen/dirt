import random
from dirt.components.combat import CombatComponent
from dirt.components.dialogue import DialogueComponent
from dirt.components.body import BodyComponent

class Proselytizer(object):
    def __init__(self):
        self.combativeness = CombatComponent(health=2.0, power=0.5)
        self.mouth = DialogueComponent(color=(0x40, 0x40, 0xe0))
        self.appearance = BodyComponent(path='data/proselytizer.png')

        self.combativeness.add_attack_hook(self.on_attack)
        self.combativeness.add_ignore_hook(self.on_ignore)
        self.combativeness.add_death_hook(self.on_death)

        # Greet the player.
        self.mouth.say('Dost thou\nhave a\ndonation?')

    def reward(self, player):
        player.gain_money(random.randint(0, 3))

    def engage(self, player):
        self.combativeness.take_turn(player)
        player.enter_menu()

    def follow(self, player):
        self.mouth.say('A donation!')

    def draw(self, window):
        self.appearance.draw(window)
        self.mouth.draw(window)

    def tick(self):
        self.mouth.tick()

    def on_attack(self, player):
        self.mouth.say('The gods\ncurse thee!')

    def on_ignore(self, player):
        pass

    def on_death(self, player):
        self.mouth.farewell('Thou hast\nsinned...')

    def suffer(self, player, option):
        if self.combativeness.handle_option(option, player):
            # The option was handled by the combat component.
            return
        elif option == 'Donate':
            self.mouth.farewell(
                'We thank\nyou. May the\ngods be on\nyour side.')
            player.lose_money(1)
            self.combativeness.skip_turn()
            self.combativeness.surrender()
            player.pass_time()
        elif option == 'Turn out pockets':
            # The player has no money to give.
            self.mouth.farewell('Be blessed,\npoor one.')
            self.combativeness.skip_turn()
            self.combativeness.surrender()
            player.pass_time()

    def is_dead(self):
        return self.combativeness.is_done() and \
               self.mouth.is_done()

    def get_options(self, player):
        if self.combativeness.is_done():
            return []

        if player.money > 0:
            options = ['Donate']
        else:
            options = ['Turn out pockets']

        self.combativeness.add_options(options)

        return options

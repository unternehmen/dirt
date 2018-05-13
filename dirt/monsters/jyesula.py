import random
from dirt.components.combat import CombatComponent
from dirt.components.dialogue import DialogueComponent
from dirt.components.body import BodyComponent

class Jyesula:
    def __init__(self):
        self.combativeness = CombatComponent(health=100, power=1)
        self.mouth = DialogueComponent(color=(0xff, 0, 0))
        self.appearance = BodyComponent(path="data/jyesula.png")
        self.pacified = False

        self.combativeness.add_attack_hook(self.on_attack)
        self.combativeness.add_ignore_hook(self.on_ignore)
        self.combativeness.add_death_hook(self.on_death)

        self.mouth.say('Ah.  Jauld.')

    def reward(self, player):
        pass

    def engage(self, player):
        self.combativeness.take_turn(player)
        player.enter_menu()

    def follow(self, player):
        pass

    def draw(self, window):
        self.appearance.draw(window)
        self.mouth.draw(window)

    def tick(self):
        self.mouth.tick()

    def on_attack(self, player):
        messages = [
            'Hmm...',
            'No, child.',
            'Be wise.'
        ]

        self.mouth.say(messages[random.randint(0, len(messages) - 1)])

    def on_ignore(self, player):
        self.mouth.farewell('Adieu,\ncomrade.')
        self.combativeness.skip_turn()
        self.combativeness.surrender()

    def on_death(self, player):
        self.mouth.farewell('Killed by...\nyou...')

    def suffer(self, player, option):
        if self.combativeness.handle_option(option, player):
            # The option was handled by the combat component.
            return
        elif option == 'Lettre':
            self.mouth.farewell('I have no\ntime to read.\nPlease take\ncare of it.')
            self.combativeness.skip_turn()
            self.combativeness.surrender()
            player.pass_time()
        elif option == 'Pester':
            self.mouth.farewell('I must away,\nJauld.')
            self.combativeness.skip_turn()
            self.combativeness.surrender()
            player.pass_time()

    def is_dead(self):
        return self.combativeness.is_done() and \
               self.mouth.is_done()

    def get_options(self, player):
        if self.combativeness.is_done():
            return []

        options = ['Lettre', 'Pester']

        self.combativeness.add_options(options)

        return options

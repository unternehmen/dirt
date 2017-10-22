from components.combat import CombatComponent
from components.dialogue import DialogueComponent
from components.body import BodyComponent

class Rat:
    def __init__(self):
        self.combativeness = CombatComponent(health=1.0, power=0.5)
        self.mouth = DialogueComponent(color=(0x80, 0x80, 0))
        self.appearance = BodyComponent(path="data/rat.png")
        self.pacified = False

        self.combativeness.add_attack_hook(self.on_attack)
        self.combativeness.add_ignore_hook(self.on_ignore)
        self.combativeness.add_death_hook(self.on_death)

        self.mouth.say('*sniff*!\n  *sniff*!')

    def reward(self, player):
        pass

    def engage(self, player):
        self.combativeness.take_turn(player)
        player.enter_menu()

    def follow(self, player):
        if self.pacified:
            self.mouth.say('*sniff*...')
        else:
            self.mouth.say('*squarrr*!')

    def draw(self, window):
        self.appearance.draw(window)
        self.mouth.draw(window)

    def tick(self):
        self.mouth.tick()

    def on_attack(self, player):
        self.mouth.say('*squeaky\nsqueak*!')
        self.pacified = False

    def on_ignore(self, player):
        self.mouth.say('*squeeeak*!')

    def on_death(self, player):
        self.mouth.farewell('*squoo*...')

    def suffer(self, player, option):
        if self.combativeness.handle_option(option, player):
            # The option was handled by the combat component.
            return
        elif option == 'Back away slowly':
            if self.pacified:
                self.mouth.farewell('...')
                self.combativeness.skip_turn()
                self.combativeness.surrender()
            else:
                self.mouth.say('*SQUEEEAK!*')
            player.pass_time()
        elif option == 'Bide':
            self.mouth.say('... *squeak*?')
            self.pacified = True
            player.pass_time()

    def is_dead(self):
        return self.combativeness.is_done() and \
               self.mouth.is_done()

    def get_options(self, player):
        if self.combativeness.is_done():
            return []

        options = ['Back away slowly', 'Bide']

        self.combativeness.add_options(options)

        return options

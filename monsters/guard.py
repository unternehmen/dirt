from components.combat import CombatComponent
from components.dialogue import DialogueComponent
from components.body import BodyComponent

class Guard:
    def __init__(self):
        self.combativeness = CombatComponent(health=10.0, power=0.5)
        self.mouth = DialogueComponent(color=(0xff, 0x99, 0x99))
        self.appearance = BodyComponent(path="data/guard.png")

        self.combativeness.add_attack_hook(self.on_attack)
        self.combativeness.add_ignore_hook(self.on_ignore)

        # Whether this guard is hostile yet.
        self.hostile = False

        # Greet the player.
        self.mouth.say('Greetings,\ncitizen.\nAnything\nto report?')

    def reward(self, player):
        pass

    def engage(self, player):
        self.combativeness.take_turn(player)
        player.enter_menu()

    def on_attack(self, player):
        if not self.hostile:
            self.mouth.say('Assault!')
            self.hostile = True
        else:
            self.mouth.say('Not on my watch!')

    def on_ignore(self, player):
        if not self.hostile:
            self.mouth.farewell('Have a nice\nday, citizen.')
            self.combativeness.skip_turn()
            self.combativeness.surrender()
        else:
            self.mouth.say('Trying to run,\nare you?!')

    def follow(self, player):
        if self.hostile:
            self.mouth.say('Get back here!')

    def suffer(self, player, option):
        if self.combativeness.handle_option(option, player):
            # The option was handled by the combat component.
            return
        else:
            if option == 'Advice':
                # The player has asked about the local news.
                self.mouth.farewell(
                    "I'd watch\nthe shadows\nif I were\nyou.")
                self.combativeness.skip_turn()
                self.combativeness.surrender()
                player.pass_time()
            elif option == 'Proselytizers':
                # The player has no money to give.
                self.mouth.farewell(
                    "We guards\ndon't meddle\nwith the\nchurch.")
                self.combativeness.skip_turn()
                self.combativeness.surrender()
                player.pass_time()

    def is_dead(self):
        return self.combativeness.is_done() and \
               self.mouth.is_done()

    def get_options(self, player):
        if self.combativeness.is_done():
            return []

        options = ['Advice', 'Proselytizers']

        self.combativeness.add_options(options)

        return options

    def draw(self, window):
        self.appearance.draw(window)
        self.mouth.draw(window)

    def tick(self):
        self.mouth.tick()


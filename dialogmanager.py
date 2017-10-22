import pygame
from utils import draw_text

class Say(object):
    def __init__(self, text):
        self.text = text

class Choose(object):
    def __init__(self, *choices):
        self.choices = choices

class BigMessage(object):
    def __init__(self, text):
        self.text = text

class DialogManager(object):
    font = None
    bubble_image = None

    def __init__(self):
        self.mode      = 'inactive'   # 'inactive' | 'saying' | 'choosing'
        self.thread    = None
        self.backdrop  = None

        # for Say commands
        self.text      = ''
        self.timer     = 0

        # for Choose commands
        self.selection = 0
        self.choices   = []

        # load the font
        if DialogManager.font is None:
            DialogManager.font = \
              pygame.font.Font(None, 15)

        if DialogManager.bubble_image is None:
            DialogManager.bubble_image = \
              pygame.image.load('data/speech_bubble.png')

    def _advance(self, data=None):
        try:
            command = self.thread.send(data)
        except StopIteration:
            self.mode = 'inactive'
            return

        if isinstance(command, Say):
            self.mode      = 'saying'
            self.text      = command.text
            self.timer     = 30
        elif isinstance(command, Choose):
            self.mode      = 'choosing'
            self.choices   = command.choices
            self.selection = 0
        elif isinstance(command, BigMessage):
            self.mode      = 'bigmessage'
            self.text = command.text
        else:
            assert False, 'no such dialog command: %s' % str(command)

    def start(self, action, backdrop=None):
        self.thread = action()
        self._advance()
        self.backdrop = backdrop

    def key_pressed(self, key):
        if self.mode == 'choosing':
            if key == pygame.K_DOWN:
                if self.selection < len(self.choices) - 1:
                    self.selection += 1
            elif key == pygame.K_UP:
                if self.selection > 0:
                    self.selection -= 1
            elif key == pygame.K_RETURN:
                selection = self.selection
                self.choices = []
                self.selection = 0
                self._advance(selection)
        elif self.mode == 'bigmessage':
            if key == pygame.K_RETURN:
                self._advance()

    def update(self):
        if self.mode == 'saying':
            self.timer -= 1

            if self.timer <= 0:
                self.text = ''
                self.timer = 0
                self._advance()

    def draw(self, window, font):
        # Draw the backdrop if applicable.
        if self.mode != 'inactive' and self.backdrop is not None:
            window.blit(self.backdrop, (0, 0))

        if self.mode == 'saying':
            # Draw the message.
            window.blit(DialogManager.bubble_image, (0, 0))
            draw_text(DialogManager.font,
                      self.text, (0, 0, 0),
                      window, 10, 10)
        elif self.mode == 'choosing':
            # Draw the choices.
            cursor = 165
            for i, choice in enumerate(self.choices):
                block = font.render(choice, True, (0, 0, 0))

                window.blit(block, (10, cursor))

                if i == self.selection:
                    window.fill((0, 0, 0), (3, cursor + 5, 4, 4))

                cursor += 18
        elif self.mode == 'bigmessage':
            window.fill((255, 255, 255))
            draw_text(font, self.text, (0, 0, 0), window, 20, 20)
            draw_text(font, '[Enter]', (0, 0, 0), window, 250, 210)

    def is_active(self):
        return self.mode != 'inactive'

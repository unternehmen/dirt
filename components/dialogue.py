import pygame
from utils import draw_text

class DialogueComponent:
    font = None
    bubble_img = None

    def __init__(self, color=(0, 0, 0)):
        self.message_text = ""
        self.message_timer = 0
        self.closing = False
        self.color = color
        self.start_hooks = []
        self.stop_hooks = []

        if DialogueComponent.font is None:
            DialogueComponent.font = \
              pygame.font.Font(None, 15)

        if DialogueComponent.bubble_img is None:
            DialogueComponent.bubble_img = \
              pygame.image.load('data/speech_bubble.png')

    def say(self, text):
        self.message_text = text
        self.message_timer = 30
        for hook in self.start_hooks:
            hook()

    def farewell(self, text):
        self.say(text)
        self.closing = True

    def draw(self, window):
        if self.message_timer > 0:
            window.blit(DialogueComponent.bubble_img, (0, 0))
            draw_text(DialogueComponent.font,
                      self.message_text, self.color,
                      window, 10, 10)

    def tick(self):
        if self.message_timer > 0:
            self.message_timer -= 1

            if self.message_timer == 0:
                for hook in self.stop_hooks:
                    hook()

    def is_done(self):
        return self.message_timer == 0 and self.closing

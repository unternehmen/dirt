import pygame

class BodyComponent:
    def __init__(self, path=''):
        self.sprite = pygame.image.load(path)

    def draw(self, window):
        window.blit(self.sprite, (0, 0))

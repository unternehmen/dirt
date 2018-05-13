import pygame
from dirt.utils import load_image

class BodyComponent:
    def __init__(self, path=''):
        self.sprite = load_image(path)

    def draw(self, window):
        window.blit(self.sprite, (0, 0))

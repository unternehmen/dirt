# -*- coding: utf-8 -*-

class Timer:
    '''A class that helps keep track of timed callbacks.'''
    def __init__(self, number_of_frames, callback=None, data=None):
        self.counter = 0
        self.number_of_frames = number_of_frames
        self.callback = callback
        self.data = data

    def advance(self):
        self.counter += 1

    def is_done(self):
        return self.counter >= self.number_of_frames

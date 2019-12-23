import pygame
import sys
import os
from start import load_image, start_screen

start_screen()
player_group = pygame.sprite.Group()
images = {'player': load_image('player.jpg')}


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group)

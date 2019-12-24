import pygame
import sys
from start import *

all_sprites = pygame.sprite.Group()
lessons_group = pygame.sprite.Group()


class Lesson(pygame.sprite.Sprite):
    def __init__(self, n):
        super().__init__(lessons_group, all_sprites)
        self.image = load_image(f'lesson{n}.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = 160
        if n == 1:
            self.rect.y = 25
        elif n == 2:
            self.rect.y = 250
        else:
            self.rect.y = 475

    def update(self, *args):
        if args[0] == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(args[0].pos):



def display_lessons():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    for i in range(3):
        Lesson(i + 1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            all_sprites.update(event)
            all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


display_lessons()

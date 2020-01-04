import random
import pygame
import os
import sys

FPS = 30
pygame.init()
size = WIDTH, HEIGHT = 450, 650
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    sp = []
    intro_text = ["PySpace", 'Играть']
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = [160, -170]
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        text_coord[1] += 230
        intro_rect.top = text_coord[1]
        text_coord[0] -= 20
        intro_rect.x = text_coord[0]
        text_coord[0] += intro_rect.height
        sp.append(intro_rect)
        screen.blit(string_rendered, intro_rect)
    r = sp[1]
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN and r.collidepoint(event.pos):
                return display_lessons()
        pygame.display.flip()
        clock.tick(FPS)


all_sprites = pygame.sprite.Group()
my_group = pygame.sprite.Group()
lessons_group = pygame.sprite.Group()


class MySprite(pygame.sprite.Sprite):
    def __init__(self, pov, x, y):
        super().__init__(all_sprites, my_group)
        if not pov:
            self.image = load_image('strelki.png', -1)
        else:
            self.image = load_image('strelki1.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        if self.rect.collidepoint(args[0].pos):
            return True
        else:
            return False


class Lesson(pygame.sprite.Sprite):
    def __init__(self, n):
        super().__init__(lessons_group, all_sprites)
        self.image = load_image(f'lesson{n}.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = 160
        self.n = n
        if n == 1:
            self.rect.y = 25
        elif n == 2:
            self.rect.y = 250
        else:
            self.rect.y = 475

    def update(self, *args):
        if self.rect.collidepoint(args[0].pos):
            return generate_level(f'level{self.n}.txt'), self.n
        else:
            return False


def display_lessons(n=None):
    if n is None:
        fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        for i in range(3):
            Lesson(i + 1)
        MySprite(True, 0, 0)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i in lessons_group:
                        if i.update(event):
                            return i.update(event)
                    for i in my_group:
                        if i.update(event):
                            return start_screen()
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
    else:
        for i in lessons_group:
            if i.n == n:
                return generate_level(f'level{n}.txt'), n


def generate_level(filename):
    filename = "levels/" + filename
    sp = []
    with open(filename, mode='r') as mapfile:
        text = mapfile.readlines()
        map_width = int(text[1])
        for i in text[0].strip().split(';'):
            sp1 = []
            if not i:
                continue
            for j in range(0, len(i) - 1, 2):
                k = i[j]
                typ = i[j + 1]
                if typ == 'm':
                    elem = '*'
                else:
                    elem = typ
                # m - Метеоры
                # k - корабли, которые не двигаются
                # n - корабли которые двигаются
                # b - босс
                sp1.extend((k, elem))
            sp.append(sp1)
    map = []
    sp = sp[::-1]
    for i in range(len(sp)):
        s = []
        for j in range(0, len(sp[i]) - 1, 2):
            k = int(sp[i][j])
            elem = sp[i][j + 1]
            s += k * elem
        if map_width < len(s):
            s = s[:map_width]
        if not s.count('b'):
            s += (map_width - len(s)) * '-'
            random.shuffle(s)
            map.append(''.join(s))
        else:
            lw = map_width
            if lw % 2 != 0:
                pl_xn = (lw - 1) // 2
            else:
                pl_xn = lw // 2
            sp1 = []
            for i1 in range(lw):
                if i1 != pl_xn:
                    sp1.append('-')
                else:
                    sp1.append('b')
            map.append(''.join(sp1))

    return map


def end_screen(won, n):
    sp = []
    if won:
        intro_text = ["Вы победили"]
    else:
        intro_text = ["Вы проиграли"]
    intro_text.append("К уровням")
    intro_text.append("Главное меню")
    if won and n != 3:
        intro_text.append('К следующему уровню')  # Пока не работает, сделаю после 2-3 релиза
    else:
        intro_text.append('Повторить попытку')
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = [(100, 100), (120, 300), (95, 350)]
    if won and n != 3:
        text_coord.append((30, 250))
    else:
        text_coord.append((75, 250))
    for line in range(len(intro_text)):
        string_rendered = font.render(intro_text[line], 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord[line][1]
        intro_rect.x = text_coord[line][0]
        sp.append(intro_rect)
        screen.blit(string_rendered, intro_rect)
    r = sp[1]  # Переход к уровням
    r1 = sp[2]  # Переход к главному меню
    r2 = sp[3]  # Переход к повтору или следующему уровню
    # Зависит от прохождения уровня
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if r.collidepoint(event.pos):
                    return display_lessons()
                if r1.collidepoint(event.pos):
                    return start_screen()
                if r2.collidepoint(event.pos):
                    if not won or n == 3:
                        return display_lessons(n)
                    else:
                        return display_lessons(n + 1)
        pygame.display.flip()
        clock.tick(FPS)

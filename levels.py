import random
import pygame
import os
import sys


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


def sound_name(name):
    fullname = os.path.join('sound', name)
    return fullname


def load_sound(name):
    snd = pygame.mixer.Sound(sound_name(name))
    return snd


FPS = 30
pygame.init()
size = WIDTH, HEIGHT = 450, 650
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
music = 0
images = {'player': load_image('player.png', -1), 'meteor0': load_image('meteor.png', -1),
          'meteor90': load_image('meteor90.png', -1), 'meteor180': load_image('meteor180.png', -1),
          'meteor270': load_image('meteor270.png', -1),
          'red_weap': load_image('red_weapon.png', -1), 'shkala': load_image('shkala.png', -1),
          'amk': load_image('amk.png', -1), 'enemy': load_image('enemy.png', -1),
          'gre_weap': load_image('green_weapon.png', -1), 'boss': load_image('boss.png', -1),
          'osk1': load_image("oskol1.png", -1), 'osk2': load_image("oskol2.png", -1),
          'osk3': load_image("oskol3.png", -1), 'fon1': load_image('fon.jpg'), 'fon2': load_image('fon2.jpg'),
          'fon3': load_image('fon3.jpg'), 'strelki': load_image('strelki.png', -1),
          'sterki1': load_image('strelki1.png', -1), 'fonb1': load_image('fonb.jpg'), 'fonb2': load_image('fonb2.jpg'),
          'fonb3': load_image('fonb3.jpg'), 'boom': load_image('vsr.gif', -1)}
sounds = {'main_theme': sound_name("John Williams_-_Ben Kenobi's Death _ Tie Fighter Attack.mp3"),
          'game_theme': sound_name("Order 66.mp3"), 'won_theme': sound_name('Cantina band.mp3'),
          'lose_theme': sound_name("John_Williams_-_Approaching_the_Throne_(musicport.org).mp3"),
          'boss_theme': sound_name("boss_theme.mp3"),
          'enemy explode': load_sound("TIE fighter explode.wav"), 'enemy fire': load_sound("TIE fighter fire 1.wav"),
          'player fire': load_sound("XWing fire.wav"), 'player explode': load_sound("XWing explode.wav"),
          'boss fire': load_sound("TIE fighter fire 3.wav")}


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    global music
    sp = []
    intro_text = ["PySpace", 'Играть']
    if music == 0:
        pygame.mixer_music.load(sounds['main_theme'])
        pygame.mixer_music.play(-1)
        pygame.mixer_music.set_volume(0.6)
        music = 1
    screen.fill((0, 0, 0))
    Fon(-400, -200, fon_group, 1)
    fon_group.draw(screen)
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
            elif event.type == pygame.MOUSEBUTTONDOWN and r.collidepoint(event.pos):
                return display_lessons()
        pygame.display.flip()
        clock.tick(FPS)


player = None
all_sprites = pygame.sprite.Group()
my_group = pygame.sprite.Group()
lessons_group = pygame.sprite.Group()
fon_group = pygame.sprite.Group()


class MySprite(pygame.sprite.Sprite):
    def __init__(self, pov, x, y):
        super().__init__(all_sprites, my_group)
        if not pov:
            self.image = images['strelki']
        else:
            self.image = images['sterki1']
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
            if self.n == 3:
                pygame.mixer_music.load(sounds['boss_theme'])
            else:
                pygame.mixer_music.load(sounds['game_theme'])
            pygame.mixer_music.play(-1)
            return generate_level(f'level{self.n}.txt'), self.n
        else:
            return False


def display_lessons(n=None):
    global music
    if n is None:
        screen.fill((0, 0, 0))
        Fon(-10, -10, fon_group, 2)
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
                if n == 3:
                    pygame.mixer_music.load(sounds['boss_theme'])

                else:
                    pygame.mixer_music.load(sounds['game_theme'])
                pygame.mixer_music.play(-1)
                pygame.mixer_music.set_volume(0.6)
                music = 0
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
                # n - корабли которые двигаются
                # b - босс
                sp1.extend((k, elem))
            sp.append(sp1)
    map1 = []
    sp = sp[::-1]
    for i in range(len(sp)):
        s = []
        for j in range(0, len(sp[i]) - 1, 2):
            k = int(sp[i][j])
            elem = sp[i][j + 1]
            s += k * elem
        if map_width < len(s):
            s = s[:map_width]
        if not s.count('b') and not s.count('n'):
            s += (map_width - len(s)) * '-'
            random.shuffle(s)
            map1.append(''.join(s))
        elif s.count('n'):
            s = '--n'
            s += (map_width - len(s)) * '-'
            map1.append(''.join(s))
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
            map1.append(''.join(sp1))

    return map1


class Fon(pygame.sprite.Sprite):
    def __init__(self, x, y, fon_gr, n, b=False):
        super().__init__(all_sprites, fon_gr)
        if not b:
            self.image = images[f'fon{n}']
        else:
            self.image = images[f'fonb{n}']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.n = 0


def end_screen(won, n):
    global music
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
    if won:
        pygame.mixer_music.load(sounds['won_theme'])
        pygame.mixer_music.play(-1)
        pygame.mixer_music.set_volume(0.6)
    else:
        pygame.mixer_music.load(sounds['lose_theme'])
    pygame.mixer_music.play(-1)
    music = 0
    screen.fill((0, 0, 0))
    Fon(-400, -200, fon_group, 3)
    fon_group.draw(screen)
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

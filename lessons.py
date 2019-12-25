import random
from start import *

all_sprites = pygame.sprite.Group()
lessons_group = pygame.sprite.Group()


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
            return generate_level(f'level{self.n}.txt')
        else:
            return False


def display_lessons():
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    for i in range(3):
        Lesson(i + 1)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i in lessons_group:
                    if i.update(event):
                        return i.update(event)

        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def generate_level(filename):
    filename = "data/" + filename
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
        s += (map_width - len(s)) * '-'
        random.shuffle(s)
        map.append(''.join(s))
    return map



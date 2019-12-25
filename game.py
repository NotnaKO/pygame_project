from lessons import *
import pygame

player_group = pygame.sprite.Group()
meteors_group = pygame.sprite.Group()
images = {'player': load_image('player.jpg', -1), 'meteor': load_image('meteor.jpg', -1)}


class Player(pygame.sprite.Sprite):
    def __init__(self, y, x):
        super().__init__(player_group, all_sprites)
        self.image = images['player']
        self.rect = self.image.get_rect()
        self.rect.x = x * COLCOUNT
        self.rect.y = y * GAME_SPEED
        self.play = True
        self.damage = 10
        self.health = 100
        self.speed = PLAYER_SPEED

    def hurt(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.play = False

    def heal(self, health):
        self.health += health
        if self.health > 100:
            self.health = 100

    def move(self):
        if self.play:
            self.rect.y -= self.speed

    def update(self):  # делает стандартный ход
        self.move()
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)
            spr.hurt(self.damage)
            self.hurt(self.damage)
        if righting and not lefting:
            self.move_right()
        if lefting and not righting:
            self.move_left()
        if accel and not deccel:
            self.acceleration()
        if deccel and not accel:
            self.deceleration()

    def move_right(self):
        if self.rect.right + PLAYER_SPEED <= WIDTH:
            self.rect.x += PLAYER_SPEED

    def move_left(self):
        if self.rect.x - PLAYER_SPEED >= 0:
            self.rect.x -= PLAYER_SPEED

    def acceleration(self):  # ускорение
        self.rect.y -= PLAYER_SPEED // 2

    def deceleration(self):
        self.rect.y += PLAYER_SPEED // 2


class Meteor(pygame.sprite.Sprite):
    def __init__(self, y, x):
        super().__init__(meteors_group, all_sprites)
        self.image = images['meteor']
        self.rect = self.image.get_rect()
        self.rect.y = y * GAME_SPEED
        self.rect.x = x * COLCOUNT
        self.vect = [random.randint(-1, 1), random.randint(0, 1)]
        self.damage = 50
        self.health = 30

    def move(self):
        self.rect.x += self.vect[0]
        self.rect.y += self.vect[1]

    def hurt(self, damage):
        self.health -= damage
        if self.health <= 0:
            pass  # Здесь должна быть анимация уничтожения метеора


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0

    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h - HEIGHT)


GAME_SPEED = 200  # дальность расположения метеоров
COLCOUNT = WIDTH // 9  # Адаптировать к разным уровням
MYEVENTTYPE = 10
PLAYER_SPEED = 2
start_screen()
levelmap = display_lessons()
camera = Camera()
all_sprites = pygame.sprite.Group()
lessons_group = None
lw = len(levelmap[0])
if lw % 2 != 0:
    pl_xn = (lw - 1) // 2
else:
    pl_xn = lw // 2
sp = []
for i in range(lw):
    if i != pl_xn:
        sp.append('-')
    else:
        sp.append('P')
levelmap.append(''.join(sp).replace('P', '-'))
levelmap.append(''.join(sp))


def view_lesson():
    for i in range(len(levelmap)):
        for j in range(len(levelmap[i])):
            if levelmap[i][j] == '-':
                continue
            elif levelmap[i][j] == '*':
                Meteor(i, j)
            elif levelmap[i][j] == 'P':
                player = Player(i, j)
    return player


player = view_lesson()
fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
screen.blit(fon, (0, 0))
righting, lefting = False, False
accel, deccel = False, False

while True:
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            terminate()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                lefting = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                righting = True
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                accel = True
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                deccel = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                lefting = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                righting = False
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                accel = False
            if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                deccel = False
    player.update()
    camera.update(player)
    for sprite in all_sprites:
        camera.apply(sprite)
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

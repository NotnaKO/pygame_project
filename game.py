from end import *
import pygame


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
        self.speed = PLAYERSPEED
        self.ammunition = PLAYERAMMUN

    def hurt(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.play = False
            self.delete()

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
        if self.rect.right + PLAYERSPEED <= WIDTH:
            self.rect.x += PLAYERSPEED

    def move_left(self):
        if self.rect.x - PLAYERSPEED >= 0:
            self.rect.x -= PLAYERSPEED

    def acceleration(self):  # ускорение
        self.rect.y -= PLAYERSPEED // 2

    def deceleration(self):
        self.rect.y += PLAYERSPEED // 2

    def shot_e(self):
        if self.ammunition > 0:
            PlayerWeapon(1)
        self.ammunition -= 1

    def shot_q(self):
        if self.ammunition > 0:
            PlayerWeapon(0)
        self.ammunition -= 1

    def delete(self):
        global player
        player_group.remove(self)
        all_sprites.remove(self)
        player = None


class Meteor(pygame.sprite.Sprite):
    def __init__(self, y, x):
        super().__init__(meteors_group, all_sprites)
        self.image = images['meteor']
        self.rect = self.image.get_rect()
        self.rect.y = y * GAME_SPEED
        self.rect.x = x * COLCOUNT
        self.vect = [random.randint(-1, 1), random.randint(0, 1)]
        self.damage = 50
        self.chl = False
        self.chr = False
        self.health = 30
        self.a = False

    def move(self):
        self.rect.x += self.vect[0]
        self.rect.y += self.vect[1]

    def hurt(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.delete()

    def delete(self):  # Пока так, но позже с анимацией
        meteors_group.remove(self)
        all_sprites.remove(self)

    def fun(self):
        self.a = False

    def change_moving(self):
        self.vect = [-self.vect[0], self.vect[1]]

    def change_moving_with_spr(self, spr):
        if self.a or spr.a:
            return
        self.a = True
        spr.a = True
        if spr.rect.x <= self.rect.x:
            if spr.vect[0] != -2:
                spr.vect[0] -= 1
            if self.vect[0] != 2:
                self.vect[0] += 1
        if spr.rect.x > self.rect.x:
            if spr.vect[0] != 2:
                spr.vect[0] += 1
            if self.vect[0] != -2:
                self.vect[0] -= 1
        if spr.rect.y <= self.rect.y:
            if spr.vect[1] >= 1:
                spr.vect[1] -= 1
            if self.vect[1] != 2:
                self.vect[1] += 1
        if spr.rect.y > self.rect.y:
            if spr.vect[1] != 2:
                spr.vect[1] += 1
            if self.vect[1] >= 1:
                self.vect[1] -= 1
        self.hurt(1)
        spr.hurt(1)

    def pas_move(self):
        self.rect.y += 1

    def update(self):
        if player.rect.y - (self.rect.y + self.rect.h) > HEIGHT:
            pas = True
        else:
            pas = False
        if not pas:
            self.move()
            sp_spr = pygame.sprite.spritecollide(self, meteors_group, False)
            spr = None
            for i1 in sp_spr:
                if i1 is not self:
                    spr = i1
            if player is not None:
                if spr is not None:
                    self.change_moving_with_spr(spr)
                    spr.change_moving_with_spr(self)
                if player.rect.y - (self.rect.y + self.rect.h) > HEIGHT:
                    if self.rect.right >= WIDTH and not self.chr:
                        self.chr = True
                        self.change_moving()
                    if self.rect.x < 0 and not self.chl:
                        self.chl = True
                        self.change_moving()
                    if self.rect.right < WIDTH:
                        self.chr = False
                    if self.rect.x >= 0:
                        self.chl = False
                if self.rect.y > player.rect.y + player.rect.h or self.rect.x >= WIDTH or self.rect.right < 0:
                    self.delete()
        else:
            self.pas_move()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, enemies_group)
        self.image = images['enemy']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Camera:
    def __init__(self):
        self.dy = 0

    def apply(self, obj):
        if type(obj) != Shakla and type(obj) != AmCount and type(obj) != Enemy:
            obj.rect.y += self.dy

    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h - HEIGHT)


class Shakla(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = images['shkala']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.rw = 94
        self.rh = 13
        self.color = None

    def draw(self, h):
        if h >= 70:
            self.color = pygame.Color('green')
        elif 30 <= h < 70:
            self.color = pygame.Color('yellow')
        else:
            self.color = pygame.Color('red')
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y + 12, self.rw * (h / 100), self.rh - 3))

    def update(self):
        if player is not None:
            self.draw(player.health)


class AmCount(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites)
        self.image = images['amk']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, amm):
        if amm < 0:
            amm = 0
        intro_text = [str(amm)]
        font = pygame.font.Font(None, 20)
        text_coord = [(self.rect.x + 22, self.rect.y + 8)]
        for line in range(len(intro_text)):
            string_rendered = font.render(intro_text[line], 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            intro_rect.top = text_coord[line][1]
            intro_rect.x = text_coord[line][0]
            screen.blit(string_rendered, intro_rect)

    def update(self):
        if player is not None:
            self.draw(player.ammunition)


def view_lesson():
    player1 = None
    for i1 in range(len(levelmap)):
        for j in range(len(levelmap[i1])):
            if levelmap[i1][j] == '-':
                continue
            elif levelmap[i1][j] == '*':
                Meteor(i1 + 1, j)
            elif levelmap[i1][j] == 'P':
                player1 = Player(i1, j)
    return player1


class PlayerWeapon(pygame.sprite.Sprite):
    def __init__(self, n1):
        super().__init__(all_sprites, weapons_group)
        self.image = images['red_weap']
        self.rect = self.image.get_rect()
        if n1 == 0:
            self.rect.x = player.rect.x + 2
        else:
            self.rect.x = player.rect.right - 2
        self.rect.y = player.rect.y
        self.damage = 30

    def move(self):
        self.rect.y -= PLAYERSPEED * 3

    def update(self):
        self.move()
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)
            spr.hurt(self.damage)
            self.damage = 0
            self.delete()

    def delete(self):
        weapons_group.remove(self)
        all_sprites.remove(self)


GAME_SPEED = 200  # дальность расположения метеоров
MYEVENTTYPE = 10
PLAYERSPEED = 2
PLAYERAMMUN = 20
METEORSK = 0  # Урон от столкновения между собой метеоров
player_group = pygame.sprite.Group()
meteors_group = pygame.sprite.Group()
weapons_group = pygame.sprite.Group()
enemies_group = pygame.sprite.Group()
images = {'player': load_image('player.png', -1), 'meteor': load_image('meteor.jpg', -1),
          'red_weap': load_image('red_weapon.png', -1), 'shkala': load_image('shkala.png', -1),
          'amk': load_image('amk.png', -1), 'enemy': load_image('enemy.jpg', -1)}
camera = Camera()
all_sprites = pygame.sprite.Group()
levelmap, n = start_screen()
while True:
    lessons_group = None
    lw = len(levelmap[0])
    COLCOUNT = WIDTH // lw
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
    for i in range(5):
        levelmap.append(''.join(sp).replace('P', '-'))
    levelmap.append(''.join(sp))

    player = view_lesson()
    fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
    screen.blit(fon, (0, 0))
    righting, lefting = False, False
    accel, deccel = False, False
    sk = Shakla(0, 0)
    am = AmCount(WIDTH - 50, 4)
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
                if event.key == pygame.K_e and player is not None:
                    player.shot_e()
                if event.key == pygame.K_q and player is not None:
                    player.shot_q()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    lefting = False
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    righting = False
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    accel = False
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    deccel = False
        if player is None:
            levelmap, n = end_screen(False, n)
            break
        k = 0
        for i in meteors_group:
            k += 1
        if k == 0:
            levelmap, n = end_screen(True, n)
            break
        if player is not None:
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
        all_sprites.draw(screen)
        all_sprites.update()
        for i in meteors_group:
            i.fun()
        pygame.display.flip()
        clock.tick(FPS)

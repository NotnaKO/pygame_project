from levels import *


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        self.image = images['player']
        self.rect = self.image.get_rect()
        self.rect.x = x * COLCOUNT
        self.rect.y = y * GAME_SPEED
        self.damage = 30
        self.health = 100
        self.speed = PLAYERSPEED
        self.ammunition = PLAYERAMMUN

    def hurt(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.delete()

    def heal(self, health):
        self.health += health
        if self.health > 100:
            self.health = 100

    def move(self):
        if player is not None:
            self.rect.y -= self.speed

    def reamm(self):
        if self.ammunition < 10:
            self.ammunition += 1
        if self.ammunition < 7:
            self.ammunition += 1
        if self.ammunition < 4:
            self.ammunition += 1

    def update(self):  # делает стандартный ход
        self.move()
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)
            spr.hurt(self.damage)
            self.hurt(spr.damage)
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
            s = sounds['player fire']
            s.play()
        self.ammunition -= 1

    def shot_q(self):
        if self.ammunition > 0:
            PlayerWeapon(0)
            s = sounds['player fire']
            s.play()
        self.ammunition -= 1

    def delete(self):
        global player
        s = sounds['player explode']
        s.play()
        player_group.remove(self)
        all_sprites.remove(self)
        player = None


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
        self.rect.y -= PLAYERSPEED * 4

    def update(self):
        self.move()
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)
        elif pygame.sprite.spritecollideany(self, enemies_group):
            spr = pygame.sprite.spritecollideany(self, enemies_group)
        elif boss is not None and pygame.sprite.spritecollideany(self, boss_group):
            spr = boss
        else:
            spr = None
        if spr is not None:
            spr.hurt(self.damage)
            self.damage = 0
            self.delete()
        if player is None:
            self.delete()
        elif player.rect.top - HEIGHT > self.rect.top + self.rect.h:
            self.delete()

    def delete(self):
        weapons_group.remove(self)
        all_sprites.remove(self)


class Meteor(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(meteors_group, all_sprites)
        grad = random.choice(('0', '90', '180', '270'))
        self.image = images[f"meteor{grad}"]
        self.rect = self.image.get_rect()
        self.rect.y = y * GAME_SPEED
        self.rect.x = x * COLCOUNT
        self.vect = list()
        self.vect.append(random.randint(-1, 1))
        self.vect.append(random.randint(-1, 1))
        self.damage = 20
        self.chl = False
        self.chr = False
        self.health = 30
        self.a = False

    def move(self):
        self.rect.x += self.vect[0]
        self.rect.y += self.vect[1]

    def hurt(self, damage):
        if self.check():
            self.health -= damage
            if self.health <= 0:
                self.delete()

    def delete(self):  # Пока так, но позже с анимацией
        meteors_group.remove(self)
        all_sprites.remove(self)
        particle_count = 3
        # возможные скорости
        numbers = range(-5, 6)
        for _ in range(particle_count):
            Oskol((self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2), random.choice(numbers),
                  random.choice(numbers))

    def fun(self):
        self.a = False

    def check(self):
        if player.rect.top + player.rect.h - self.rect.top < HEIGHT:
            return True
        return False

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
        self.hurt(METEORSK)
        spr.hurt(METEORSK)

    def pas_move(self):
        pass

    def update(self):
        if player is None:
            return
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
                    self.kill()
        else:
            self.pas_move()


class Oskol(pygame.sprite.Sprite):
    fire = [images['osk1'], images['osk2'], images['osk3']]
    for i in range(len(fire)):
        for scale in (20, 17, 22):
            fire.append(pygame.transform.scale(fire[i], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites, osk_group)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY
        self.n = 0

    def update(self):
        self.n += 1
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if player is None:
            return
        if self.rect.y > player.rect.y + player.rect.h or self.rect.x >= WIDTH or self.rect.right < 0 \
                or self.n > FPS * 2:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, enemies_group)
        self.image = images['enemy']
        self.rect = self.image.get_rect()
        if 0 < x < WIDTH:
            self.rect.x = x * COLCOUNT
        elif x <= 0:
            self.rect.x = 2
        else:
            self.rect.x = WIDTH - 2
        self.rect.y = y * GAME_SPEED
        self.damage = 30
        self.health = 60
        self.danger = 0
        self.danger_r = 0
        self.danger_l = 0
        self.ammunition = 10
        self.lefting = False
        self.righting = False
        self.coord = self.rect.x
        self.sp = []
        self.shot = False

    def hurt(self, dam):
        if self.get_moved():
            self.health -= dam
            if self.health <= 0:
                self.delete()

    def delete(self):
        s = sounds['enemy explode']
        s.play()
        enemies_group.remove(self)
        all_sprites.remove(self)

    def heal(self, health):
        self.health += health
        if self.health > 60:
            self.health = 60

    def reamm(self):
        if self.ammunition <= 15:
            self.ammunition += 1
        if self.ammunition < 7:
            self.ammunition += 1

    def shot_left(self):
        if self.ammunition > 0 and self.shot == 2:
            EnemyWeapon(self, 0)
            self.ammunition -= 1
            self.shot = False

    def shot_right(self):
        if self.ammunition > 0 and self.shot == 1:
            EnemyWeapon(self, 1)
            self.ammunition -= 1
            self.shot = False

    def move_right(self):
        if self.rect.right + ENEMYSPEED <= WIDTH + 5:
            self.rect.x += ENEMYSPEED

    def move_left(self):
        if self.rect.x - ENEMYSPEED >= -5:
            self.rect.x -= ENEMYSPEED

    def shot1(self, n1):
        if self.get_moved():
            s = sounds['enemy fire']
            s.play()
            if n1 == 1:
                self.shot_right()
            else:
                self.shot_left()

    def update(self):
        self.danger = 0
        self.danger_r = 0
        self.danger_l = 0
        self.sp = []
        k1 = 0
        if player is None:
            return
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)
            spr.hurt(self.damage)
            self.hurt(spr.damage)
        for i1 in weapons_group:
            if type(i1) == PlayerWeapon:
                k1 += 1
        if not self.righting and not self.lefting:
            for i1 in weapons_group:
                if type(i1) == PlayerWeapon:
                    if self.rect.x <= i1.rect.right <= self.rect.right \
                            or self.rect.x <= i1.rect.x <= self.rect.right:
                        if WIDTH - i1.rect.right > i1.rect.x:
                            self.danger += 1
                            self.sp.append(i1.rect.right + 10)
                        else:
                            self.danger += 1
                            self.sp.append(i1.rect.x - 10)
                    if i1.rect.x > self.rect.right:
                        self.danger_r += 1
                        self.sp.append(i1.rect.x - 10)
                    if i1.rect.right < self.rect.x:
                        self.danger_l += 1
                        self.sp.append(i1.rect.right + 10)
            if self.rect.x < 5:
                self.danger_l += 5
            if WIDTH - self.rect.right < 5:
                self.danger_r += 5
            if self.danger:
                if self.danger_r <= self.danger and self.danger_l > self.danger_r:
                    self.righting = True
                    self.coord = max(self.sp)
                elif self.danger_l <= self.danger and self.danger_l < self.danger_r:
                    self.lefting = True
                    self.coord = min(self.sp)
                elif self.danger_l == self.danger_r and self.danger_r < self.danger:
                    if self.rect.right - max(self.sp) - 7 < min(self.sp) - self.rect.x:
                        self.righting = True
                        self.coord = max(self.sp)
                    else:
                        self.lefting = True
                        self.coord = min(self.sp)
        elif self.righting and self.rect.x < self.coord:
            self.move_right()
        elif self.lefting and self.rect.right > self.coord:
            self.move_left()
        if self.righting and self.rect.x >= self.coord:
            self.righting = False
        elif self.lefting and self.rect.right <= self.coord:
            self.lefting = False
        if self.lefting and self.rect.x < 0:
            self.lefting = False
            self.coord = self.rect.w + 1
        elif self.righting and self.rect.right > WIDTH:
            self.righting = False
            self.coord = WIDTH - self.rect.right - 1
        if self.rect.x <= player.rect.x <= self.rect.right or self.rect.x <= player.rect.right <= self.rect.right:
            if player.rect.top - self.rect.top < HEIGHT:
                if player.rect.x < self.rect.right < player.rect.right:
                    self.shot = 1
                elif player.rect.x < self.rect.x < player.rect.right:
                    self.shot = 2

        elif not self.lefting and not self.righting and player.rect.top - self.rect.top - self.rect.h < HEIGHT \
                and k1 == 0:
            if abs(player.rect.x - self.rect.right) < abs(player.rect.right - self.rect.x):
                self.righting = True
                self.coord = player.rect.x + 3
            else:
                self.lefting = True
                self.coord = player.rect.right - 3

    def get_moved(self):
        if not player:
            return
        if player.rect.top + player.rect.h - self.rect.top < HEIGHT:
            return True
        return False


class EnemyWeapon(PlayerWeapon):
    def __init__(self, enemy, n1):
        super().__init__(n1)
        self.image = images['gre_weap']
        self.rect = self.image.get_rect()
        if n1 == 0:
            self.rect.x = enemy.rect.x + 10
        else:
            self.rect.x = enemy.rect.right - 10
        self.rect.y = enemy.rect.y + enemy.rect.h

    def move(self):
        self.rect.y += PLAYERSPEED * 2

    def update(self):
        self.move()
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)
        elif pygame.sprite.spritecollideany(self, player_group):
            spr = player
        else:
            spr = None
        if spr is not None:
            spr.hurt(self.damage)
            self.damage = 0
            self.delete()
        if player is None:
            self.delete()
        elif self.rect.top > player.rect.y + player.rect.h:
            self.delete()


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, boss_group)
        self.image = images['boss']
        self.rect = self.image.get_rect()
        self.rect.x = x * COLCOUNT - 5
        self.rect.y = y * GAME_SPEED
        self.health = 500
        self.shield_health = 0
        self.damage = 20
        self.n = 0
        self.shield_rect = None
        self.circle = 0
        self.max_radius = self.rect.h // 2 + 5
        self.circle_radius = 3
        pygame.time.set_timer(SHIELDSTART, 5000)
        pygame.time.set_timer(SHIELDEND, 10000)
        pygame.time.set_timer(BOSSSHOT, 2200)
        self.start_shield()

    def hurt(self, damage):
        if damage <= 0:
            return
        if self.shield_health > damage:
            self.shield_health -= damage
        elif self.shield_health == damage:
            self.shield_health -= damage
            self.end_shield()
        else:
            damage -= self.shield_health
            self.shield_health = 0
            self.end_shield()
            self.health -= damage
            if self.health <= 0:
                self.delete()

    def delete(self):
        global boss  # Пока так, но позже с анимацией
        s = sounds['enemy explode']
        s.play()
        boss_group.remove(self)
        all_sprites.remove(self)
        boss = None

    def inter_shot(self):
        s = sounds['enemy fire']
        s.play()
        BossWeapon(self.rect.x, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.right, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.x + self.rect.w // 4, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.right - self.rect.w // 4, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.right - self.rect.w // 2, self.rect.top + self.rect.h, 0)

    def sq_shot(self):
        s = sounds['boss fire']
        s.play()
        s.set_volume(0.8)
        for i1 in range(25, -26, -10):
            BossWeapon(self.rect.x + self.rect.w // 2 - 5, self.rect.top + self.rect.h, i1)

    def out_shot(self):  # Нужно подобрать правильные углы
        BossWeapon(self.rect.x, self.rect.top + self.rect.h, 20)
        BossWeapon(self.rect.x, self.rect.top + self.rect.h, 15)
        BossWeapon(self.rect.x, self.rect.top + self.rect.h, 10)
        BossWeapon(self.rect.right, self.rect.top + self.rect.h, -20)
        BossWeapon(self.rect.right, self.rect.top + self.rect.h, -15)
        BossWeapon(self.rect.right, self.rect.top + self.rect.h, -10)
        s = sounds['boss fire']
        s.play()
        s.set_volume(0.8)

    def change_circle_radius(self):
        if self.circle == 1:
            self.circle_radius += 2
        elif self.circle == -1:
            self.circle_radius -= 2
        if self.circle_radius > 5:
            color = pygame.color.Color('black')
            color.r = 66
            color.b = 151
            color.g = 138
            color.a = 100
            self.shield_rect = pygame.draw.circle(screen, color,
                                                  (self.rect.x + self.rect.w // 2,
                                                   self.rect.y + self.rect.h // 2),
                                                  self.circle_radius, 5)

    def start_shield(self):
        if self.circle_radius < self.max_radius:
            self.circle = 1
            self.shield_health = 90

    def end_shield(self):
        self.circle = -1
        self.shield_health = 0

    def shot(self):
        if not self.get_moved():
            return
        if self.rect.x <= player.rect.x - 8 <= self.rect.right \
                or self.rect.x <= player.rect.right + 8 <= self.rect.right:
            self.inter_shot()
        else:
            self.n = random.randint(0, 1)
            if self.n != 1:
                self.sq_shot()
            else:
                self.out_shot()

    def chrad(self):
        if (self.circle_radius < 5 and self.circle == -1) or (
                self.circle_radius > self.max_radius - 5 and self.circle == 1):
            self.circle = 0
        self.change_circle_radius()

    def get_moved(self):
        if not player:
            return
        if player.rect.top + player.rect.h - self.rect.top < HEIGHT:
            return True
        return False

    def update(self):
        self.chrad()


class BossWeapon(PlayerWeapon):
    def __init__(self, x, y, angle):
        super().__init__(0)
        self.image = pygame.transform.rotate(images['gre_weap'], -angle)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vect = pygame.math.Vector2()
        self.vect.x = 0
        self.vect.y = PLAYERSPEED * 2
        self.damage = 20
        vect1 = pygame.math.Vector2()
        vect1.x = 0
        vect1.y = PLAYERSPEED
        self.vect = find_vect(vect1, self.vect.rotate(angle))

    def move(self):
        self.rect.x += self.vect.x
        self.rect.y += self.vect.y

    def update(self):
        self.move()
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)
        elif pygame.sprite.spritecollideany(self, player_group):
            spr = player
        else:
            spr = None
        if spr is not None:
            spr.hurt(self.damage)
            self.damage = 0
            self.delete()
        if player is None:
            self.delete()
        elif (self.rect.top > player.rect.y + player.rect.h) or (self.rect.right < 0) or (self.rect.x > WIDTH):
            self.delete()


class Camera:
    def __init__(self):
        self.dy = 0

    def apply(self, obj):
        if type(obj) != Shakla and type(obj) != AmCount and type(obj) != Enemy and type(obj) != Meteor \
                and type(obj) != Boss:
            obj.rect.y += self.dy
        elif type(obj) == Enemy:
            if not check():
                obj.rect.y += self.dy
        elif type(obj) == Meteor:
            if (check() and obj.check()) or not check():
                obj.rect.y += self.dy
        elif type(obj) == Boss:
            if boss is not None:
                if not obj.get_moved() and not check():
                    obj.rect.y += self.dy

    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h - HEIGHT)


class Shakla(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, slu_group)
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
        super().__init__(all_sprites, slu_group)
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
                Meteor(j, i1)
            elif levelmap[i1][j] == 'n':
                Enemy(j, i1)
            elif levelmap[i1][j] == 'P':
                player1 = Player(j, i1)
            elif levelmap[i1][j] == 'b':
                Boss(j, i1)
    return player1


def check():
    for i1 in enemies_group:
        if i1.get_moved():
            return True
    return False


def find_vect(vect1, vect2):  # Вектор 2 - тот который хочешь получить
    vect3 = -vect1 + vect2
    return vect3


GAME_SPEED = 200  # дальность расположения метеоров
MYEVENTTYPE = 10
SHOTTYPE1 = 21
SHOTTYPE2 = 22
PLAYERSPEED = 5
GRAVITY = 0
KILLTYPE = 14
ENEMYSPEED = PLAYERSPEED * 1.3
ENEMYLEVEL = 7
PLAYERAMMUN = 30
HEALTYPE = 31
AMMTYPE = 11
SHIELDSTART = 25
SHIELDEND = 26
BOSSSHOT = 27
PLUSRADIUS = 28
METEORSK = 1  # Урон от столкновения между собой метеоров
levelmap, n = start_screen()
while True:
    osk_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    meteors_group = pygame.sprite.Group()
    weapons_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()
    boss_group = pygame.sprite.Group()
    slu_group = pygame.sprite.Group()
    fon_group = pygame.sprite.Group()
    boss = None
    all_sprites = pygame.sprite.Group()
    sp_sprites = [fon_group, osk_group, weapons_group, meteors_group, enemies_group, player_group, boss_group,
                  slu_group]
    pygame.time.set_timer(SHOTTYPE1, (10 - ENEMYLEVEL) * 1000)
    pygame.time.set_timer(SHOTTYPE2, (10 - ENEMYLEVEL) * 1000)
    pygame.time.set_timer(AMMTYPE, 2500)
    pygame.time.set_timer(HEALTYPE, 10000)
    screen.fill((0, 0, 0))
    n2 = random.choice((1, 3))
    Fon(-200, -1200, fon_group, n2, True)
    camera = Camera()
    sk = Shakla(0, 0)
    am = AmCount(WIDTH - 50, 4)
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
    righting, lefting = False, False
    accel, deccel = False, False
    for i in boss_group:
        boss = i
    while True:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
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
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    lefting = False
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    righting = False
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    accel = False
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    deccel = False
            elif event.type == SHOTTYPE1:
                for i in enemies_group:
                    if type(i) is Enemy:
                        i.shot1(1)
            elif event.type == SHOTTYPE2:
                for i in enemies_group:
                    if type(i) is Enemy:
                        i.shot1(2)
            elif event.type == HEALTYPE:
                if player is not None:
                    player.heal(10)
                for i in enemies_group:
                    i.heal(10)
            elif event.type == 11:
                if player is not None:
                    player.reamm()
                for i in enemies_group:
                    i.reamm()
            if boss is not None:
                if event.type == SHIELDSTART:
                    boss.start_shield()
                elif event.type == SHIELDEND:
                    boss.end_shield()
                elif event.type == BOSSSHOT:
                    boss.shot()
                elif event.type == PLUSRADIUS:
                    boss.chrad()
        if player is None:
            levelmap, n = end_screen(False, n)
            break
        k = 0
        for i in meteors_group:
            k += 1
        for i in enemies_group:
            k += 1
        if k == 0 and boss is None:
            levelmap, n = end_screen(True, n)
            break
        if player is not None:
            camera.update(player)
            for sprite in all_sprites:
                camera.apply(sprite)
        for i in sp_sprites:
            i.draw(screen)
        all_sprites.update()
        fon_group.update()
        for i in meteors_group:
            i.fun()
        pygame.display.flip()
        clock.tick(FPS)

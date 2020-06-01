from const import *
from levels import Fon2, start_screen, terminate, end_screen
from data import images, sounds
import random


def check():
    """Проверяет есть ли вражеские корабли в зоне видимости игрока"""
    # Проверяем все вражеские корабли
    # Метод get_moved отвечает за видимость игроком у вражеских кораблей
    for i1 in enemies_group:
        if i1.get_moved():
            return True
    return False


class Camera:
    """Класс камеры"""

    def __init__(self):
        self.dy = 0

    def apply(self, obj):
        # Некоторые объекты не двигаются или имеют собственное движение
        # Поэтому пассивное движение камеры для них не подходит
        if type(obj) != Scale and type(obj) != AmCount and type(obj) != Enemy and type(obj) != Meteor \
                and type(obj) != Boss and type(obj) != Fon2:
            obj.rect.y += self.dy  # Обычные объекты
        elif type(obj) == Enemy:
            if not check():  # Вражеские корабли не двигаются по вертеикали, когда их видит игрок
                obj.rect.y += self.dy
        elif type(obj) == Meteor:
            # Астероиды тоже не двигаются по вертикали, когда игрок видит вражеские корабли или эти астероиды
            if (check() and obj.check()) or not check():
                obj.rect.y += self.dy
        elif type(obj) == Boss:
            if boss is not None:
                if not obj.get_moved() and not check():
                    # Босс двигается по вертикали, если его не видят или игрок не видит другие вражеские корабли
                    # За видимость игроком у босса также отвечает метод get_moved
                    obj.rect.y += self.dy

    def update(self, target):
        self.dy = -(target.rect.y + target.rect.h - HEIGHT)


class Scale(pygame.sprite.Sprite):
    """Класс шкалы здоровья игрока"""

    def __init__(self, x, y):
        super().__init__(all_sprites, service_group)
        self.image = images['scale']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.scale_width = 94
        self.scale_height = 13
        self.color = None

    def draw(self, h):
        """Функция рисует шкалу, меняя её цвет с снижением здоровья игрока"""
        if h >= 70:
            self.color = pygame.Color('green')
        elif 30 <= h < 70:
            self.color = pygame.Color('yellow')
        else:
            self.color = pygame.Color('red')
        pygame.draw.rect(screen, self.color,
                         (self.rect.x, self.rect.y + 12, self.scale_width * (h / 100), self.scale_height - 3))

    def update(self):
        if player is not None:
            self.draw(player.health)


class AmCount(pygame.sprite.Sprite):
    """Класс показателя оставшихся боеприпасов"""

    def __init__(self, x, y):
        super().__init__(all_sprites, service_group)
        self.image = images['amk']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, amm):
        if amm < 0:  # Если боеприпасов не осталось, а пользователь пытается стрелять, то нужно показывать 0
            amm = 0
        intro_text = [str(amm)]
        font = pygame.font.Font(None, 20)
        text_coord = [(self.rect.x + 22, self.rect.y + 8)]
        for line in range(len(intro_text)):  # Печатаем количество оставшихся боеприпасов
            string_rendered = font.render(intro_text[line], 1, pygame.Color('white'))
            intro_rect = string_rendered.get_rect()
            intro_rect.top = text_coord[line][1]
            intro_rect.x = text_coord[line][0]
            screen.blit(string_rendered, intro_rect)

    def update(self):
        if player is not None:
            self.draw(player.ammunition)


class Meteor(pygame.sprite.Sprite):
    """Класс астероида"""

    def __init__(self, x, y, group):
        """Инициализация астероида"""
        super().__init__(group, all_sprites, group)
        grad = random.choice(('0', '90', '180', '270'))  # Выбираем угол поворота картинки для разноообразия
        self.image = images[f"meteor{grad}"]  # Загружаем подходящую картинку
        self.rect = self.image.get_rect()
        self.rect.y = y * GAME_SPEED
        self.rect.x = x * COLUMN_COUNT
        self.vect = list()  # Определяем вектор скорости в координатах x и y
        # Чтобы астероиды сильно не улетали от игрока по вертикали очень сильно по y минимальное значение проекции скорости равна -1
        self.vect.append(random.randint(-2, 2))
        self.vect.append(random.randint(-1, 2))
        self.damage = 20
        self.change_left = False  # Можно ли двигаться влево?
        self.change_right = False  # Эти два флага нужны, чтобы астероиды не улетали до того, как игрок увидит их
        self.health = 30
        self.invulnerability = False  # Неуязвимость

    def move(self):
        self.rect.x += self.vect[0] * METEOR_SPEED
        self.rect.y += self.vect[1] * METEOR_SPEED

    def hurt(self, damage):
        """Функция для получения урона"""
        if self.check2():
            self.health -= damage
            if self.health <= 0:
                self.delete()

    def delete(self):
        """Уничтожение астероидов, создание осколков"""
        meteors_group.remove(self)
        all_sprites.remove(self)
        particle_count = random.randint(3, 4)  # количество осколков
        numbers = range(-5, 6)  # возможные скорости для осколков
        for _ in range(particle_count):
            Oskol((self.rect.x + self.rect.w // 2, self.rect.y + self.rect.h // 2), random.choice(numbers),
                  random.choice(numbers))

    def fun(self):
        """Функция для уменьшения количества столкновений"""
        if self.far_check():  # Если игрок не видит астероиды, то не стоит им отскакивать
            self.invulnerability = True
        self.invulnerability = False

    def check(self):
        """Проверяет видит ли игрок весь астероид"""
        if player is None:
            return
        if player.rect.top + player.rect.h - self.rect.top < HEIGHT:
            return True
        return False

    def check2(self):
        """Функция проверяет видит ли игрок какую-то часть астероида"""
        if player is None:
            return
        if player.rect.top + player.rect.h - self.rect.top - self.rect.h < HEIGHT:
            return True
        return False

    def far_check(self):
        """Функция проверяет близко ли астероид к тому, что бы появиться на экране"""
        if player is None:
            return
        if player.rect.top + player.rect.h - self.rect.top - self.rect.h < HEIGHT + 10:
            return True
        return False

    def change_moving(self):
        """Функция меняет направление проекции вектора скорости на гооризонтальную ось координат"""
        self.vect = [-self.vect[0], self.vect[1]]

    def change_moving_with_spr(self, spr):
        """Функция обрабатывает столкновения астероидов"""
        if self.invulnerability or spr.invulnerability:
            return
        # Максимальное значение проекции скорости равна по модулю 2
        # Поэтому выше этой скорости никакие столкновения не приводят
        # При встрече двух астероидов левый увеличивает свою скорость влево, правый - вправо
        # Аналогично для встречи верхнего и нижнего
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
            if spr.vect[1] >= -1:
                spr.vect[1] -= 1
            if self.vect[1] != 2:
                self.vect[1] += 1
        if spr.rect.y > self.rect.y:
            if spr.vect[1] != 2:
                spr.vect[1] += 1
            if self.vect[1] >= -1:
                self.vect[1] -= 1
        self.hurt(METEOR_MINI_DAMAGE)
        spr.hurt(METEOR_MINI_DAMAGE)

    def passive_move(self):
        pass

    def update(self):
        if player is None:
            return
        if not self.check2():  # Если игрок не видит, то астероид двигается пассивно
            passive = True
        else:
            passive = False
        if not passive:
            self.move()  # Если нет, то ходит и сталкивается с другими
            sp_spr = pygame.sprite.spritecollide(self, meteors_group, False)
            spr = None
            for i1 in sp_spr:
                if i1 is not self:
                    spr = i1
            if player is not None:
                if spr is not None:
                    self.change_moving_with_spr(spr)
                    spr.change_moving_with_spr(self)
                if self.rect.y > player.rect.y + player.rect.h or self.rect.x >= WIDTH or self.rect.right < 0:
                    # Если астероид пролетает игрока, то уже не встретит игрока, поэтому можно его удалить
                    self.kill()
        else:
            self.passive_move()


class Player(pygame.sprite.Sprite):
    """Класс игрока"""

    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        self.image = images['player']  # Изображение
        self.rect = self.image.get_rect()
        self.rect.x = x * COLUMN_COUNT  # Координаты
        self.rect.y = y * GAME_SPEED
        self.damage = 30
        self.health = 100
        self.speed = PLAYER_SPEED  # Скорость игры
        self.ammunition = PLAYER_AMM  # Количество боеприпасов

    def hurt(self, damage):
        """Функция получения урона"""
        self.health -= damage
        if self.health <= 0:
            self.delete()

    def heal(self, health):
        """Функция для лечения"""
        self.health += health
        if self.health > 100:
            self.health = 100

    def move(self):
        """Функция для перемещения"""
        if player is not None:
            self.rect.y -= self.speed

    def reamm(self):
        """Функция для восстановление боеприпасов"""
        if self.ammunition < PLAYER_AMM:
            self.ammunition += 1
        if self.ammunition < 10:
            self.ammunition += 1
        if self.ammunition < 3:
            self.ammunition += 1

    def update(self):
        """Обработка событий"""
        self.move()  # Игрок перемещается вперёд
        if pygame.sprite.spritecollideany(self, meteors_group):  # Встречи с астероидами
            spr = pygame.sprite.spritecollideany(self, meteors_group)
            spr.hurt(self.damage)
            self.hurt(spr.damage)
        if righting and not lefting:  # Игрок перемещается вправо
            self.move_right()
        if lefting and not righting:  # Игрок перемещается влево
            self.move_left()
        if accel and not deccel:  # Игрок ускоряется вперёд
            self.acceleration()
        if deccel and not accel:
            self.deceleration()  # Игрок замедляется

    def move_right(self):
        if self.rect.right + PLAYER_SPEED <= WIDTH:
            self.rect.x += PLAYER_SPEED

    def move_left(self):
        if self.rect.x - PLAYER_SPEED >= 0:
            self.rect.x -= PLAYER_SPEED

    def acceleration(self):  # ускорение
        self.rect.y -= PLAYER_SPEED // 2

    def deceleration(self):  # Замедление
        self.rect.y += PLAYER_SPEED // 2

    def shot_e(self):  # Выстрел справа, с клавиши E
        if self.ammunition > 0:
            PlayerWeapon(1)
            s = sounds['player fire']
            s.play()
        self.ammunition -= 1

    def shot_q(self):  # Выстрел слева, с клавиши Q
        if self.ammunition > 0:
            PlayerWeapon(0)
            s = sounds['player fire']
            s.play()
        self.ammunition -= 1

    def delete(self):  # Уничтожение игрока
        global player
        s = sounds['player explode']
        s.play()
        player_group.remove(self)
        all_sprites.remove(self)
        player = None


class Enemy(Meteor):
    """Класс вражеских кораблей"""

    def __init__(self, x, y):
        super().__init__(x, y, enemies_group)
        self.image = images['enemy']
        self.rect = self.image.get_rect()
        self.rect.x = x * COLUMN_COUNT
        self.rect.y = y * GAME_SPEED
        self.damage = 30
        self.health = 60
        self.danger_middle = 0  # Это 3 счетчика, чтобы рассчитывать движение по дествиям игрока
        self.danger_right = 0
        self.danger_left = 0
        self.ammunition = 10
        self.moving = False
        self.coordinate_to_go = self.rect.x  # Координата, к которой нужно перемещаться
        self.old_counter = 0
        self.list_of_player_weapons = []
        self.shot = False  # Флаг, чтобы корабли постоянно не стреляли
        self.change_coord = True  # Флаг, чтобы корабль не дергался, постоянно меняя направление

    def hurt(self, dam):
        """Функция получения урона"""
        if self.get_moved():
            self.health -= dam
            if self.health <= 0:
                self.delete()

    def delete(self):
        """Уничтожение корабля и создание взрыва после него"""
        s = sounds['enemy explode']
        s.play()
        enemies_group.remove(self)
        all_sprites.remove(self)
        Boom(self.rect.x, self.rect.y)

    def heal(self, health):
        """Пополнение здоровья"""
        self.health += health
        if self.health > 60:
            self.health = 60

    def reamm(self):
        """Пополнение боеприпасов"""
        if self.ammunition < 7:
            self.ammunition += 1

    def shot_left(self):
        """Выстрел слева(для игрока)"""
        if self.ammunition > 0 and self.shot == 2:
            EnemyWeapon(self, 0)
            self.ammunition -= 1
            self.shot = False

    def shot_right(self):
        """Выстрел справа"""
        if self.ammunition > 0 and self.shot == 1:
            EnemyWeapon(self, 1)
            self.ammunition -= 1
            self.shot = False

    def move_right(self):
        if self.rect.right + ENEMY_SPEED <= WIDTH + 5:
            # Не приближаю вражеский корабль очень близко к краям, чтобы он не уходил за них
            self.rect.x += ENEMY_SPEED

    def move_left(self):
        if self.rect.x - ENEMY_SPEED >= -5:
            self.rect.x -= ENEMY_SPEED

    def do_shot(self, n1):
        """Функция делает выстрел справа, если аргумент 1, иначе делает выстрел слева"""
        if self.get_moved():
            if n1 == 1:
                self.shot_right()
            else:
                self.shot_left()

    def update(self):
        if player is None or not self.check2():
            return
        self.danger_middle = 0
        self.danger_right = 0
        self.danger_left = 0
        self.list_of_player_weapons = []  # Список с координатами левой стороны выстрела
        player_weapons_counter = 0
        if self.coordinate_to_go < 0:
            self.coordinate_to_go = 1
        if self.coordinate_to_go > WIDTH:
            self.coordinate_to_go = WIDTH - 1
        if pygame.sprite.spritecollideany(self, meteors_group):  # Если сталкивается с астероидами
            spr = pygame.sprite.spritecollideany(self, meteors_group)
            spr.hurt(self.damage)
            self.hurt(spr.damage)

        for i1 in weapons_group:
            if type(i1) == PlayerWeapon:
                player_weapons_counter += 1
                if self.rect.x <= i1.rect.right <= self.rect.right \
                        or self.rect.x <= i1.rect.x <= self.rect.right:
                    # Если выстрел нацелен на вражеский корабль, то это угроза в середине
                    self.danger_middle += 1
                elif i1.rect.x > self.rect.right:
                    # Если выстрел пролетает справа и пока не задевает корабль, то это тоже стоит учитовать
                    self.danger_right += 1
                elif i1.rect.right < self.rect.x:
                    # Если выстрел пролетает слева и пока не задевает корабль, то это тоже стоит учитовать
                    self.danger_left += 1
                self.list_of_player_weapons.append(i1.rect.x)
        if player_weapons_counter != self.old_counter:
            self.change_coord = True
        if self.rect.x < 17:
            # Если прижиматься к краям, то это делает корабль более уязвимым
            self.danger_left += 2
        if WIDTH - self.rect.right < 17:
            self.danger_right += 2
        if self.change_coord:
            if self.danger_middle:  # Если кораблю угрожает попадание, то нужно двигаться
                if self.danger_right <= self.danger_middle and self.danger_left > self.danger_right:
                    # Если справа безопаснее, то двигаемся так, чтобы все выстрелы пролетели слева
                    # Если справа стена, то приходится двигаться влево
                    self.coordinate_to_go = max(self.list_of_player_weapons) + 17 + 3 if max(
                        self.list_of_player_weapons) + 17 + 3 < WIDTH - self.rect.w - 7 else min(
                        self.list_of_player_weapons) - self.rect.w - 3
                elif self.danger_left <= self.danger_middle and self.danger_left < self.danger_right:
                    # Если слева безопаснее, то двигаемся так, чтобы все выстрелы пролетели справа
                    # Если слева стена, то двигаемся вправо
                    self.coordinate_to_go = min(self.list_of_player_weapons) - self.rect.w - 3 if min(
                        self.list_of_player_weapons) - self.rect.w - 3 > 5 else max(
                        self.list_of_player_weapons) + 17 + 3
                elif self.danger_left == self.danger_right and self.danger_right < self.danger_middle:
                    if abs(self.rect.x - min(self.list_of_player_weapons) + self.rect.w) > abs(max(
                            self.list_of_player_weapons) - self.rect.x):
                        self.coordinate_to_go = max(self.list_of_player_weapons) + 17 + 3 if max(
                            self.list_of_player_weapons) + 17 + 3 < WIDTH - self.rect.w - 7 else min(
                            self.list_of_player_weapons) - self.rect.w - 3
                    else:
                        self.coordinate_to_go = min(self.list_of_player_weapons) - self.rect.w - 3 if min(
                            self.list_of_player_weapons) - self.rect.w - 3 > 5 else max(
                            self.list_of_player_weapons) + 17 + 3
        if self.coordinate_to_go - 1.5 <= self.rect.x <= self.coordinate_to_go + 1.5:
            self.moving = False
        elif self.coordinate_to_go > self.rect.x:
            self.moving = True
            self.move_right()
        elif self.rect.x > self.coordinate_to_go:
            self.moving = True
            self.move_left()
        if player.rect.x <= self.rect.right <= player.rect.right or player.rect.x <= self.rect.x <= player.rect.right:
            if self.check2():
                if player.rect.x <= self.rect.right <= player.rect.right:
                    self.shot = 1
                elif player.rect.x <= self.rect.x <= player.rect.right:
                    self.shot = 2
        elif not self.moving and self.check2() and player_weapons_counter == 0:
            if abs(player.rect.x - self.rect.right) < abs(player.rect.right - self.rect.x):
                self.coordinate_to_go = player.rect.x
            else:
                self.coordinate_to_go = player.rect.right - 17 - 7
        self.old_counter = player_weapons_counter
        self.change_coord = False

    def get_moved(self):
        if not player:
            return
        if player.rect.top + player.rect.h - self.rect.top < HEIGHT:
            return True
        return False


class Boss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, boss_group)
        self.image = images['boss']
        self.rect = self.image.get_rect()
        self.rect.x = x * COLUMN_COUNT - 5
        self.rect.y = y * GAME_SPEED
        self.health = 500
        self.shield_health = 0
        self.damage = 20
        self.n = 0
        self.shield_rect = None
        self.circle = 0
        self.max_radius = self.rect.h // 2 + 5
        self.circle_radius = 3
        pygame.time.set_timer(SHIELD_START_TYPE, 5000)
        pygame.time.set_timer(SHIELD_END_TYPE, 10000)
        pygame.time.set_timer(BOSS_SHOT_TYPE, 2200)
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

    def shield_hurt(self, damage):
        if damage <= 0:
            return
        if self.shield_health > damage:
            self.shield_health -= damage
        else:
            self.shield_health = 0
            self.end_shield()

    def delete(self):
        global boss
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

    def out_shot(self):
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
            pygame.draw.circle(screen, color,
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
        self.shield_rect = None

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
            self.shield_rect = (self.rect.x - 21, self.rect.top, self.max_radius * 2 - 2, self.max_radius * 2)
        self.change_circle_radius()

    def get_moved(self):
        if not player:
            return
        if player.rect.top + player.rect.h - self.rect.top < HEIGHT:
            return True
        return False

    def update(self):
        self.chrad()
        if self.shield_rect is not None:
            self.shield_rect = (self.rect.x - 21, self.rect.top, self.max_radius * 2 - 2, self.max_radius * 2)


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
        self.tim = FPS * 2

    def update(self):
        self.n += 1
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if player is None:
            return
        if self.rect.y > player.rect.y + player.rect.h or self.rect.x >= WIDTH or self.rect.right < 0 \
                or self.n > self.tim:
            self.kill()


class Boom(Oskol):
    def __init__(self, x, y):
        super().__init__((x, y), 0, -PLAYER_SPEED // 2)
        self.image = images['boom']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tim = FPS * 14 // 10


def view_lesson():
    player1 = None
    for i1 in range(len(levelmap)):
        for j in range(len(levelmap[i1])):
            if levelmap[i1][j] == '-':
                continue
            elif levelmap[i1][j] == '*':
                Meteor(j, i1, meteors_group)
            elif levelmap[i1][j] == 'n':
                Enemy(j, i1)
            elif levelmap[i1][j] == 'P':
                player1 = Player(j, i1)
            elif levelmap[i1][j] == 'b':
                Boss(j, i1)
    return player1


def find_vect(vect1, vect2):  # Вектор 2 - тот который хочешь получить
    vect3 = -vect1 + vect2
    return vect3


class PlayerWeapon(pygame.sprite.Sprite):
    """Класс для выстрелов игрока"""

    def __init__(self, n1):
        """Создаёт выстрел, n1 - флаг, для того чтобы понимать слева или справа создавать выстрел"""
        super().__init__(all_sprites, weapons_group)
        self.image = images['red_weap']
        self.rect = self.image.get_rect()
        if n1 == 0:
            self.rect.x = player.rect.x + 9
        else:
            self.rect.x = player.rect.right - 9
        self.rect.y = player.rect.y
        self.damage = 30

    def move(self):
        """Функция для движения вперёд"""
        self.rect.y -= PLAYER_SPEED * 4

    def update(self):
        self.move()
        if boss is not None:  # У босса может появляться щит, поэтому этот случай рассмотрим отдельно
            # Если у босса нет щита, это обычный случай
            if boss.shield_rect is not None:
                x1, y1, w1, h1 = self.rect.x, self.rect.top, self.rect.w, self.rect.h
                x2, y2, w2, h2 = boss.shield_rect  # Смотрим размеры щита
                # Если координаты совпадают, то наносим ему урон
                if (x1 + w1 >= x2 >= x1 and y1 + h1 >= y2 >= y1) or (x2 + w2 >= x1 >= x2 and y2 + h2 >= y1 >= y2):
                    boss.shield_hurt(self.damage)
                    self.delete()  # Убираем этот объект
        # spr - это спрайт, которому наносим урон
        if pygame.sprite.spritecollideany(self, meteors_group):
            spr = pygame.sprite.spritecollideany(self, meteors_group)  # Сталкиваемся с астероидом
        elif pygame.sprite.spritecollideany(self, enemies_group):
            spr = pygame.sprite.spritecollideany(self, enemies_group)  # Сталкиваемся с вражескими кораблями
        elif boss is not None and pygame.sprite.spritecollideany(self, boss_group):
            spr = boss  # Сталкиваемся с боссом
        else:
            spr = None  # Ни с кем не сталкиваемся
        if player is None:
            self.delete()  # Игрок уничтожен, игра закончена
        elif player.rect.top - HEIGHT > self.rect.top + self.rect.h:
            self.delete()  # Выстрел улетел далеко и исчезает
        elif spr is not None:
            spr.hurt(self.damage)  # Если с кем-то сталкиваемся, то наносим ему урон
            self.damage = 0
            self.delete()

    def delete(self):
        """Убираем объект с поля"""
        weapons_group.remove(self)
        all_sprites.remove(self)


class EnemyWeapon(PlayerWeapon):
    def __init__(self, enemy, n1):
        super().__init__(n1)
        s = sounds['enemy fire']
        s.play()
        self.image = images['gre_weap']
        self.rect = self.image.get_rect()
        if n1 == 0:
            self.rect.x = enemy.rect.x + 9
        else:
            self.rect.x = enemy.rect.right - 9
        self.rect.y = enemy.rect.y + enemy.rect.h

    def move(self):
        self.rect.y += PLAYER_SPEED * 2

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


class BossWeapon(PlayerWeapon):
    def __init__(self, x, y, angle):
        super().__init__(0)
        self.image = pygame.transform.rotate(images['gre_weap'], -angle)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vect = pygame.math.Vector2()
        self.vect.x = 0
        self.vect.y = PLAYER_SPEED * 2
        self.damage = 20
        vect1 = pygame.math.Vector2()
        vect1.x = 0
        vect1.y = PLAYER_SPEED
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


levelmap, n = start_screen()
while True:
    all_sprites, fon_group, osk_group, weapons_group, meteors_group, enemies_group, player_group, boss_group, service_group, boss = restart_sprites_for_game()
    sp_sprites = [fon_group, osk_group, weapons_group, meteors_group, enemies_group, player_group, boss_group,
                  service_group]
    righting, lefting = False, False
    accel, deccel = False, False
    pygame.time.set_timer(SHOT_TYPE1, int((10 - ENEMY_LEVEL) * 1000))
    pygame.time.set_timer(SHOT_TYPE2, int((10 - ENEMY_LEVEL) * 1000))
    pygame.time.set_timer(AMM_TYPE, 3500)
    pygame.time.set_timer(HEAL_TYPE, 10000)
    screen.fill((0, 0, 0))
    n2 = random.choice((1, 3))
    camera = Camera()
    sk = Scale(0, 0)
    am = AmCount(WIDTH - 50, 4)
    lessons_group = None
    player = view_lesson()
    Fon2(-200, -1200, fon_group, n2, True)
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
            elif event.type == SHOT_TYPE1:
                for i in enemies_group:
                    if type(i) is Enemy:
                        i.do_shot(1)
            elif event.type == SHOT_TYPE2:
                for i in enemies_group:
                    if type(i) is Enemy:
                        i.do_shot(2)
            elif event.type == HEAL_TYPE:
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
                if event.type == SHIELD_START_TYPE:
                    boss.start_shield()
                elif event.type == SHIELD_END_TYPE:
                    boss.end_shield()
                elif event.type == BOSS_SHOT_TYPE:
                    boss.shot()
                elif event.type == PLUS_RADIUS:
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

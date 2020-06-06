from const import *
from levels import Fon, start_screen, terminate, end_screen, pause_screen, display_lessons
from data import images, sounds
import random
import pygame


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
                and type(obj) != Boss and type(obj) != Fon2 and type(obj) != Fire:
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

    def __init__(self, x, y, falcon_mod):
        super().__init__(all_sprites, service_group)
        self.image = images['scale']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.h_max = 100 if not falcon_mod else 150
        self.scale_width = 94
        self.scale_height = 13
        self.color = None

    def draw(self, h):
        """Функция рисует шкалу, меняя её цвет с снижением здоровья игрока"""
        if h >= 0.7 * self.h_max:
            self.color = pygame.Color('green')
        elif 0.3 * self.h_max <= h < self.h_max * 0.7:
            self.color = pygame.Color('yellow')
        else:
            self.color = pygame.Color('red')
        pygame.draw.rect(screen, self.color,
                         (self.rect.x, self.rect.y + 12, self.scale_width * (h / self.h_max), self.scale_height - 3))

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
        # Чтобы астероиды сильно не улетали от игрока по вертикали очень сильно,
        # По y минимальное значение проекции скорости равна -1
        self.vect.append(random.randint(-2, 2))
        self.vect.append(random.randint(-1, 2))
        self.damage = 20
        self.change_left = False  # Можно ли двигаться влево?
        self.change_right = False  # Эти два флага нужны, чтобы астероиды не улетали до того, как игрок увидит их
        self.health = 30
        self.invulnerability = False  # Неуязвимость
        self.scene_second_counter = 0

    def move(self):
        self.rect.x += self.vect[0] * METEOR_SPEED
        self.rect.y += self.vect[1] * METEOR_SPEED

    def scene_move(self):
        """Функция для перемещения в сцене"""
        self.rect.y += 2

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

    def update(self, scene=False):
        if not scene:
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
        else:
            self.move()
            sp_spr = pygame.sprite.spritecollide(self, meteors_group, False)
            spr = None
            for i1 in sp_spr:
                if i1 is not self:
                    spr = i1
            if spr is not None:
                self.change_moving_with_spr(spr)
                spr.change_moving_with_spr(self)
            if self.rect.x >= WIDTH or self.rect.right < 0:
                # Если астероид пролетает игрока, то уже не встретит игрока, поэтому можно его удалить
                self.kill()


class Player(pygame.sprite.Sprite):
    """Класс игрока"""

    def __init__(self, x, y, group, coordinates_not_for_scenes=True, append_to_all_sprites=True, scene_speed=False):
        if append_to_all_sprites:
            super().__init__(group, all_sprites)
        else:  # В стартовой сцене, ещё нет all_sprites, поэтому его не нужно туда добавлять
            super().__init__(group)
        self.image = images['player']  # Изображение
        self.rect = self.image.get_rect()
        if coordinates_not_for_scenes:  # Для удобства в сценах используются обычные координаты, а не по карте уровня
            self.rect.x = x * COLUMN_COUNT  # Координаты
            self.rect.y = y * GAME_SPEED
        else:
            self.rect.x = x
            self.rect.y = y
        self.damage = 30
        self.health = 100
        if scene_speed:
            self.speed = -PLAYER_SPEED  # Скорость игрока для стартовой сцены другая
        else:
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

    def move(self, scene=False):
        """Функция для перемещения"""
        if player is not None or scene:
            # Когда происходит стартовая сцена, то player = None, поэтому используется параметр scene
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
        global player, player_lose_coordinates
        Boom(self.rect.x, self.rect.y, player_die=True)
        player_lose_coordinates = [self.rect.x, self.rect.y]
        s = sounds['player explode']
        s.play()
        player_group.remove(self)
        all_sprites.remove(self)
        player = None


class Falcon(Player):
    """Класс второго персонажа"""

    def __init__(self, x, y, group, coordinates_not_for_scenes=True, append_to_all_sprites=True, scene_speed=False):
        super().__init__(x, y, group, coordinates_not_for_scenes, append_to_all_sprites, scene_speed)
        self.image = images['falcon']
        self.rect = self.image.get_rect()
        if coordinates_not_for_scenes:  # Для удобства в сценах используются обычные координаты, а не по карте уровня
            self.rect.x = x * COLUMN_COUNT  # Координаты
            self.rect.y = y * GAME_SPEED
        else:
            self.rect.x = x
            self.rect.y = y
        self.health = 150

    def shot_e(self):  # Выстрел справа, с клавиши E
        if self.ammunition > 0:
            FalconWeapon(1)
            s = sounds['player fire']
            s.play()
        self.ammunition -= 1

    def shot_q(self):  # Выстрел слева, с клавиши Q
        if self.ammunition > 0:
            FalconWeapon(0)
            s = sounds['player fire']
            s.play()
        self.ammunition -= 1


class Enemy(Meteor):
    """Класс вражеских кораблей"""

    def __init__(self, x, y, group):
        super().__init__(x, y, group)
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
        self.shot_choice = None  # Переменная, чтобы знать с какой стороны стрелять по игроку
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
        if self.ammunition > 0 and self.shot_choice == 0:
            EnemyWeapon(self, 0)
            self.ammunition -= 1
            self.shot_choice = None

    def shot_right(self):
        """Выстрел справа"""
        if self.ammunition > 0 and self.shot_choice == 1:
            EnemyWeapon(self, 1)
            self.ammunition -= 1
            self.shot_choice = None

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

    def update(self, scene=False):
        if scene:
            self.scene_move()
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
            # Если количество выстрелов игрока изменилось, то можно менять координату
            # Если нет, то безопасное место уже было определено и нужно к нему двигаться
            self.change_coord = True
        if self.rect.x < 17:
            # Если прижиматься к краям, то это делает корабль более уязвимым
            self.danger_left += 2
        if WIDTH - self.rect.right < 17:
            self.danger_right += 2
        if self.change_coord:  # Если можно менять координату, то выбираем бзопасное место
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
                    # Если слева и справа одинаково опасно, то двигаемся туда, где больше места, учитывая стены
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
            # Корабли могут двигаться только по определённым точкам, поэтому будем считать,
            # что достигли безопасного места, если попали в него с небольшой погрешностью
            self.moving = False
        elif self.coordinate_to_go > self.rect.x:
            # Если не достигли безопасного места и оно справа, то двигаемся вправо
            self.moving = True
            self.move_right()
        elif self.rect.x > self.coordinate_to_go:
            self.moving = True
            self.move_left()
        if self.check2():
            if player.rect.x <= self.rect.right <= player.rect.right:
                # Если игрок попадает под правое орудие, то стреляем им
                self.shot_choice = 1
            elif player.rect.x <= self.rect.x <= player.rect.right:
                # Если он попадает под левое орудие, то стреляем из него
                self.shot_choice = 0
        if not self.moving and self.check2() and player_weapons_counter == 0:
            # Если опасности нет и игрок сражается с данным кораблём, то начинаем нападать
            # Для этого перемещаемся к нему
            if abs(player.rect.x - self.rect.right) < abs(player.rect.right - self.rect.x):
                self.coordinate_to_go = player.rect.x
            else:
                self.coordinate_to_go = player.rect.right - 17 - 7
        self.old_counter = player_weapons_counter
        self.change_coord = False

    def get_moved(self):
        """Функция показывает, видит ли игрок этот корабль"""
        if not player:
            return
        if player.rect.top + player.rect.h - self.rect.top < HEIGHT:
            return True
        return False


class Boss(Enemy):
    """Класс босса"""

    def __init__(self, x, y):
        super().__init__(x, y, boss_group)
        self.image = images['boss']
        self.rect = self.image.get_rect()
        self.rect.x = x * COLUMN_COUNT - 5
        self.rect.y = y * GAME_SPEED
        self.health = BOSS_HEALTH
        self.shield_health = 0
        self.damage = 20
        self.shot_choice = 0
        self.f = 1  # Фаза босса
        self.shield_rect = None
        self.circle_run = 0  # Переменная, показывающая, что происходит со щитом
        self.max_radius = self.rect.h // 2 + 5
        self.circle_radius = 3
        pygame.time.set_timer(SHIELD_START_TYPE, 10000)
        pygame.time.set_timer(BOSS_SHOT_TYPE, 2200)
        self.start_shield()  # Создаём щит

    def hurt(self, damage):
        """Функция получения урона"""
        if damage <= 0:
            return
        if self.shield_health >= damage:  # В случае босса нужно учитывать поглощение урона щитом
            self.shield_hurt(damage)
        else:
            self.shield_hurt(damage)
            damage -= self.shield_health
            self.health -= damage
            if self.health <= 0:
                self.delete()
            elif self.health <= BOSS_HEALTH // 2 and self.f == 1:
                Fire(270, 35)
                self.f = 2
            elif self.health <= BOSS_HEALTH * 0.25 and self.f == 2:
                self.f = 3
                Fire(230, 90)

    def shield_hurt(self, damage):
        """Функция для получения урона щитом. Используется при попадании в босса в щите и просто попадания в щит"""
        if damage <= 0:
            return
        if self.shield_health > damage:
            self.shield_health -= damage
        else:
            self.shield_health = 0
            self.end_shield()

    def delete(self):
        """Функция уничтожения босса"""
        global boss
        s = sounds['enemy explode']
        s.play()
        Boom(self.rect.x - 75, self.rect.y, boss_die=True)
        boss_group.remove(self)
        all_sprites.remove(self)
        boss = None

    def inter_shot(self):
        """Функция для одного из видов ударов босса. Выпускает 5 паралельных выстрелов под себя"""
        s = sounds['enemy fire']
        s.play()
        BossWeapon(self.rect.x, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.right, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.x + self.rect.w // 4, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.right - self.rect.w // 4, self.rect.top + self.rect.h, 0)
        BossWeapon(self.rect.right - self.rect.w // 2, self.rect.top + self.rect.h, 0)

    def square_shot(self):
        """Функция для одного из видов ударов босса. Выпускает множество выстрелов по всем направлениям"""
        s = sounds['boss fire']
        s.play()
        s.set_volume(0.8)
        for i1 in range(25, -26, -10):
            BossWeapon(self.rect.x + self.rect.w // 2 - 5, self.rect.top + self.rect.h, i1)

    def out_shot(self):
        """Функция для одного из видов ударов босса. Выпускает 6 выстрелов по направлению к краям экрана"""
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
        """Функция, изменяющая щит босса"""
        # Переменная self.circle_run показывает как нужно менять щит
        # Если она равна 1, увеличиваем
        # Если она равна -1, уменьшаем
        if self.circle_run == 1:
            self.circle_radius += 2
        elif self.circle_run == -1:
            self.circle_radius -= 2
        if self.circle_radius > 5:
            color = pygame.color.Color('black')  # Рисуем щит
            color.r = 66
            color.b = 151
            color.g = 138
            color.a = 100
            pygame.draw.circle(screen, color,
                               (self.rect.x + self.rect.w // 2,
                                self.rect.y + self.rect.h // 2),
                               self.circle_radius, 5)

    def start_shield(self):
        """Функция для создания щита"""
        if self.circle_radius < self.max_radius:
            self.circle_run = 1  # Увеличиваем щит с помощью этой переменной
            self.shield_health = BOSS_SHIELD_MAX_HEALTH  # Увеличиваем здоровье щита

    def end_shield(self):
        """Функция для того чтобы убрать щит"""
        self.circle_run = -1  # Уменьшаем щит с помощью этой переменной
        self.shield_health = 0  # Убираем здоровье щита
        self.shield_rect = None

    def shot(self):
        """Функция, управляющая атаками босса"""
        if not self.get_moved():
            return
        if self.rect.x <= player.rect.x - 8 <= self.rect.right \
                or self.rect.x <= player.rect.right - 3 <= self.rect.right:
            if self.f != 3:
                self.inter_shot()  # Если игрок под боссом, делаем атаку вниз
            else:
                self.shot_choice = random.choice([0, 0, 0, 1])  # В 3 фазе шанс атаки 25% на атаку игрока под боссом
                if self.shot_choice == 1:
                    self.square_shot()
                else:
                    self.inter_shot()
        else:
            if self.f > 1:  # Атака по всей площади довольно жёсткая,
                if self.f == 2:  # поэтому используем её только со второй фазы
                    self.shot_choice = random.choice([0, 0, 1, 1])  # В ней шанс такой атаки 50 %
                    if self.shot_choice == 1:
                        self.square_shot()
                    else:
                        self.out_shot()
                elif self.f == 3:
                    self.shot_choice = random.choice([0, 1, 1, 1])  # В 3 фазе шанс атаки 75%
                    if self.shot_choice == 1:
                        self.square_shot()
                    else:
                        self.out_shot()
            else:
                # Эту атаку используем, если здоровья ещё много или с шансом 25 %
                self.out_shot()

    def change_radius_event(self):
        """Функция, которая обрабатывает событие, связанные с изменением щита.
         Также закрепляет щит в статичном состоянии"""
        if (self.circle_radius < 5 and self.circle_run == -1) or (
                self.circle_radius > self.max_radius - 5 and self.circle_run == 1):
            self.circle_run = 0  # Если щит достиг максимального или минимального значения, то он не должен дальше расти
            self.shield_rect = (self.rect.x - 21, self.rect.top, self.max_radius * 2 - 2, self.max_radius * 2)
        self.change_circle_radius()  # Вызываем изменения щита

    def update(self, scene=False):
        if scene:
            self.scene_move()
        if player is None:
            return
        self.change_radius_event()
        if self.shield_rect is not None:
            self.shield_rect = (self.rect.x - 21, self.rect.top, self.max_radius * 2 - 2, self.max_radius * 2)


class Oskol(pygame.sprite.Sprite):
    """Класс осколка астероида"""
    img_list = [images['osk1'], images['osk2'], images['osk3']]
    for i in range(len(img_list)):
        for scale in (20, 17, 22):  # Создаём различные картинки для осколков
            img_list.append(pygame.transform.scale(img_list[i], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites, osk_group)
        self.image = random.choice(self.img_list)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]  # Вектор скорости
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY
        self.time_counter = 0  # Счётчик для измерения время жизни
        self.tim = FPS * 2  # Время жизни

    def update(self, scene=False):
        """Обработка событий"""
        if player is None and not scene:
            return
        self.time_counter += 1
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if scene:
            if self.rect.x >= WIDTH or self.rect.right < 0 or self.time_counter > self.tim:
                self.kill()
        else:
            if self.rect.y > player.rect.y + player.rect.h or self.rect.x >= WIDTH or self.rect.right < 0 \
                    or self.time_counter > self.tim:
                self.kill()


class Fire(pygame.sprite.Sprite):
    """Класс огня для босса"""

    def __init__(self, x, y):
        super().__init__(all_sprites, fire_group)
        self.image = images['fire']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.scene_second_counter = 0

    def scene_move(self):
        self.rect.y += 2

    def update(self, scene=False):
        if scene:
            self.scene_move()


class Boom(Oskol):
    """Класс взрыва вражеских кораблей
    Использует родительский класс Oskol"""

    def __init__(self, x, y, player_die=False, boss_die=False):
        super().__init__((x, y), 0, -PLAYER_SPEED // 2)
        if player_die:
            self.image = images['player_boom']
        elif boss_die:
            self.image = images['boss_boom']
        else:
            self.image = images['boom']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.tim = FPS * 14 // 10

    def update(self, scene=False):
        if not scene:
            super().update(scene)
        else:
            self.time_counter += 1
            if self.time_counter > self.tim:
                self.kill()


class PlayerWeapon(pygame.sprite.Sprite):
    """Класс для выстрелов игрока"""

    def __init__(self, n1):
        """Создаёт выстрел, n1 - флаг, для того чтобы понимать слева или справа создавать выстрел"""
        super().__init__(all_sprites, weapons_group)
        self.image = images['red_weap']
        self.rect = self.image.get_rect()
        if n1 == 0:  # n1 - показатель с какой стороны нужно создавать выстрел
            self.rect.x = player.rect.x + 9
        else:
            self.rect.x = player.rect.right - 9
        self.rect.y = player.rect.y
        self.damage = 20

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


class FalconWeapon(PlayerWeapon):
    """Класс выстрелов для второго вида игрока"""

    def __init__(self, n1):
        super().__init__(n1)
        if n1 == 0:  # n1 - показатель с какой стороны нужно создавать выстрел
            self.rect.x = player.rect.x + 15
        else:
            self.rect.x = player.rect.right - 20
        self.damage = 30


class EnemyWeapon(PlayerWeapon):
    """Класс выстрела вражеского корабля.
    Использует родительский класс PlayerWeapon"""

    def __init__(self, enemy, n1):
        super().__init__(n1)
        s = sounds['enemy fire']
        s.play()
        self.image = images['gre_weap']
        self.rect = self.image.get_rect()
        if n1 == 0:  # n1 - показатель с какой стороны нужно создавать выстрел
            self.rect.x = enemy.rect.x + 9
        else:
            self.rect.x = enemy.rect.right - 9
        self.rect.y = enemy.rect.y + enemy.rect.h

    def move(self):
        self.rect.y += PLAYER_SPEED * 2

    def update(self):
        self.move()
        if pygame.sprite.spritecollideany(self, meteors_group):  # spr - спрайт, в который попали
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
    """Класс выстрелов босса. Использует родительский класс PlayerWeapon"""

    def __init__(self, x, y, angle):
        """Функция инициализации выстрела.
         Отличается от остальных выстрелов, потому что выстрелы босса могут иметь разные направления"""
        super().__init__(0)
        self.image = pygame.transform.rotate(images['gre_weap'], -angle)  # Поворачиваем выстрел под нужным углом
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vect = pygame.math.Vector2()  # Создаём вектор скорости в неподвижной системе отсчёта
        self.vect.x = 0
        self.vect.y = PLAYER_SPEED * 2
        self.damage = 20
        vect1 = pygame.math.Vector2()  # Создаём переносную скорость игрока
        vect1.x = 0
        vect1.y = PLAYER_SPEED
        # Используем функцию для нахождения вектора скорости в системе отсчёта игрока
        self.vect = find_vect(-vect1, self.vect.rotate(angle))

    def move(self):
        self.rect.x += self.vect.x
        self.rect.y += self.vect.y

    def update(self):
        """Функция обработки событий. Похожа на такую же функцию у выстрелов вражеских кораблей"""
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


class Target:
    """Класс для фокусирования в сценах"""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 0, 0)


class Fon2(Fon):
    """Фон, который двигается"""

    def __init__(self, x, y, fon_gr, n1, battle=False):
        super().__init__(x, y, fon_gr, n1, battle)

    def update(self,
               *args):  # В сценах нужно двигать фон быстрее обычного, поэтому в параметры к update в них добавляем True
        if any(args):
            self.move(True)
        else:
            self.n += 1  # Используем счётчик от родительского класса
            if self.n % 2 == 0:
                self.move()

    def move(self, scene=False):
        if player is not None:  # Ограничение по координате игрока, чтобы не выходить за фон
            if player.rect.top + player.rect.h - self.rect.top > HEIGHT - 5:
                self.rect.y += 0.5
        elif scene:  # Когда происходит стартовая сцена, то player = None, поэтому используется параметр scene
            self.rect.y += 0.5


def view_lesson(falcon_mode):
    """Функция для воплощения на экран карты уровня"""
    player1 = None
    for i1 in range(len(level_map)):
        for j in range(len(level_map[i1])):
            if level_map[i1][j] == '-':
                continue
            elif level_map[i1][j] == '*':
                Meteor(j, i1, meteors_group)
            elif level_map[i1][j] == 'n':
                Enemy(j, i1, enemies_group)
            elif level_map[i1][j] == 'P':
                if falcon_mode:  # Создаём игрока в зависимости от выбора пользователя
                    player1 = Falcon(j, i1, player_group)
                else:
                    player1 = Player(j, i1, player_group)
            elif level_map[i1][j] == 'b':
                Boss(j, i1)
    return player1


def first_scene(scene_fon_number, scene_fon_group, falcon_mode):
    """Функция для стартовой сцены"""
    scene_player_group = get_sprites_group()  # Создаём группу для игрока
    scene_cam = Camera()  # Создаём камеру для сцены
    screen.fill((0, 0, 0))
    # Создаём макет игрока, который будет лететь в это сцене.
    if falcon_mode:
        scene_player = Falcon(4 * COLUMN_COUNT, -100, scene_player_group, coordinates_not_for_scenes=False,
                              append_to_all_sprites=False,
                              scene_speed=True)
    else:
        scene_player = Player(4 * COLUMN_COUNT, -100, scene_player_group, coordinates_not_for_scenes=False,
                              append_to_all_sprites=False,
                              scene_speed=True)
    Fon2(-200, -1200, scene_fon_group, scene_fon_number, True)  # Фон, который будет двигаться
    tar = Target(225, 600)  # И класс для фокусирования камеры
    while True:
        for scene_event in pygame.event.get():  # Запускаем обработчик событий
            if scene_event.type == pygame.QUIT:
                terminate()
        scene_cam.update(tar)  # Фокусируем камеру
        if scene_player.rect.y > tar.rect.y - 50:
            return  # Если игрок долетел до края останавливаем стартовую стцену
        scene_fon_group.draw(screen)
        scene_player_group.draw(screen)
        scene_player.move(True)  # Двигаем игрока
        scene_fon_group.update(True)  # Двигаем фон быстрее обычного
        pygame.display.flip()
        clock.tick(FPS)


def won_scene(scene_fon_group, scene_player, scene_player_group, scene_boom_group):
    """Сцена для победы. В ней мы сразу получаем объект игрока, его группу и фон"""
    scene_cam = Camera()
    tar = Target(225, scene_player.rect.y)
    while True:
        for scene_event in pygame.event.get():  # Запускаем обработчик событий
            if scene_event.type == pygame.QUIT:
                terminate()
        scene_cam.update(tar)
        scene_boom_group.update(True)
        scene_player.move(True)
        scene_fon_group.update(True)
        if abs(tar.rect.bottom - scene_player.rect.bottom) > HEIGHT:
            return  # Когда игрок скрылся за экран, то заканчиваем сцену
        scene_fon_group.draw(screen)
        scene_player_group.draw(screen)
        scene_boom_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


def lose_scene(scene_list_of_sprites, lose_coord, scene_fon_group):
    """Сцена поражения.
    В ней мы получаем список спрайтов, которые нужно рисовать, координаты уничтожения игрока, группу для фонов"""
    scene_cam = Camera()
    tar = Target(225, lose_coord[1])
    second_counter = 0
    while True:
        for scene_event in pygame.event.get():  # Запускаем обработчик событий
            if scene_event.type == pygame.QUIT:
                terminate()
        if second_counter > 3 * FPS:  # Когда проходит три секунды, заканчиваем сцену
            return
        screen.fill((0, 0, 0))
        scene_cam.update(tar)
        scene_fon_group.draw(screen)
        for i1 in scene_list_of_sprites:
            i1.draw(screen)
            i1.update(True)
        pygame.display.flip()
        clock.tick(FPS)
        second_counter += 1


def find_vect(vect1, vect2):
    """Функция для нахождения скорости выстрела босса в системе отсчёта игрока"""
    vect3 = vect1 + vect2
    return vect3


def choice_mode_screen():
    """Функция для выбора корабля игрока"""
    screen.fill((0, 0, 0))
    maket_group, choice_fon_group = get_sprites_group(), get_sprites_group()  # Создаём макеты для кораблей
    Fon(-300, -200, choice_fon_group, 2)  # Создаём фон
    # Создаём корабли
    pl1 = Player((WIDTH - 100) // 2, 100, maket_group, coordinates_not_for_scenes=False, append_to_all_sprites=False)
    pl2 = Falcon((WIDTH - 100) // 2, 400, maket_group, coordinates_not_for_scenes=False, append_to_all_sprites=False)
    while True:
        for choice_event in pygame.event.get():
            if choice_event.type == pygame.QUIT:
                terminate()
            # Смотрим за выбором пользователя
            elif choice_event.type == pygame.MOUSEBUTTONDOWN and pl1.rect.collidepoint(choice_event.pos):
                return False
            elif choice_event.type == pygame.MOUSEBUTTONDOWN and pl2.rect.collidepoint(choice_event.pos):
                return True
        choice_fon_group.draw(screen)
        maket_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)


# Запускаем игру, используя функции из модуля levels
# Функция start_screen выводит главное меню. Затем она вызывает функцию display_lesson и возвращает её.
# Функция display_lesson позволяет игроку выбрать уровень и возвращает сгенерированную карту данного уровня и его номер
level_map, lesson_number, falcon_mode = start_screen(choice_mode_screen, falcon_mode=False)
while True:  # Запускаем первый игровой цикл, повторяющий создание уровней и обрабатывающий конец прохождения уровней
    pygame.mouse.set_visible(False)
    # Генерируем все нужные для игры группы спрайтов функцией из модуля const
    # Также создаём переменную boss созначением None
    player_lose_coordinates = []
    fon_group = get_sprites_group()
    fon_number = random.choice((1, 3))  # Выбираем фон для игры
    first_scene(fon_number, fon_group, falcon_mode)
    all_sprites, osk_group, weapons_group, meteors_group, enemies_group, player_group, boss_group, service_group, boss, fire_group = restart_sprites_for_game()
    # Создаём список для удобного рисования спрайтов
    sp_sprites = [fon_group, osk_group, weapons_group, meteors_group, enemies_group, player_group, boss_group,
                  service_group, fire_group]
    exit_via_pause = None
    righting, lefting = False, False  # Создаём флаги для управления игрока
    accel, deccel = False, False
    timer_on()  # Включаем таймеры  на события игры
    screen.fill((0, 0, 0))
    camera = Camera()
    sk = Scale(0, 0, falcon_mode)
    am = AmCount(WIDTH - 50, 4)
    player = view_lesson(
        falcon_mode)  # Создаём спрайты по карте уровня с помощью view_lesson, которая возвращает объект игрока
    for i in boss_group:  # Создаём переменную boss с объектом босса, если он есть, если нет, то она остаётся None
        boss = i
    while True:  # Запускаем игровой цикл самого уровня
        screen.fill((0, 0, 0))
        for event in pygame.event.get():  # Запускаем обработчик событий
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                # С помощью следующих нажатий клавиш реализуется управление игроком
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    lefting = True
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    righting = True
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    accel = True
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    deccel = True
                if event.key == pygame.K_e and player is not None:  # С помощью клавиш E и Q можно стрелять
                    player.shot_e()
                if event.key == pygame.K_q and player is not None:
                    player.shot_q()
                if event.key == pygame.K_SPACE:  # С помощью пробела, игра ставится на паузу
                    exit_via_pause = pause_screen(lesson_number)
                    if exit_via_pause != 'play':
                        break
            elif event.type == pygame.KEYUP:
                # Когда пользователь перестаёт нажимать клавишу, то её действие должно прекратиться
                if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                    lefting = False
                if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                    righting = False
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    accel = False
                if event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    deccel = False
            elif event.type == SHOT_TYPE1:  # Во время данных двух событий вражеские корабли делают выстрелы
                for i in enemies_group:
                    if type(i) is Enemy:
                        i.do_shot(1)
            elif event.type == SHOT_TYPE2:
                for i in enemies_group:
                    if type(i) is Enemy:
                        i.do_shot(0)
            elif event.type == HEAL_TYPE:  # Во время этого события происходит восстановление здоровья
                if player is not None:
                    player.heal(10)
                for i in enemies_group:
                    i.heal(10)
            elif event.type == AMM_TYPE:  # Во время этого события происходит пополнение боеприпасов
                if player is not None:
                    player.reamm()
                for i in enemies_group:
                    i.reamm()
            if boss is not None:  # Далее идут события, связанные с боссом
                if event.type == SHIELD_START_TYPE:  # Это событие включает щит
                    boss.start_shield()
                elif event.type == BOSS_SHOT_TYPE:  # Это событие делает атаку босса
                    boss.shot()
        if exit_via_pause is not None and exit_via_pause != 'play':
            break
        if player is None:
            # Если игрок уничтожен, то пользователь проиграл, поэтому выходим из цикла и пишем о поражении
            lose_scene([meteors_group, boss_group, osk_group, enemies_group, fire_group], player_lose_coordinates,
                       fon_group)
            level_map, lesson_number, falcon_mode = end_screen(False, lesson_number, falcon_mode, choice_mode_screen)
            break
        k = 0  # Считаем количество оставшихся вражеских кораблей и астероидов с помощью переменной k
        for i in meteors_group:
            k += 1
        for i in enemies_group:
            k += 1
        if k == 0 and boss is None:  # Если никого больше не осталось, то выходим из цикла и пишем о победе
            won_scene(fon_group, player, player_group, osk_group)
            level_map, lesson_number, falcon_mode = end_screen(True, lesson_number, falcon_mode, choice_mode_screen)
            break
        if player is not None:
            camera.update(player)  # Настраиваем камеру на игрока
            for sprite in all_sprites:  # Меняем координаты объектов с помощью камеры
                camera.apply(sprite)
        for i in sp_sprites:
            i.draw(screen)
        all_sprites.update()
        fon_group.update()
        for i in meteors_group:
            i.fun()  # Обновляем астероиды для их столконвений
        pygame.display.flip()
        clock.tick(FPS)
    if exit_via_pause == 'les':
        level_map, lesson_number, falcon_mode = display_lessons(falcon_mode, choice_mode_screen)
    elif exit_via_pause == 'main':
        level_map, lesson_number, falcon_mode = start_screen(choice_mode_screen, falcon_mode)

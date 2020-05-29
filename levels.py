import random
import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('pic', name)
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
          'boss fire': load_sound("TIE fighter fire 3.wav")}  # Файлы музыки и картинок


def terminate():
    """Функция для выхода"""
    pygame.quit()
    sys.exit()


def start_screen():
    """Выводит главное меню"""
    global music
    sp = []
    intro_text = ["PySpace", 'Играть']
    if music == 0:  # Запускаем музыку, если она ещё не играет
        pygame.mixer_music.load(sounds['main_theme'])
        pygame.mixer_music.play(-1)
        pygame.mixer_music.set_volume(0.6)
        music = 1
    screen.fill((0, 0, 0))
    Fon(-400, -200, fon_group, 1)
    fon_group.draw(screen)
    font = pygame.font.Font(None, 50)
    text_coord = [160, -170]  # Заполняем фон
    for line in intro_text:  # Выводим текст главного меню
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
        for event in pygame.event.get():  # Ждём щелчка для показа уровней
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN and r.collidepoint(event.pos):
                return display_lessons()
        pygame.display.flip()
        clock.tick(FPS)


player = None  # Объект игрока, первоначально не задан
all_sprites = pygame.sprite.Group()
my_group = pygame.sprite.Group()  # Группа спрайтов для специальных объектов (стрелок для перехода)
lessons_group = pygame.sprite.Group()  # Группа спрайтов для показа значков уровней
fon_group = pygame.sprite.Group()  # Группа спрайтов для фонов


class Fon(pygame.sprite.Sprite):
    """ Класс фонов для игры"""

    def __init__(self, x, y, fon_gr, n, b=False):
        """Для инициализации нужны координаты, номер фона (также как для уровней) n, указание фон для босса или нет b"""
        super().__init__(all_sprites, fon_gr)
        if not b:
            self.image = images[f'fon{n}']
        else:
            self.image = images[f'fonb{n}']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.n = 0


class MySprite(pygame.sprite.Sprite):
    """Класс для стрелок"""

    def __init__(self, pov, x, y):  # Создаём спрайт
        super().__init__(all_sprites, my_group)
        if not pov:  # Смотрим какая стрелка нам нужна
            self.image = images['strelki']
        else:
            self.image = images['sterki1']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):  # Смотрим, есть ли нажатие
        if self.rect.collidepoint(args[0].pos):
            return True
        else:
            return False


class Lesson(pygame.sprite.Sprite):
    """Класс для показа значков уровней
    Всего уровней 3"""

    def __init__(self, n):  # Создаём значок
        super().__init__(lessons_group, all_sprites)
        self.image = load_image(f'lesson{n}.png', -1)
        self.rect = self.image.get_rect()
        self.rect.x = 160
        self.lesson_number = n
        if n == 1:  # Выбираем координату по высоте, которая подходит данному уровню
            self.rect.y = 25
        elif n == 2:
            self.rect.y = 250
        else:
            self.rect.y = 475

    def choice_music(self):
        if self.lesson_number == 3:  # Выбираем музыку, которая будет играть
            pygame.mixer_music.load(sounds['boss_theme'])
        else:
            pygame.mixer_music.load(sounds['game_theme'])
        pygame.mixer_music.play(-1)

    def update(self, *args):  # Смотрим на действия пользователя
        if self.rect.collidepoint(args[0].pos):
            self.choice_music()
            return generate_level(
                f'level{self.lesson_number}.txt'), self.lesson_number  # Возвращаем загруженный уровень
        else:
            return False


def display_lessons(lesson_number=None):
    """Показываем уровни и запускаем их.
    lesson_number нужно для того чтобы запускать определённый уровень без выбора пользователя.
    Когда пользователь сам заходит, то lesson_number=None"""
    global music
    if lesson_number is None:  # Случай, когда пользователь выбирает уровень
        screen.fill((0, 0, 0))
        Fon(-10, -10, fon_group, 2)
        for i in range(3):  # Загружаем значки уровней
            Lesson(i + 1)
        MySprite(True, 0, 0)  # Загружаем стрелочку
        while True:
            for event in pygame.event.get():  # Отслеживаем действия пользователя
                if event.type == pygame.QUIT:  # Выход
                    terminate()
                if event.type == pygame.MOUSEBUTTONDOWN:  # Нажатие на уровень
                    for i in lessons_group:
                        if i.update(event):
                            return i.update(event)
                    for i in my_group:  # Нажатие на стрелку
                        if i.update(event):
                            return start_screen()
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
    else:  # Случай, когда пользователь нажал на кнопку по переходу на какой-то уровень, проходя уровень
        for i in lessons_group:
            if i.lesson_number == lesson_number:
                i.choice_music()
                pygame.mixer_music.set_volume(0.6)
                music = 0
                return generate_level(f'level{lesson_number}.txt'), lesson_number


def generate_level(filename):  # Собираем уровень
    """Уровни изначально заданы только количеством врагов и волн
    Конфигурация собирается в этом уровне по файлу из папки levels"""
    filename = "levels/" + filename  # Расположение файла
    sp = []
    with open(filename, mode='r') as map_file:  # Открываем файл
        text = map_file.readlines()
        map_width = 9  # Количество возможных координат появления врагов и препятствий
        for i in text[0].strip().split(';'):  # Расшифровываем запись
            sp1 = []
            if not i:
                continue
            for j in range(0, len(i) - 1, 2):
                k = i[j]
                typ = i[j + 1]  # Определяем тип врага
                if typ == 'm':
                    elem = '*'
                else:
                    elem = typ
                # m - Метеоры
                # n - корабли врагов
                # b - босс
                sp1.extend((k, elem))
            sp.append(sp1)  # Получаем список с количеством врагов
    map1 = []
    sp = sp[::-1]
    for i in range(len(sp)):  # Формируем список строк с точным расположением врагов и свободных мест
        s = []
        for j in range(0, len(sp[i]) - 1, 2):  # Собираем одну строку с всеми врагами в определённое время появления
            k = int(sp[i][j])
            elem = sp[i][j + 1]
            s += k * elem
        if map_width < len(s):  # Исключаем возможные ошибки с слишком большим количеством врагов в уровне
            s = s[:map_width]
            print('Слишком много врагов, уровень обрезан')
        if not s.count('b') and not s.count('n'):  # Если только метеориты в линии
            s += (map_width - len(s)) * '-'  # Добавляем количество свободных мест
            random.shuffle(s)  # Перемешиваем, чтобы добавить вариантов
            map1.append(''.join(s))
        elif not s.count('b') and s.count('n'):  # Если только корабли в линии
            s = '--n'
            # Добавляем вражеский корабль, не важно где они будут стоять, так как они позиционируются по игроку
            s += (map_width - len(s)) * '-'
            map1.append(''.join(s))
        else:  # Если есть босс
            lw = map_width
            if lw % 2 != 0:  # Ставим босса по середине
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


def end_screen(won, lesson_number):
    """Функция для обработки конца игры
    won - показатель победы"""
    global music
    sp = []
    if won:
        intro_text = ["Вы победили"]
    else:
        intro_text = ["Вы проиграли"]
    intro_text.append("К уровням")
    intro_text.append("Главное меню")
    if won and lesson_number != 3:  # Если уровень третий, то следущего уровня нет
        intro_text.append('К следующему уровню')
    else:
        intro_text.append('Повторить попытку')
    if won:  # Музыка победы
        pygame.mixer_music.load(sounds['won_theme'])
        pygame.mixer_music.play(-1)
        pygame.mixer_music.set_volume(0.6)
    else:  # Музыка поражения
        pygame.mixer_music.load(sounds['lose_theme'])
    pygame.mixer_music.play(-1)
    music = 0
    screen.fill((0, 0, 0))
    Fon(-400, -200, fon_group, 3)
    fon_group.draw(screen)
    font = pygame.font.Font(None, 50)
    text_coord = [(100, 100), (120, 300), (95, 350)]
    if won and lesson_number != 3:  # В зависимости от длины слова меняется координата
        text_coord.append((30, 250))
    else:
        text_coord.append((75, 250))
    for line in range(len(intro_text)):  # Загрузка текста
        string_rendered = font.render(intro_text[line], 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord[line][1]
        intro_rect.x = text_coord[line][0]
        sp.append(intro_rect)
        screen.blit(string_rendered, intro_rect)
    button_for_lessons = sp[1]  # Переход к уровням
    button_for_main = sp[2]  # Переход к главному меню
    button_for_next_lesson = sp[3]  # Переход к повтору или следующему уровню
    # Зависит от прохождения уровня
    while True:  # Обработка действий пользователя
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выход
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Нажатие на кнопки
                if button_for_lessons.collidepoint(event.pos):
                    return display_lessons()
                if button_for_main.collidepoint(event.pos):
                    return start_screen()
                if button_for_next_lesson.collidepoint(event.pos):
                    # Используем второй случай display_lessons с переходом на другой уровень без выбора пользователя
                    if not won or lesson_number == 3:
                        return display_lessons(lesson_number)
                    else:
                        return display_lessons(lesson_number + 1)
        pygame.display.flip()
        clock.tick(FPS)

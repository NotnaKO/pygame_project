import random
import sys
from const import *
from data import images, sounds, load_image

player = None  # Объект игрока, первоначально не задан
all_sprites, my_group, lessons_group, fon_group = restart_sprites_for_lessons()


class PlayerLayout(pygame.sprite.Sprite):
    def __init__(self, x, y, layout_group):
        super().__init__(layout_group)
        self.image = images['player']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class FalconLayout(pygame.sprite.Sprite):
    def __init__(self, x, y, layout_group):
        super().__init__(layout_group)
        self.image = images['falcon']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


def terminate():
    """Функция для выхода"""
    pygame.quit()
    sys.exit()


def draw_start_screen(intro_text, sp, falcon_mode):
    screen.fill((0, 0, 0))
    Fon(-400, -200, fon_group, 1)
    fon_group.draw(screen)
    lay_group = get_sprites_group()
    if falcon_mode:
        FalconLayout(170, 450, lay_group)
    else:
        PlayerLayout(170, 450, lay_group)
    lay_group.draw(screen)
    font = pygame.font.Font(None, 50)
    text_coord = [(140, 70), (150, 200), (80, 260), (150, 320)]
    for line in range(len(intro_text)):  # Загрузка текста
        string_rendered = font.render(intro_text[line], 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord[line][1]
        intro_rect.x = text_coord[line][0]
        sp.append(intro_rect)
        screen.blit(string_rendered, intro_rect)
    return sp[1], sp[2], sp[3]


def start_screen(function_for_choice_mode_screen, falcon_mode):
    """Выводит главное меню"""
    global music
    pygame.mouse.set_visible(True)
    sp = []
    intro_text = ["PySpace", 'Играть', 'Выбор корабля', "Выход"]
    if music == 0:  # Запускаем музыку, если она ещё не играет
        pygame.mixer_music.load(sounds['main_theme'])
        pygame.mixer_music.play(-1)
        pygame.mixer_music.set_volume(0.6)
        music = 1
    play_button, choice_button, exit_button = draw_start_screen(intro_text, sp, falcon_mode)
    while True:
        for event in pygame.event.get():  # Ждём щелчка для показа уровней
            if event.type == pygame.QUIT or (
                    event.type == pygame.MOUSEBUTTONDOWN and exit_button.collidepoint(event.pos)):
                terminate()  # Выход
            elif event.type == pygame.MOUSEBUTTONDOWN and play_button.collidepoint(event.pos):
                return display_lessons(falcon_mode, function_for_choice_mode_screen)
            elif event.type == pygame.MOUSEBUTTONDOWN and choice_button.collidepoint(event.pos):
                falcon_mode = function_for_choice_mode_screen()
                play_button, choice_button, exit_button = draw_start_screen(intro_text, sp, falcon_mode)
        pygame.display.flip()
        clock.tick(FPS)


class Fon(pygame.sprite.Sprite):
    """ Класс фонов для игры"""

    def __init__(self, x, y, fon_gr, n, battle=False):
        """Для инициализации нужны координаты, номер фона (также как для уровней) n,
         указание фон для битвы или нет batle"""
        super().__init__(all_sprites, fon_gr)
        if not battle:
            self.image = images[f'fon{n}']
        else:
            self.image = images[f'fonb{n}']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.n = 0  # Счётчик


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

    def update(self, event, falcon_mode):  # Смотрим на действия пользователя
        if self.rect.collidepoint(event.pos):
            self.choice_music()
            return generate_level(
                f'level{self.lesson_number}.txt'), self.lesson_number, falcon_mode  # Возвращаем загруженный уровень
        else:
            return False


def display_lessons(falcon_mode, function_for_choice_mode_screen, lesson_number=None):
    """Показываем уровни и запускаем их.
    lesson_number нужно для того чтобы запускать определённый уровень без выбора пользователя.
    Когда пользователь сам заходит, то lesson_number=None"""
    global music
    pygame.mouse.set_visible(True)
    if lesson_number is None:  # Случай, когда пользователь выбирает уровень
        if music == 0:  # Запускаем музыку, если она ещё не играет
            pygame.mixer_music.load(sounds['main_theme'])
            pygame.mixer_music.play(-1)
            pygame.mixer_music.set_volume(0.6)
            music = 1
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
                        answer = i.update(event, falcon_mode)
                        if answer:
                            return answer
                    for i in my_group:  # Нажатие на стрелку
                        if i.update(event):
                            return start_screen(function_for_choice_mode_screen, falcon_mode)
            all_sprites.draw(screen)
            pygame.display.flip()
            clock.tick(FPS)
    else:  # Случай, когда пользователь нажал на кнопку по переходу на какой-то уровень, проходя уровень
        for i in lessons_group:
            if i.lesson_number == lesson_number:
                i.choice_music()
                pygame.mixer_music.set_volume(0.6)
                music = 0
                return generate_level(f'level{lesson_number}.txt'), lesson_number, falcon_mode


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
                # m - астероиды
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
            level_width = map_width
            if level_width % 2 != 0:  # Ставим босса по середине
                pl_xn = (level_width - 1) // 2
            else:
                pl_xn = level_width // 2
            sp1 = []
            for i1 in range(level_width):
                if i1 != pl_xn:
                    sp1.append('-')
                else:
                    sp1.append('b')
            map1.append(''.join(sp1))
    if LEVEL_WIDTH % 2 != 0:
        pl_xn = (LEVEL_WIDTH - 1) // 2
    else:
        pl_xn = LEVEL_WIDTH // 2
    sp = []
    for i in range(LEVEL_WIDTH):
        if i != pl_xn:
            sp.append('-')
        else:
            sp.append('P')
    for i in range(5):
        map1.append(''.join(sp).replace('P', '-'))
    map1.append(''.join(sp))
    return map1


def pause_screen(lesson_number):
    """Выводит окно для паузы"""
    global music
    pygame.mouse.set_visible(True)
    answer = None
    sp = []
    k = 0
    intro_text = ['Пауза', "Продолжить", "К уровням", "Главное меню"]
    screen.fill((0, 0, 0))
    Fon(-400, -200, fon_group, lesson_number)
    fon_group.draw(screen)
    font = pygame.font.Font(None, 50)
    text_coord = [(170, 100), (110, 300), (130, 350), (100, 400)]
    for line in range(len(intro_text)):  # Загрузка текста
        string_rendered = font.render(intro_text[line], 1, pygame.Color('white'))
        intro_rect = string_rendered.get_rect()
        intro_rect.top = text_coord[line][1]
        intro_rect.x = text_coord[line][0]
        sp.append(intro_rect)
        screen.blit(string_rendered, intro_rect)
    play_button = sp[1]
    lesson_button = sp[2]
    main_menu_button = sp[3]
    while True:  # Обработка действий пользователя
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Выход
                terminate()
            elif event.type == pygame.MOUSEBUTTONDOWN:  # Нажатие на кнопки
                if lesson_button.collidepoint(event.pos):
                    answer = 'les'
                    pygame.mixer_music.play(-1)
                    music = 0
                if main_menu_button.collidepoint(event.pos):
                    answer = 'main'
                    pygame.mixer_music.play(-1)
                    music = 0
                if play_button.collidepoint(event.pos):
                    answer = 'play'

        if k % FPS == 0:  # Когда прошла секунда, смотрим сделал ли пользователь выбор или нет
            if answer is not None:
                return answer  # Если время прошло выбор сделан, то отправляем этот выбор
            else:
                pygame.time.wait(1000)  # Если нет, то останвливаем время дальше, чтобы не потерять события в игре
            k = 0
        k += 1
        pygame.display.flip()
        clock.tick(FPS)


def end_screen(won, lesson_number, falcon_mode, function_for_choice_mode_screen):
    """Функция для обработки конца игры
    won - показатель победы"""
    global music
    pygame.mouse.set_visible(True)
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
    text_coord = [(100, 100), (130, 300), (95, 350)]
    if won and lesson_number != 3:  # В зависимости от длины слова меняется координата
        text_coord.append((30, 250))
    else:
        text_coord.append((60, 250))
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
                    return display_lessons(falcon_mode, function_for_choice_mode_screen)
                if button_for_main.collidepoint(event.pos):
                    return start_screen(function_for_choice_mode_screen, falcon_mode)
                if button_for_next_lesson.collidepoint(event.pos):
                    # Используем второй случай display_lessons с переходом на другой уровень без выбора пользователя
                    if not won or lesson_number == 3:
                        return display_lessons(falcon_mode, function_for_choice_mode_screen, lesson_number)
                    else:
                        return display_lessons(falcon_mode, function_for_choice_mode_screen, lesson_number + 1)
        pygame.display.flip()
        clock.tick(FPS)

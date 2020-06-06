import pygame


def create_cursor():
    pygame.mouse.set_cursor(*pygame.cursors.broken_x)


GAME_SPEED = 200  # дальность расположения метеоров
MY_EVENT_TYPE = 10  # Просто число для события
SHOT_TYPE1 = 21  # Событие для выстрела слева
SHOT_TYPE2 = 22
PLAYER_SPEED = 5
KILL_TYPE = 14
ENEMY_SPEED = 4.5
METEOR_SPEED = PLAYER_SPEED * 0.2
ENEMY_LEVEL = 9
PLAYER_AMM = 30
HEAL_TYPE = 31
BOSS_HEALTH = 800
BOSS_SHIELD_MAX_HEALTH = 90
AMM_TYPE = 11
SHIELD_START_TYPE = 25
BOSS_SHOT_TYPE = 27
GRAVITY = 0
METEOR_MINI_DAMAGE = 0  # Урон от столкновения между собой астероидов
FPS = 30
size = WIDTH, HEIGHT = 450, 650
LEVEL_WIDTH = 9
COLUMN_COUNT = WIDTH // LEVEL_WIDTH
pygame.init()
create_cursor()
screen = pygame.display.set_mode(size)
clock = pygame.time.Clock()
music = 0
player = None  # Объект игрока, первоначально не задан


def restart_sprites_for_game():
    boss1 = None
    return (get_sprites_group(), get_sprites_group(), get_sprites_group(), get_sprites_group(),
            get_sprites_group(), get_sprites_group(), get_sprites_group(),
            get_sprites_group(), boss1, get_sprites_group())


def restart_sprites_for_lessons():
    return get_sprites_group(), get_sprites_group(), get_sprites_group(), get_sprites_group()


def get_sprites_group():
    return pygame.sprite.Group()


def timer_on():
    pygame.time.set_timer(SHOT_TYPE1, int((10 - ENEMY_LEVEL) * 1000))  # Запускаем два таймера выстрелов для врагов
    pygame.time.set_timer(SHOT_TYPE2, int((10 - ENEMY_LEVEL) * 1000))
    pygame.time.set_timer(AMM_TYPE, 3500)  # Таймер восстановления боеприпасов
    pygame.time.set_timer(HEAL_TYPE, 10000)  # Таймер восстановления здоровья

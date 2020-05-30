import os
import pygame


def load_image(name, colorkey=None):
    """Загрузка фотографий"""
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
    """Получение полного имени файла звука"""
    fullname = os.path.join('sound', name)
    return fullname


def load_sound(name):
    """Загрузка звука"""
    snd = pygame.mixer.Sound(sound_name(name))
    return snd


images = {'player': load_image('player.png', -1), 'meteor0': load_image('meteor.png', -1),
          'meteor90': load_image('meteor90.png', -1), 'meteor180': load_image('meteor180.png', -1),
          'meteor270': load_image('meteor270.png', -1),
          'red_weap': load_image('red_weapon.png', -1), 'scale': load_image('shkala.png', -1),
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

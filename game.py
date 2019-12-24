from lessons import *

start_screen()
player_group = pygame.sprite.Group()
images = {'player': load_image('player.jpg')}


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(player_group)
        self.image = load_image('player.png')
        self.rect = self.image.get_rect()
        self.play = True
        self.damage = 10
        self.health = 100
        self.speed = 10

    def hurt(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.play = False

    def heal(self, health):
        self.health += health
        if self.health > 100:
            self.health = 100

    def move(self):
        self.rect.y -= self.speed


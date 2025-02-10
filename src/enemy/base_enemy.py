import pygame
from utils import load_image

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group, health, speed, points):
        super().__init__()
        self.bullet_group = bullet_group
        self.health = health
        self.speed = speed
        self.points = points

    def take_damage(self, damage):
        self.health -= damage

    def wrap_position(self):
        # Wrap enemy position within the play area (horizontal: 15%-85% of screen width; vertical: full height)
        screen = pygame.display.get_surface()
        if not screen:
            return
        sw, sh = screen.get_size()
        left_bound = int(sw * 0.16)
        right_bound = int(sw * 0.84)
        if self.rect.right < left_bound:
            self.rect.left = right_bound
        elif self.rect.left > right_bound:
            self.rect.right = left_bound
        if self.rect.top > sh:
            self.rect.bottom = 0
        elif self.rect.bottom < 0:
            self.rect.top = sh

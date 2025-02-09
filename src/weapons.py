# src/weapons.py
import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vy, damage=1):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = vy
        self.damage = damage

    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < 0 or self.rect.top > 800:
            self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, vy, damage=5):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = vy
        self.damage = damage

    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < 0 or self.rect.top > 800:
            self.kill()

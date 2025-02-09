# src/powerups.py
import pygame
from utils import load_image

class BasePowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, color, size):
        super().__init__()
        self.image = load_image(image_path, color, size)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > 800:
            self.kill()

class ShieldPowerUp(BasePowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/powerup_shield.png", (0, 0, 255), (24, 24))
        self.shield_amount = 25

    def apply(self, player):
        player.shield += self.shield_amount
        if player.shield > 100:
            player.shield = 100

class WeaponUpgradePowerUp(BasePowerUp):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/powerup_weapon.png", (255, 255, 0), (24, 24))

    def apply(self, player):
        player.weapon_level += 1

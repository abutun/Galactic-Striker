# src/weapon/weapon7.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet
import pygame

class Weapon7(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Fireball Shot: one large, high-damage bullet.
        x = player.rect.centerx
        y = player.rect.top
        damage = 4 * player.weapon_level
        bullet = Bullet(x, y, 0, -player.bullet_speed, damage)
        bullet.image = pygame.Surface((10, 20))
        bullet.image.fill((255, 100, 0))
        bullet.rect = bullet.image.get_rect(center=(x, y))
        bullet_group.add(bullet)

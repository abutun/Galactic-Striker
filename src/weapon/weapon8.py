# src/weapon/weapon8.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet
import pygame

class Weapon8(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Laser Beam: fires a thin beam bullet.
        x = player.rect.centerx
        y = player.rect.top
        damage = 3 * player.weapon_level
        bullet = Bullet(x, y, 0, -player.bullet_speed, damage)
        bullet.image = pygame.Surface((3, 20))
        bullet.image.fill((0, 255, 0))
        bullet.rect = bullet.image.get_rect(center=(x, y))
        bullet_group.add(bullet)

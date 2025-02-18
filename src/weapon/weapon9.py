# src/weapon/weapon9.py
import pygame
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon
from src.utils.utils import load_image

class Weapon9(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # War. I. Plasma Shot: one very powerful bullet.
        x = player.rect.centerx
        y = player.rect.top
        damage = 6 * player.weapon_level
        bullet = Bullet(x, y, 0, -player.bullet_speed, damage)
        bullet.image = pygame.Surface((5, 20))
        bullet.image.fill((255, 0, 255))
        bullet.rect = bullet.image.get_rect(center=(x, y))
        bullet_group.add(bullet)

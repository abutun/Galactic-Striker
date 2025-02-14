# src/weapon/weapon3.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet

class Weapon3(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Triple Shot: one bullet straight, one left, one right.
        spacing = 5
        x = player.rect.centerx
        y = player.rect.top
        damage = 1 * player.weapon_level
        bullet_center = Bullet(x, y, 0, -player.bullet_speed, damage)
        bullet_left = Bullet(x - spacing, y, -1, -player.bullet_speed, damage)
        bullet_right = Bullet(x + spacing, y, 1, -player.bullet_speed, damage)
        bullet_group.add(bullet_center)
        bullet_group.add(bullet_left)
        bullet_group.add(bullet_right)

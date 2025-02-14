# src/weapon/weapon5.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet

class Weapon5(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Super Triple Shot: fires three bullets with increased damage.
        spacing = 7
        x = player.rect.centerx
        y = player.rect.top
        damage = int(1.5 * player.weapon_level)
        bullet_center = Bullet(x, y, 0, -player.bullet_speed, damage)
        bullet_left = Bullet(x - spacing, y, -1, -player.bullet_speed, damage)
        bullet_right = Bullet(x + spacing, y, 1, -player.bullet_speed, damage)
        bullet_group.add(bullet_center)
        bullet_group.add(bullet_left)
        bullet_group.add(bullet_right)

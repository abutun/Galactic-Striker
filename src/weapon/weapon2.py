# src/weapon/weapon2.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet

class Weapon2(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Double Shot: fires two bullets in a slight spread.
        spacing = 5
        x = player.rect.centerx
        y = player.rect.top
        damage = 1 * player.weapon_level
        bullet_left = Bullet(x - spacing, y, -1, -player.bullet_speed, damage)
        bullet_right = Bullet(x + spacing, y, 1, -player.bullet_speed, damage)
        bullet_group.add(bullet_left)
        bullet_group.add(bullet_right)

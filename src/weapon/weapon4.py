# src/weapon/weapon4.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet

class Weapon4(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Quad Shot: fires four bullets with wider spread.
        spacing = 10
        x = player.rect.centerx
        y = player.rect.top
        damage = 1 * player.weapon_level
        b1 = Bullet(x - spacing, y, -2, -player.bullet_speed, damage)
        b2 = Bullet(x - spacing//2, y, -1, -player.bullet_speed, damage)
        b3 = Bullet(x + spacing//2, y, 1, -player.bullet_speed, damage)
        b4 = Bullet(x + spacing, y, 2, -player.bullet_speed, damage)
        bullet_group.add(b1)
        bullet_group.add(b2)
        bullet_group.add(b3)
        bullet_group.add(b4)

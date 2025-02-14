# src/weapon/weapon6.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet

class Weapon6(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Plasma Shot: fires a denser spread of 4 bullets.
        spacing = 5
        x = player.rect.centerx
        y = player.rect.top
        damage = 2 * player.weapon_level
        b1 = Bullet(x - spacing, y, -1, -player.bullet_speed, damage)
        b2 = Bullet(x, y, 0, -player.bullet_speed, damage)
        b3 = Bullet(x + spacing, y, 1, -player.bullet_speed, damage)
        b4 = Bullet(x, y, 0, -player.bullet_speed - 1, damage)
        bullet_group.add(b1)
        bullet_group.add(b2)
        bullet_group.add(b3)
        bullet_group.add(b4)

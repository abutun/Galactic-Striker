# src/weapon/weapon1.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet

class Weapon1(PrimaryWeapon):
    def fire(self, player, bullet_group):
        # Single Shot: one bullet fired straight upward.
        x = player.rect.centerx
        y = player.rect.top
        vx = 0
        vy = -player.bullet_speed
        damage = 1 * player.weapon_level
        bullet = Bullet(x, y, vx, vy, damage)
        bullet_group.add(bullet)

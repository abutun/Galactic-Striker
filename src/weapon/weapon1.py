# src/weapon/weapon1.py
from .base_weapon import PrimaryWeapon
from src.weapons import Bullet
import logging

logger = logging.getLogger(__name__)

class Weapon1(PrimaryWeapon):
    def fire(self, player, bullet_group):
        try:
            x = player.rect.centerx
            y = player.rect.top
            vx = 0
            vy = -player.bullet_speed
            damage = max(1, 1 * player.weapon_level)  # Ensure minimum damage of 1
            bullet = Bullet(x, y, vx, vy, damage)
            bullet_group.add(bullet)
        except Exception as e:
            logger.error(f"Error firing weapon: {e}")

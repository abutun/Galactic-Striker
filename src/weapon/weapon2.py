# src/weapon/weapon2.py
import pygame
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon
from src.utils.utils import load_image

class Weapon2(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)
        self.bullet_damage = 2
        self.spacing = 15

    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            # Dual parallel shots
            bullet_left = Bullet(x - self.spacing/2, y, 0, -self.bullet_speed, self.bullet_damage)
            bullet_right = Bullet(x + self.spacing/2, y, 0, -self.bullet_speed, self.bullet_damage)
            self.bullet_group.add(bullet_left, bullet_right)
            self.last_fire = now
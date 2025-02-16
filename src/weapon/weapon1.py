# src/weapon/weapon1.py
import pygame
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon
from src.utils import load_image

class Weapon1(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)

    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            bullet = Bullet(x, y, 0, -self.bullet_speed, self.bullet_damage)
            self.bullet_group.add(bullet)
            self.last_fire = now

# src/weapon/weapon3.py
import pygame
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon
import math

class Weapon3(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)
        self.bullet_damage = 1
        self.spread = 15  # Spread angle in degrees

    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            # Triple shot with spread
            for angle in [-self.spread/2, 0, self.spread]:
                rad = math.radians(angle)
                vx = self.bullet_speed * math.sin(rad)
                vy = -self.bullet_speed * math.cos(rad)
                bullet = Bullet(x, y, vx, vy, self.bullet_damage)
                self.bullet_group.add(bullet)
            self.last_fire = now

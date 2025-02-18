# src/weapon/weapon6.py
import pygame
import math
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon

class Weapon6(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)
        self.bullet_damage = 1
        self.fire_delay = 400
        self.num_bullets = 5  # 5-way spread

    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            # 5-way spread shot
            angle_spread = 60  # Total spread angle
            for i in range(self.num_bullets):
                angle = -angle_spread/2 + (angle_spread/(self.num_bullets-1)) * i
                rad = math.radians(angle)
                vx = self.bullet_speed * math.sin(rad)
                vy = -self.bullet_speed * math.cos(rad)
                bullet = Bullet(x, y, vx, vy, self.bullet_damage)
                self.bullet_group.add(bullet)
            self.last_fire = now

# src/weapon/weapon4.py
import pygame
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon

class Weapon4(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)
        self.bullet_damage = 2
        self.fire_delay = 250  # Balanced firing rate
        self.spacing = 15  # Space between bullets
        
    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            # Four parallel shots in a symmetrical pattern
            bullet1 = Bullet(x - self.spacing, y, 0, -self.bullet_speed, self.bullet_damage)
            bullet2 = Bullet(x - self.spacing/3, y, 0, -self.bullet_speed, self.bullet_damage)
            bullet3 = Bullet(x + self.spacing/3, y, 0, -self.bullet_speed, self.bullet_damage)
            bullet4 = Bullet(x + self.spacing, y, 0, -self.bullet_speed, self.bullet_damage)
            
            self.bullet_group.add(bullet1, bullet2, bullet3, bullet4)
            self.last_fire = now

# src/weapon/weapon4.py
import pygame
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon

class Weapon4(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)
        self.bullet_damage = 2
        self.fire_delay = 200  # Faster firing rate

    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            # Dual parallel shots
            spacing = 10
            bullet_left = Bullet(x - spacing, y, 0, -self.bullet_speed, self.bullet_damage)
            bullet_right = Bullet(x + spacing, y, 0, -self.bullet_speed, self.bullet_damage)
            self.bullet_group.add(bullet_left, bullet_right)
            self.last_fire = now

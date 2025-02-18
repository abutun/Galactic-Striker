# src/weapon/weapon5.py
import pygame
from src.weapon.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon

class Weapon5(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)
        self.bullet_damage = 3
        self.fire_delay = 300  # Slower but more powerful

    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            # Large powerful shot
            bullet = Bullet(x, y, 0, -self.bullet_speed, self.bullet_damage)
            bullet.image = pygame.Surface((10, 20))  # Larger bullet
            bullet.image.fill((255, 100, 0))  # Orange color
            bullet.rect = bullet.image.get_rect(center=(x, y))
            self.bullet_group.add(bullet)
            self.last_fire = now

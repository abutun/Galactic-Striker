# src/weapon/weapon7.py
import pygame
from src.weapons import Bullet
from src.weapon.base_weapon import PrimaryWeapon

class Weapon7(PrimaryWeapon):
    def __init__(self, bullet_group):
        super().__init__(bullet_group)
        self.bullet_damage = 4
        self.fire_delay = 500  # Slow but very powerful

    def fire(self, x, y):
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            # Fireball shot
            bullet = Bullet(x, y, 0, -self.bullet_speed, self.bullet_damage)
            bullet.image = pygame.Surface((15, 25))
            bullet.image.fill((255, 50, 0))  # Bright orange
            bullet.rect = bullet.image.get_rect(center=(x, y))
            self.bullet_group.add(bullet)
            self.last_fire = now

# src/enemy/swarmer_enemy.py
import pygame
import random
import math
from enemy.base_enemy import BaseEnemy
from utils import load_image

class SwarmerEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group):
        # Call parent's __init__ first.
        super().__init__(x, y, bullet_group, health=1, speed=3, points=150)
        self.image = load_image("assets/sprites/enemy_swarmer.png", (255, 69, 0), (32, 32))
        self.rect = self.image.get_rect(center=(x, y))
        # For zigzag pattern.
        self.direction = random.choice([-1, 1])
        # Choose a random movement pattern.
        self.movement_pattern = random.choice(["direct", "zigzag", "circular"])
        # For circular movement, add a time offset.
        self.time_offset = random.random() * 2 * math.pi
        self.fire_delay = 2000  # milliseconds between shots
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        # Apply the chosen movement pattern.
        if self.movement_pattern == "direct":
            self.rect.y += self.speed
        elif self.movement_pattern == "zigzag":
            self.rect.y += self.speed
            self.rect.x += self.direction * 2
        elif self.movement_pattern == "circular":
            self.rect.y += self.speed
            # Use a sine function for horizontal oscillation.
            t = pygame.time.get_ticks() / 1000.0 + self.time_offset
            amplitude = 20  # adjust amplitude as desired
            self.rect.x += int(math.sin(t) * amplitude)

        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now

        # Wrap position within the play area (see base_enemy.py for details).
        self.wrap_position()

    def fire(self):
        bullet = pygame.sprite.Sprite()
        bullet.image = pygame.Surface((5, 10))
        bullet.image.fill((255, 69, 0))
        bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
        bullet.speed = 6
        bullet.damage = 1

        def update_bullet(self):
            self.rect.y += self.speed
            screen = pygame.display.get_surface()
            if screen:
                _, sh = screen.get_size()
                if self.rect.top > sh:
                    self.kill()

        bullet.update = update_bullet.__get__(bullet)
        self.bullet_group.add(bullet)

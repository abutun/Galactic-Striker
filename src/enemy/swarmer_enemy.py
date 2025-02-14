# src/enemy/swarmer_enemy.py

import pygame
import random
import math
from enemy.base_enemy import BaseEnemy
from utils import load_image
from weapons import Bullet
from global_state import global_player

class SwarmerEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group):
        super().__init__(x, y, bullet_group, health=1, speed=3, points=150)
        self.image = load_image("assets/sprites/enemy_swarmer.png", (255, 69, 0), (32, 32))
        self.rect = self.image.get_rect(center=(x, y))
        self.direct_phase = True
        self.movement_pattern = None
        self.fire_delay = 2000
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        if self.path:
            self.follow_path()
        else:
            screen = pygame.display.get_surface()
            if screen:
                _, sh = screen.get_size()
                if self.rect.y < sh * 0.85:
                    self.rect.y += self.speed
                else:
                    if self.movement_pattern is None:
                        self.movement_pattern = random.choice(["zigzag", "circular", "random"])
                    if self.movement_pattern == "zigzag":
                        self.rect.y += self.speed
                        self.rect.x += random.choice([-2, 2])
                    elif self.movement_pattern == "circular":
                        t = pygame.time.get_ticks() / 1000.0
                        amplitude = 20
                        self.rect.y += self.speed
                        self.rect.x += int(math.sin(t) * amplitude)
                    elif self.movement_pattern == "random":
                        self.rect.y += self.speed
                        self.rect.x += random.randint(-3, 3)
        self.wrap_position()
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now

    def fire(self):
        if global_player is not None:
            player_pos = global_player.rect.center
            enemy_pos = self.rect.center
            dx = player_pos[0] - enemy_pos[0]
            dy = player_pos[1] - enemy_pos[1]
            angle = math.atan2(dy, dx)
            bullet_speed = 6
            vx = bullet_speed * math.cos(angle)
            vy = bullet_speed * math.sin(angle)
        else:
            vx = 0
            vy = 6
        bullet = pygame.sprite.Sprite()
        bullet.image = pygame.Surface((5, 10))
        bullet.image.fill((255, 69, 0))
        bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
        bullet.vx = vx
        bullet.vy = vy
        bullet.damage = 1

        def update_bullet(self):
            self.rect.x += self.vx
            self.rect.y += self.vy
            screen = pygame.display.get_surface()
            if screen:
                _, sh = screen.get_size()
                if self.rect.top > sh or self.rect.left < 0 or self.rect.right > screen.get_width():
                    self.kill()

        bullet.update = update_bullet.__get__(bullet)
        self.bullet_group.add(bullet)

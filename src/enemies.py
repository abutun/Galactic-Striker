# src/enemies.py
import pygame
import random
from utils import load_image

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group, health, speed, points):
        super().__init__()
        self.bullet_group = bullet_group
        self.health = health
        self.speed = speed
        self.points = points  # Score awarded when destroyed.

    def take_damage(self, damage):
        self.health -= damage

class GruntEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group):
        self.image = load_image("assets/sprites/enemy_grunt.png", (255, 0, 0), (32, 32))
        super().__init__(x, y, bullet_group, health=2, speed=2, points=100)
        self.rect = self.image.get_rect(center=(x, y))
        self.fire_delay = 1500  # Milliseconds between shots.
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now
        # Remove the enemy if it leaves the screen.
        surface = pygame.display.get_surface()
        if surface:
            _, sh = surface.get_size()
            if self.rect.top > sh:
                self.kill()

    def fire(self):
        bullet = pygame.sprite.Sprite()
        bullet.image = pygame.Surface((5, 10))
        bullet.image.fill((255, 0, 0))
        bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
        bullet.speed = 5
        bullet.damage = 1
        def update_bullet(self):
            self.rect.y += self.speed
            surface = pygame.display.get_surface()
            if surface:
                _, sh = surface.get_size()
                if self.rect.top > sh:
                    self.kill()
        bullet.update = update_bullet.__get__(bullet)
        self.bullet_group.add(bullet)

class SwarmerEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group):
        self.image = load_image("assets/sprites/enemy_swarmer.png", (255, 69, 0), (32, 32))
        super().__init__(x, y, bullet_group, health=1, speed=3, points=150)
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = random.choice([-1, 1])
        self.fire_delay = 2000
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        self.rect.x += self.direction * 2
        surface = pygame.display.get_surface()
        if surface:
            sw, _ = surface.get_size()
            if self.rect.left < 0 or self.rect.right > sw:
                self.direction *= -1
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now
        surface = pygame.display.get_surface()
        if surface:
            _, sh = surface.get_size()
            if self.rect.top > sh:
                self.kill()

    def fire(self):
        bullet = pygame.sprite.Sprite()
        bullet.image = pygame.Surface((5, 10))
        bullet.image.fill((255, 69, 0))
        bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
        bullet.speed = 6
        bullet.damage = 1
        def update_bullet(self):
            self.rect.y += self.speed
            surface = pygame.display.get_surface()
            if surface:
                _, sh = surface.get_size()
                if self.rect.top > sh:
                    self.kill()
        bullet.update = update_bullet.__get__(bullet)
        self.bullet_group.add(bullet)

class BossEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group, phases=3):
        self.image = load_image("assets/sprites/enemy_boss.png", (255, 255, 0), (64, 64))
        super().__init__(x, y, bullet_group, health=20 * phases, speed=1, points=1000)
        self.rect = self.image.get_rect(center=(x, y))
        self.phases = phases
        self.current_phase = 1
        self.fire_delay = 1000
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now
        # Transition to a new phase if health is low.
        if self.health < (20 * self.phases) * (1 - self.current_phase / self.phases) and self.current_phase < self.phases:
            self.current_phase += 1
            self.fire_delay = max(500, self.fire_delay - 200)
        surface = pygame.display.get_surface()
        if surface:
            _, sh = surface.get_size()
            if self.rect.top > sh:
                self.kill()

    def fire(self):
        # Fire a spread of projectiles.
        for angle in (-15, 0, 15):
            bullet = pygame.sprite.Sprite()
            bullet.image = pygame.Surface((8, 16))
            bullet.image.fill((255, 255, 0))
            bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
            rad = angle * 3.14 / 180
            bullet.vx = 3 * pygame.math.Vector2(1, 0).rotate(angle).x
            bullet.vy = 3 * pygame.math.Vector2(0, 1).rotate(angle).y + 3
            bullet.damage = 2
            def update_bullet(self):
                self.rect.x += self.vx
                self.rect.y += self.vy
                surface = pygame.display.get_surface()
                if surface:
                    sw, sh = surface.get_size()
                    if self.rect.top > sh or self.rect.left < 0 or self.rect.right > sw:
                        self.kill()
            bullet.update = update_bullet.__get__(bullet)
            self.bullet_group.add(bullet)

import pygame
from enemy.base_enemy import BaseEnemy
from utils import load_image

class GruntEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group):
        # Call parent's initializer first.
        super().__init__(x, y, bullet_group, health=2, speed=2, points=100)
        self.image = load_image("assets/sprites/enemy_grunt.png", (255, 0, 0), (32, 32))
        self.rect = self.image.get_rect(center=(x, y))
        self.fire_delay = 1500  # milliseconds between shots
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        # Move downwards.
        self.rect.y += self.speed
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now

        # Wrap the enemy's position within the play area.
        self.wrap_position()

    def fire(self):
        bullet = pygame.sprite.Sprite()
        bullet.image = pygame.Surface((5, 10))
        bullet.image.fill((255, 0, 0))
        bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
        bullet.speed = 5
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

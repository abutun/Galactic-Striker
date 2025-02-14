import pygame
import math
import random
from src.enemy.base_enemy import BaseEnemy
from src.utils import load_image
from src.global_state import global_player

class Alien(BaseEnemy):
    def __init__(self, x, y, bullet_group, health, speed, points, image_file, size):
        super().__init__(x, y, bullet_group, health, speed, points)
        # Load the image as a PNG now.
        self.image = load_image(image_file, (255, 255, 255), size)
        self.rect = self.image.get_rect(center=(x, y))
        self.fire_delay = 2000  # milliseconds delay between shots
        self.last_fire = pygame.time.get_ticks()
        self.path = None  # For enemy group movement (absolute coordinates)
        self.path_index = 0

    def follow_path(self):
        if self.path and self.path_index < len(self.path):
            target = self.path[self.path_index]
            dx = target[0] - self.rect.centerx
            dy = target[1] - self.rect.centery
            distance = math.hypot(dx, dy)
            if distance < 5:
                self.path_index += 1
            else:
                vx = (dx / distance) * self.speed
                vy = (dy / distance) * self.speed
                self.rect.x += vx
                self.rect.y += vy
        else:
            self.rect.y += self.speed

    def update(self):
        screen = pygame.display.get_surface()
        if screen:
            _, sh = screen.get_size()
            if self.rect.y < sh * 0.85:
                self.rect.y += self.speed
            else:
                if self.path:
                    self.follow_path()
                else:
                    pattern = random.choice(["zigzag", "circular", "random"])
                    if pattern == "zigzag":
                        self.rect.y += self.speed
                        self.rect.x += random.choice([-2, 2])
                    elif pattern == "circular":
                        t = pygame.time.get_ticks() / 1000.0
                        amplitude = 20
                        self.rect.y += self.speed
                        self.rect.x += int(math.sin(t) * amplitude)
                    elif pattern == "random":
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
            dx = player_pos[0] - self.rect.centerx
            dy = player_pos[1] - self.rect.centery
            angle = math.atan2(dy, dx)
            bullet_speed = 5
            vx = bullet_speed * math.cos(angle)
            vy = bullet_speed * math.sin(angle)
        else:
            vx, vy = 0, 5
        bullet = pygame.sprite.Sprite()
        bullet.image = pygame.Surface((5, 10))
        bullet.image.fill((255, 0, 0))
        bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
        bullet.vx = vx
        bullet.vy = vy
        bullet.damage = 1
        def update_bullet(self):
            self.rect.x += self.vx
            self.rect.y += self.vy
            scr = pygame.display.get_surface()
            if scr:
                sw, sh = scr.get_size()
                if self.rect.top > sh or self.rect.left < 0 or self.rect.right > sw:
                    self.kill()
        bullet.update = update_bullet.__get__(bullet)
        self.bullet_group.add(bullet)

class NonBossAlien(Alien):
    def __init__(self, x, y, bullet_group, enemy_category="small", enemy_type=1, subtype=1):
        """
        enemy_category: "small" or "large"
        enemy_type: integer 1..25
        subtype: integer 1 or 2
        """
        if enemy_category == "small":
            health = 1
            points = 100
            size = (32, 32)
        else:
            health = 3
            points = 200
            size = (48, 48)
        # Construct image filename using PNG extension.
        filename = f"assets/aliens/alien_{enemy_type:02d}_{enemy_category}_{subtype}.png"
        super().__init__(x, y, bullet_group, health, speed=2, points=points, image_file=filename, size=size)

class BossAlien(Alien):
    def __init__(self, x, y, bullet_group, boss_type=1):
        health = 20
        points = 1000
        size = (96, 96)
        filename = f"assets/aliens/boss_{boss_type:02d}.png"
        super().__init__(x, y, bullet_group, health, speed=1, points=points, image_file=filename, size=size)
        self.fire_delay = 1000

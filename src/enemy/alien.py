import pygame
import math
import random
from src.enemy.base_enemy import BaseEnemy
from src.utils.utils import load_image
from src.config.global_state import global_player
from src.weapons import Bullet
import logging

from src.config.game_settings import ALIEN_SETTINGS

logger = logging.getLogger(__name__)

class Alien(BaseEnemy):
    def __init__(self, x, y, bullet_group, health, speed, points):
        super().__init__(x, y, bullet_group, health, speed, points)
        self.fire_delay = 2000  # milliseconds delay between shots
        self.last_fire = pygame.time.get_ticks()
        self.path = None
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

        bullet = Bullet(self.rect.centerx, self.rect.bottom, vx, vy, 1)
        bullet.image.fill((255, 0, 0))  # Red for enemy bullets
        self.bullet_group.add(bullet)

    def take_damage(self, damage):
        self.health -= damage
        
        # Play hit sound based on alien type
        if hasattr(self, 'sound_manager') and self.sound_manager:
            sound_suffix = '1' if hasattr(self, 'enemy_type') and 'small' in self.enemy_type else '2'
            self.sound_manager.play(f'alien_hit_{sound_suffix}')
            
            if self.health <= 0:
                self.sound_manager.play(f'alien_death_{sound_suffix}')
                self.kill()

class NonBossAlien(Alien):
    def __init__(self, x, y, bullet_group, enemy_type="small", enemy_subtype=1):
        # Set up base stats based on enemy type
        if enemy_type == "small":
            health = ALIEN_SETTINGS["small"]["base_health"]
            points = ALIEN_SETTINGS["small"]["base_points"]
            size = ALIEN_SETTINGS["small"]["size"]
            speed = ALIEN_SETTINGS["small"]["speed_modifier"]
        else:  # large
            health = ALIEN_SETTINGS["large"]["base_health"]
            points = ALIEN_SETTINGS["large"]["base_points"]
            size = ALIEN_SETTINGS["large"]["size"]
            speed = ALIEN_SETTINGS["large"]["speed_modifier"]
            
        # Call parent constructor with base stats
        super().__init__(x, y, bullet_group, health, speed, points)
        
        # Load sprite based on type and subtype
        try:
            self.image = load_image(f"assets/aliens/{enemy_type}.png", fallback_color=(255, 0, 0),size=size)
            self.rect = self.image.get_rect(center=(x, y))
        except Exception as e:
            logger.error(f"Error loading alien sprite: {e}")
            # Create fallback surface
            self.image = pygame.Surface(size)
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect(center=(x, y))
        
        self.enemy_type = enemy_type  # Store the enemy type
        self.enemy_subtype = enemy_subtype

class BossAlien(Alien):
    def __init__(self, x, y, bullet_group, boss_type=1):
        health = ALIEN_SETTINGS["boss"]["base_health"] * boss_type
        points = ALIEN_SETTINGS["boss"]["base_points"]
        speed = ALIEN_SETTINGS["boss"]["speed_modifier"]
        
        super().__init__(x, y, bullet_group, health, speed, points)
        
        # Load boss sprite
        try:
            size = ALIEN_SETTINGS["boss"]["size"]
            self.image = load_image(
                f"assets/aliens/boss_{boss_type:02d}.png",
                fallback_color=(255, 255, 0),
                size=size
            )
            self.rect = self.image.get_rect(center=(x, y))
        except Exception as e:
            logger.error(f"Error loading boss sprite: {e}")
            self.image = pygame.Surface(ALIEN_SETTINGS["boss"]["size"])
            self.image.fill((255, 255, 0))
            self.rect = self.image.get_rect(center=(x, y))

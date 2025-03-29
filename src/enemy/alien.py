import pygame
import math
import random
from src.enemy.base_enemy import BaseEnemy
from src.utils.utils import load_image
from src.state.global_state import global_player
from src.weapon.weapons import Bullet
import logging

from src.config.game_settings import ALIEN_SETTINGS

logger = logging.getLogger(__name__)

class Alien(BaseEnemy):
    def __init__(self, id, x, y, bullet_group, health, speed, points, type, sub_type):
        super().__init__(id, x, y, bullet_group, health, speed, points, type, sub_type)
        # Randomize initial fire delay between 1500-2500ms
        self.fire_delay = random.randint(1500, 2500)
        self.last_fire = pygame.time.get_ticks() + random.randint(0, 1000)  # Randomize initial fire time
        self.path = None
        self.path_index = 0
        # Add spacing properties
        self.min_spacing = 40  # Minimum space between aliens

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
        try:
            # Update animation
            self.animation.update()
            
            # Update sprite with current animation frame
            current_frame = self.animation.get_current_frame()
            if self.type == "small":
                target_size = ALIEN_SETTINGS["small"]["size"]
            elif self.type == "large":
                target_size = ALIEN_SETTINGS["large"]["size"]
            else:  # boss
                target_size = ALIEN_SETTINGS["boss"]["size"]
            
            self.image = pygame.transform.scale(current_frame, target_size)
            
            # Regular movement and behavior updates
            screen = pygame.display.get_surface()
            if screen:
                _, sh = screen.get_size()
                
                # Check for collisions with other aliens and adjust position
                self.maintain_spacing()
                
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
                            
            # Handle firing
            now = pygame.time.get_ticks()
            if now - self.last_fire > self.fire_delay:
                self.fire()
                self.last_fire = now
                
        except Exception as e:
            logger.error(f"Error updating alien: {e}")

    def maintain_spacing(self):
        """Maintain minimum spacing between aliens"""
        for sprite in self.groups()[0].sprites():  # Get all sprites from the same group
            if sprite != self and isinstance(sprite, Alien):
                dx = self.rect.centerx - sprite.rect.centerx
                dy = self.rect.centery - sprite.rect.centery
                distance = math.hypot(dx, dy)
                
                if distance < self.min_spacing:
                    # Calculate repulsion vector
                    if distance > 0:
                        force_x = (dx / distance) * (self.min_spacing - distance) * 0.1
                        force_y = (dy / distance) * (self.min_spacing - distance) * 0.1
                    else:  # If exactly overlapping, move randomly
                        angle = random.uniform(0, 2 * math.pi)
                        force_x = math.cos(angle) * self.min_spacing * 0.1
                        force_y = math.sin(angle) * self.min_spacing * 0.1
                        
                    # Apply forces
                    self.rect.x += force_x
                    self.rect.y += force_y

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

        self.sound_manager.play(f'alien_fire_{self.sub_type}')

    def take_damage(self, damage):
        self.health -= damage
        
        # Play hit sound based on alien type
        self.sound_manager.play(f'alien_hit_{self.sub_type}')
            
        if self.health <= 0:
            self.sound_manager.play(f'alien_death_{self.sub_type}')
            self.kill()

class NonBossAlien(Alien):
    def __init__(self, id, x, y, bullet_group, alien_type="small", alien_subtype=1):
        # Set up base stats based on enemy type
        if alien_type == "small":
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
        super().__init__(id, x, y, bullet_group, health, speed, points, alien_type, alien_subtype)
        
        # Load sprite based on type and subtype
        try:
            self.image = load_image(f"assets/aliens/alien_{id}_{alien_type}_{alien_subtype}.png", fallback_color=(255, 0, 0),size=size)
            self.rect = self.image.get_rect(center=(x, y))
        except Exception as e:
            logger.error(f"Error loading alien sprite: {e}")
            # Create fallback surface
            self.image = pygame.Surface(size)
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect(center=(x, y))
        
        self.alien_type = alien_type  # Store the alien type
        self.alien_subtype = alien_subtype

class BossAlien(Alien):
    def __init__(self, id, x, y, bullet_group, boss_type=1):
        health = ALIEN_SETTINGS["boss"]["base_health"] * boss_type
        points = ALIEN_SETTINGS["boss"]["base_points"]
        speed = ALIEN_SETTINGS["boss"]["speed_modifier"]
        
        super().__init__(id, x, y, bullet_group, health, speed, points, "boss", boss_type)
        
        # Load boss sprite
        try:
            size = ALIEN_SETTINGS["boss"]["size"]
            self.image = load_image(
                f"assets/aliens/boss_{id}_{boss_type}.png",
                fallback_color=(255, 255, 0),
                size=size
            )
            self.rect = self.image.get_rect(center=(x, y))
        except Exception as e:
            logger.error(f"Error loading boss sprite: {e}")
            self.image = pygame.Surface(ALIEN_SETTINGS["boss"]["size"])
            self.image.fill((255, 255, 0))
            self.rect = self.image.get_rect(center=(x, y))

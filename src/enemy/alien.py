import pygame
import math
import random
from src.enemy.base_enemy import BaseEnemy
from src.utils.utils import load_image
from src.state.global_state import global_player
from src.weapon.weapons import Bullet
import logging
from src.utils.sprite_animation import SpriteAnimation

from src.config.game_settings import ALIEN_SETTINGS, PLAY_AREA

logger = logging.getLogger(__name__)

class Alien(BaseEnemy):
    def __init__(self, id, x, y, bullet_group, life, speed, points, type, sub_type, animation=None):
        super().__init__(id, x, y, bullet_group, life, speed, points, type, sub_type, animation)
        # Randomize initial fire delay between 1500-2500ms
        self.fire_delay = random.randint(5000, 15000)
        self.last_fire = pygame.time.get_ticks() + random.randint(0, 10000)  # Randomize initial fire time
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
                sw, sh = screen.get_size()
                
                # Define play area boundaries from settings
                left_boundary = sw * PLAY_AREA["left_boundary"]
                right_boundary = sw * PLAY_AREA["right_boundary"]
                
                # Check for collisions with other aliens and adjust position
                self.maintain_spacing()
                
                # Update position based on pattern
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
                
                # Wrap position within play area
                if self.rect.top > sh:  # Wrap vertically
                    self.rect.bottom = 0
                
                # Wrap horizontally - appear on opposite side
                if self.rect.right < left_boundary:  # Going beyond left boundary
                    self.rect.left = right_boundary - self.rect.width*2
                elif self.rect.left > right_boundary:  # Going beyond right boundary
                    self.rect.right = left_boundary + self.rect.width*2
                
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
        self.life -= 1
        
        # Play hit sound based on alien type
        self.sound_manager.play(f'alien_hit_{self.sub_type}')
            
        if self.life <= 0:
            self.sound_manager.play(f'alien_death_{self.sub_type}')
            self.kill()

class NonBossAlien(Alien):
    def __init__(self, id, x, y, bullet_group, alien_type, alien_subtype, animation=None):
        # Initialize base class first
        super().__init__(id, x, y, bullet_group, 
                        ALIEN_SETTINGS[alien_type]["base_life"], 
                        ALIEN_SETTINGS[alien_type]["speed_modifier"], 
                        ALIEN_SETTINGS[alien_type]["base_points"], 
                        alien_type, alien_subtype, animation)
        
        # Store the alien type and subtype
        self.alien_type = alien_type
        self.alien_subtype = alien_subtype

class BossAlien(BaseEnemy):
    def __init__(self, id, x, y, bullet_group, animation=None):
        super().__init__(id, x, y, bullet_group, 
                        ALIEN_SETTINGS["boss"]["base_life"],
                        ALIEN_SETTINGS["boss"]["speed_modifier"],
                        ALIEN_SETTINGS["boss"]["base_points"],
                        "boss", "1", animation)

        self.rect = self.image.get_rect(center=(x, y))
        self.phases = 3
        self.current_phase = 1
        self.fire_delay = 1000
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        screen = pygame.display.get_surface()
        if screen:
            _, sh = screen.get_size()
            if self.rect.y < sh * 0.85:
                self.rect.y += self.speed
            else:
                pattern = random.choice(["zigzag", "circular", "random"])
                if pattern == "zigzag":
                    self.rect.y += self.speed
                    self.rect.x += random.choice([-2, 2])
                elif pattern == "circular":
                    t = pygame.time.get_ticks() / 1000.0
                    amplitude = 15
                    self.rect.y += self.speed
                    self.rect.x += int(math.sin(t) * amplitude)
                elif pattern == "random":
                    self.rect.y += self.speed
                    self.rect.x += random.randint(-3, 3)
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now
        if self.life < (20 * self.phases) * (1 - self.current_phase / self.phases) and self.current_phase < self.phases:
            self.current_phase += 1
            self.fire_delay = max(500, self.fire_delay - 200)
        self.wrap_position()

    def fire(self):
        if global_player is not None:
            player_pos = global_player.rect.center
            enemy_pos = self.rect.center
            dx = player_pos[0] - enemy_pos[0]
            dy = player_pos[1] - enemy_pos[1]
            angle = math.atan2(dy, dx)
            bullet_speed = 3
            vx = bullet_speed * math.cos(angle)
            vy = bullet_speed * math.sin(angle)
        else:
            vx = 0
            vy = 3
        for angle_offset in (-15, 0, 15):
            bullet = pygame.sprite.Sprite()
            bullet.image = pygame.Surface((8, 16))
            bullet.image.fill((255, 255, 0))
            bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
            rad = math.radians(angle_offset)
            vx_offset = vx + 3 * math.cos(rad)
            vy_offset = vy + 3 * math.sin(rad)
            bullet.vx = vx_offset
            bullet.vy = vy_offset
            bullet.damage = 2

            def update_bullet(self):
                self.rect.x += self.vx
                self.rect.y += self.vy
                screen = pygame.display.get_surface()
                if screen:
                    sw, sh = screen.get_size()
                    if self.rect.top > sh or self.rect.left < 0 or self.rect.right > sw:
                        self.kill()

            bullet.update = update_bullet.__get__(bullet)
            self.bullet_group.add(bullet)
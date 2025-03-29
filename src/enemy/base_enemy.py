# src/enemy/base_enemy.py

import pygame
import math
from src.utils.utils import load_image
from .behavior_tree import *
import logging
from src.utils.utils import ResourceManager
from src.config.game_settings import ALIEN_SETTINGS
from src.utils.sprite_animation import SpriteAnimation

logger = logging.getLogger(__name__)

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, id, x: int, y: int, bullet_group: pygame.sprite.Group, health=1, speed=2, points=100, type="small", sub_type=1):
        super().__init__()
        try:
            logger.info(f"Initializing enemy: id={id}, type={type}, sub_type={sub_type}")
            self.bullet_group = bullet_group
            self.health = health
            self.speed = speed
            self.points = points
            self.type = type
            self.sub_type = sub_type
            self.id = id
            
            # Initialize animation
            sprite_sheet = load_image(
                f"assets/aliens/alien_{id}_{type}_{sub_type}.png",  # Assuming this naming convention
                fallback_color=(255, 0, 0),
                size=(1050, 1050)  # Original size of sprite sheet
            )
            
            # Create animation handler (3x3 grid like player)
            self.animation = SpriteAnimation(
                sprite_sheet=sprite_sheet,
                frame_width=350,
                frame_height=350,
                rows=3,
                cols=3
            )

            # Set initial image and scale it
            self.image = self.animation.get_current_frame()
            
            # Scale image based on alien type
            if type == "small":
                target_size = ALIEN_SETTINGS["small"]["size"]
            elif type == "large":
                target_size = ALIEN_SETTINGS["large"]["size"]
            else:  # boss
                target_size = ALIEN_SETTINGS["boss"]["size"]
                
            self.image = pygame.transform.scale(self.image, target_size)
            self.rect = self.image.get_rect(center=(x, y))
            
            # Other properties
            self.shoot_interval = 2000
            self.last_shot = 0
            self.path = None
            self.path_index = 0
            
            # Setup behavior tree
            self.behavior_tree = Selector([
                Sequence([
                    FollowPath(),
                    FireAtPlayer()
                ]),
                Sequence([
                    MoveTowardsPlayer(),
                    FireAtPlayer()
                ])
            ])
            
            # Context for behavior tree
            self.context = {
                'enemy': self,
                'player': None  # Will be set during update
            }
            
        except Exception as e:
            logger.error(f"Error initializing enemy: {e}")
            # Create fallback surface
            if type == "small":
                size = ALIEN_SETTINGS["small"]["size"]
            elif type == "large":
                size = ALIEN_SETTINGS["large"]["size"]
            else:
                size = ALIEN_SETTINGS["boss"]["size"]
            self.image = pygame.Surface(size)
            self.image.fill((255, 0, 0))
            self.rect = self.image.get_rect(center=(x, y))
            
    def update(self) -> None:
        """Update enemy behavior."""
        try:
            # Update context with current game state
            from src.state.global_state import global_player
            self.context['player'] = global_player
            
            # Execute behavior tree
            self.behavior_tree.execute(self.context)
            
            # Ensure enemy stays in bounds
            self.wrap_position()
            
        except Exception as e:
            logger.error(f"Error updating enemy: {e}")
            
    def take_damage(self, damage: int) -> None:
        """Handle taking damage."""
        try:
            self.health -= damage
        except Exception as e:
            logger.error(f"Error handling damage: {e}")

    def follow_path(self):
        if self.path and len(self.path) > 0:
            # Ensure target_index is valid.
            if self.path_index >= len(self.path):
                # Finished path—clear the path so that normal movement resumes.
                self.path = None
                return
            target = self.path[self.path_index]
            current_x, current_y = self.rect.center
            dx = target[0] - current_x
            dy = target[1] - current_y
            dist = math.hypot(dx, dy)
            if dist < 5:
                # Move to next target.
                self.path_index += 1
            else:
                # Move toward the target point.
                move_x = self.speed * dx / dist
                move_y = self.speed * dy / dist
                self.rect.x += move_x
                self.rect.y += move_y

    def wrap_position(self):
        screen = pygame.display.get_surface()
        if not screen:
            return
        sw, sh = screen.get_size()
        left_bound = int(sw * 0.15)
        right_bound = int(sw * 0.85)
        if self.rect.right < left_bound:
            self.rect.left = right_bound
        elif self.rect.left > right_bound:
            self.rect.right = left_bound
        if self.rect.top > sh:
            self.rect.bottom = 0
        elif self.rect.bottom < 0:
            self.rect.top = sh

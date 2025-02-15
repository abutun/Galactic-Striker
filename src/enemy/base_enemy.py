# src/enemy/base_enemy.py

import pygame
import math
from utils import load_image
from .behavior_tree import *
import logging
from utils import ResourceManager

logger = logging.getLogger(__name__)

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, bullet_group: pygame.sprite.Group, 
                 health: int, speed: float, points: int):
        super().__init__()
        try:
            self.bullet_group = bullet_group
            self.health = health
            self.speed = speed
            self.points = points
            self.path = None
            self.target_index = 0
            
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
            raise
            
    def update(self) -> None:
        """Update enemy behavior."""
        try:
            # Update context with current game state
            from global_state import global_player
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
            if self.target_index >= len(self.path):
                # Finished path—clear the path so that normal movement resumes.
                self.path = None
                return
            target = self.path[self.target_index]
            current_x, current_y = self.rect.center
            dx = target[0] - current_x
            dy = target[1] - current_y
            dist = math.hypot(dx, dy)
            if dist < 5:
                # Move to next target.
                self.target_index += 1
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

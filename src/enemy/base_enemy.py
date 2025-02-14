# src/enemy/base_enemy.py

import pygame
import math
from utils import load_image

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group, health, speed, points):
        super().__init__()
        self.bullet_group = bullet_group
        self.health = health
        self.speed = speed
        self.points = points
        # Optionally, an enemy may be given a movement path:
        self.path = None
        self.target_index = 0

    def take_damage(self, damage):
        self.health -= damage

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

    def update(self):
        # In the base class we let the enemy follow a path if assigned.
        if self.path:
            self.follow_path()

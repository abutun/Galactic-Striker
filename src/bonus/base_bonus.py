from abc import ABC, abstractmethod
import math
import pygame
from src.utils.utils import load_image

class Bonus(pygame.sprite.Sprite, ABC):
    def __init__(self, x, y, image_path=None, fallback_color=(255, 255, 255), size=(24, 24)):
        pygame.sprite.Sprite.__init__(self)  # Initialize Sprite first
        self.speed = 1.25
        
        # Load image
        if image_path:
            try:
                self.image = load_image(image_path, (0, 0, 0), size)
            except:
                self.image = pygame.Surface(size)
                self.image.fill(fallback_color)
        else:
            self.image = pygame.Surface(size)
            self.image.fill(fallback_color)

        self.original_image = self.image  # Keep a copy of the original image            
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False
        self.duration = None  # For temporary bonuses
        self.start_time = None

        # Rotation attributes for Y-axis effect
        self.rotation_angle = 0  # Angle in degrees
        self.rotation_speed = 0.5  # Speed of rotation (degrees per frame)
        self.rotation_direction = 1  # 1 for forward, -1 for backward

    @abstractmethod
    def apply(self, player, game_context=None):
        """Apply bonus effect to player"""
        self.sound_manager.play("bonus_reward")

    def update(self):
        """Move bonus down the screen, rotate around Y-axis, and check duration"""
        # Move down
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

        # Update rotation angle
        self.rotation_angle += self.rotation_speed * self.rotation_direction
        if self.rotation_angle >= 180 or self.rotation_angle <= 0:
            self.rotation_direction *= -1  # Reverse direction at 0° and 180°

        # Simulate Y-axis rotation by scaling the width
        # Use cosine to scale the width (cos(0) = 1, cos(90) = 0, cos(180) = -1)
        scale_factor = abs(math.cos(math.radians(self.rotation_angle)))
        original_width, original_height = self.original_image.get_size()
        new_width = int(original_width * scale_factor)

        # Prevent zero width (can cause issues with scaling)
        if new_width < 1:
            new_width = 1

        # Scale the image to simulate Y-axis rotation
        self.image = pygame.transform.scale(self.original_image, (new_width, original_height))

        # Update the rect to keep the sprite centered
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

        # Check duration
        if self.duration and self.start_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time > self.duration:
                self.remove_effect()

    def remove_effect(self):
        """Override this method for bonuses that need cleanup"""
        pass
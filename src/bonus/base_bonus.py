from abc import ABC, abstractmethod
import pygame
from src.utils import load_image

class Bonus(pygame.sprite.Sprite, ABC):
    def __init__(self, x, y, image_path=None, fallback_color=(255, 255, 255), size=(24, 24)):
        pygame.sprite.Sprite.__init__(self)  # Initialize Sprite first
        self.speed = 2
        
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
            
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False
        self.duration = None  # For temporary bonuses
        self.start_time = None

    @abstractmethod
    def apply(self, player, game_context=None):
        """Apply bonus effect to player"""
        pass

    def update(self):
        """Move bonus down the screen and check duration"""
        # Move down
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()
            
        # Check duration
        if self.duration and self.start_time:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time > self.duration:
                self.remove_effect()

    def remove_effect(self):
        """Override this method for bonuses that need cleanup"""
        pass

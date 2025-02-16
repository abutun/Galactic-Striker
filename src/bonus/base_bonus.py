import pygame
from src.utils import load_image

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path=None, fallback_color=(255, 255, 255), size=(20, 20), speed=2):
        super().__init__()
        self.speed = speed
        
        # Load image if path provided, otherwise use fallback
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
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

    def apply(self, player, game_context=None):
        raise NotImplementedError("Subclasses must implement apply()")

import pygame
from utils import load_image

class BaseBonus(pygame.sprite.Sprite):
    def __init__(self, x, y, image_path, fallback_color, size):
        super().__init__()
        self.image = load_image(image_path, fallback_color, size)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        screen = pygame.display.get_surface()
        if screen:
            _, sh = screen.get_size()
            if self.rect.top > sh:
                self.kill()

    def apply(self, player, game_context=None):
        raise NotImplementedError("Subclasses must implement apply()")

import pygame
from src.utils import load_image

pygame.init()
pygame.display.set_mode((640, 480))  # Set a temporary display mode for testing

image = load_image("assets/sprites/enemy_grunt.png", (255, 0, 0), (32, 32))
if image is None:
    print("Image is None!")
else:
    print("Image loaded successfully!")
pygame.quit()

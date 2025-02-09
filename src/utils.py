# src/utils.py
import pygame

def load_image(path, fallback_color, size):
    try:
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading image {path}: {e}. Using placeholder.")
        image = pygame.Surface(size)
        image.fill(fallback_color)
    return image

def load_sound(path):
    try:
        sound = pygame.mixer.Sound(path)
    except Exception as e:
        print(f"Error loading sound {path}: {e}.")
        sound = None
    return sound

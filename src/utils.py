import os
import pygame

def resource_path(relative_path):
    """
    Returns the absolute path to a resource file.
    Assumes the base directory is one level above the src folder.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    normalized_path = os.path.normpath(relative_path)
    return os.path.join(base_dir, normalized_path)

def load_image(path, fallback_color, size):
    full_path = resource_path(path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}. Using placeholder.")
        image = pygame.Surface(size, pygame.SRCALPHA)
        image.fill(fallback_color)
        return image
    try:
        image = pygame.image.load(full_path)
        if pygame.display.get_surface():
            image = image.convert_alpha()
        else:
            image = image.convert()
        image = pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading image {full_path}: {e}. Using placeholder.")
        image = pygame.Surface(size, pygame.SRCALPHA)
        image.fill(fallback_color)
    return image

def load_sound(path):
    full_path = resource_path(path)
    if not os.path.exists(full_path):
        print(f"Sound file not found: {full_path}.")
        return None
    try:
        sound = pygame.mixer.Sound(full_path)
    except Exception as e:
        print(f"Error loading sound {full_path}: {e}.")
        sound = None
    return sound

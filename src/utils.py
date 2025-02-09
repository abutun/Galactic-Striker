import os
import pygame


def resource_path(*path_parts):
    """
    Returns the absolute path to a resource file.
    The base directory is assumed to be one level above the src folder.

    Example:
        resource_path("assets", "sprites", "player.png")
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, *path_parts)


def load_image(path, fallback_color, size):
    """
    Loads an image from a given relative path (using os.path.join for cross-platform compatibility).
    If the file is not found or cannot be loaded, returns a placeholder Surface filled with fallback_color.

    :param path: A relative file path string (e.g., "assets/sprites/enemy_swarmer.png")
    :param fallback_color: A tuple (R, G, B) used to fill the Surface if the image fails to load.
    :param size: A tuple (width, height) to which the image will be scaled.
    :return: A pygame.Surface object.
    """
    # Normalize the path and split it into parts so that resource_path can join them.
    normalized_path = os.path.normpath(path)
    path_parts = normalized_path.split(os.sep)
    full_path = resource_path(*path_parts)

    if not os.path.exists(full_path):
        print(f"File not found: {full_path}. Using placeholder.")
        image = pygame.Surface(size, pygame.SRCALPHA)
        image.fill(fallback_color)
        return image
    try:
        image = pygame.image.load(full_path)
        # Ensure a display is set; if so, use convert_alpha(), otherwise use convert().
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
    """
    Loads a sound file from a given relative path using os.path.join.
    If the file is not found or cannot be loaded, returns None.

    :param path: A relative file path string (e.g., "assets/audio/laser.wav")
    :return: A pygame.mixer.Sound object or None.
    """
    normalized_path = os.path.normpath(path)
    path_parts = normalized_path.split(os.sep)
    full_path = resource_path(*path_parts)

    if not os.path.exists(full_path):
        print(f"Sound file not found: {full_path}.")
        return None
    try:
        sound = pygame.mixer.Sound(full_path)
    except Exception as e:
        print(f"Error loading sound {full_path}: {e}.")
        sound = None
    return sound

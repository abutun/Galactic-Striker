import os
import pygame


def resource_path(relative_path):
    """
    Returns the absolute path to a resource file.
    The base directory is assumed to be one level above the src folder.

    :param relative_path: A relative file path string (e.g., "assets/sprites/player.png")
    :return: Absolute path to the resource.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    # Normalize the relative path (this converts forward slashes to backslashes on Windows)
    normalized_path = os.path.normpath(relative_path)
    return os.path.join(base_dir, normalized_path)


def load_image(path, fallback_color, size):
    """
    Loads an image from the given relative path. If loading fails or the file does not exist,
    a placeholder Surface filled with the fallback_color is returned.

    :param path: A relative file path string (e.g., "assets/sprites/enemy_swarmer.png")
    :param fallback_color: A tuple (R, G, B) to fill the placeholder surface if needed.
    :param size: A tuple (width, height) to which the image will be scaled.
    :return: A pygame.Surface object.
    """
    full_path = resource_path(path)
    if not os.path.exists(full_path):
        print(f"File not found: {full_path}. Using placeholder.")
        image = pygame.Surface(size, pygame.SRCALPHA)
        image.fill(fallback_color)
        return image
    try:
        image = pygame.image.load(full_path)
        # If a display is set, use convert_alpha(); otherwise use convert().
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
    Loads a sound from the given relative path. If the sound file is not found or cannot be loaded,
    returns None.

    :param path: A relative file path string (e.g., "assets/audio/laser.wav")
    :return: A pygame.mixer.Sound object or None.
    """
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

import os
import pygame
import logging
from typing import Dict, Tuple, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResourceManager:
    _image_cache: Dict[str, pygame.Surface] = {}
    _sound_cache: Dict[str, Optional[pygame.mixer.Sound]] = {}
    
    @classmethod
    def load_image(cls, path: str, fallback_color: Tuple[int, int, int], size: Tuple[int, int]) -> pygame.Surface:
        """Load an image with caching."""
        cache_key = f"{path}_{size[0]}_{size[1]}"
        
        if cache_key in cls._image_cache:
            return cls._image_cache[cache_key].copy()
        
        try:
            full_path = resource_path(path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {full_path}")
                
            image = pygame.image.load(full_path)
            if pygame.display.get_surface():
                image = image.convert_alpha()
            else:
                image = image.convert()
            image = pygame.transform.scale(image, size)
            cls._image_cache[cache_key] = image
            return image.copy()
            
        except Exception as e:
            logger.error(f"Error loading image {path}: {e}")
            # Create fallback surface
            image = pygame.Surface(size, pygame.SRCALPHA)
            image.fill(fallback_color)
            cls._image_cache[cache_key] = image
            return image.copy()

    @classmethod
    def clear_cache(cls):
        """Clear all resource caches."""
        cls._image_cache.clear()
        cls._sound_cache.clear()

    @classmethod
    def load_sound(cls, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound with caching."""
        if path in cls._sound_cache:
            return cls._sound_cache[path]
            
        try:
            full_path = resource_path(path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"File not found: {full_path}")
                
            sound = pygame.mixer.Sound(full_path)
            cls._sound_cache[path] = sound
            return sound
        except Exception as e:
            logger.error(f"Error loading sound {path}: {e}")
            cls._sound_cache[path] = None
            return None

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_image(path: str, fallback_color: tuple, size: tuple) -> pygame.Surface:
    """Load an image with fallback options."""
    try:
        if os.path.exists(path):
            image = pygame.image.load(path).convert_alpha()
        else:
            logger.warning(f"File not found: {path}. Using placeholder.")
            image = pygame.Surface(size, pygame.SRCALPHA)
            image.fill(fallback_color)
            
        if size:
            image = pygame.transform.scale(image, size)
        return image
    except Exception as e:
        logger.error(f"Error loading image {path}: {e}")
        # Create a fallback surface
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill(fallback_color)
        return surface

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

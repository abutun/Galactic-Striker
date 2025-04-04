import pygame
import logging
from typing import Dict, Optional
from src.utils.sprite_animation import SpriteAnimation
from src.utils.utils import load_image

logger = logging.getLogger(__name__)

class ResourcePreloader:
    def __init__(self):
        self.cached_animations: Dict[str, SpriteAnimation] = {}
        self.cached_boss_animations: Dict[str, SpriteAnimation] = {}

    def preload_level_resources(self, level_data) -> None:
        """Preload all resources needed for a level"""
        try:
            if not level_data or not level_data.alien_groups:
                return

            for group in level_data.alien_groups:
                parts = group['alien_type'].split('_')
                type_name = parts[0]
                id_value = parts[1]

                if type_name == "alien":
                    alien_type = parts[2]
                    alien_subtype = parts[3]
                    self._preload_alien_sprite(id_value, alien_type, alien_subtype)
                elif type_name == "boss":
                    self._preload_boss_sprite(id_value)

        except Exception as e:
            logger.error(f"Error preloading level resources: {e}")

    def _preload_alien_sprite(self, id: str, alien_type: str, subtype: str) -> None:
        """Preload alien sprite animation"""
        try:
            key = f"{id}_{alien_type}_{subtype}"
            if key not in self.cached_animations:
                sprite_sheet = load_image(
                    f"assets/aliens/alien_{id}_{alien_type}_{subtype}.png",
                    fallback_color=(255, 0, 0),
                    size=(1050, 1050)
                )
                
                animation = SpriteAnimation(
                    sprite_sheet=sprite_sheet,
                    frame_width=350,
                    frame_height=350,
                    rows=3,
                    cols=3
                )
                self.cached_animations[key] = animation
                logger.info(f"Preloaded alien sprite: {key}")

        except Exception as e:
            logger.error(f"Error preloading alien sprite: {e}")

    def _preload_boss_sprite(self, id: str) -> None:
        """Preload boss sprite animation"""
        try:
            key = f"boss_{id}"
            if key not in self.cached_boss_animations:
                sprite_sheet = load_image(
                    f"assets/aliens/boss_{id}.png",
                    fallback_color=(255, 255, 0),
                    size=(1050, 1050)
                )
                
                animation = SpriteAnimation(
                    sprite_sheet=sprite_sheet,
                    frame_width=350,
                    frame_height=350,
                    rows=3,
                    cols=3
                )
                self.cached_boss_animations[key] = animation
                logger.info(f"Preloaded boss sprite: {key}")

        except Exception as e:
            logger.error(f"Error preloading boss sprite: {e}")

    def get_alien_animation(self, id: str, alien_type: str, subtype: str) -> Optional[SpriteAnimation]:
        """Get cached alien animation"""
        key = f"{id}_{alien_type}_{subtype}"
        return self.cached_animations.get(key)

    def get_boss_animation(self, id: str) -> Optional[SpriteAnimation]:
        """Get cached boss animation"""
        key = f"boss_{id}"
        return self.cached_boss_animations.get(key)

    def clear_cache(self) -> None:
        """Clear all cached animations"""
        self.cached_animations.clear()
        self.cached_boss_animations.clear() 
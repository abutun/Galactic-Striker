import pygame
import logging
import json
from src.utils.utils import load_image
from src.config.game_settings import ALIEN_SETTINGS
from src.utils.sprite_animation import SpriteAnimation

logger = logging.getLogger(__name__)

class ResourcePreloader:
    def __init__(self):
        self.cached_animations = {}
        self.cached_boss_animations = {}
        self.current_level = 0
        self.preload_buffer = 2  # Preload current and next level
        
    def preload_initial_level(self):
        """Preload first level before game starts"""
        try:
            logger.info("Preloading initial level resources")
            # Preload level 1
            self._preload_level_resources(1)
            # Preload level 2 in advance
            self._preload_level_resources(2)
        except Exception as e:
            logger.error(f"Error preloading initial level: {e}")

    def preload_next_level(self, current_level: int):
        """Preload resources for the next level while current level is running"""
        try:
            next_level = current_level + 1
            logger.info(f"Preloading resources for level {next_level}")
            self._preload_level_resources(next_level)
            
            # Clean up resources from older levels
            self._cleanup_old_resources(current_level - 1)
        except Exception as e:
            logger.error(f"Error preloading next level: {e}")

    def _preload_level_resources(self, level_number: int):
        """Load and cache all resources for a specific level"""
        try:
            # Load level data
            with open(f"assets/levels/{level_number:03d}.json", "r") as f:
                level_data = json.load(f)
            
            # Get unique alien types from level data
            alien_types = set()
            for group in level_data.get('alien_groups', []):
                alien_type = group.get('alien_type', '')
                if alien_type:
                    parts = alien_type.split('_')
                    if len(parts) >= 2:
                        alien_types.add((parts[0], parts[1]))  # (type, id)
            
            # Preload each alien type
            for alien_type, alien_id in alien_types:
                if alien_type == "alien":
                    # Load both subtypes for regular aliens
                    for subtype in [1, 2]:
                        key = f"{alien_id}_{alien_type}_{subtype}"
                        if key not in self.cached_animations:
                            try:
                                sprite_sheet = load_image(
                                    f"assets/aliens/alien_{alien_id}_{alien_type}_{subtype}.png",
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
                                logger.info(f"Preloaded alien sprite: {key} for level {level_number}")
                            except Exception as e:
                                logger.error(f"Error preloading alien sprite {key}: {e}")
                
                elif alien_type == "boss":
                    # Load boss sprite
                    key = f"boss_{alien_id}"
                    if key not in self.cached_boss_animations:
                        try:
                            sprite_sheet = load_image(
                                f"assets/aliens/boss_{alien_id}.png",
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
                            logger.info(f"Preloaded boss sprite: {key} for level {level_number}")
                        except Exception as e:
                            logger.error(f"Error preloading boss sprite {key}: {e}")
                            
        except FileNotFoundError:
            logger.warning(f"Level {level_number} data not found")
        except Exception as e:
            logger.error(f"Error preloading level {level_number} resources: {e}")

    def _cleanup_old_resources(self, level_number: int):
        """Remove cached resources from levels we've passed"""
        try:
            if level_number < 1:
                return
                
            # Load old level data to know what to clean up
            with open(f"assets/levels/{level_number:03d}.json", "r") as f:
                level_data = json.load(f)
            
            # Get alien types from old level
            for group in level_data.get('alien_groups', []):
                alien_type = group.get('alien_type', '')
                if alien_type:
                    parts = alien_type.split('_')
                    if len(parts) >= 2:
                        if parts[0] == "alien":
                            for subtype in [1, 2]:
                                key = f"{parts[1]}_{parts[0]}_{subtype}"
                                if key in self.cached_animations:
                                    del self.cached_animations[key]
                                    logger.info(f"Cleaned up alien sprite: {key}")
                        elif parts[0] == "boss":
                            key = f"boss_{parts[1]}"
                            if key in self.cached_boss_animations:
                                del self.cached_boss_animations[key]
                                logger.info(f"Cleaned up boss sprite: {key}")
                                
        except Exception as e:
            logger.error(f"Error cleaning up resources for level {level_number}: {e}")

    def get_alien_animation(self, alien_id, alien_type, subtype):
        """Get cached animation for alien type"""
        key = f"{alien_id}_{alien_type}_{subtype}"
        return self.cached_animations.get(key)
    
    def get_boss_animation(self, boss_type):
        """Get cached animation for boss type"""
        key = f"boss_{boss_type}"
        return self.cached_boss_animations.get(key) 
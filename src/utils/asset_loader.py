import os
import pygame
from typing import Dict, Optional
from functools import lru_cache

class AssetLoader:
    _instance = None
    _images: Dict[str, pygame.Surface] = {}
    _sounds: Dict[str, pygame.mixer.Sound] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @lru_cache(maxsize=100)
    def load_image(self, path: str, colorkey: Optional[tuple] = None, size: Optional[tuple] = None) -> pygame.Surface:
        if path in self._images:
            image = self._images[path]
        else:
            try:
                image = pygame.image.load(path).convert_alpha()
                if colorkey:
                    image.set_colorkey(colorkey)
                if size:
                    image = pygame.transform.scale(image, size)
                self._images[path] = image
            except pygame.error as e:
                print(f"Couldn't load image: {path}")
                raise e
        return image

    @lru_cache(maxsize=50)
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        if path in self._sounds:
            return self._sounds[path]
        try:
            sound = pygame.mixer.Sound(path)
            self._sounds[path] = sound
            return sound
        except pygame.error:
            print(f"Couldn't load sound: {path}")
            return None

    def preload_assets(self, asset_paths: Dict[str, str]):
        for asset_type, path in asset_paths.items():
            if asset_type.startswith('image'):
                self.load_image(path)
            elif asset_type.startswith('sound'):
                self.load_sound(path) 
import pygame
import os
import logging
from src.utils import load_sound

logger = logging.getLogger(__name__)

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self._load_sounds()
        self.enabled = True
        
    def _load_sounds(self):
        """Load all game sound effects."""
        try:
            # Player sounds
            self.sounds['player_fire'] = load_sound('assets/sounds/player_fire.wav')
            self.sounds['player_hit'] = load_sound('assets/sounds/player_hit.wav')
            self.sounds['player_death'] = load_sound('assets/sounds/player_death.wav')
            
            # Alien sounds
            self.sounds['alien_fire_1'] = load_sound('assets/sounds/alien_fire_1.wav')
            self.sounds['alien_fire_2'] = load_sound('assets/sounds/alien_fire_2.wav')
            self.sounds['alien_hit_1'] = load_sound('assets/sounds/alien_hit_1.wav')
            self.sounds['alien_hit_2'] = load_sound('assets/sounds/alien_hit_2.wav')
            self.sounds['alien_death_1'] = load_sound('assets/sounds/alien_death_1.wav')
            self.sounds['alien_death_2'] = load_sound('assets/sounds/alien_death_2.wav')
            
            # Adjust volumes
            for sound in self.sounds.values():
                sound.set_volume(0.7)
                
        except Exception as e:
            logger.error(f"Error loading sounds: {e}")
            self.enabled = False

    def play(self, sound_name):
        """Play a sound by name."""
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                logger.error(f"Error playing sound {sound_name}: {e}")

    def toggle(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled 
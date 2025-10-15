import pygame
import logging
from src.utils.utils import load_sound

logger = logging.getLogger(__name__)

class SoundManager:
    def __init__(self, enabled: bool = True, sfx_volume: float = 0.7):
        self.sounds = {}
        self.master_volume = max(0.0, min(1.0, sfx_volume))
        self.enabled = enabled and pygame.mixer.get_init() is not None

        if self.enabled:
            self._load_sounds()
        else:
            logger.warning("Sound system unavailable. Continuing without audio.")
        
    def _load_sounds(self):
        """Load all game sound effects."""
        try:
            # Player sounds
            self.sounds['player_fire'] = load_sound('assets/sounds/player_fire.wav')
            self.sounds['player_hit'] = load_sound('assets/sounds/player_hit.wav')
            self.sounds['player_death'] = load_sound('assets/sounds/player_death.wav')
            
            # Alien sounds
            self.sounds['alien_fire_01'] = load_sound('assets/sounds/alien_fire_01.wav')
            self.sounds['alien_fire_02'] = load_sound('assets/sounds/alien_fire_02.wav')
            self.sounds['alien_hit_01'] = load_sound('assets/sounds/alien_hit_01.wav')
            self.sounds['alien_hit_02'] = load_sound('assets/sounds/alien_hit_02.wav')
            self.sounds['alien_death_01'] = load_sound('assets/sounds/alien_death_01.wav')
            self.sounds['alien_death_02'] = load_sound('assets/sounds/alien_death_02.wav')

            # Bonus sounds
            self.sounds['bonus_reward'] = load_sound('assets/sounds/bonus_reward.wav')
            self.sounds['collision'] = load_sound('assets/sounds/collision.wav')
            
            # Adjust volumes
            for sound in self.sounds.values():
                if sound:
                    sound.set_volume(self.master_volume)
                
        except Exception as e:
            logger.error(f"Error loading sounds: {e}")
            self.enabled = False

    def play(self, sound_name):
        """Play a sound by name."""
        if self.enabled and sound_name in self.sounds and self.sounds[sound_name]:
            try:
                self.sounds[sound_name].play()
            except Exception as e:
                logger.error(f"Error playing sound {sound_name}: {e}")

    def toggle(self):
        """Toggle sound on/off."""
        self.enabled = not self.enabled
        if self.enabled:
            self.resume_all()
        else:
            self.pause_all()

    def pause_all(self):
        """Pause all currently playing sounds."""
        if pygame.mixer.get_init():
            pygame.mixer.pause()

    def resume_all(self):
        """Resume playback after a pause."""
        if pygame.mixer.get_init():
            pygame.mixer.unpause()

    def set_master_volume(self, value: float) -> None:
        """Update global SFX volume."""
        self.master_volume = max(0.0, min(1.0, value))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.master_volume)

import pygame
import logging
from src.utils.utils import ResourceManager, load_image
from src.weapon.weapon_factory import WeaponFactory
from src.weapons import Missile, Bullet

logger = logging.getLogger(__name__)

# List of rank names.
RANK_NAMES = [
    "Ensign", "Lieutenant", "Commander", "Captain", "Admiral",
    "Admiral 1 Bronze Star", "Admiral 2 Bronze Star", "Admiral 3 Bronze Star",
    "Admiral 1 Silver Star", "Admiral 2 Silver Star", "Admiral 3 Silver Star",
    "Admiral 1 Gold Star", "Admiral 2 Gold Star", "Admiral 3 Gold Star",
    "Galactic Knight", "Galactic Lord", "Galactic Overlord", "Galactic Grandmaster",
    "Galactic Grandmaster 1 Gold Star", "Galactic Grandmaster 2 Gold Star", "Galactic Grandmaster 3 Gold Star",
    "Galactic Champion", "Galactic God",
    "Galactic Pluto Rank", "Galactic Neptune Rank", "Galactic Uranus Rank", "Galactic Saturn Rank",
    "Galactic Jupiter Rank", "Galactic Mars Rank", "Galactic Tellus Rank", "Galactic Venus Rank",
    "Galactic Mercury Rank", "Galactic Sol Rank"
]


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, bullet_group: pygame.sprite.Group):
        super().__init__()
        try:
            # Load the base player image first with 50% larger size (48x48 instead of 32x32)
            self.base_image = load_image("assets/sprites/player.png", (0, 255, 0), (48, 48))
            self.image = self.base_image.copy()  # Create initial copy
            self.rect = self.image.get_rect(center=(x, y))
            
            # Initialize player attributes
            self.bullet_group = bullet_group
            self.speed = 5
            self.health = 100
            self.shield = 0
            self.lives = 3
            self.money = 0
            self.weapon_level = 1
            self.bullet_speed = 7
            self.bullet_count = 1
            self.time_stat = 0
            self.primary_weapon = 4
            self.fire_delay = 250
            self.last_fire = 0
            
            # Secondary weapon: rockets
            self.rockets = 10  # initial pack of 10 rockets
            self.max_rockets = 50
            
            # Status flags
            self.scoop_active = False
            self.autofire = False
            self.shield_active = False
            self.mirror_mode = False
            self.drunk_mode = False
            
            # Rank system
            self.rank = 1
            self.rank_markers = []
            self.letters = []
            
            # Now update the rank marker
            self.update_rank_marker()
            
        except Exception as e:
            logger.error(f"Error initializing player: {e}")
            raise

    def update_rank_marker(self):
        try:
            self.image = self.base_image.copy()
            if self.rank_markers:
                text = pygame.font.Font(None, 20).render(str(len(self.rank_markers)), True, (255, 255, 255))
                self.image.blit(text, (0, self.image.get_height() - text.get_height()))
        except Exception as e:
            logger.error(f"Error updating rank marker: {e}")

    def check_rank_upgrade(self):
        if len(self.rank_markers) >= 6:
            if self.rank < len(RANK_NAMES):
                self.rank += 1
            self.rank_markers = []
            self.update_rank_marker()

    def update(self) -> None:
        """Update player state with proper error handling."""
        try:
            keys = pygame.key.get_pressed()
            
            # Keep player within play area bounds
            play_area_left = int(pygame.display.get_surface().get_width() * 0.12)
            play_area_right = int(pygame.display.get_surface().get_width() * 0.88)
            
            dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
            self.rect.x += dx
            
            # Clamp to play area
            self.rect.clamp_ip(pygame.Rect(
                play_area_left, 0,
                play_area_right - play_area_left,
                pygame.display.get_surface().get_height()
            ))
            
            # Handle firing
            now = pygame.time.get_ticks()
            if (keys[pygame.K_SPACE] or self.autofire) and now - self.last_fire >= self.fire_delay:
                self.fire_bullet()
                self.last_fire = now
                
            # Secondary fire with left shift
            if keys[pygame.K_LSHIFT]:
                self.fire_secondary()
                
            self.check_rank_upgrade()
        except Exception as e:
            logger.error(f"Error updating player: {e}")

    def fire_bullet(self) -> None:
        """Fire the current weapon."""
        try:
            weapon = WeaponFactory.create_weapon(self.primary_weapon, self.bullet_group)
            bullet = weapon.fire(self.rect.centerx, self.rect.top)
            if bullet:  # If bullet was created successfully
                self.bullet_group.add(bullet)
                self.all_sprites.add(bullet)  # Add to all_sprites too
            
            # Play sound if available
            if hasattr(self, 'laser_sound') and self.laser_sound:
                self.laser_sound.play()
        except Exception as e:
            logger.error(f"Error firing weapon: {e}")

    def fire_secondary(self):
        """Fire secondary weapon (missiles)."""
        if self.rockets > 0:
            missile = Missile(self.rect.centerx, self.rect.top)
            self.bullet_group.add(missile)
            self.rockets -= 1

    def take_damage(self, damage: int) -> None:
        """Handle taking damage with proper error checking."""
        try:
            if self.shield_active:
                self.shield_active = False
                self.sound_manager.play('player_hit')
                return
            
            self.health -= damage
            self.sound_manager.play('player_hit')
            
            if self.health <= 0:
                self.sound_manager.play('player_death')
                self.kill()
        except Exception as e:
            logger.error(f"Error handling damage: {e}")

    def fire(self):
        if pygame.time.get_ticks() - self.last_fire > self.fire_delay:
            self.weapon.fire(self.rect.centerx, self.rect.top)
            self.sound_manager.play('player_fire')
            self.last_fire = pygame.time.get_ticks()

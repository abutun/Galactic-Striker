import pygame
import logging
from src.utils.utils import ResourceManager, load_image
from src.weapon.weapon_factory import WeaponFactory
from src.weapon.weapons import Missile, Bullet
from src.utils.sprite_animation import SpriteAnimation
from src.config.game_settings import PLAYER_SETTINGS, PLAY_AREA

logger = logging.getLogger(__name__)

# List of rank names.
RANK_NAMES = [
    "Ensign", "Lieutenant", "Commander", "Captain", "Admiral",
    "Admiral 1 Bronze Star", "Admiral 2 Bronze Star", "Admiral 3 Bronze Star",
    "Admiral 1 Silver Star", "Admiral 2 Silver Star", "Admiral 3 Silver Star",
    "Admiral 1 Gold Star", "Admiral 2 Gold Star", "Admiral 3 Gold Star",
    "Galactic Knight", "Galactic Lord", "Galactic Overlord", "Galactic Grandmaster",
    "Galactic Grandmaster 1 Gold Star", "Galactic Grandmaster 2 Gold Star", 
    "Galactic Grandmaster 3 Gold Star", "Galactic Champion", "Galactic God", 
    "Galactic Pluto Rank", "Galactic Neptune Rank", "Galactic Uranus Rank", 
    "Galactic Saturn Rank", "Galactic Jupiter Rank", "Galactic Mars Rank", 
    "Galactic Tellus Rank", "Galactic Venus Rank", "Galactic Mercury Rank", 
    "Galactic Sol Rank"
]


class Player(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, bullet_group: pygame.sprite.Group):
        super().__init__()
        try:
            # Load sprite sheet
            sprite_sheet = load_image("assets/sprites/player_1.png", (0, 255, 0), (828, 990))
            
            frame_width = 276
            frame_height = 330
            
            # Create animation handler
            self.animation = SpriteAnimation(
                sprite_sheet=sprite_sheet,
                frame_width=frame_width,
                frame_height=frame_height,
                rows=3,
                cols=3
            )
            
            # Set initial image and rect
            self.image = self.animation.get_current_frame()
            
            # Scale the image to desired size (use PLAYER_SETTINGS)
            target_size = PLAYER_SETTINGS.get("size", (64, 64))

            self.image = pygame.transform.scale(self.image, target_size)
            
            self.rect = self.image.get_rect()
            
            # Set initial position
            screen = pygame.display.get_surface()
            if screen:
                # Position player at 98% of screen height
                self.rect.bottom = int(screen.get_height() * 0.99)
                # Center horizontally within play area
                play_area_left = int(screen.get_width() * 0.12)
                play_area_right = int(screen.get_width() * 0.88)
                play_area_width = play_area_right - play_area_left
                self.rect.centerx = play_area_left + (play_area_width // 2)
            else:
                self.rect.x = x
                self.rect.y = y
            
            # Initialize player attributes
            self.bullet_group = bullet_group
            self.speed = 5
            self.health = 3
            self.max_health = 6  # Cap maximum health at 5
            self.shield = 0
            self.lives = 3
            self.money = 0
            self.weapon_level = 1
            self.bullet_speed = 7
            self.bullet_count = 1
            self.time_stat = 0
            self.primary_weapon = 1
            self.fire_delay = 250
            self.last_fire = 0
            
            # Secondary weapon: rockets
            self.rockets = 3  # initial pack of 3 rockets
            self.max_rockets = 15
            
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
            self.image = self.animation.get_current_frame()
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
            # Update animation
            self.animation.update()
            
            # Update player image with current animation frame
            current_frame = self.animation.get_current_frame()
            target_size = PLAYER_SETTINGS.get("size", (64, 64))
            self.image = pygame.transform.scale(current_frame, target_size)
            
            # Handle movement with boundaries
            screen = pygame.display.get_surface()
            if not screen:
                return
            
            # Calculate movement boundaries from settings
            left_boundary = int(screen.get_width() * PLAY_AREA["left_boundary"])
            right_boundary = int(screen.get_width() * PLAY_AREA["right_boundary"])
            
            # Handle movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and self.rect.left > left_boundary:
                self.rect.x -= self.speed
            if keys[pygame.K_RIGHT] and self.rect.right < right_boundary:
                self.rect.x += self.speed
            
            # Handle firing
            now = pygame.time.get_ticks()
            if keys[pygame.K_SPACE] and now - self.last_fire >= self.fire_delay:
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
            self.sound_manager.play('player_fire')
        except Exception as e:
            logger.error(f"Error firing weapon: {e}")

    def fire_secondary(self):
        """Fire secondary weapon (missiles)."""
        if self.rockets > 0:
            missile = Missile(self.rect.centerx, self.rect.top)
            self.bullet_group.add(missile)
            self.rockets -= 1

    def take_damage(self, damage: int) -> None:
        """Handle player taking damage."""
        if self.shield > 0:
            self.shield -= damage
            if self.shield < 0:
                self.shield = 0
            if self.sound_manager:
                self.sound_manager.play('shield_hit')
        else:
            # Always decrease health by 1 regardless of damage amount
            self.health -= 1
            if self.sound_manager:
                self.sound_manager.play('player_hit')
                
            if self.health <= 0:
                self.health = 0
                self.sound_manager.play('player_death')
                # Signal game over
                self.kill()

    def add_health(self):
        """Add one health point up to max_health."""
        if self.health < self.max_health:
            self.health += 1
            if self.sound_manager:
                self.sound_manager.play('health_pickup')
            return True
        return False

    def fire(self):
        if pygame.time.get_ticks() - self.last_fire > self.fire_delay:
            self.weapon.fire(self.rect.centerx, self.rect.top)
            self.sound_manager.play('player_fire')
            self.last_fire = pygame.time.get_ticks()

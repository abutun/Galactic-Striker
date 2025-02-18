import os
import sys
import logging
import random
import pygame

# Configure logging
logger = logging.getLogger(__name__)

# Core game components
from src.player.player import Player, RANK_NAMES
from src.enemy.alien import NonBossAlien
from src.misc.background import Background
from src.manager.score_manager import ScoreManager
from src.manager.sound_manager import SoundManager
from src.manager.level_manager import LevelManager
from src.level.level_editor import LevelEditor
from src.utils.asset_loader import AssetLoader

# Game settings and state
from src.config.game_settings import (
    ALIEN_SETTINGS,
    FORMATIONS,
    MOVEMENT_PATTERNS,
    SPECIAL_EFFECTS
)
import src.state.global_state as global_state

# Bonus system imports
from src.bonus import (
    # Money bonuses
    MoneyBonus10, MoneyBonus50, MoneyBonus100, MoneyBonus200,
    
    # Weapon bonuses
    SingleShotBonus, DoubleShotBonus, TripleShotBonus, QuadShotBonus,
    
    # Special bonuses
    RankMarker, LetterBonus, ShipAutofireBonus, AlienScoopBonus,
    MoneyBombBonus, GemBombBonus,
    
    # Power-up bonuses
    ExtraSpeedBonus, ExtraBulletBonus, ExtraTimeBonus,
    ExtraBulletSpeedBonus, ExtraLifeBonus,
    
    # Special effects bonuses
    BonusMeteorstormBonus, BonusMemorystationBonus,
    
    # Modifier bonuses
    DecreaseStrengthRedBonus, DecreaseStrengthGreenBonus,
    DecreaseStrengthBlueBonus, X2ScoreMultiplierBonus,
    X5ScoreMultiplierBonus, CashDoublerBonus,
    
    # Game mode bonuses
    MirrorModeBonus, DrunkModeBonus, FreezeModeBonus,
    WarpForwardBonus
)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)


# Developer mode overlay function.
def draw_dev_info(screen, player, level_manager, score_manager):
    info_lines = [
        "Developer Mode: ON",
        f"Level: {level_manager.level_data.level_number}",
        f"Rank: {RANK_NAMES[player.rank - 1]} (#{player.rank})",
        f"Collected Rank Markers: {len(player.rank_markers)}",
        f"Scoop Active: {player.scoop_active}",
        f"Weapon Level: {player.weapon_level}",
        f"Primary Weapon: {player.primary_weapon}",
        f"Health: {player.health}",
        f"Shield: {player.shield}",
        f"Speed: {player.speed}",
        f"Money: {player.money}",
        f"Time Stat: {player.time_stat}",
        f"Bullet Speed: {player.bullet_speed}",
        f"Bullet Count: {player.bullet_count}",
        f"Score: {score_manager.score}",
        f"Letters: {', '.join(player.letters) if player.letters else 'None'}"
    ]
    overlay = pygame.Surface((210, 300))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    font = pygame.font.Font(None, 20)
    y_offset = 10
    for line in info_lines:
        text_surface = font.render(line, True, (255, 255, 255))
        overlay.blit(text_surface, (10, y_offset))
        y_offset += text_surface.get_height() + 2
    screen.blit(overlay, (10, 100))


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialize sound system
        
        # Get the display info
        display_info = pygame.display.Info()
        self.settings = self.load_settings()
        
        # Set up fullscreen display
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings['screen_width'] = self.screen.get_width()
        self.settings['screen_height'] = self.screen.get_height()
        
        pygame.display.set_caption("Galactic Striker")
        
        # Initialize clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bonus_group = pygame.sprite.Group()
        
        # Create background with borders
        self.background = Background(self.screen.get_width(), self.screen.get_height(), scroll_speed=1)
        
        # Create player at the bottom center of the screen
        player_x = self.screen.get_width() // 2
        player_y = self.screen.get_height() - 30  # 100 pixels from bottom
        self.player = Player(player_x, player_y, self.player_bullets)
        self.all_sprites.add(self.player)
        
        # Initialize managers
        self.score_manager = ScoreManager()
        self.sound_manager = SoundManager()
        self.level_manager = LevelManager(1, self.enemies, self.all_sprites, self.enemy_bullets)
        self.editor = LevelEditor()

        # Pass sound manager to objects that need it
        self.player.sound_manager = self.sound_manager
        self.level_manager.sound_manager = self.sound_manager
        
        self.running = True
        self.dev_mode = False  # developer mode toggle
        self.editing = False  # editing mode toggle


    def load_settings(self):
        """Load game settings from config."""
        return {
            'alien_settings': ALIEN_SETTINGS,
            'formations': FORMATIONS,
            'movement_patterns': MOVEMENT_PATTERNS,
            'special_effects': SPECIAL_EFFECTS,
            'screen_width': 1024,
            'screen_height': 768,
            'fps': 60,
            'debug': False,
            'music_volume': 0.5,
            'sfx_volume': 0.7,
            'difficulty': 1,
            'fullscreen': False
        }

    def init_game_objects(self):
        """Initialize game objects and groups."""
        self.bonus_group = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        
        # Player spawns at 95% of screen height, centered in play area
        play_area_left = int(self.screen.get_width() * 0.12)
        play_area_width = self.screen.get_width() - (2 * play_area_left)
        self.player = Player(play_area_left + (play_area_width // 2),
                            int(self.screen.get_height() * 0.95),
                            self.player_bullets)
        self.all_sprites.add(self.player)
        global_state.global_player = self.player

        self.score_manager = ScoreManager()
        self.level_manager = LevelManager(1, self.enemies, self.all_sprites, self.enemy_bullets)

    def handle_collisions(self):
        """Handle all game collisions."""
        # Player bullets hitting enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, False, True)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                enemy.take_damage(bullet.damage)
                if enemy.health <= 0:
                    self.spawn_rewards(enemy.rect.center)
                    enemy.kill()
                    self.score_manager.add_score(enemy.points)

        # Enemy bullets hitting player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        for bullet in hits:
            self.player.take_damage(bullet.damage)

        # Player collecting bonuses
        hits = pygame.sprite.spritecollide(self.player, self.bonus_group, True)
        for bonus in hits:
            # Check if bonus accepts game_context
            if 'game_context' in bonus.apply.__code__.co_varnames:
                bonus.apply(self.player, {"score_manager": self.score_manager, "enemy_group": self.enemies})
            else:
                bonus.apply(self.player)  # For bonuses that don't use game_context

    def update(self, dt):
        """Update game state."""
        # Update all game objects
        self.background.update()
        self.all_sprites.update()
        self.player_bullets.update()
        self.enemy_bullets.update()
        self.enemies.update()
        self.bonus_group.update()
        self.level_manager.update()

        # Handle collisions
        self.handle_collisions()

    def spawn_rewards(self, position):
        """Spawn rewards at the given position."""
        try:
            # Random chance to spawn different rewards
            chance = random.random()
            
            if chance < 0.3:  # 30% chance for money bonuses
                reward_class = random.choice([MoneyBonus10, MoneyBonus50, MoneyBonus100, MoneyBonus200])
                reward = reward_class(position[0], position[1])
                
            elif chance < 0.5:  # 20% chance for shot upgrades
                reward_class = random.choice([SingleShotBonus, DoubleShotBonus, TripleShotBonus, QuadShotBonus])
                reward = reward_class(position[0], position[1])
                
            elif chance < 0.7:  # 20% chance for rank marker
                reward = RankMarker(position[0], position[1])
                
            elif chance < 0.9:  # 20% chance for letter bonus
                letters = 'EXTRA'  # or 'EXTRA' or whatever letters you want to use
                reward = LetterBonus(position[0], position[1], random.choice(letters))
                
            else:  # 10% chance for special bonuses
                reward_class = random.choice([
                    ShipAutofireBonus, AlienScoopBonus,
                    MoneyBombBonus, GemBombBonus
                ])
                reward = reward_class(position[0], position[1])

            # Set sound manager for the reward if it needs sounds
            if hasattr(reward, 'sound_manager'):
                reward.sound_manager = self.sound_manager
            
            self.bonus_group.add(reward)
            self.all_sprites.add(reward)
            
        except Exception as e:
            logger.error(f"Error spawning rewards: {e}")

    def spawn_alien_group(self, group_data):
        """Spawn a group of aliens."""
        try:
            aliens = []
            for pos in group_data['positions']:
                alien = NonBossAlien(pos[0], pos[1], self.enemy_bullets, group_data['alien_type'])
                alien.sound_manager = self.sound_manager  # Set sound manager for each alien
                aliens.append(alien)
                self.enemies.add(alien)
                self.all_sprites.add(alien)
        except Exception as e:
            logger.error(f"Error spawning alien group 0x0001: {e}")

    def draw(self, dev_mode, editing):
        """Draw game state."""
        self.background.draw(self.screen)
        
        # Draw all sprites including bullets
        self.all_sprites.draw(self.screen)
        self.player_bullets.draw(self.screen)  # Explicitly draw bullets
        self.enemy_bullets.draw(self.screen)   # Explicitly draw bullets
        
        # Draw score
        self.score_manager.draw(self.screen, 10, 10)
        
        if dev_mode:
            draw_dev_info(self.screen, self.player, self.level_manager, self.score_manager)

        if editing:
            self.editor.draw()           
        
        pygame.display.flip()

    def show_level_intro(self, level_number):
        """Display level introduction screen with countdown while game continues."""
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 36)
        
        # Create text surfaces
        level_text = font_large.render(f"LEVEL {level_number}", True, (255, 255, 255))
        level_rect = level_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 50))
        
        countdown = 5
        start_time = pygame.time.get_ticks()
        
        while countdown > 0:
            current_time = pygame.time.get_ticks()
            dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                #elif event.type == pygame.KEYDOWN:
                #    if event.key == pygame.K_ESCAPE:
                #        return  # Allow skipping the intro
            
            # Update countdown
            elapsed = (current_time - start_time) / 1000  # Convert to seconds
            if elapsed >= 1.0:
                countdown -= 1
                start_time = current_time
            
            # Update game state
            self.update(dt)  # Use existing update method
            
            # Draw game state
            self.background.draw(self.screen)
            self.all_sprites.draw(self.screen)
            self.player_bullets.draw(self.screen)
            self.enemy_bullets.draw(self.screen)
            self.bonus_group.draw(self.screen)
            self.score_manager.draw(self.screen, 10, 10)
            
            # Draw semi-transparent overlay
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black
            self.screen.blit(overlay, (0, 0))
            
            # Draw level text and countdown
            self.screen.blit(level_text, level_rect)
            countdown_text = font_large.render(str(countdown), True, (255, 255, 255))
            countdown_rect = countdown_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
            self.screen.blit(countdown_text, countdown_rect)
            
            pygame.display.flip()

    def run(self):
        """Main game loop."""
        try:
            # Show intro and load first level
            self.show_level_intro(1)
            self.level_manager.spawn_next_group()  # Spawn first group after countdown
            
            while self.running:
                dt = self.clock.tick(60) / 1000.0
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_F3:
                            self.settings['debug'] = not self.settings['debug']
                        elif event.key == pygame.K_e:
                            self.editing = not self.editing
                        elif event.key == pygame.K_d:
                            self.dev_mode = not self.dev_mode

                # Update game state
                self.update(dt)
                
                # Check if level is complete
                if self.level_manager.level_complete:
                    next_level = self.level_manager.current_level + 1
                    self.show_level_intro(next_level)  # Show intro while game continues
                    self.level_manager.load_next_level()  # Load next level after countdown
                    self.level_manager.spawn_next_group()  # Spawn first group of new level

                # Draw everything
                self.draw(self.dev_mode, self.editing)
                pygame.display.flip()
            
            pygame.quit()
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            pygame.quit()
            raise

if __name__ == '__main__':
    game = Game()
    game.run()

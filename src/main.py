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

# Game settings and state
from src.config.game_settings import (
    ALIEN_SETTINGS,
    FORMATIONS,
    MOVEMENT_PATTERNS,
    SPECIAL_EFFECTS,
    PLAY_AREA
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
        play_area_left = int(self.screen.get_width() * PLAY_AREA["left_boundary"])
        play_area_width = int(self.screen.get_width() * PLAY_AREA["width_percentage"])
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
        if hits:
            self.player.take_damage(1)  # Always reduce health by 1
            if self.player.health <= 0:
                self.game_over()

        # Player collecting bonuses
        hits = pygame.sprite.spritecollide(self.player, self.bonus_group, True)
        for bonus in hits:
            # Check if bonus accepts game_context
            if 'game_context' in bonus.apply.__code__.co_varnames:
                bonus.apply(self.player, {"score_manager": self.score_manager, "enemy_group": self.enemies})
            else:
                bonus.apply(self.player)

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
        """Spawn rewards with probability based on level difficulty."""
        try:
            # Base chance starts at 15% and increases with level difficulty
            base_chance = 0.15 + (min(self.level_manager.current_level, 100) * 0.001)  # Max +10% at level 100
            
            # Only proceed if we hit the spawn chance
            if random.random() > base_chance:
                return
            
            chance = random.random()
            reward = None
            
            # Define reward groups with their probabilities and classes
            reward_groups = {
                # Money bonuses (15%)
                (0, 0.15): [
                    (MoneyBonus10, 0.4),     # 6%
                    (MoneyBonus50, 0.3),     # 4.5%
                    (MoneyBonus100, 0.2),    # 3%
                    (MoneyBonus200, 0.1)     # 1.5%
                ],
                # Weapon bonuses (15%)
                (0.15, 0.30): [
                    (SingleShotBonus, 0.2),   # 3%
                    (DoubleShotBonus, 0.2),   # 3%
                    (TripleShotBonus, 0.2),   # 3%
                    (QuadShotBonus, 0.2),     # 3%
                ],
                # Stat bonuses (15%)
                (0.30, 0.45): [
                    (ExtraSpeedBonus, 0.25),       # 3.75%
                    (ExtraBulletBonus, 0.25),      # 3.75%
                    (ExtraTimeBonus, 0.25),        # 3.75%
                    (ExtraBulletSpeedBonus, 0.25)  # 3.75%
                ],
                # Special bonuses (15%)
                (0.45, 0.60): [
                    (ShipAutofireBonus, 0.2),    # 3%
                    (AlienScoopBonus, 0.2),      # 3%
                    (MoneyBombBonus, 0.2),       # 3%
                    (GemBombBonus, 0.2),         # 3%
                    (ExtraLifeBonus, 0.2)        # 3%
                ],
                # Game mode bonuses (15%)
                (0.60, 0.75): [
                    (MirrorModeBonus, 0.2),      # 3%
                    (DrunkModeBonus, 0.2),       # 3%
                    (FreezeModeBonus, 0.2),      # 3%
                    (WarpForwardBonus, 0.2),     # 3%
                    (CashDoublerBonus, 0.2)      # 3%
                ],
                # Modifier bonuses (15%)
                (0.75, 0.90): [
                    (DecreaseStrengthRedBonus, 0.15),    # 2.25%
                    (DecreaseStrengthGreenBonus, 0.15),  # 2.25%
                    (DecreaseStrengthBlueBonus, 0.15),   # 2.25%
                    (X2ScoreMultiplierBonus, 0.15),      # 2.25%
                    (X5ScoreMultiplierBonus, 0.15),      # 2.25%
                    (BonusMeteorstormBonus, 0.125),      # 1.875%
                    (BonusMemorystationBonus, 0.125)     # 1.875%
                ],
                # Collection bonuses (10%)
                (0.90, 1.0): [
                    (RankMarker, 0.4),    # 4%
                    (lambda x, y: LetterBonus(x, y, random.choice('BONUS')), 0.6)  # 6%
                ]
            }

            # Find the appropriate group based on chance
            for (min_prob, max_prob), rewards in reward_groups.items():
                if min_prob <= chance < max_prob:
                    # Select reward from group based on internal probabilities
                    sub_chance = random.random()
                    cumulative = 0
                    for reward_class, prob in rewards:
                        cumulative += prob
                        if sub_chance <= cumulative:
                            reward = reward_class(position[0], position[1])
                            break

            # Only proceed if we got a reward
            if reward:
                reward.sound_manager = self.sound_manager
                self.bonus_group.add(reward)
                self.all_sprites.add(reward)
                logger.info(f"Spawned reward: {reward.__class__.__name__} at position {position}")
            
        except Exception as e:
            logger.error(f"Error spawning rewards: {e}")

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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # Allow skipping the intro
            
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

    def game_over(self):
        """Handle game over state."""
        try:
            # Draw the final game state once
            self.draw(self.dev_mode, self.editing)
            
            # Create and setup overlay
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Dark semi-transparent overlay
            self.screen.blit(overlay, (0, 0))
            
            # Setup fonts
            font_large = pygame.font.Font(None, 74)
            font_small = pygame.font.Font(None, 36)
            
            # Create text surfaces
            game_over_text = font_large.render("GAME OVER", True, (255, 0, 0))
            score_text = font_small.render(f"Final Score: {self.score_manager.score}", True, (255, 255, 255))
            press_text = font_small.render("Press SPACE/ENTER to quit", True, (255, 255, 255))
            
            # Position text
            game_over_rect = game_over_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 50))
            score_rect = score_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
            press_rect = press_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 100))
            
            # Draw all text elements once
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(press_text, press_rect)
            
            # Update display once
            pygame.display.flip()
            
            # Event loop
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and 
                        event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE)
                    ):
                        self.running = False
                        return
                
                # Control frame rate without redrawing
                self.clock.tick(60)
                
        except Exception as e:
            logger.error(f"Error in game over screen: {e}")

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
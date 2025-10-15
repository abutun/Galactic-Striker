import logging
from typing import Optional

import pygame

# Configure logging
logger = logging.getLogger(__name__)

# Core game components
from src.player.player import Player, RANK_NAMES
from src.misc.background import Background
from src.manager.score_manager import ScoreManager
from src.manager.sound_manager import SoundManager
from src.manager.level_manager import LevelManager
from src.manager.reward_manager import RewardManager
from src.ui.hud_overlay import HUDOverlay
from src.ui.level_intro import LevelIntroOverlay
from src.ui.settings_menu import SettingsMenu

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
    X3ScoreMultiplierBonus, X4ScoreMultiplierBonus,
    X5ScoreMultiplierBonus, CashDoublerBonus,
    
    # Game mode bonuses
    MirrorModeBonus, DrunkModeBonus, FreezeModeBonus,
    WarpForwardBonus
)

# Developer mode overlay function.
def draw_dev_info(screen, player, level_manager, score_manager):
    width, height = 320, 420
    panel_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    panel_surface.fill((26, 32, 54, 220))
    pygame.draw.rect(panel_surface, (110, 140, 210), panel_surface.get_rect(), width=2, border_radius=16)

    title_font = pygame.font.Font(None, 26)
    text_font = pygame.font.Font(None, 18)

    title_surface = title_font.render("DEVELOPER MODE", True, (220, 230, 255))
    panel_surface.blit(title_surface, (20, 18))

    stats = [
        ("Level", str(level_manager.level_data.level_number)),
        ("Rank", f"{RANK_NAMES[player.rank - 1]} (#{player.rank})"),
        ("Score", f"{score_manager.score:,}"),
        ("Combo", str(score_manager.combo)),
        ("Multiplier", str(score_manager.multiplier)),
        ("Lives", str(player.life)),
        ("Shield", str(player.shield)),
        ("Weapon", str(player.primary_weapon)),
        ("Autofire", str(player.autofire)),
        ("Scoop", str(player.scoop_active)),
        ("Mirror", str(player.mirror_mode)),
        ("Drunk", str(player.drunk_mode)),
        ("Letters", ", ".join(player.letters) if player.letters else "None"),
    ]

    y = 56
    for label, value in stats:
        line_surface = text_font.render(f"{label.upper()}: {value}", True, (200, 210, 235))
        panel_surface.blit(line_surface, (20, y))
        y += 24

    screen.blit(panel_surface, (20, 186))


class Game:
    def __init__(self):
        pygame.init()
        self.settings = self.load_settings()

        # Attempt to initialise audio, fall back gracefully when unavailable.
        self.mixer_available = True
        try:
            pygame.mixer.init()
        except pygame.error as exc:
            self.mixer_available = False
            logger.warning("Audio initialisation failed: %s. Running without sound.", exc)

        pygame.display.set_caption("Galactic Striker")
        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings['screen_width'] = self.screen.get_width()
        self.settings['screen_height'] = self.screen.get_height()

        # Initialize clock for controlling frame rate
        self.clock = pygame.time.Clock()
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.player_bullets = pygame.sprite.Group()
        self.enemy_bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.bonus_group = pygame.sprite.Group()
        
        # Create background with borders
        self.background = Background(
            self.screen.get_width(),
            self.screen.get_height(),
            scroll_speed=1,
            density=self.settings.get('star_density', 0.00025)
        )
        self.hud_overlay = HUDOverlay(self.screen.get_size())
        
        # Create player at the bottom center of the screen
        player_x = self.screen.get_width() // 2
        player_y = self.screen.get_height() - 30  # 30 pixels from bottom
        self.player = Player(player_x, player_y, self.player_bullets, self.all_sprites)
        self.all_sprites.add(self.player)
        global_state.global_player = self.player
        
        # Initialize managers
        self.score_manager = ScoreManager()
        self.sound_manager = SoundManager(enabled=self.mixer_available, sfx_volume=self.settings.get('sfx_volume', 0.7))
        self.level_manager = LevelManager(1, self.enemies, self.all_sprites, self.enemy_bullets)
        self.reward_manager = RewardManager()

        # Pass sound manager to objects that need it
        self.player.sound_manager = self.sound_manager
        self.level_manager.sound_manager = self.sound_manager
        self.score_manager.player = self.player
        
        self.running = True
        self.dev_mode = bool(self.settings.get('debug', False))
        self.paused = False
        self.pause_font_large = pygame.font.Font(None, 86)
        self.pause_font_small = pygame.font.Font(None, 36)
        self.level_intro: Optional[LevelIntroOverlay] = None
        self.level_intro_pending_level: Optional[int] = None
        self.level_intro_spawn_queued = False

        self.settings_menu = SettingsMenu(self.screen.get_size())
        self._configure_settings_menu()

        pygame.mouse.set_visible(False)
        self.schedule_level_intro(self.level_manager.current_level, initial=True)


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
            'fullscreen': True,
            'star_density': 0.00025
        }

    def _configure_settings_menu(self) -> None:
        """Register adjustable settings for the in-game menu."""
        self.settings_menu.add_option(
            "Developer Overlay",
            getter=lambda: self.dev_mode,
            setter=self._set_dev_mode,
            kind="toggle",
            description="Display internal stats while playing.",
        )
        self.settings_menu.add_option(
            "Difficulty",
            getter=lambda: self.settings.get('difficulty', 1),
            setter=self._set_difficulty,
            kind="range",
            step=1,
            min_value=1,
            max_value=10,
            description="Adjusts enemy behaviour scaling.",
        )
        self.settings_menu.add_option(
            "Effects Volume",
            getter=lambda: self.settings.get('sfx_volume', 0.7),
            setter=self._set_sfx_volume,
            kind="range",
            step=0.05,
            min_value=0.0,
            max_value=1.0,
            description="Master volume for sound effects.",
        )
        self.settings_menu.add_option(
            "Star Density",
            getter=lambda: self.settings.get('star_density', 0.00025),
            setter=self._set_star_density,
            kind="range",
            step=0.00005,
            min_value=0.00005,
            max_value=0.0015,
            formatter=lambda value: f"{value:.5f}",
            description="Visual density of the starfield backdrop.",
        )

    def _set_dev_mode(self, value) -> None:
        self.dev_mode = bool(value)

    def _set_sfx_volume(self, value) -> None:
        volume = max(0.0, min(1.0, float(value)))
        self.settings['sfx_volume'] = volume
        if self.sound_manager:
            self.sound_manager.set_master_volume(volume)

    def _set_star_density(self, value) -> None:
        density = max(0.00005, min(0.0015, float(value)))
        self.settings['star_density'] = density
        self.background.set_density(density)

    def _set_difficulty(self, value) -> None:
        self.settings['difficulty'] = int(max(1, min(10, int(value))))

    def schedule_level_intro(self, level_number: int, initial: bool = False) -> None:
        """Prepare a non-blocking intro overlay for the given level."""
        level_data = getattr(self.level_manager, "level_data", None)
        level_name = getattr(level_data, "name", None) if level_data else None
        self.level_intro = LevelIntroOverlay(
            level_number,
            level_name=level_name,
            countdown_seconds=3.0 if not initial else 4.0,
            hold_seconds=0.8,
            screen_size=self.screen.get_size(),
        )
        self.level_intro_pending_level = level_number
        self.level_intro_spawn_queued = True
        self.level_manager.next_group_pending = False
        if initial:
            self.level_manager.active_groups = []

    def _update_level_intro(self, dt: float) -> None:
        if not self.level_intro or self.paused:
            return
        self.level_intro.update(dt)
        if self.level_intro_spawn_queued and self.level_intro.should_spawn():
            self.level_manager.spawn_next_group()
            self.level_intro.mark_spawned()
            self.level_intro_spawn_queued = False
        if self.level_intro.is_finished():
            self.level_intro = None
            self.level_intro_pending_level = None

    def handle_collisions(self):
        """Handle all game collisions."""
        # Player bullets hitting enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, False, True)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                enemy.take_damage(bullet.damage)
                if enemy.life <= 0:
                    self.spawn_rewards(enemy.rect.center)
                    enemy.kill()
                    self.score_manager.add_score(enemy.points)

        # Enemy bullets hitting player
        hits = pygame.sprite.spritecollide(self.player, self.enemy_bullets, True)
        if hits:
            self.player.take_damage(1)  # Always reduce life by 1
            if self.player.life <= 0:
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
        if self.paused:
            return

        # Update all game objects
        self.background.update(dt)
        self.all_sprites.update()
        self.player_bullets.update()
        self.enemy_bullets.update()
        self.enemies.update()
        self.bonus_group.update()
        self.level_manager.update()
        self.score_manager.update()

        # Handle collisions
        self.handle_collisions()

    def spawn_rewards(self, position):
        """Spawn rewards with probability based on level difficulty."""
        reward = self.reward_manager.spawn_reward(
            position, 
            self.level_manager.current_level, 
            self.sound_manager
        )
        
        if reward:
            self.bonus_group.add(reward)
            self.all_sprites.add(reward)

    def toggle_pause(self) -> None:
        """Pause or resume gameplay while keeping the scene visible."""
        self.paused = not self.paused
        if self.sound_manager:
            if self.paused:
                self.sound_manager.pause_all()
            else:
                self.sound_manager.resume_all()
        if self.paused or self.settings_menu.active:
            pygame.mouse.set_visible(True)
        else:
            pygame.mouse.set_visible(False)

    def restart_level(self) -> None:
        """Reset the current level and respawn the player."""
        logger.info("Restarting level %s", self.level_manager.current_level)

        if self.paused:
            self.paused = False
            if self.sound_manager:
                self.sound_manager.resume_all()

        # Clear existing entities but reuse sprite groups to keep references intact.
        for group in (self.all_sprites, self.player_bullets, self.enemy_bullets, self.enemies, self.bonus_group):
            group.empty()

        # Re-create player and propagate references.
        self.player = Player(
            self.screen.get_width() // 2,
            self.screen.get_height() - 30,
            self.player_bullets,
            self.all_sprites
        )
        self.player.sound_manager = self.sound_manager
        self.all_sprites.add(self.player)
        global_state.global_player = self.player
        self.score_manager.player = self.player
        self.score_manager.reset(False)

        # Reset level state and respawn enemies.
        self.level_manager.enemy_group = self.enemies
        self.level_manager.sprite_group = self.all_sprites
        self.level_manager.bullet_group = self.enemy_bullets
        self.level_manager.reset_level()

        self.schedule_level_intro(self.level_manager.current_level)

    def draw_pause_overlay(self) -> None:
        """Render a pause overlay with handy shortcuts."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((12, 16, 32, 200))
        self.screen.blit(overlay, (0, 0))

        title_surface = self.pause_font_large.render("PAUSED", True, (255, 230, 185))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 60))
        self.screen.blit(title_surface, title_rect)

        options = [
            "Enter - Resume Mission",
            "R - Restart Level",
            "S - Settings",
            "Q - Quit to Desktop"
        ]

        for idx, option in enumerate(options):
            text_surface = self.pause_font_small.render(option, True, (220, 230, 255))
            text_rect = text_surface.get_rect(center=(self.screen.get_width() // 2, title_rect.bottom + 30 + idx * 36))
            self.screen.blit(text_surface, text_rect)

    def draw(self):
        """Draw game state."""
        # Draw background (without borders)
        self.background.draw(self.screen)
        
        # Draw all sprites including bullets
        self.all_sprites.draw(self.screen)
        self.player_bullets.draw(self.screen)  # Explicitly draw bullets
        self.enemy_bullets.draw(self.screen)   # Explicitly draw bullets
        
        # Draw borders ON TOP of the sprites
        self.background.draw_borders(self.screen)

        # HUD overlay
        self.hud_overlay.draw(self.screen, self.player, self.score_manager, self.level_manager, paused=self.paused)
        
        if self.dev_mode:
            draw_dev_info(self.screen, self.player, self.level_manager, self.score_manager)

    def game_over(self):
        """Handle game over state."""
        try:
            # Draw the final game state once
            self.draw()
            
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
            while self.running:
                dt = self.clock.tick(self.settings.get('fps', 60)) / 1000.0
                
                # Handle events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                        continue

                    if self.settings_menu.active:
                        self.settings_menu.handle_event(event)
                        if self.settings_menu.active:
                            continue
                        if event.type == pygame.KEYDOWN:
                            # Suppress the key that closed the menu
                            continue

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            self.toggle_pause()
                        elif event.key == pygame.K_RETURN and self.paused:
                            self.toggle_pause()
                        elif event.key == pygame.K_r and self.paused:
                            self.restart_level()
                        elif event.key == pygame.K_q and self.paused:
                            self.running = False
                        elif event.key == pygame.K_s:
                            if self.settings_menu.active:
                                self.settings_menu.close()
                            else:
                                if not self.paused:
                                    self.toggle_pause()
                                self.settings_menu.open()
                        elif event.key == pygame.K_F3 and not self.paused:
                            self.settings['debug'] = not self.settings['debug']
                            self.dev_mode = self.settings['debug']
                        elif event.key == pygame.K_d and not self.paused:
                            self.dev_mode = not self.dev_mode

                # Update game state
                if not self.paused:
                    self.update(dt)
                    self._update_level_intro(dt)
                else:
                    self.background.update(dt * 0.3)
                
                # Check if level is complete
                if not self.paused and self.level_manager.level_complete:
                    # Reset score manager's combo and multiplier
                    self.score_manager.reset(False)

                    self.level_manager.load_next_level()  # Load next level data
                    self.schedule_level_intro(self.level_manager.current_level)

                # Draw everything
                self.draw()
                if self.level_intro:
                    self.level_intro.draw(self.screen)
                if self.paused:
                    self.draw_pause_overlay()
                if self.settings_menu.active:
                    self.settings_menu.update(dt)
                    self.settings_menu.draw(self.screen)
                pygame.display.flip()
            
            pygame.quit()
        except Exception as e:
            logger.error(f"Error in game loop: {e}")
            pygame.quit()
            raise

if __name__ == '__main__':
    game = Game()
    game.run()

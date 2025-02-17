import os
import sys


# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import pygame
import random
from src.player import Player, RANK_NAMES
from src.bonus import (
    RankMarker, LetterBonus, MoneyBonus10, MoneyBonus50, MoneyBonus100, MoneyBonus200, SingleShotBonus, DoubleShotBonus, TripleShotBonus, QuadShotBonus, ExtraSpeedBonus, ExtraBulletBonus, ExtraTimeBonus, ExtraBulletSpeedBonus, ExtraLifeBonus, ShipAutofireBonus, AlienScoopBonus, MoneyBombBonus, GemBombBonus, LetterBonus, BonusMeteorstormBonus, BonusMemorystationBonus, DecreaseStrengthRedBonus, DecreaseStrengthGreenBonus, DecreaseStrengthBlueBonus, X2ScoreMultiplierBonus, X5ScoreMultiplierBonus, CashDoublerBonus, MirrorModeBonus, DrunkModeBonus, FreezeModeBonus, WarpForwardBonus
)  # Explicit imports from bonus module
from src.scoring import ScoreManager
from src.utils import load_sound
from src.background import Background
from src.level_manager import LevelManager
import src.global_state as global_state
from src.config.game_settings import (
    ALIEN_SETTINGS,
    FORMATIONS,
    MOVEMENT_PATTERNS,
    SPECIAL_EFFECTS
)


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
    overlay = pygame.Surface((270, 400))
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
        player_y = self.screen.get_height() - 100  # 100 pixels from bottom
        self.player = Player(player_x, player_y, self.player_bullets)
        self.all_sprites.add(self.player)
        
        # Initialize managers
        self.level_manager = LevelManager(1, self.enemies, self.all_sprites, self.enemy_bullets)
        self.score_manager = ScoreManager()
        
        # Set initial game state
        self.running = True
        self.level_manager.spawn_next_group()

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

        # Load sounds
        self.laser_sound = load_sound("assets/audio/laser.wav")
        self.explosion_sound = load_sound("assets/audio/explosion.wav")

        if self.laser_sound:
            self.laser_sound.set_volume(0.5)
        if self.explosion_sound:
            self.explosion_sound.set_volume(0.7)

    def run(self):
        """Main game loop."""
        running = True
        dev_mode = False
        level_intro_duration = 3000
        previous_time = pygame.time.get_ticks()

        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - previous_time) / 1000.0
            previous_time = current_time

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_d:
                        dev_mode = not dev_mode

            # Game update logic
            self.update(dt)
            
            # Drawing
            self.draw(dev_mode)
            
            # Cap the frame rate
            pygame.time.Clock().tick(60)

        pygame.quit()
        sys.exit()

    def update(self, dt):
        """Update game state."""
        self.background.update()
        
        # Update all sprite groups
        self.all_sprites.update()
        self.player_bullets.update()
        self.enemy_bullets.update()
        self.enemies.update()
        
        # Update level
        if self.level_manager.update():  # Returns True when level is complete
            next_level = self.level_manager.level_data.level_number + 1
            # Show level intro before starting new level
            self.show_level_intro(next_level)
            self.level_manager.load_level(next_level)
            self.level_manager.spawn_next_group()
        
        # Check collisions
        # Player bullets hitting enemies
        hits = pygame.sprite.groupcollide(self.enemies, self.player_bullets, False, True)
        for enemy, bullets in hits.items():
            for bullet in bullets:
                enemy.take_damage(bullet.damage)
                if enemy.health <= 0:
                    # Spawn rewards when enemy is destroyed
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
            bonus.apply(self.player)

    def spawn_rewards(self, pos):
        """Spawn rewards when an enemy is destroyed."""
        # Random chance to spawn different rewards
        chance = random.random()
        
        # Common bonuses (40% total chance)
        if chance < 0.15:  # 15% chance for money bonuses
            money_choices = [
                (MoneyBonus10, 0.4),    # 6%
                (MoneyBonus50, 0.3),    # 4.5%
                (MoneyBonus100, 0.2),   # 3%
                (MoneyBonus200, 0.1)    # 1.5%
            ]
            bonus_class = random.choices([b[0] for b in money_choices], 
                                       weights=[b[1] for b in money_choices])[0]
            reward = bonus_class(pos[0], pos[1])
        
        elif chance < 0.25:  # 10% chance for shot upgrades
            shot_choices = [
                SingleShotBonus, DoubleShotBonus, 
                TripleShotBonus, QuadShotBonus
            ]
            reward = random.choice(shot_choices)(pos[0], pos[1])
        
        elif chance < 0.40:  # 15% chance for stat bonuses
            stat_choices = [
                ExtraSpeedBonus, ExtraBulletBonus,
                ExtraTimeBonus, ExtraBulletSpeedBonus
            ]
            reward = random.choice(stat_choices)(pos[0], pos[1])
        
        # Uncommon bonuses (15% total chance)
        elif chance < 0.45:  # 5% chance for rank marker
            reward = RankMarker(pos[0], pos[1], "red")
        
        elif chance < 0.50:  # 5% chance for life bonus
            reward = ExtraLifeBonus(pos[0], pos[1])
        
        elif chance < 0.55:  # 5% chance for special bonuses
            special_choices = [
                ShipAutofireBonus, AlienScoopBonus,
                MoneyBombBonus, GemBombBonus
            ]
            reward = random.choice(special_choices)(pos[0], pos[1])
        
        # Rare bonuses (10% total chance)
        elif chance < 0.60:  # 5% chance for letter bonus
            letters = 'EXTRA'
            reward = LetterBonus(pos[0], pos[1], random.choice(letters))
        
        elif chance < 0.65:  # 5% chance for bonus level triggers
            bonus_choices = [
                BonusMeteorstormBonus,
                BonusMemorystationBonus
            ]
            reward = random.choice(bonus_choices)(pos[0], pos[1])
        
        # Very rare bonuses (5% total chance)
        elif chance < 0.70:  # 5% chance for hidden/special effects
            hidden_choices = [
                (DecreaseStrengthRedBonus, 0.1),
                (DecreaseStrengthGreenBonus, 0.1),
                (DecreaseStrengthBlueBonus, 0.1),
                (X2ScoreMultiplierBonus, 0.15),
                (X5ScoreMultiplierBonus, 0.1),
                (CashDoublerBonus, 0.15),
                (MirrorModeBonus, 0.1),
                (DrunkModeBonus, 0.1),
                (FreezeModeBonus, 0.05),
                (WarpForwardBonus, 0.05)
            ]
            bonus_class = random.choices([b[0] for b in hidden_choices], 
                                       weights=[b[1] for b in hidden_choices])[0]
            reward = bonus_class(pos[0], pos[1])
        
        # If a reward was chosen, add it to the game
        if 'reward' in locals():
            self.bonus_group.add(reward)
            self.all_sprites.add(reward)

    def draw(self, dev_mode):
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
        
        pygame.display.flip()

    def show_level_intro(self, level_number):
        """Display level introduction screen with countdown."""
        font_large = pygame.font.Font(None, 74)
        font_small = pygame.font.Font(None, 36)
        
        # Create text surfaces
        level_text = font_large.render(f"LEVEL {level_number}", True, (255, 255, 255))
        level_pos = level_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 - 50))
        
        start_time = pygame.time.get_ticks()
        countdown = 3
        last_update = start_time
        dt = 0

        while countdown > 0:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_update) / 1000.0  # Delta time in seconds
            last_update = current_time
            
            elapsed = (current_time - start_time) / 1000  # Convert to seconds
            if elapsed >= 1.0:
                countdown -= 1
                start_time = current_time

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return  # Allow skipping the intro
            
            # Update game state
            self.background.update()
            self.all_sprites.update()
            self.player_bullets.update()
            self.enemy_bullets.update()
            self.enemies.update()
            self.bonus_group.update()
            
            # Check collisions
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
                bonus.apply(self.player, {"score_manager": self.score_manager, "enemy_group": self.enemies})
            
            # Draw everything
            self.background.draw(self.screen)
            self.all_sprites.draw(self.screen)
            self.player_bullets.draw(self.screen)
            self.enemy_bullets.draw(self.screen)
            self.score_manager.draw(self.screen, 10, 10)
            
            # Draw level intro overlay
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))  # Semi-transparent black overlay
            self.screen.blit(overlay, (0, 0))
            
            # Draw level text and countdown
            self.screen.blit(level_text, level_pos)
            countdown_text = font_large.render(str(countdown), True, (255, 255, 255))
            countdown_pos = countdown_text.get_rect(center=(self.screen.get_width()//2, self.screen.get_height()//2 + 50))
            self.screen.blit(countdown_text, countdown_pos)
            
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()

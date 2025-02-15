import pygame
import sys
import random
from player import Player, RANK_NAMES
from bonus import *
from level_editor import LevelEditor
from scoring import ScoreManager
from utils import load_sound
from background import Background
from level_manager import LevelManager
import global_state
from weapons import Missile  # global_state holds global_player


# Developer mode overlay function.
def draw_dev_info(screen, player, level_manager, score_manager):
    info_lines = [
        "Developer Mode: ON",
        f"Level: {level_manager.level_number}",
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


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Galactic Striker")
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()

    background = Background(screen_width, screen_height, scroll_speed=1)

    all_sprites = pygame.sprite.RenderUpdates()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bonus_group = pygame.sprite.Group()

    # Player spawns at 95% of screen height.
    player = Player(screen_width // 2, int(screen_height * 0.95), player_bullets)
    all_sprites.add(player)
    global_state.global_player = player  # set global player

    score_manager = ScoreManager()
    editor = LevelEditor()
    editing = False

    # Start at level 1.
    current_level = 1
    level_manager = LevelManager(current_level, enemies, all_sprites, enemy_bullets)

    laser_sound = load_sound("assets/audio/laser.wav")
    explosion_sound = load_sound("assets/audio/explosion.wav")

    # Add sound volume control
    if laser_sound:
        laser_sound.set_volume(0.5)  # 50% volume
    if explosion_sound:
        explosion_sound.set_volume(0.7)  # 70% volume

    dev_mode = False  # developer mode toggle

    # Intro duration in milliseconds.
    level_intro_duration = 3000

    # Pre-load commonly used fonts
    FONTS = {
        'small': pygame.font.Font(None, 20),
        'medium': pygame.font.Font(None, 30),
        'large': pygame.font.Font(None, 50)
    }

    def start_meteorstorm():
        print("Meteorstorm bonus level started!")

    def start_memorystation():
        print("Memorystation bonus level started!")

    def warp_forward():
        print("Warping forward!")

    game_context = {
        "enemy_group": enemies,
        "score_manager": score_manager,
        "start_meteorstorm": start_meteorstorm,
        "start_memorystation": start_memorystation,
        "warp_forward": warp_forward
    }

    # Add game states
    class GameState:
        MENU = "menu"
        PLAYING = "playing"
        PAUSED = "paused"
        GAME_OVER = "game_over"
        
    current_state = GameState.PLAYING
    
    # Add pause functionality
    def toggle_pause():
        nonlocal current_state
        if current_state == GameState.PLAYING:
            current_state = GameState.PAUSED
        elif current_state == GameState.PAUSED:
            current_state = GameState.PLAYING
    
    running = True
    previous_time = pygame.time.get_ticks()
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - previous_time) / 1000.0  # Convert to seconds
        previous_time = current_time
        
        # Add escape key handling
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_state == GameState.PLAYING:
                        toggle_pause()
                    else:
                        running = False
                if event.key == pygame.K_p:
                    toggle_pause()
                if event.key == pygame.K_e:
                    editing = not editing
                if event.key == pygame.K_d:
                    dev_mode = not dev_mode
            if editing:
                editor.handle_event(event)

        if current_state == GameState.PAUSED:
            # Draw pause screen
            continue

        background.update()
        all_sprites.update()
        
        # Check for new projectiles and play sound
        for projectile in player_bullets:
            if hasattr(projectile, 'just_spawned') and projectile.just_spawned:
                if laser_sound:
                    if isinstance(projectile, Missile):
                        # Optional: You could add a different sound for missiles
                        laser_sound.set_volume(0.7)  # Louder for missiles
                        laser_sound.play()
                        laser_sound.set_volume(0.5)  # Reset volume
                    else:
                        laser_sound.play()
                projectile.just_spawned = False
        
        player_bullets.update()
        enemy_bullets.update()
        bonus_group.update()
        score_manager.update(dt)

        # Check time since level start.
        current_level_time = pygame.time.get_ticks() - level_manager.start_time

        # If within intro period, display level intro text and skip level updates.
        if current_level_time < level_intro_duration:
            # Draw background and sprites, then overlay level intro text.
            background.draw(screen)
            all_sprites.draw(screen)
            player_bullets.draw(screen)
            enemy_bullets.draw(screen)
            bonus_group.draw(screen)
            score_manager.draw(screen)

            font = pygame.font.Font(None, 50)
            level_text = f"Level {level_manager.level_number}"
            text_surface = font.render(level_text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(text_surface, text_rect)
        else:
            # Once intro period is over, update the level.
            level_manager.update()
            if level_manager.is_level_complete():
                current_level += 1
                if current_level > 250:
                    print("All levels complete!")
                    running = False
                else:
                    level_manager.load_next_level(current_level)
                    print(f"Level {current_level} started!")

            # Collision: Player bullets vs. Enemies.
            hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
            for enemy, bullets in hits.items():
                for bullet in bullets:
                    enemy.take_damage(bullet.damage)
                    bullet.kill()
                if enemy.health <= 0:
                    enemy.kill()
                    score_manager.add_points(enemy.points)
                    if explosion_sound:
                        explosion_sound.play()
                    if random.random() < 0.3:
                        bonus_classes = [
                            SingleShotBonus, DoubleShotBonus, TripleShotBonus, QuadShotBonus,
                            ExtraSpeedBonus, ExtraBulletBonus, ExtraTimeBonus, ExtraBulletSpeedBonus,
                            MoneyBonus10, MoneyBonus50, MoneyBonus100, MoneyBonus200,
                            ExtraLifeBonus, ShipAutofireBonus, ShieldBonus, AlienScoopBonus,
                            MoneyBombBonus, GemBombBonus,
                            ExtraLetterBonus,
                            RankMarkerBonus,
                            BonusMeteorstormBonus, BonusMemorystationBonus,
                            DecreaseStrengthRedBonus, DecreaseStrengthGreenBonus, DecreaseStrengthBlueBonus,
                            X2ScoreMultiplierBonus, X5ScoreMultiplierBonus,
                            CashDoublerBonus, MirrorModeBonus, DrunkModeBonus, FreezeModeBonus, WarpForwardBonus
                        ]
                        chosen_bonus = random.choice(bonus_classes)
                        if chosen_bonus == ExtraLetterBonus:
                            letter = random.choice(["E", "X", "T", "R", "A"])
                            bonus_instance = chosen_bonus(enemy.rect.centerx, enemy.rect.centery, letter)
                        else:
                            bonus_instance = chosen_bonus(enemy.rect.centerx, enemy.rect.centery)
                        bonus_group.add(bonus_instance)
                        all_sprites.add(bonus_instance)

            # Collision: Enemy bullets vs. Player.
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for bullet in hits:
                player.take_damage(bullet.damage)
                bullet.kill()
                if player.health <= 0:
                    print("Game Over!")
                    running = False

            # Collision: Player collides with Bonuses.
            hits = pygame.sprite.spritecollide(player, bonus_group, True)
            for bonus in hits:
                bonus.apply(player, game_context)

            # Optional: Player collides with Enemies.
            hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in hits:
                player.take_damage(1)
                enemy.take_damage(1)
                if enemy.health <= 0:
                    enemy.kill()
                    score_manager.add_points(enemy.points)
                if player.health <= 0:
                    print("Game Over!")
                    running = False

            background.draw(screen)
            all_sprites.draw(screen)
            player_bullets.draw(screen)
            enemy_bullets.draw(screen)
            bonus_group.draw(screen)
            score_manager.draw(screen)
            font = pygame.font.Font(None, 30)
            rank_text = font.render(f"Rank: {RANK_NAMES[player.rank - 1]}", True, (255, 255, 255))
            screen.blit(rank_text, (10, 10))

        if dev_mode:
            draw_dev_info(screen, player, level_manager, score_manager)

        pygame.display.flip()
        clock.tick(60)

    print(f"Final Rank: {RANK_NAMES[player.rank - 1]}")
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

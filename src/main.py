import pygame
import sys
import random
from player import Player, RANK_NAMES
from enemy.grunt_enemy import GruntEnemy
from enemy.swarmer_enemy import SwarmerEnemy
from enemy.boss_enemy import BossEnemy
from weapons import Bullet, Missile
from bonus import *
from level_editor import LevelEditor
from scoring import ScoreManager
from utils import load_sound
from background import Background
from level_manager import LevelManager


# Developer mode overlay function.
def draw_dev_info(screen, player, level_manager, score_manager):
    info_lines = []
    info_lines.append("Developer Mode: ON")
    info_lines.append(f"Level: {level_manager.level_number}")
    info_lines.append(f"Rank: {RANK_NAMES[player.rank - 1]} (#{player.rank})")
    info_lines.append(f"Collected Rank Markers: {len(player.rank_markers)}")
    info_lines.append(f"Shot Count: {player.shot_count}")
    info_lines.append(f"Weapon Level: {player.weapon_level}")
    info_lines.append(f"Health: {player.health}")
    info_lines.append(f"Shield: {player.shield}")
    info_lines.append(f"Speed: {player.speed}")
    info_lines.append(f"Money: {player.money}")
    info_lines.append(f"Time Stat: {player.time_stat}")
    info_lines.append(f"Bullet Speed: {player.bullet_speed}")
    info_lines.append(f"Score: {score_manager.score}")
    info_lines.append(f"Letters: {', '.join(player.letters) if player.letters else 'None'}")
    # Create a semi-transparent overlay surface.
    overlay_width = 300
    overlay_height = 200
    overlay = pygame.Surface((overlay_width, overlay_height))
    overlay.set_alpha(200)  # semi-transparent
    overlay.fill((0, 0, 0))
    font = pygame.font.Font(None, 20)
    y_offset = 10
    for line in info_lines:
        text_surface = font.render(line, True, (255, 255, 255))
        overlay.blit(text_surface, (10, y_offset))
        y_offset += text_surface.get_height() + 2
    # Blit the overlay onto the main screen.
    screen.blit(overlay, (10, 100))


def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Galactic Striker")
    clock = pygame.time.Clock()
    screen_width, screen_height = screen.get_size()

    background = Background(screen_width, screen_height, scroll_speed=1)

    # Sprite groups.
    all_sprites = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bonus_group = pygame.sprite.Group()

    player = Player(screen_width // 2, int(screen_height * 0.85), player_bullets)
    all_sprites.add(player)

    score_manager = ScoreManager()
    editor = LevelEditor()
    editing = False

    # Start at level 1.
    current_level = 1
    level_manager = LevelManager(current_level, enemies, all_sprites, enemy_bullets)

    laser_sound = load_sound("assets/audio/laser.wav")
    explosion_sound = load_sound("assets/audio/explosion.wav")

    # Developer mode flag.
    dev_mode = True

    # Example game context for bonus effects.
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

    running = True
    while running:
        dt = clock.get_time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Toggle editor mode with E.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    editing = not editing
                # Toggle developer mode with D.
                if event.key == pygame.K_d:
                    dev_mode = not dev_mode
            if editing:
                editor.handle_event(event)
            if event.type == pygame.USEREVENT + 1 and not editing:
                # LevelManager now schedules enemy spawns; no longer using random spawns here.
                pass  # (Spawn events are handled by the LevelManager.)

        if editing:
            editor.update()
        else:
            background.update()
            all_sprites.update()
            player_bullets.update()
            enemy_bullets.update()
            bonus_group.update()
            score_manager.update(dt)

            level_manager.update()
            if level_manager.is_level_complete():
                current_level += 1
                if current_level > 100:
                    print("All levels complete!")
                    running = False
                else:
                    level_manager.load_next_level(current_level)
                    print(f"Level {current_level} started!")

            # Collision: Player bullets vs. enemies.
            hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
            for enemy, bullets in hits.items():
                for bullet in bullets:
                    enemy.take_damage(bullet.damage)
                if enemy.health <= 0:
                    enemy.kill()
                    score_manager.add_points(enemy.points)
                    if explosion_sound:
                        explosion_sound.play()
                    # 30% chance to drop a bonus.
                    if random.random() < 0.3:
                        bonus_classes = [
                            SingleShotBonus, DoubleShotBonus, TripleShotBonus, QuadShotBonus,
                            ExtraSpeedBonus, ExtraBulletBonus, ExtraTimeBonus, ExtraBulletSpeedBonus,
                            MoneyBonus10, MoneyBonus50, MoneyBonus100, MoneyBonus200,
                            ExtraLifeBonus, ShipAutofireBonus, ShieldBonus, AlienScoopBonus,
                            MoneyBombBonus, GemBombBonus,
                            ExtraLetterBonus,  # Supply a letter when applying.
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
                if player.health <= 0:
                    print("Game Over!")
                    running = False

            # Collision: Player collides with bonuses.
            hits = pygame.sprite.spritecollide(player, bonus_group, True)
            for bonus in hits:
                bonus.apply(player, game_context)

            # Optional: Player collides with enemies.
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
        if editing:
            editor.draw(screen)
        else:
            all_sprites.draw(screen)
            player_bullets.draw(screen)
            enemy_bullets.draw(screen)
            bonus_group.draw(screen)
            score_manager.draw(screen)
            # Display player's current rank in the upper left.
            font = pygame.font.Font(None, 30)
            rank_text = font.render(f"Rank: {RANK_NAMES[player.rank - 1]}", True, (255, 255, 255))
            screen.blit(rank_text, (10, 10))

        # If developer mode is enabled, draw the developer info overlay.
        if dev_mode:
            draw_dev_info(screen, player, level_manager, score_manager)

        pygame.display.flip()
        clock.tick(60)

    print(f"Final Rank: {RANK_NAMES[player.rank - 1]}")
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

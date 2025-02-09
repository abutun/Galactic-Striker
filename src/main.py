# src/main.py
import pygame
import sys
import random
from player import Player
from enemies import GruntEnemy, SwarmerEnemy, BossEnemy
from weapons import Bullet, Missile
from powerups import ShieldPowerUp, WeaponUpgradePowerUp
from level_editor import LevelEditor
from scoring import ScoreManager
from utils import load_sound

def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 800))
    pygame.display.set_caption("Galactic Striker")
    clock = pygame.time.Clock()

    # Sprite groups
    all_sprites = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    # Create the player (starting near the bottom center)
    player = Player(320, 700, player_bullets)
    all_sprites.add(player)

    # Initialize the score manager
    score_manager = ScoreManager()

    # Create a level editor instance (toggle with E)
    editor = LevelEditor()
    editing = False

    # Set up an enemy spawn timer (every 2 seconds)
    SPAWN_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY, 2000)

    # (Optionally) load background music and sound effects
    laser_sound = load_sound("assets/audio/laser.wav")
    explosion_sound = load_sound("assets/audio/explosion.wav")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Toggle editor mode with the E key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    editing = not editing

            # Pass events to the level editor if in editing mode
            if editing:
                editor.handle_event(event)
            else:
                # (Other game-related event handling could go here)
                pass

            # Enemy spawning (only when not in editor mode)
            if event.type == SPAWN_ENEMY and not editing:
                enemy_type = random.choice(["grunt", "swarmer"])
                if enemy_type == "grunt":
                    enemy = GruntEnemy(random.randint(50, 590), -50, enemy_bullets)
                elif enemy_type == "swarmer":
                    enemy = SwarmerEnemy(random.randint(50, 590), -50, enemy_bullets)
                enemies.add(enemy)
                all_sprites.add(enemy)

        if editing:
            editor.update()
        else:
            # Update all sprites
            all_sprites.update()

            # ------------------------
            # Collision detection
            # ------------------------

            # Player bullets hitting enemies
            hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
            for enemy, bullets in hits.items():
                for bullet in bullets:
                    enemy.take_damage(bullet.damage)
                    if enemy.health <= 0:
                        score_manager.add_points(enemy.points)
                        enemy.kill()
                        # Chance to drop a power-up
                        if random.random() < 0.2:
                            pu = ShieldPowerUp(enemy.rect.centerx, enemy.rect.centery)
                            powerups.add(pu)
                            all_sprites.add(pu)
                        # (Play explosion sound here if desired)

            # Enemy bullets hitting the player
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for bullet in hits:
                player.take_damage(bullet.damage)
                if player.health <= 0:
                    print("Game Over!")
                    running = False

            # Player collecting power-ups
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for pu in hits:
                pu.apply(player)

        # ------------------------
        # Rendering
        # ------------------------
        screen.fill((0, 0, 0))  # Black background

        if editing:
            editor.draw(screen)
        else:
            all_sprites.draw(screen)
            score_manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

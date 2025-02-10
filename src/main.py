# src/main.py
import pygame
import sys
import random
from player import Player
from enemy.grunt_enemy import GruntEnemy
from enemy.swarmer_enemy import SwarmerEnemy
from enemy.boss_enemy import BossEnemy
from weapons import Bullet, Missile
from powerups import ShieldPowerUp, WeaponUpgradePowerUp
from level_editor import LevelEditor
from scoring import ScoreManager
from utils import load_sound
from background import Background

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
    powerups = pygame.sprite.Group()

    player = Player(screen_width // 2, int(screen_height * 0.85), player_bullets)
    all_sprites.add(player)

    score_manager = ScoreManager()
    editor = LevelEditor()
    editing = False

    SPAWN_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY, 2000)

    laser_sound = load_sound("assets/audio/laser.wav")
    explosion_sound = load_sound("assets/audio/explosion.wav")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    editing = not editing

            if editing:
                editor.handle_event(event)

            if event.type == SPAWN_ENEMY and not editing:
                enemy_type = random.choice(["grunt", "swarmer"])
                x = random.randint(50, screen_width - 50)
                if enemy_type == "grunt":
                    enemy = GruntEnemy(x, -50, enemy_bullets)
                elif enemy_type == "swarmer":
                    enemy = SwarmerEnemy(x, -50, enemy_bullets)
                enemies.add(enemy)
                all_sprites.add(enemy)

        if editing:
            editor.update()
        else:
            background.update()
            all_sprites.update()
            player_bullets.update()
            enemy_bullets.update()

            # --- Collision Handling ---

            # Player bullets hit enemies.
            hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
            for enemy, bullets in hits.items():
                for bullet in bullets:
                    enemy.take_damage(bullet.damage)
                if enemy.health <= 0:
                    enemy.kill()
                    score_manager.add_points(enemy.points)
                    # Optionally play an explosion sound here.
                    if explosion_sound:
                        explosion_sound.play()

            # Enemy bullets hit player.
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for bullet in hits:
                player.take_damage(bullet.damage)
                if player.health <= 0:
                    print("Game Over!")
                    running = False

            # Optional: Player collides with enemy ships.
            hits = pygame.sprite.spritecollide(player, enemies, False)
            for enemy in hits:
                # For example, inflict damage to both.
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
            score_manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()

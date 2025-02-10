import pygame
import sys
import random
from player import Player
from enemy.grunt_enemy import GruntEnemy
from enemy.swarmer_enemy import SwarmerEnemy
from enemy.boss_enemy import BossEnemy
from weapons import Bullet, Missile
from bonus import *
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

    all_sprites = pygame.sprite.Group()
    player_bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    # We'll use the bonus group for all bonus/powerup sprites.
    bonus_group = pygame.sprite.Group()

    player = Player(screen_width // 2, int(screen_height * 0.85), player_bullets)
    all_sprites.add(player)

    score_manager = ScoreManager()
    editor = LevelEditor()
    editing = False

    SPAWN_ENEMY = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_ENEMY, 2000)

    laser_sound = load_sound("assets/audio/laser.wav")
    explosion_sound = load_sound("assets/audio/explosion.wav")

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
            bonus_group.update()
            score_manager.update(dt)

            # Collision: Player bullets vs. Enemies.
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
                            ExtraLetterBonus,  # For letters, you might choose a specific letter.
                            RankMarkerBonus,
                            BonusMeteorstormBonus, BonusMemorystationBonus,
                            DecreaseStrengthRedBonus, DecreaseStrengthGreenBonus, DecreaseStrengthBlueBonus,
                            X2ScoreMultiplierBonus, X5ScoreMultiplierBonus,
                            CashDoublerBonus, MirrorModeBonus, DrunkModeBonus, FreezeModeBonus, WarpForwardBonus
                        ]
                        chosen_bonus = random.choice(bonus_classes)
                        # For letter bonus, specify a letter.
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

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()

import logging
import pygame
import math
import random
from src.enemy.base_enemy import BaseEnemy
from src.utils.utils import load_image
from src.state.global_state import global_player
from src.utils.sprite_animation import SpriteAnimation

from src.config.game_settings import ALIEN_SETTINGS

logger = logging.getLogger(__name__)

class BossEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group):
        super().__init__(x, y, bullet_group)
        self.image = load_image(
            f"assets/aliens/boss_{self.type_number:02d}.png",
            fallback_color=(255, 255, 0),
            size=ALIEN_SETTINGS["boss"]["size"]
        )
        self.rect = self.image.get_rect(center=(x, y))
        self.phases = 3
        self.current_phase = 1
        self.fire_delay = 1000
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        screen = pygame.display.get_surface()
        if screen:
            _, sh = screen.get_size()
            if self.rect.y < sh * 0.85:
                self.rect.y += self.speed
            else:
                pattern = random.choice(["zigzag", "circular", "random"])
                if pattern == "zigzag":
                    self.rect.y += self.speed
                    self.rect.x += random.choice([-2, 2])
                elif pattern == "circular":
                    t = pygame.time.get_ticks() / 1000.0
                    amplitude = 15
                    self.rect.y += self.speed
                    self.rect.x += int(math.sin(t) * amplitude)
                elif pattern == "random":
                    self.rect.y += self.speed
                    self.rect.x += random.randint(-3, 3)
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now
        if self.health < (20 * self.phases) * (1 - self.current_phase / self.phases) and self.current_phase < self.phases:
            self.current_phase += 1
            self.fire_delay = max(500, self.fire_delay - 200)
        self.wrap_position()

    def fire(self):
        if global_player is not None:
            player_pos = global_player.rect.center
            enemy_pos = self.rect.center
            dx = player_pos[0] - enemy_pos[0]
            dy = player_pos[1] - enemy_pos[1]
            angle = math.atan2(dy, dx)
            bullet_speed = 3
            vx = bullet_speed * math.cos(angle)
            vy = bullet_speed * math.sin(angle)
        else:
            vx = 0
            vy = 3
        for angle_offset in (-15, 0, 15):
            bullet = pygame.sprite.Sprite()
            bullet.image = pygame.Surface((8, 16))
            bullet.image.fill((255, 255, 0))
            bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
            rad = math.radians(angle_offset)
            vx_offset = vx + 3 * math.cos(rad)
            vy_offset = vy + 3 * math.sin(rad)
            bullet.vx = vx_offset
            bullet.vy = vy_offset
            bullet.damage = 2

            def update_bullet(self):
                self.rect.x += self.vx
                self.rect.y += self.vy
                screen = pygame.display.get_surface()
                if screen:
                    sw, sh = screen.get_size()
                    if self.rect.top > sh or self.rect.left < 0 or self.rect.right > sw:
                        self.kill()

            bullet.update = update_bullet.__get__(bullet)
            self.bullet_group.add(bullet)

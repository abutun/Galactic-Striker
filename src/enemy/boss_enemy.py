import pygame
from enemy.base_enemy import BaseEnemy
from utils import load_image


class BossEnemy(BaseEnemy):
    def __init__(self, x, y, bullet_group, phases=3):
        super().__init__(x, y, bullet_group, health=20 * phases, speed=1, points=1000)
        self.image = load_image("assets/sprites/enemy_boss.png", (255, 255, 0), (64, 64))
        self.rect = self.image.get_rect(center=(x, y))
        self.phases = phases
        self.current_phase = 1
        self.fire_delay = 1000  # milliseconds between shots
        self.last_fire = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.speed
        now = pygame.time.get_ticks()
        if now - self.last_fire > self.fire_delay:
            self.fire()
            self.last_fire = now

        # Transition to a new phase if health drops below a threshold.
        if self.health < (20 * self.phases) * (
                1 - self.current_phase / self.phases) and self.current_phase < self.phases:
            self.current_phase += 1
            self.fire_delay = max(500, self.fire_delay - 200)

        self.wrap_position()

    def fire(self):
        for angle in (-15, 0, 15):
            bullet = pygame.sprite.Sprite()
            bullet.image = pygame.Surface((8, 16))
            bullet.image.fill((255, 255, 0))
            bullet.rect = bullet.image.get_rect(center=self.rect.midbottom)
            bullet.vx = 3 * pygame.math.Vector2(1, 0).rotate(angle).x
            bullet.vy = 3 * pygame.math.Vector2(0, 1).rotate(angle).y + 3
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

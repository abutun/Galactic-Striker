import pygame
from src.utils import load_image
from .base_bonus import Bonus

class ExtraSpeedBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_speed.png", (0, 0, 255), (24, 24))
    def apply(self, player, game_context=None):
        player.speed += 2

class ExtraBulletBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_bullet.png", (255, 165, 0), (24, 24))
    def apply(self, player, game_context=None):
        if hasattr(player, 'bullet_count'):
            player.bullet_count += 1
        else:
            player.bullet_count = 1

class ExtraTimeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_time.png", (0, 255, 0), (24, 24))
    def apply(self, player, game_context=None):
        if hasattr(player, 'time_stat'):
            player.time_stat += 5
        else:
            player.time_stat = 5

class ExtraBulletSpeedBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_bullet_speed.png", (255, 0, 0), (24, 24))
    def apply(self, player, game_context=None):
        if hasattr(player, 'bullet_speed'):
            player.bullet_speed += 2
        else:
            player.bullet_speed = 2

class PowerUp(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.image = load_image("assets/bonuses/power_up.png", (0, 0, 0), (20, 20))
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((0, 255, 0))  # Green
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        player.weapon_level = min(player.weapon_level + 1, 7)

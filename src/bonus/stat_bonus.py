import pygame
from src.utils.utils import load_image
from .base_bonus import Bonus

class ExtraSpeedBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            image_path="assets/sprites/extra_speed.png",
            fallback_color=(0, 255, 255),  # Cyan
            size=(24, 24)
        )
        
    def apply(self, player, game_context=None):
        if hasattr(player, 'speed'):
            player.speed = min(player.speed + 1, 8)  # Cap at 8
        else:
            player.speed = 5

class ExtraBulletBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            image_path="assets/sprites/extra_bullet.png",
            fallback_color=(255, 255, 0),  # Yellow
            size=(24, 24)
        )
        
    def apply(self, player, game_context=None):
        if hasattr(player, 'bullet_count'):
            player.bullet_count = min(player.bullet_count + 1, 4)  # Cap at 4
        else:
            player.bullet_count = 2

class ExtraTimeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(
            x, y,
            image_path="assets/sprites/extra_time.png",
            fallback_color=(0, 255, 0),  # Green
            size=(24, 24)
        )
        
    def apply(self, player, game_context=None):
        if hasattr(player, 'time_stat'):
            player.time_stat = min(player.time_stat + 30, 300)  # Cap at 300 seconds
        else:
            player.time_stat = 30

class ExtraBulletSpeedBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(
            x, y, 
            image_path="assets/sprites/extra_bullet_speed.png",
            fallback_color=(255, 128, 0),  # Orange
            size=(24, 24)
        )
        
    def apply(self, player, game_context=None):
        """Increase player's bullet speed"""
        if hasattr(player, 'bullet_speed'):
            player.bullet_speed = min(player.bullet_speed + 1, 10)  # Cap at 10
        else:
            player.bullet_speed = 7  # Default value

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

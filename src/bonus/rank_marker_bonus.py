from src.utils.utils import load_image
from .base_bonus import Bonus
import pygame

class RankMarker(Bonus):
    def __init__(self, x, y, color="red"):
        super().__init__(x, y)
        try:
            self.image = load_image(f"assets/sprites/rank_marker_{color}.png", (0, 0, 0), (32, 32))
        except:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 215, 0))  # Gold color
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        self.sound_manager.play("bonus_reward")
        player.rank_markers.append(self)
        player.check_rank_upgrade()

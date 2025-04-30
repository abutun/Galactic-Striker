import pygame
from src.utils.utils import load_image
from .base_bonus import Bonus

class LetterBonus(Bonus):
    def __init__(self, x, y, letter):
        super().__init__(x, y)
        self.letter = letter
        try:
            self.image = load_image(f"assets/sprites/letter_{letter}.png", (0, 0, 0), (32, 32))
        except:
            self.image = pygame.Surface((32, 32))
            self.image.fill((128, 0, 128))  # Purple
            font = pygame.font.Font(None, 20)
            text = font.render(letter, True, (255, 255, 255))
            self.image.blit(text, text.get_rect(center=self.image.get_rect().center))
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        self.sound_manager.play("bonus_reward")
        if self.letter not in player.letters:
            player.letters.append(self.letter)

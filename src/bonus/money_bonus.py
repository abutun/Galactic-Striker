import pygame
from src.utils.utils import load_image
from .base_bonus import Bonus

class MoneyBonus(Bonus):
    def __init__(self, x, y, amount=10):
        super().__init__(x, y)
        self.amount = amount
        try:
            self.image = load_image(f"assets/sprites/money_bonus_{amount}.png", (0, 0, 0), (32, 32))
        except:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 223, 0))  # Gold
            font = pygame.font.Font(None, 20)
            text = font.render("$", True, (0, 0, 0))
            self.image.blit(text, text.get_rect(center=self.image.get_rect().center))
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        self.sound_manager.play("bonus_reward") 
        player.money += self.amount

class MoneyBonus10(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 10)

class MoneyBonus50(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 50)

class MoneyBonus100(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 100)

class MoneyBonus200(MoneyBonus):
    def __init__(self, x, y):
        super().__init__(x, y, 200)

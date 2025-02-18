import pygame
import random
from src.utils.utils import load_image

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, speed=2):
        super().__init__()
        self.speed = speed
        self.rect = pygame.Rect(x, y, 20, 20)
        
    def update(self):
        self.rect.y += self.speed
        if self.rect.top > pygame.display.get_surface().get_height():
            self.kill()

class RankMarker(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.image = load_image("assets/bonuses/rank_marker.png", (0, 0, 0), (20, 20))
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 215, 0))  # Gold color
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        player.rank_markers.append(self)
        player.check_rank_upgrade()

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

class HealthBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.image = load_image("assets/bonuses/health.png", (0, 0, 0), (20, 20))
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 0, 0))  # Red
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        player.health = min(player.health + 20, 100)

class ShieldBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.image = load_image("assets/bonuses/shield.png", (0, 0, 0), (20, 20))
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((0, 0, 255))  # Blue
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        player.shield = min(player.shield + 20, 100)

class WeaponUpgrade(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y)
        try:
            self.image = load_image("assets/bonuses/weapon.png", (0, 0, 0), (20, 20))
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 255, 0))  # Yellow
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        player.primary_weapon = min(player.primary_weapon + 1, 7)

class LetterBonus(Bonus):
    def __init__(self, x, y, letter):
        super().__init__(x, y)
        self.letter = letter
        try:
            self.image = load_image(f"assets/bonuses/letter_{letter}.png", (0, 0, 0), (20, 20))
        except:
            self.image = pygame.Surface((20, 20))
            self.image.fill((128, 0, 128))  # Purple
            font = pygame.font.Font(None, 20)
            text = font.render(letter, True, (255, 255, 255))
            self.image.blit(text, text.get_rect(center=self.image.get_rect().center))
        self.rect = self.image.get_rect(center=(x, y))

    def apply(self, player):
        if self.letter not in player.letters:
            player.letters.append(self.letter) 
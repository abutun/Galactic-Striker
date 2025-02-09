# src/scoring.py
import pygame

class ScoreManager:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont(None, 30)

    def add_points(self, points):
        self.score += points

    def draw(self, screen):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        sw, _ = screen.get_size()
        text_rect = score_text.get_rect(topright=(sw - 10, 10))
        screen.blit(score_text, text_rect)

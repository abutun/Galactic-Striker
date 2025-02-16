import pygame
import logging

logger = logging.getLogger(__name__)

class ScoreManager:
    def __init__(self):
        self.score = 0
        self.high_score = self.load_high_score()
        self.multiplier = 1
        self.combo = 0
        self.combo_timer = 0
        self.combo_timeout = 2000  # 2 seconds to maintain combo

    def add_score(self, points):
        """Add points to the current score."""
        try:
            base_points = points * self.multiplier
            combo_bonus = int(base_points * (self.combo * 0.1))  # 10% bonus per combo level
            total_points = base_points + combo_bonus
            
            self.score += total_points
            self.combo += 1
            self.combo_timer = pygame.time.get_ticks()
            
            # Update high score if needed
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
                
            return total_points
        except Exception as e:
            logger.error(f"Error adding score: {e}")
            return 0

    def update(self):
        """Update score-related mechanics."""
        try:
            # Check combo timer
            now = pygame.time.get_ticks()
            if now - self.combo_timer > self.combo_timeout:
                self.combo = 0
        except Exception as e:
            logger.error(f"Error updating score: {e}")

    def reset(self):
        """Reset the current score."""
        self.score = 0
        self.multiplier = 1
        self.combo = 0
        self.combo_timer = 0

    def load_high_score(self):
        """Load high score from file."""
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except:
            return 0

    def save_high_score(self):
        """Save current high score to file."""
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except Exception as e:
            logger.error(f"Error saving high score: {e}")

    def draw(self, surface, x, y):
        """Draw score information."""
        try:
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            high_score_text = font.render(f"High Score: {self.high_score}", True, (255, 255, 255))
            
            if self.combo > 1:
                combo_text = font.render(f"Combo: x{self.combo}", True, (255, 255, 0))
                surface.blit(combo_text, (x, y + 60))
                
            surface.blit(score_text, (x, y))
            surface.blit(high_score_text, (x, y + 30))
        except Exception as e:
            logger.error(f"Error drawing score: {e}")

class ScoreMultiplier:
    def __init__(self):
        self.base_multiplier = 1.0
        self.combo_count = 0
        self.combo_timer = 0
        self.max_combo_time = 2.0  # seconds
        
    def update(self, dt):
        self.combo_timer -= dt
        if self.combo_timer <= 0:
            self.reset_combo()
            
    def add_hit(self):
        self.combo_count += 1
        self.combo_timer = self.max_combo_time
        return self.get_multiplier()
        
    def get_multiplier(self):
        return self.base_multiplier * (1 + self.combo_count * 0.1)

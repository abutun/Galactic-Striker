import pygame

class ScoreManager:
    def __init__(self):
        self.score = 0
        self.font = pygame.font.SysFont(None, 30)
        self.multiplier = 1
        self.multiplier_time = 0

    def add_points(self, points):
        self.score += points * self.multiplier

    def activate_multiplier(self, mult, duration):
        self.multiplier = mult
        self.multiplier_time = duration * 1000

    def update(self, dt):
        if self.multiplier_time > 0:
            self.multiplier_time -= dt
            if self.multiplier_time <= 0:
                self.multiplier = 1

    def draw(self, screen):
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        sw, _ = screen.get_size()
        text_rect = score_text.get_rect(topright=(sw - 10, 10))
        screen.blit(score_text, text_rect)

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

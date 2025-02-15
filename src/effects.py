import pygame
import random
import math

class EffectManager:
    def __init__(self):
        self.effects = pygame.sprite.Group()
        
    def add_explosion(self, x, y, size=1.0):
        ExplosionEffect(x, y, size, self.effects)
        
    def add_shield_hit(self, x, y):
        ShieldHitEffect(x, y, self.effects)
        
    def add_power_up_sparkle(self, x, y):
        PowerUpSparkle(x, y, self.effects)

class ExplosionEffect(pygame.sprite.Sprite):
    def __init__(self, x, y, size, group):
        super().__init__(group)
        self.particles = [(random.gauss(0, 1), random.gauss(0, 1)) 
                         for _ in range(20)]
        self.life = 30
        self.x = x
        self.y = y
        self.size = size
        
    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.kill()
            
    def draw(self, screen):
        for px, py in self.particles:
            pos = (self.x + px * (30 - self.life) * self.size, 
                  self.y + py * (30 - self.life) * self.size)
            pygame.draw.circle(screen, (255, 200, 50), 
                             (int(pos[0]), int(pos[1])), 
                             int(self.life / 5)) 
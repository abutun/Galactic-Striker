import pygame
import math

class LaserBeam:
    def __init__(self, player):
        self.player = player
        self.charge = 0
        self.max_charge = 100
        self.width = 5
        
    def update(self):
        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
            self.charge = min(self.charge + 1, self.max_charge)
            self.width = 5 + (self.charge / self.max_charge) * 20
        else:
            self.fire()
            
    def fire(self):
        if self.charge > 20:
            # Create powerful laser beam
            pass
            
class BlackHoleBomb:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 10
        self.lifetime = 5.0  # seconds
        self.affected_enemies = []
        
    def update(self, dt):
        self.lifetime -= dt
        for enemy in self.affected_enemies:
            # Pull enemies toward black hole
            dx = self.x - enemy.rect.centerx
            dy = self.y - enemy.rect.centery
            dist = math.sqrt(dx*dx + dy*dy)
            if dist > 0:
                force = 500 / (dist * dist)
                enemy.rect.x += dx * force * dt
                enemy.rect.y += dy * force * dt 
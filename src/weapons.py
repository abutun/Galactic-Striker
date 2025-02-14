import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, damage=1):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill((0, 255, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = vx
        self.vy = vy
        self.damage = damage

    def update(self):
        self.rect.x += self.vx
        self.rect.y += self.vy
        surface = pygame.display.get_surface()
        if surface:
            sw, sh = surface.get_size()
            # Kill the bullet if it moves off-screen.
            if self.rect.bottom < 0 or self.rect.top > sh or self.rect.right < 0 or self.rect.left > sw:
                self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, vy, damage=5):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = vy
        self.damage = damage

    def update(self):
        self.rect.y += self.vy
        surface = pygame.display.get_surface()
        if surface:
            _, sh = surface.get_size()
            if self.rect.bottom < 0 or self.rect.top > sh:
                self.kill()

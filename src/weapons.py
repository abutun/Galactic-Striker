import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, damage):
        super().__init__()
        # Make bullets larger and more visible
        self.image = pygame.Surface((8, 16), pygame.SRCALPHA)  # Transparent surface
        
        # Draw a more visible bullet
        if vy < 0:  # Player bullets
            pygame.draw.rect(self.image, (255, 255, 0), (0, 0, 8, 16))  # Yellow
            pygame.draw.rect(self.image, (255, 200, 0), (2, 12, 4, 4))  # Orange trail
        else:  # Enemy bullets
            pygame.draw.rect(self.image, (255, 0, 0), (0, 0, 8, 16))    # Red
            pygame.draw.rect(self.image, (255, 100, 100), (2, 0, 4, 4)) # Light red trail
        
        self.rect = self.image.get_rect(center=(x, y))
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.creation_time = pygame.time.get_ticks()
        self.max_lifetime = 5000  # 5 seconds max lifetime
        self.just_spawned = True  # Add this flag back

    def update(self):
        # Add bullet trail effect
        if self.vy < 0:  # Player bullets going up
            pygame.draw.line(self.image, (255, 200, 0), 
                           (3, 12), (3, 8), 2)  # Yellow trail
        else:  # Enemy bullets going down
            pygame.draw.line(self.image, (255, 100, 100), 
                           (3, 0), (3, 4), 2)  # Red trail
        
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        # Add lifetime check
        if pygame.time.get_ticks() - self.creation_time > self.max_lifetime:
            self.kill()
            return
            
        # Kill if off screen
        screen = pygame.display.get_surface()
        if screen:
            sw, sh = screen.get_size()
            if (self.rect.bottom < 0 or self.rect.top > sh or 
                self.rect.right < 0 or self.rect.left > sw):
                self.kill()

class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, vy, damage=5):
        super().__init__()
        self.image = pygame.Surface((10, 20))
        self.image.fill((255, 0, 255))
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = vy
        self.damage = damage
        self.just_spawned = True  # Add this flag for missiles too

    def update(self):
        self.rect.y += self.vy
        surface = pygame.display.get_surface()
        if surface:
            _, sh = surface.get_size()
            if self.rect.bottom < 0 or self.rect.top > sh:
                self.kill()

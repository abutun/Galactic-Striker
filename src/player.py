# src/player.py
import pygame
from weapons import Bullet, Missile
from utils import load_image

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group):
        super().__init__()
        self.image = load_image("assets/sprites/player.png", (0, 255, 0), (64, 64))
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.health = 3
        self.shield = 100
        self.weapon_level = 1
        self.fire_delay = 250  # milliseconds between primary shots
        self.last_fire = pygame.time.get_ticks()
        self.bullet_group = bullet_group

        # Variables for secondary (chargeable) missile attack
        self.missile_charge = 0
        self.missile_charging = False
        self.missile_charge_rate = 0.5  # charge units per frame
        self.missile_max_charge = 100

    def update(self):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed
        self.rect.x += dx
        self.rect.y += dy

        # Keep the player within screen bounds (640x800)
        self.rect.clamp_ip(pygame.Rect(0, 0, 640, 800))

        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE]:
            # If holding shift, charge the missile instead of auto-firing laser
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.missile_charging = True
                self.missile_charge += self.missile_charge_rate
                if self.missile_charge > self.missile_max_charge:
                    self.missile_charge = self.missile_max_charge
            else:
                # Auto-fire primary laser if enough time has passed
                if now - self.last_fire >= self.fire_delay:
                    self.fire_bullet()
                    self.last_fire = now
        else:
            if self.missile_charging:
                # On release, fire a charged missile
                self.fire_missile(self.missile_charge)
                self.missile_charge = 0
                self.missile_charging = False

    def fire_bullet(self):
        # Create a bullet moving upward; damage scales with weapon level
        bullet = Bullet(self.rect.centerx, self.rect.top, -10, damage=1 * self.weapon_level)
        self.bullet_group.add(bullet)

    def fire_missile(self, charge):
        # Fire a missile with damage based on the charge level
        missile = Missile(self.rect.centerx, self.rect.top, -8, damage=int(charge / 10))
        self.bullet_group.add(missile)

    def take_damage(self, damage):
        # Shields absorb damage first
        if self.shield > 0:
            self.shield -= damage * 10  # shield takes more damage per hit
            if self.shield < 0:
                self.health += self.shield // 10  # subtract remaining damage from health
                self.shield = 0
        else:
            self.health -= damage
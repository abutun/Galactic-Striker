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
        self.fire_delay = 250  # Milliseconds between shots.
        self.last_fire = pygame.time.get_ticks()
        self.bullet_group = bullet_group

        # Variables for the secondary (chargeable) missile attack.
        self.missile_charge = 0
        self.missile_charging = False
        self.missile_charge_rate = 0.5  # Charge units per frame.
        self.missile_max_charge = 100

    def update(self):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        dy = (keys[pygame.K_DOWN] - keys[pygame.K_UP]) * self.speed
        self.rect.x += dx
        self.rect.y += dy

        # Clamp the player within the current screen boundaries.
        surface = pygame.display.get_surface()
        if surface:
            sw, sh = surface.get_size()
            self.rect.clamp_ip(pygame.Rect(0, 0, sw, sh))

        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE]:
            # Hold SHIFT to charge a missile instead of firing lasers.
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                self.missile_charging = True
                self.missile_charge += self.missile_charge_rate
                if self.missile_charge > self.missile_max_charge:
                    self.missile_charge = self.missile_max_charge
            else:
                if now - self.last_fire >= self.fire_delay:
                    self.fire_bullet()
                    self.last_fire = now
        else:
            if self.missile_charging:
                self.fire_missile(self.missile_charge)
                self.missile_charge = 0
                self.missile_charging = False

    def fire_bullet(self):
        bullet = Bullet(self.rect.centerx, self.rect.top, -10, damage=1 * self.weapon_level)
        self.bullet_group.add(bullet)

    def fire_missile(self, charge):
        missile = Missile(self.rect.centerx, self.rect.top, -8, damage=int(charge / 10))
        self.bullet_group.add(missile)

    def take_damage(self, damage):
        # Shields absorb damage first.
        if self.shield > 0:
            self.shield -= damage * 10
            if self.shield < 0:
                self.health += self.shield // 10  # Remaining damage subtracts from health.
                self.shield = 0
        else:
            self.health -= damage

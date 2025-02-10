import pygame
from weapons import Bullet, Missile
from utils import load_image

RANK_NAMES = [
    "Ensign", "Lieutenant", "Commander", "Captain", "Admiral",
    "Admiral 1 Bronze Star", "Admiral 2 Bronze Star", "Admiral 3 Bronze Star",
    "Admiral 1 Silver Star", "Admiral 2 Silver Star", "Admiral 3 Silver Star",
    "Admiral 1 Gold Star", "Admiral 2 Gold Star", "Admiral 3 Gold Star",
    "Galactic Knight", "Galactic Lord", "Galactic Overlord", "Galactic Grandmaster",
    "Galactic Grandmaster 1 Gold Star", "Galactic Grandmaster 2 Gold Star", "Galactic Grandmaster 3 Gold Star",
    "Galactic Champion", "Galactic God",
    "Galactic Pluto Rank", "Galactic Neptune Rank", "Galactic Uranus Rank", "Galactic Saturn Rank",
    "Galactic Jupiter Rank", "Galactic Mars Rank", "Galactic Tellus Rank", "Galactic Venus Rank",
    "Galactic Mercury Rank", "Galactic Sol Rank"
]

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, bullet_group):
        super().__init__()
        self.image = load_image("assets/sprites/player.png", (0, 255, 0), (64, 64))
        self.base_image = self.image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.health = 3
        self.shield = 100
        self.weapon_level = 1
        self.shot_count = 1
        self.fire_delay = 250
        self.last_fire = pygame.time.get_ticks()
        self.bullet_group = bullet_group

        # Additional stats
        self.bullet_count = 1
        self.time_stat = 30
        self.bullet_speed = 10
        self.money = 0
        self.lives = 3
        self.armour = 0
        self.autofire = False
        self.shield_active = False
        self.scoop_active = False
        self.letters = []
        self.rank_markers = []
        self.rank = 1
        self.mirror_mode = False
        self.drunk_mode = False

        self.update_rank_marker()

    def update_rank_marker(self):
        self.image = self.base_image.copy()
        font = pygame.font.Font(None, 14)
        rank_text = RANK_NAMES[self.rank - 1]
        text_surface = font.render(rank_text, True, (255, 255, 255))
        self.image.blit(text_surface, (0, self.image.get_height() - text_surface.get_height()))

    def check_rank_upgrade(self):
        if len(self.rank_markers) >= 6:
            if self.rank < len(RANK_NAMES):
                self.rank += 1
            self.rank_markers = []
            self.update_rank_marker()

    def update(self):
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_RIGHT] - keys[pygame.K_LEFT]) * self.speed
        self.rect.x += dx

        surface = pygame.display.get_surface()
        if surface:
            sw, sh = surface.get_size()
            self.rect.clamp_ip(pygame.Rect(0, 0, sw, sh))

        now = pygame.time.get_ticks()
        if keys[pygame.K_SPACE]:
            if now - self.last_fire >= self.fire_delay:
                self.fire_bullet()
                self.last_fire = now

        self.check_rank_upgrade()

    def fire_bullet(self):
        spacing = 10
        count = self.shot_count
        start_x = self.rect.centerx - ((count - 1) * spacing) // 2
        for i in range(count):
            bullet = Bullet(start_x + i * spacing, self.rect.top, -self.bullet_speed, damage=1 * self.weapon_level)
            self.bullet_group.add(bullet)

    def fire_missile(self, charge):
        missile = Missile(self.rect.centerx, self.rect.top, -8, damage=int(charge / 10))
        self.bullet_group.add(missile)

    def take_damage(self, damage):
        if self.shield > 0:
            self.shield -= damage * 10
            if self.shield < 0:
                self.health += self.shield // 10
                self.shield = 0
        else:
            self.health -= damage

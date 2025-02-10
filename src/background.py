import pygame
from utils import load_image

class Background:
    def __init__(self, screen_width, screen_height, scroll_speed=1):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.scroll_speed = scroll_speed
        self.bg_image = load_image("assets/background/space_bg.png", (0, 0, 0), (screen_width, screen_height))
        self.y1 = 0
        self.y2 = -screen_height

        self.IS_MOBILE = False
        if not self.IS_MOBILE:
            self.border_width = int(screen_width * 0.15)
            self.left_border_image = load_image("assets/background/left_border.png", (30, 30, 30), (self.border_width, screen_height))
            self.right_border_image = load_image("assets/background/right_border.png", (30, 30, 30), (self.border_width, screen_height))
        else:
            self.border_width = 0
            self.left_border_image = None
            self.right_border_image = None

    def update(self):
        self.y1 += self.scroll_speed
        self.y2 += self.scroll_speed
        if self.y1 >= self.screen_height:
            self.y1 = self.y2 - self.screen_height
        if self.y2 >= self.screen_height:
            self.y2 = self.y1 - self.screen_height

    def draw(self, screen):
        sw, sh = screen.get_size()
        if self.left_border_image and self.right_border_image:
            play_area_x = self.border_width
            play_area_width = sw - 2 * self.border_width
            bg_image_scaled = pygame.transform.scale(self.bg_image, (play_area_width, sh))
        else:
            play_area_x = 0
            play_area_width = sw
            bg_image_scaled = self.bg_image

        screen.blit(bg_image_scaled, (play_area_x, self.y1))
        screen.blit(bg_image_scaled, (play_area_x, self.y2))

        if self.left_border_image and self.right_border_image:
            screen.blit(self.left_border_image, (0, 0))
            screen.blit(self.right_border_image, (sw - self.border_width, 0))

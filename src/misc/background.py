import pygame
from src.utils.utils import load_image
import random
from src.config.game_settings import PLAY_AREA

class Background:
    def __init__(self, width, height, scroll_speed=1):
        self.screen_width = width
        self.screen_height = height
        self.scroll_speed = scroll_speed
        self.border_width = int(width * PLAY_AREA["left_boundary"])  # Use same boundary for borders
        self.play_area_width = int(width * PLAY_AREA["width_percentage"])

        # Load or create main background
        try:
            self.bg_image = load_image("assets/background/space_bg.png", (0, 0, 0), (self.play_area_width, height))
        except:
            # Create a simple starfield background as fallback
            self.bg_image = pygame.Surface((self.play_area_width, height))
            self.bg_image.fill((0, 0, 40))  # Dark blue
            # Add some stars
            for _ in range(100):
                x = random.randint(0, self.play_area_width)
                y = random.randint(0, height)
                size = random.randint(1, 3)
                color = random.choice([(255, 255, 255), (200, 200, 255), (255, 255, 200)])
                pygame.draw.circle(self.bg_image, color, (x, y), size)

        # Load or create border images
        try:
            self.left_border = load_image("assets/background/left_border.png", (30, 30, 30), (self.border_width, height))
            self.right_border = load_image("assets/background/right_border.png", (30, 30, 30), (self.border_width, height))
        except:
            # Create simple gradient borders as fallback
            self.left_border = self._create_border_gradient(self.border_width, height, True)
            self.right_border = self._create_border_gradient(self.border_width, height, False)

        # Set up rectangles for positioning
        self.bg_rect1 = self.bg_image.get_rect(topleft=(self.border_width, 0))
        self.bg_rect2 = self.bg_image.get_rect(topleft=(self.border_width, -height))
        
        self.left_border_rect = self.left_border.get_rect(topleft=(0, 0))
        self.right_border_rect = self.right_border.get_rect(topleft=(width - self.border_width, 0))
        
        # Track position with floats for smooth scrolling
        self.y1 = float(self.bg_rect1.y)
        self.y2 = float(self.bg_rect2.y)

    def _create_border_gradient(self, width, height, is_left):
        """Create a gradient border as fallback."""
        surface = pygame.Surface((width, height))
        for x in range(width):
            alpha = 255 - int(255 * (x/width if is_left else (1 - x/width)))
            color = (20, 20, 40, alpha)
            pygame.draw.line(surface, color, (x, 0), (x, height))
        return surface

    def update(self):
        # Move both background images down
        self.y1 += self.scroll_speed
        self.y2 += self.scroll_speed
        
        # Update rectangle positions
        self.bg_rect1.y = int(self.y1)
        self.bg_rect2.y = int(self.y2)
        
        # Reset positions for seamless scrolling
        if self.bg_rect1.top >= self.screen_height:
            self.bg_rect1.bottom = self.bg_rect2.top
            self.y1 = float(self.bg_rect1.y)
        if self.bg_rect2.top >= self.screen_height:
            self.bg_rect2.bottom = self.bg_rect1.top
            self.y2 = float(self.bg_rect2.y)

    def draw(self, surface):
        # Draw scrolling background
        surface.blit(self.bg_image, self.bg_rect1)
        surface.blit(self.bg_image, self.bg_rect2)
        
        # Draw borders
        surface.blit(self.left_border, self.left_border_rect)
        surface.blit(self.right_border, self.right_border_rect)

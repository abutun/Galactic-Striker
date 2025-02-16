import math
import pygame
import os
import random
import sys
from typing import Tuple, List

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.game_settings import (
    ALIEN_SETTINGS
)

class AlienSpriteGenerator:
    def __init__(self):
        self.small_size = ALIEN_SETTINGS["small"]["size"]  # Get from game settings
        self.large_size = ALIEN_SETTINGS["large"]["size"]
        self.boss_size = ALIEN_SETTINGS["boss"]["size"]
        self.base_path = "assets/aliens"
        
        # Create base directory if it doesn't exist
        os.makedirs(self.base_path, exist_ok=True)
        
        # Store base colors for each alien type
        self.alien_colors = {}

    def generate_random_color(self) -> Tuple[int, int, int]:
        """Generate a random base color."""
        return (random.randint(50, 255), 
                random.randint(50, 255), 
                random.randint(50, 255))
    
    def get_variant_color(self, base_color: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Generate a variant of the base color."""
        return (min(255, base_color[0] + random.randint(-50, 50)),
                min(255, base_color[1] + random.randint(-50, 50)),
                min(255, base_color[2] + random.randint(-50, 50)))

    def generate_shape_points(self, size: Tuple[int, int], complexity: int) -> List[Tuple[int, int]]:
        """Generate random polygon points for alien shape."""
        points = []
        center_x, center_y = size[0] // 2, size[1] // 2
        
        for i in range(complexity):
            angle = (2 * math.pi * i) / complexity
            radius = random.uniform(0.3, 0.9) * min(size[0], size[1]) // 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            points.append((int(x), int(y)))
            
        return points

    def create_alien_sprite(self, type_num: int, size: Tuple[int, int], 
                          complexity: int) -> List[pygame.Surface]:
        """Create a unique alien sprite with two variants (for subtypes)."""
        sprites = []
        
        # Get or generate base color for this alien type
        if type_num not in self.alien_colors:
            self.alien_colors[type_num] = self.generate_random_color()
        base_color = self.alien_colors[type_num]
        
        # Generate shape points once to keep consistent shape
        points = self.generate_shape_points(size, complexity)
        
        # Create two variants with different colors (for subtypes 1 and 2)
        for subtype in range(2):
            surface = pygame.Surface(size, pygame.SRCALPHA)
            
            # Use base color for subtype 1, variant for subtype 2
            color = base_color if subtype == 0 else self.get_variant_color(base_color)
            
            # Draw base shape (same for both subtypes)
            pygame.draw.polygon(surface, color, points)
            
            # Add details based on type
            if type_num <= 25:  # Regular aliens
                # Add circular elements
                radius = min(size) // 6
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (size[0]//4, size[1]//4), radius)
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (3*size[0]//4, size[1]//4), radius)
                
                # Add some variation in the details based on subtype
                detail_color = (255, 255, 255) if subtype == 0 else color
                pygame.draw.line(surface, detail_color,
                               (size[0]//2, size[1]//3),
                               (size[0]//2, 2*size[1]//3), 2)
            else:  # Boss aliens
                # Boss-specific details
                pygame.draw.polygon(surface, (255, 255, 255), [
                    (size[0]//4, size[1]//4),
                    (size[0]//3, size[1]//3),
                    (size[0]//4, size[1]//3)
                ])
            
            sprites.append(surface)
        
        return sprites

    def generate_all_aliens(self):
        """Generate all alien types with animation frames."""
        pygame.init()
        
        # Generate regular aliens (25 types, 2 sizes, 2 subtypes each)
        for type_num in range(1, 26):
            # Generate base shape and color for this type
            if type_num not in self.alien_colors:
                self.alien_colors[type_num] = self.generate_random_color()
            
            # Small aliens
            for subtype in [1, 2]:  # Generate for both subtypes
                sprites = self.create_alien_sprite(type_num, self.small_size, 6)
                filename = f"alien_{type_num:02d}_small_{subtype:02d}.png"
                pygame.image.save(sprites[subtype-1], 
                                os.path.join(self.base_path, filename))

            # Large aliens (same shape as small, different size)
            for subtype in [1, 2]:  # Generate for both subtypes
                sprites = self.create_alien_sprite(type_num, self.large_size, 6)
                filename = f"alien_{type_num:02d}_large_{subtype:02d}.png"
                pygame.image.save(sprites[subtype-1], 
                                os.path.join(self.base_path, filename))

        # Generate boss aliens (25 types)
        for boss_num in range(1, 26):
            sprite = self.create_alien_sprite(boss_num, self.boss_size, 12)[0]
            filename = f"boss_{boss_num:02d}.png"
            pygame.image.save(sprite, os.path.join(self.base_path, filename))

        pygame.quit()

if __name__ == "__main__":
    generator = AlienSpriteGenerator()
    generator.generate_all_aliens() 
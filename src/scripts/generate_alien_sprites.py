import math
import pygame
import os
import random
from typing import Tuple, List

class AlienSpriteGenerator:
    def __init__(self):
        self.small_size = (32, 32)
        self.large_size = (64, 64)
        self.boss_size = (128, 128)
        self.base_path = "assets/aliens"
        
        # Create base directory if it doesn't exist
        os.makedirs(self.base_path, exist_ok=True)

    def generate_random_color(self) -> Tuple[int, int, int]:
        return (random.randint(50, 255), 
                random.randint(50, 255), 
                random.randint(50, 255))

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
        """Create a unique alien sprite with animation frames."""
        sprites = []
        
        for frame in range(2):  # Generate 2 frames for animation
            surface = pygame.Surface(size, pygame.SRCALPHA)
            color = self.generate_random_color()
            
            # Create base shape
            points = self.generate_shape_points(size, complexity)
            pygame.draw.polygon(surface, color, points)
            
            # Add details based on type and frame
            if type_num <= 25:
                # Add circular elements
                radius = min(size) // 6
                offset = frame * 2  # Slight movement for animation
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (size[0]//4 + offset, size[1]//4), radius)
                pygame.draw.circle(surface, (255, 255, 255), 
                                 (3*size[0]//4 - offset, size[1]//4), radius)
            else:
                # Add angular elements with animation
                offset = frame * 3
                pygame.draw.polygon(surface, (255, 255, 255), [
                    (size[0]//4 + offset, size[1]//4),
                    (size[0]//3 + offset, size[1]//3),
                    (size[0]//4 + offset, size[1]//3)
                ])
            
            sprites.append(surface)
        
        return sprites

    def generate_all_aliens(self):
        """Generate all alien types with animation frames."""
        pygame.init()
        
        # Generate regular aliens (25 types, 2 sizes, 2 frames each)
        for type_num in range(1, 26):
            # Small aliens
            sprites = self.create_alien_sprite(type_num, self.small_size, 6)
            for frame in range(1, 3):
                filename = f"alien_{type_num:02d}_small_{frame}.png"
                pygame.image.save(sprites[frame-1], 
                                os.path.join(self.base_path, filename))

            # Large aliens
            sprites = self.create_alien_sprite(type_num, self.large_size, 8)
            for frame in range(1, 3):
                filename = f"alien_{type_num:02d}_large_{frame}.png"
                pygame.image.save(sprites[frame-1], 
                                os.path.join(self.base_path, filename))

        # Generate boss aliens (25 types)
        for boss_num in range(1, 26):
            sprite = self.create_alien_sprite(boss_num, self.boss_size, 12)[0]  # Just use first frame for bosses
            filename = f"boss_{boss_num:02d}.png"
            pygame.image.save(sprite, os.path.join(self.base_path, filename))

        pygame.quit()

if __name__ == "__main__":
    generator = AlienSpriteGenerator()
    generator.generate_all_aliens() 
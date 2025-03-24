import math
from venv import logger
import pygame

from src.config.game_settings import ALIEN_SETTINGS
from src.enemy.alien import NonBossAlien

class LevelManager:
    def calculate_formation_positions(self, formation, count, spacing):
        """Calculate positions for alien formation with proper spacing."""
        positions = []
        
        # Get alien size from settings (default to 32 if not found)
        alien_size = ALIEN_SETTINGS.get("size", (32, 32))
        # Add 20% buffer between ships
        min_spacing = max(alien_size[0], alien_size[1]) * 1.2
        
        try:
            if formation == "line":
                for i in range(count):
                    x = i * (min_spacing + spacing)  # Add configured spacing to minimum
                    y = 0
                    positions.append((x, y))
            
            elif formation == "v":
                mid = count // 2
                for i in range(count):
                    x = (i - mid) * (min_spacing + spacing)
                    y = abs(i - mid) * (min_spacing + spacing)
                    positions.append((x, y))
            
            elif formation == "circle":
                # Increase radius based on ship size
                radius = (count * (min_spacing + spacing)) / (2 * math.pi)
                for i in range(count):
                    angle = (2 * math.pi * i) / count
                    x = math.cos(angle) * radius
                    y = math.sin(angle) * radius
                    positions.append((x, y))
            
            elif formation == "diamond":
                size = math.ceil(math.sqrt(count))
                curr = 0
                for row in range(size):
                    cols = min(size - abs(row - size//2), count - curr)
                    for col in range(cols):
                        x = (col - cols//2) * (min_spacing + spacing)
                        y = row * (min_spacing + spacing)
                        positions.append((x, y))
                        curr += 1
                        if curr >= count:
                            break
                    if curr >= count:
                        break
                    
            elif formation == "wave":
                wavelength = (min_spacing + spacing) * 4
                for i in range(count):
                    x = i * (min_spacing + spacing)
                    y = math.sin(i * 2 * math.pi / wavelength) * (min_spacing + spacing) * 2
                    positions.append((x, y))
                
            elif formation == "cross":
                arm_length = math.ceil(count / 4)
                curr = 0
                # Vertical arm
                for i in range(-arm_length, arm_length + 1):
                    if curr >= count:
                        break
                    positions.append((0, i * (min_spacing + spacing)))
                    curr += 1
                # Horizontal arm
                for i in range(-arm_length, arm_length + 1):
                    if i == 0 or curr >= count:
                        continue
                    positions.append((i * (min_spacing + spacing), 0))
                    curr += 1
                
            elif formation == "spiral":
                a = (min_spacing + spacing) / (2 * math.pi)
                curr = 0
                theta = 0
                while curr < count:
                    r = a * theta
                    x = r * math.cos(theta)
                    y = r * math.sin(theta)
                    positions.append((x, y))
                    theta += 0.5
                    curr += 1
                
            elif formation == "star":
                points = 5
                inner_radius = (min_spacing + spacing) * 2
                outer_radius = (min_spacing + spacing) * 4
                vertices_per_point = max(1, count // (points * 2))
                curr = 0
                
                for i in range(points * 2):
                    if curr >= count:
                        break
                    radius = outer_radius if i % 2 == 0 else inner_radius
                    angle = (i * math.pi) / points
                    
                    for j in range(vertices_per_point):
                        if curr >= count:
                            break
                        t = j / vertices_per_point
                        next_radius = inner_radius if i % 2 == 0 else outer_radius
                        next_angle = ((i + 1) * math.pi) / points
                        r = radius * (1 - t) + next_radius * t
                        a = angle * (1 - t) + next_angle * t
                        x = r * math.cos(a)
                        y = r * math.sin(a)
                        positions.append((x, y))
                        curr += 1

            # Center all formations around (0,0)
            if positions:
                center_x = sum(x for x, _ in positions) / len(positions)
                center_y = sum(y for _, y in positions) / len(positions)
                positions = [(x - center_x, y - center_y) for x, y in positions]

            return positions

        except Exception as e:
            logger.error(f"Error calculating formation positions: {e}")
            # Fallback to simple line formation with proper spacing
            return [(i * (min_spacing + spacing), 0) for i in range(count)]

    def spawn_next_group(self):
        """Spawn the next group of aliens with proper spacing."""
        if not self.level_data or not self.level_data.alien_groups:
            return
        
        try:
            group = self.level_data.alien_groups.pop(0)
            positions = self.calculate_formation_positions(group.formation, group.count, group.spacing)
            
            # Adjust positions based on screen size and entry point
            screen = pygame.display.get_surface()
            if not screen:
                return
            
            sw, sh = screen.get_size()
            base_x = sw // 2
            base_y = -50
            
            # Create aliens with adjusted positions
            aliens = []
            for pos in positions:
                x = base_x + pos[0]
                y = base_y + pos[1]
                
                alien = NonBossAlien(
                    len(aliens),
                    x, y,
                    self.bullet_group,
                    group.alien_type
                )
                
                self.enemy_group.add(alien)
                self.sprite_group.add(alien)
                aliens.append(alien)
                
            self.active_groups.append({
                "aliens": aliens,
                "pattern": group.movement_pattern,
                "formation": group.formation
            })
            
        except Exception as e:
            logger.error(f"Error spawning alien group: {e}") 
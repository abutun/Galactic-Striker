import os
import json
import pygame
from src.enemy.alien import NonBossAlien, BossAlien
from src.level.level_data import *
import logging
from src.config.game_settings import MOVEMENT_PATTERNS

logger = logging.getLogger(__name__)


def load_level_json(level_number):
    filename = os.path.join("assets", "levels", f"{level_number:03d}.json")
    with open(filename, "r") as f:
        return json.load(f)


class LevelManager:
    def __init__(self, level_number, enemy_group, all_sprites, enemy_bullets):
        self.level_data = None
        self.enemy_group = enemy_group
        self.all_sprites = all_sprites
        self.enemy_bullets = enemy_bullets
        self.active_groups = []
        
        # Load level data
        self.load_level(level_number)  # Make sure we call load_level
        
        # Spawn first group of aliens
        if self.level_data:
            self.spawn_next_group()  # Spawn initial group

    def json_to_level_data(self, data) -> LevelData:
        """Convert JSON data to LevelData object."""
        try:
            alien_groups = []
            for group_data in data.get('alien_groups', []):
                path_points = [
                    PathPoint(p['x'], p['y'], p.get('wait_time', 0), p.get('shoot', False))
                    for p in group_data.get('path', [])
                ]
                
                group = AlienGroup(
                    alien_type=group_data['alien_type'],
                    count=group_data['count'],
                    formation=group_data['formation'],
                    spacing=group_data['spacing'],
                    entry_point=EntryPoint(group_data['entry_point']),
                    path=path_points,
                    movement_pattern=MovementPattern(group_data['movement_pattern']),
                    speed=group_data['speed'],
                    health=group_data['health'],
                    shoot_interval=group_data['shoot_interval'],
                    group_behavior=group_data.get('group_behavior', False)
                )
                alien_groups.append(group)

            return LevelData(
                level_number=data['level_number'],
                name=data['name'],
                difficulty=data['difficulty'],
                alien_groups=alien_groups,
                boss_data=data.get('boss_data'),
                background_speed=data.get('background_speed', 1.0),
                music_track=data.get('music_track'),
                special_effects=data.get('special_effects', [])
            )
        except Exception as e:
            logger.error(f"Error converting JSON to LevelData: {e}")
            raise

    def load_level(self, level_number):
        try:
            with open(f"assets/levels/{level_number:03d}.json", "r") as f:
                data = json.load(f)
                self.level_data = self.json_to_level_data(data)
        except FileNotFoundError:
            logger.error(f"Level {level_number} not found!")
            self.level_data = None
        except Exception as e:
            logger.error(f"Error loading level {level_number}: {e}")
            self.level_data = None

    def spawn_next_group(self):
        if not self.level_data or not self.level_data.alien_groups:
            return

        try:
            group = self.level_data.alien_groups.pop(0)
            aliens = []

            # Calculate formation positions
            positions = self.calculate_formation_positions(
                group.formation, 
                group.count, 
                group.spacing
            )

            # Create aliens above the screen
            screen = pygame.display.get_surface()
            start_y = -50  # Start above screen
            
            # Adjust start position based on entry point
            if group.entry_point == EntryPoint.TOP:
                start_x = screen.get_width() // 2
            elif group.entry_point == EntryPoint.TOP_LEFT:
                start_x = screen.get_width() * 0.2
            elif group.entry_point == EntryPoint.TOP_RIGHT:
                start_x = screen.get_width() * 0.8
            else:
                start_x = screen.get_width() // 2

            # Create aliens
            for pos in positions:
                alien = NonBossAlien(
                    start_x + pos[0], start_y + pos[1],  # Offset from start position
                    self.enemy_bullets,
                    group.alien_type
                )
                # Set additional properties
                alien.shoot_interval = group.shoot_interval
                alien.path = [
                    (p.x * screen.get_width(),
                     p.y * screen.get_height())
                    for p in group.path
                ]
                aliens.append(alien)

            self.active_groups.append({
                "aliens": aliens,
                "pattern": group.movement_pattern,
                "group_behavior": group.group_behavior
            })

            # Add aliens to sprite groups
            for alien in aliens:
                self.enemy_group.add(alien)
                self.all_sprites.add(alien)
        except Exception as e:
            logger.error(f"Error spawning alien group: {e}")

    def calculate_formation_positions(self, formation, count, spacing):
        positions = []
        screen = pygame.display.get_surface()
        center_x = screen.get_width() // 2

        try:
            if formation == "line":
                total_width = (count - 1) * spacing
                start_x = center_x - (total_width // 2)
                for i in range(count):
                    positions.append((start_x + i * spacing, -50))

            elif formation == "v":
                for i in range(count):
                    x = center_x + (i // 2 * spacing if i % 2 == 0 else -(i // 2 + 1) * spacing)
                    y = -50 + (i // 2 * spacing)
                    positions.append((x, y))

            elif formation == "circle":
                import math
                radius = spacing * count / (2 * math.pi)
                for i in range(count):
                    angle = (2 * math.pi * i) / count
                    x = center_x + radius * math.cos(angle)
                    y = -50 + radius * math.sin(angle)
                    positions.append((x, y))
        except Exception as e:
            logger.error(f"Error calculating formation positions: {e}")
            # Return a simple line formation as fallback
            return [(center_x + i * 50, -50) for i in range(count)]

        return positions

    def update(self):
        try:
            # Update active groups
            for group in self.active_groups[:]:
                aliens_alive = [a for a in group["aliens"] if a.alive()]
                
                if not aliens_alive:
                    self.active_groups.remove(group)
                    self.spawn_next_group()
                    continue

                if group["group_behavior"]:
                    # Update group movement pattern
                    self.update_group_pattern(aliens_alive, group["pattern"])

            # Check if level is complete
            if not self.active_groups and not self.level_data.alien_groups:
                return True
            return False
        except Exception as e:
            logger.error(f"Error updating level: {e}")
            return False

    def update_group_pattern(self, aliens, pattern):
        try:
            if pattern == MovementPattern.SWARM:
                # Implement swarm behavior
                pass
            elif pattern == MovementPattern.WAVE:
                # Implement wave behavior
                pass
            # Add other patterns...
        except Exception as e:
            logger.error(f"Error updating group pattern: {e}")

    def is_level_complete(self):
        return not self.active_groups and not self.level_data.alien_groups

    def load_next_level(self, next_level_number):
        self.level_number = next_level_number
        self.load_level(next_level_number)
        self.start_time = pygame.time.get_ticks()

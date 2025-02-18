import os
import json
import pygame
from src.enemy.alien import NonBossAlien, BossAlien
from src.level.level_data import *
import logging
from src.config.game_settings import MOVEMENT_PATTERNS
from typing import List, Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


def load_level_json(level_number):
    filename = os.path.join("assets", "levels", f"{level_number:03d}.json")
    with open(filename, "r") as f:
        return json.load(f)


@dataclass
class LevelData:
    level_number: int
    name: str
    difficulty: int
    alien_groups: List[Dict]  # Changed from enemy_formations
    boss_data: Optional[Dict] = None
    background_speed: float = 1.0
    music_track: Optional[str] = None
    special_effects: List[str] = None
    power_up_frequency: float = 0.2
    minimum_clear_time: float = 30.0


class LevelManager:
    def __init__(self, start_level: int, enemy_group, sprite_group, bullet_group):
        self.current_level = start_level
        self.enemy_group = enemy_group
        self.sprite_group = sprite_group
        self.bullet_group = bullet_group
        self.active_groups = []
        self.level_data = self._load_level_data(start_level)
        self.formation_index = 0
        self.level_complete = False
        self.level_transition_time = 2000  # 2 seconds between levels
        self.last_level_time = 0

        if not self.level_data:
            raise ValueError(f"Could not load level {start_level}")

    def _load_level_data(self, level_number: int) -> LevelData:
        try:
            logger.info(f"Loading level {level_number} data")
            with open(f"assets/levels/{level_number:03d}.json") as f:
                data = json.load(f)
                return LevelData(
                    level_number=level_number,
                    name=data.get('name', f'Level {level_number}'),
                    difficulty=data.get('difficulty', 1),
                    alien_groups=data.get('alien_groups', []),
                    boss_data=data.get('boss_data'),
                    background_speed=data.get('background_speed', 1.0),
                    music_track=data.get('music_track'),
                    special_effects=data.get('special_effects', []),
                    power_up_frequency=data.get('power_up_frequency', 0.2),
                    minimum_clear_time=data.get('minimum_clear_time', 30.0)
                )
        except FileNotFoundError:
            logger.error(f"Level {level_number} data not found")
            return None
        except Exception as e:
            logger.error(f"Error loading level {level_number}: {e}")
            return None

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

    def spawn_next_group(self) -> None:
        """Spawn the next group of aliens."""
        logger.info(f"Spawning next group")
        if not self.level_data or not self.level_data.alien_groups:
            logger.info(f"No more alien groups to spawn")
            return

        try:
            group = self.level_data.alien_groups.pop(0)
            logger.info(f"Spawning alien group: type={group['alien_type']}, count={group['count']}")

            # Get alien type and id
            parts = group['alien_type'].split('_')
            type = parts[0]
            id = parts[1]

            # Calculate formation positions
            positions = self.calculate_formation_positions(
                group['formation'], 
                group['count'], 
                group['spacing']
            )

            # Create aliens with adjusted positions
            aliens = []
            if type == "alien":
                alien_type = parts[2]
                alien_subtype = parts[3]
                for pos in positions:
                    alien = NonBossAlien(
                        id, 
                        x=pos[0],  # X position from formation
                        y=pos[1],  # Y position from formation
                        bullet_group=self.bullet_group,                        
                        alien_type=alien_type,
                        alien_subtype=alien_subtype
                        )
                    # Set additional properties
                    alien.health = group.get('health', 1)
                    alien.speed = group.get('speed', 2)
                    alien.sound_manager = self.sound_manager
                    
                    self.enemy_group.add(alien)
                    self.sprite_group.add(alien)
                    aliens.append(alien)
            elif type == "boss":
                boss = BossAlien(
                    id, 
                    pos[0], 
                    pos[1],
                    self.bullet_group
                )
                boss.health = group['health']
                boss.speed = group['speed']
                boss.sound_manager = self.sound_manager
                
                self.enemy_group.add(boss)
                self.sprite_group.add(boss)
                aliens.append(boss)                

            self.active_groups.append({
                "aliens": aliens,
                "pattern": group['movement_pattern'],
                "group_behavior": group.get('group_behavior', False)
            })
                
        except Exception as e:
            logger.error(f"Error spawning alien group 0x0002: {e}")

    def calculate_formation_positions(self, formation, count, spacing):
        positions = []
        screen = pygame.display.get_surface()
        center_x = screen.get_width() // 2

        try:
            if formation == MovementPattern.STRAIGHT:
                total_width = (count - 1) * spacing
                start_x = center_x - (total_width // 2)
                for i in range(count):
                    positions.append((start_x + i * spacing, -50))

            elif formation == MovementPattern.ZIGZAG:
                for i in range(count):
                    x = center_x + (i // 2 * spacing if i % 2 == 0 else -(i // 2 + 1) * spacing)
                    y = -50 + (i // 2 * spacing)
                    positions.append((x, y))

            elif formation == MovementPattern.CIRCULAR:
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
        """Update level state"""
        try:
            # Update active groups
            for group in self.active_groups[:]:
                aliens_alive = [a for a in group["aliens"] if a.alive()]
                
                if not aliens_alive:
                    self.active_groups.remove(group)
                    self.spawn_next_group()
                    continue

                if group["group_behavior"]:
                    self.update_group_pattern(aliens_alive, group["pattern"])

            # Check if level is complete
            if not self.active_groups and not self.level_data.alien_groups:
                self.level_complete = True

        except Exception as e:
            logger.error(f"Error updating level: {e}")

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

    def load_next_level(self):
        """Load the next level"""
        self.current_level += 1
        logger.info(f"Loading next level: {self.current_level}")
        self.level_data = self._load_level_data(self.current_level)
        self.level_complete = False
        self.active_groups = []
        
        # Spawn first group of new level
        if self.level_data and self.level_data.alien_groups:
            self.spawn_next_group()
        else:
            logger.error(f"Failed to load level {self.current_level}")

    def spawn_alien_group(self, group_data):
        """Spawn a group of aliens according to formation and entry point."""
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()
        
        # Adjust entry points to always start from top
        entry_points = {
            "top_left": (screen_width * 0.2, -50),
            "top_center": (screen_width * 0.5, -50),
            "top_right": (screen_width * 0.8, -50),
            "left_top": (screen_width * 0.1, 50),
            "right_top": (screen_width * 0.9, 50)
        }
        
        # Get entry position
        entry_point = group_data.get("entry_point", "top_center")
        base_x, base_y = entry_points[entry_point]

        # Calculate positions for each alien
        positions = []
        for i in range(group_data["count"]):
            x = base_x + i * group_data["spacing"]
            y = base_y
            positions.append((x, y))

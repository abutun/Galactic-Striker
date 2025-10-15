import os
import json
import pygame
from src.enemy.alien import NonBossAlien, BossAlien
from src.level.level_data import *
import logging
from src.config.game_settings import MOVEMENT_PATTERNS, PLAY_AREA, ALIEN_SETTINGS
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import math
import random

from src.utils.resource_preloader import ResourcePreloader

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
        self.preloader = ResourcePreloader()
        self.formation_index = 0
        self.level_complete = False
        self.level_transition_time = 3000  # 3 seconds between levels
        self.last_level_time = 0
        
        # Add group spawn delay properties
        self.group_spawn_delay = 4000  # 4 seconds between groups
        self.last_group_cleared_time = 0
        self.next_group_pending = False

        # preload first level data
        self.preloader.preload_level_resources(self.level_data)

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
                    movement_pattern=Movement(group_data['movement_pattern']),
                    speed=group_data['speed'],
                    life=group_data['life'],
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

    def reset_level(self, level_number: Optional[int] = None) -> None:
        """Reload the current level data so groups can be spawned again."""
        target_level = self.current_level if level_number is None else level_number
        if level_number is not None:
            self.current_level = level_number

        self.level_data = self._load_level_data(target_level)
        self.active_groups = []
        self.level_complete = False
        self.next_group_pending = False
        self.last_group_cleared_time = pygame.time.get_ticks()

        if self.level_data:
            self.preloader.clear_cache()
            self.preloader.preload_level_resources(self.level_data)

    def spawn_next_group(self) -> None:
        """Spawn the next group of aliens."""
        logger.info(f"Spawning next group")
        if not self.level_data or not self.level_data.alien_groups:
            logger.info(f"No more alien groups to spawn")
            return

        try:
            screen = pygame.display.get_surface()
            if not screen:
                return
            sw, sh = screen.get_size()
            group = self.level_data.alien_groups.pop(0)

            logger.info(f"Spawning alien group: type={group['alien_type']}, entry={group['entry_point']}, count={group['count']}")

            enttry_point = EntryPoint[group['entry_point'].upper()]

            # Get alien type and id
            parts = group['alien_type'].split('_')
            type = parts[0]
            id = parts[1]

            # Calculate formation positions relative to play area
            raw_positions = self.calculate_formation_positions(
                group['formation'],
                group['count'],
                group['spacing']
            )

            left_boundary = int(sw * PLAY_AREA.get("left_boundary", 0.115))
            right_boundary = int(sw * PLAY_AREA.get("right_boundary", 0.885))
            play_width = right_boundary - left_boundary
            max_alien_width = max(ALIEN_SETTINGS["small"]["size"][0], ALIEN_SETTINGS["large"]["size"][0])
            max_alien_height = max(ALIEN_SETTINGS["small"]["size"][1], ALIEN_SETTINGS["large"]["size"][1])
            spawn_offset = max_alien_height + 40

            entry_offsets = {
                EntryPoint.TOP_CENTER: 0.0,
                EntryPoint.TOP_LEFT: -play_width * 0.25,
                EntryPoint.TOP_RIGHT: play_width * 0.25,
                EntryPoint.LEFT_TOP: -play_width * 0.35,
                EntryPoint.RIGHT_TOP: play_width * 0.35,
            }
            horizontal_offset = entry_offsets.get(enttry_point, 0.0)

            positions = []
            for px, py in raw_positions:
                x = px + horizontal_offset
                min_x = left_boundary + max_alien_width // 2
                max_x = right_boundary - max_alien_width // 2
                x = max(min_x, min(max_x, x))
                y = py - spawn_offset
                positions.append((x, y))

            path_points = []
            if group.get('path'):
                for point in group['path']:
                    target_x = left_boundary + float(point.get('x', 0.0)) * play_width
                    target_y = max(0.0, float(point.get('y', 0.0))) * sh
                    path_points.append((target_x, target_y))
            
            # Create aliens with adjusted positions
            aliens = []
            if type == "alien":
                alien_type = parts[2]
                alien_subtype = parts[3]
                animation = self.preloader.get_alien_animation(id, alien_type, alien_subtype)
                for pos in positions:
                    alien = NonBossAlien(
                        id, 
                        x=pos[0],  # X position from formation
                        y=pos[1],  # Y position from formation
                        bullet_group=self.bullet_group,
                        alien_type=alien_type,
                        alien_subtype=alien_subtype,
                        animation=animation
                        )
                    # Set additional properties
                    alien.life = group.get('life', 1)
                    alien.speed = group.get('speed', 2)
                    alien.sound_manager = self.sound_manager
                    alien.base_x = pos[0]
                    alien.base_y = pos[1]
                    if path_points:
                        alien.path = list(path_points)
                        alien.path_index = 0
                    
                    self.enemy_group.add(alien)
                    self.sprite_group.add(alien)
                    aliens.append(alien)
            elif type == "boss":
                animation = self.preloader.get_boss_animation(id)
                boss_x, boss_y = positions[0] if positions else (sw // 2, base_y)
                boss = BossAlien(
                    id, 
                    boss_x,
                    boss_y,
                    self.bullet_group,
                    animation=animation
                )
                boss.life = group['life']
                boss.speed = group['speed']
                boss.sound_manager = self.sound_manager
                boss.base_x = boss_x
                boss.base_y = boss_y
                if path_points:
                    boss.path = list(path_points)
                    boss.path_index = 0

                self.enemy_group.add(boss)
                self.sprite_group.add(boss)
                aliens.append(boss)                

            self.active_groups.append({
                "aliens": aliens,
                "pattern": group['movement_pattern'],
                "group_behavior": group.get('group_behavior', False)
            })

            logger.info(f"Spawned alien group: type={type}, count={len(aliens)}, entry={enttry_point.value}")    
                
        except Exception as e:
            logger.error(f"Error spawning alien group 0x0002: {e}")

    def calculate_formation_positions(self, pattern: str, count: int, spacing: int = 50) -> List[Tuple[float, float]]:
        """Calculate positions for a formation pattern."""
        formation = Formation[pattern.upper()]
        logger.info(f"Calculating formation: {formation} for {count} aliens")        
        try:
            screen = pygame.display.get_surface()
            if not screen:
                return []
                
            sw, sh = screen.get_size()
            
            # Define play area boundaries from game settings
            left_boundary = int(sw * PLAY_AREA.get("left_boundary", 0.115))
            right_boundary = int(sw * PLAY_AREA.get("right_boundary", 0.885))
            play_width = right_boundary - left_boundary
            max_alien_width = max(ALIEN_SETTINGS["small"]["size"][0], ALIEN_SETTINGS["large"]["size"][0])
            
            # Calculate base positions
            positions = []
            
            if formation == Formation.LINE:
                # Line formation within boundaries
                total_width = (count - 1) * spacing
                start_x = left_boundary + (play_width - total_width) / 2
                for i in range(count):
                    x = start_x + (i * spacing)
                    positions.append((x, -50))
                    
            elif formation == Formation.V:
                # V formation within boundaries
                total_width = (count - 1) * spacing
                start_x = left_boundary + (play_width - total_width) / 2
                for i in range(count):
                    x = start_x + (i * spacing)
                    y = -50 + (abs(i - (count-1)/2) * spacing)
                    positions.append((x, y))
                    
            elif formation == Formation.CIRCLE:
                # Circle formation within boundaries
                radius = min(play_width, sh * 0.3) / 2
                center_x = left_boundary + play_width / 2
                for i in range(count):
                    angle = (2 * math.pi * i) / count
                    x = center_x + radius * math.cos(angle)
                    y = -50 + radius * math.sin(angle)
                    positions.append((x, y))
                    
            elif formation == Formation.DIAMOND:
                # Diamond formation within boundaries
                total_width = (count - 1) * spacing
                start_x = left_boundary + (play_width - total_width) / 2
                for i in range(count):
                    x = start_x + (i * spacing)
                    y = -50 + (abs(i - (count-1)/2) * spacing)
                    positions.append((x, y))
                    
            elif formation == Formation.WAVE:
                # Wave formation within boundaries
                total_width = (count - 1) * spacing
                start_x = left_boundary + (play_width - total_width) / 2
                for i in range(count):
                    x = start_x + (i * spacing)
                    y = -50 + math.sin(i * 0.5) * spacing
                    positions.append((x, y))
                    
            elif formation == Formation.CROSS:
                # Cross formation within boundaries
                center_x = left_boundary + play_width / 2
                for i in range(count):
                    if i % 2 == 0:
                        x = center_x
                        y = -50 + (i // 2) * spacing
                    else:
                        x = center_x + ((i // 2 + 1) * spacing)
                        y = -50
                    positions.append((x, y))
                    
            elif formation == Formation.SPIRAL:
                # Spiral formation within boundaries
                center_x = left_boundary + play_width / 2
                for i in range(count):
                    angle = i * 0.5
                    radius = i * spacing / 10
                    x = center_x + radius * math.cos(angle)
                    y = -50 + radius * math.sin(angle)
                    positions.append((x, y))
                    
            elif formation == Formation.STAR:
                # Star formation within boundaries
                center_x = left_boundary + play_width / 2
                for i in range(count):
                    angle = (2 * math.pi * i) / count
                    radius = spacing * (1 + math.sin(angle * 5) * 0.5)
                    x = center_x + radius * math.cos(angle)
                    y = -50 + radius * math.sin(angle)
                    positions.append((x, y))
                    
            else:
                logger.warning(f"Unknown formation pattern: {pattern}")
                return []
                
            # Ensure all positions are within boundaries
            for i, (x, y) in enumerate(positions):
                positions[i] = (
                    max(left_boundary + max_alien_width // 2, min(right_boundary - max_alien_width // 2, x)), y
                )
                
            return positions
            
        except Exception as e:
            logger.error(f"Error calculating formation positions: {e}")
            return []

    def update_group_pattern(self, aliens: List[pygame.sprite.Sprite], pattern: Movement) -> None:
        """Update alien positions based on movement pattern."""
        movement = Movement[pattern.upper()]
    
        try:
            screen = pygame.display.get_surface()
            if not screen:
                return
            
            sw, sh = screen.get_size()
            time = pygame.time.get_ticks() / 1000.0
            
            # Define play area boundaries from game settings
            left_boundary = int(sw * PLAY_AREA.get("left_boundary", 0.115))
            right_boundary = int(sw * PLAY_AREA.get("right_boundary", 0.885))
            
            def wrap_alien(alien):
                if alien.rect.right < left_boundary:
                    alien.rect.left = right_boundary - alien.rect.width
                    if hasattr(alien, "base_x"):
                        alien.base_x = alien.rect.centerx
                elif alien.rect.left > right_boundary:
                    alien.rect.right = left_boundary + alien.rect.width
                    if hasattr(alien, "base_x"):
                        alien.base_x = alien.rect.centerx
                
                if alien.rect.top > sh:
                    alien.rect.bottom = -alien.rect.height
                    if hasattr(alien, "base_y"):
                        alien.base_y = alien.rect.centery
                elif alien.rect.bottom < -alien.rect.height:
                    alien.rect.top = sh
                    if hasattr(alien, "base_y"):
                        alien.base_y = alien.rect.centery

            if movement == Movement.STRAIGHT:
                for alien in aliens:
                    alien.rect.y += alien.speed
                    wrap_alien(alien)

            elif movement == Movement.ZIGZAG:
                for idx, alien in enumerate(aliens):
                    anchor = getattr(alien, "base_x", alien.rect.x)
                    alien.rect.y += alien.speed
                    alien.rect.x = anchor + math.sin(time * 2 + idx) * 35
                    wrap_alien(alien)

            elif movement == Movement.CIRCULAR:
                for alien in aliens:
                    anchor = getattr(alien, "base_x", alien.rect.x)
                    alien.rect.y += alien.speed
                    alien.rect.x = anchor + math.sin(time * 1.5) * 28
                    wrap_alien(alien)

            elif movement == Movement.WAVE:
                for idx, alien in enumerate(aliens):
                    anchor = getattr(alien, "base_x", alien.rect.x)
                    alien.rect.y += alien.speed
                    alien.rect.x = anchor + math.sin(time * 2 + idx * 0.4) * 45
                    wrap_alien(alien)

            elif movement == Movement.SWARM:
                if aliens:
                    leader = aliens[0]
                    leader.rect.y += leader.speed
                    leader.rect.x += math.sin(time * 2.5) * leader.speed * 1.5
                    wrap_alien(leader)

                    for alien in aliens[1:]:
                        dx = leader.rect.x - alien.rect.x
                        dy = leader.rect.y - alien.rect.y
                        dist = math.hypot(dx, dy)
                        if dist > 1:
                            factor = min(0.6, 0.3 / dist)
                            alien.rect.x += dx * factor
                            alien.rect.y += dy * factor + alien.speed * 0.5
                        else:
                            alien.rect.y += alien.speed
                        wrap_alien(alien)

            elif movement == Movement.RANDOM:
                for alien in aliens:
                    jitter_x = random.uniform(-0.8, 0.8) * alien.speed
                    alien.rect.y += alien.speed
                    alien.rect.x += jitter_x
                    wrap_alien(alien)

            elif movement == Movement.CHASE:
                from src.state.global_state import global_player

                if global_player:
                    for alien in aliens:
                        dx = global_player.rect.centerx - alien.rect.centerx
                        dy = global_player.rect.centery - alien.rect.centery
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            step = min(alien.speed, dist)
                            alien.rect.x += (dx / dist) * step * 0.6
                            alien.rect.y += (dy / dist) * step * 0.6
                        else:
                            alien.rect.y += alien.speed
                        wrap_alien(alien)

            elif movement == Movement.TELEPORT:
                for alien in aliens:
                    if random.random() < 0.01:
                        alien.rect.x = random.randint(int(left_boundary), int(right_boundary - alien.rect.width))
                        alien.rect.y = -alien.rect.height
                    else:
                        alien.rect.y += alien.speed
                    wrap_alien(alien)

        except Exception as e:
            logger.error(f"Error updating group pattern: {e}")

    def update(self):
        """Update level state"""
        try:
            # Update active groups
            for group in self.active_groups[:]:
                aliens_alive = [a for a in group["aliens"] if a.alive()]
                
                if not aliens_alive:
                    self.active_groups.remove(group)
                    # Set the time when group was cleared
                    self.last_group_cleared_time = pygame.time.get_ticks()
                    self.next_group_pending = True
                    continue

                if group["group_behavior"]:
                    self.update_group_pattern(aliens_alive, group["pattern"])

            # Handle pending group spawn with delay
            if self.next_group_pending and not self.active_groups:
                current_time = pygame.time.get_ticks()
                if (current_time - self.last_group_cleared_time) >= self.group_spawn_delay:
                    if self.level_data and self.level_data.alien_groups:
                        self.spawn_next_group()
                        self.next_group_pending = False
                    else:
                        self.level_complete = True
                        self.next_group_pending = False

            # Check if level is complete (original logic)
            elif not self.active_groups and not self.level_data.alien_groups and not self.next_group_pending:
                self.level_complete = True

        except Exception as e:
            logger.error(f"Error updating level: {e}")

    def is_level_complete(self):
        return not self.active_groups and not self.level_data.alien_groups

    def load_next_level(self):
        """Load the next level"""
        self.current_level += 1
        logger.info(f"Loading next level: {self.current_level}")
        self.level_data = self._load_level_data(self.current_level)
        self.level_complete = False
        self.active_groups = []
        self.next_group_pending = False  # Spawn will be triggered explicitly after intro
        self.last_group_cleared_time = pygame.time.get_ticks()  # Start delay timer

        # Clear previous cached data
        self.preloader.clear_cache()

        # Preload next level data
        next_level_data = self._load_level_data(self.current_level + 1)
        self.preloader.preload_level_resources(next_level_data)

import json
import random
import os
import sys
import logging
from typing import List, Dict, Any
from dataclasses import dataclass

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.level.level_data import *
from src.enemy.alien_types import AlienCategory, AlienSubType, AlienType
from src.config.game_settings import (
    LEVEL_PROGRESSION, ALIEN_SETTINGS, 
    FORMATIONS, SPECIAL_EFFECTS
)

logger = logging.getLogger(__name__)

@dataclass
class LevelConfig:
    min_groups: int
    max_groups: int
    min_aliens: int
    max_aliens: int
    alien_types: List[str]
    formations: List[str]
    movement_patterns: List[str]
    entry_points: List[str]
    difficulty: int
    boss_enabled: bool

class LevelGenerator:
    def __init__(self):
        # Add formation spacing configurations with alien size consideration
        base_spacing = ALIEN_SETTINGS.get("size", (32, 32))[0] * 0.5  # 50% of alien size as additional spacing
        
        self.formation_spacing = {
            "line": {
                "min_spacing": base_spacing,
                "group_behavior_chance": 0.4
            },
            "v": {
                "min_spacing": base_spacing * 1.2,  # 20% more for V formation
                "group_behavior_chance": 0.6
            },
            "circle": {
                "min_spacing": base_spacing * 1.1,
                "group_behavior_chance": 0.7
            },
            "diamond": {
                "min_spacing": base_spacing,
                "group_behavior_chance": 0.8
            },
            "wave": {
                "min_spacing": base_spacing * 0.9,  # Slightly less for wave
                "group_behavior_chance": 0.5
            },
            "cross": {
                "min_spacing": base_spacing,
                "group_behavior_chance": 0.6
            },
            "spiral": {
                "min_spacing": base_spacing * 0.9,
                "group_behavior_chance": 0.7
            },
            "star": {
                "min_spacing": base_spacing * 1.1,
                "group_behavior_chance": 0.8
            }
        }
        
        # Keep existing difficulty configurations unchanged
        self.difficulty_configs = {
            # Tutorial levels (1-10)
            (1, 10): LevelConfig(
                min_groups=1,
                max_groups=3,
                min_aliens=5,
                max_aliens=10,
                alien_types=[f"alien_{i:02d}_{'small' if j < 2 else 'large'}_{k:02d}" 
                           for i in range(1,4) for j in range(3) for k in range(1,3)],
                formations=["line", "v", "circle", "diamond", "wave", "cross"],
                movement_patterns=["straight", "wave", "zigzag", "swarm", "circular"],
                entry_points=["top_center", "top_left", "top_right", "left_top", "right_top"],
                difficulty=1,
                boss_enabled=False
            ),
            # Early game (11-25)
            (11, 25): LevelConfig(
                min_groups=2,
                max_groups=4,
                min_aliens=5,
                max_aliens=10,
                alien_types=[f"alien_{i:02d}_{'small' if j < 2 else 'large'}_{k:02d}" 
                           for i in range(4,7) for j in range(3) for k in range(1,3)],
                formations=["line", "v", "circle", "diamond", "wave", "cross", "spiral"],
                movement_patterns=["straight", "wave", "zigzag", "swarm", "circular"],
                entry_points=["top_center", "top_left", "top_right", "left_top", "right_top"],
                difficulty=2,
                boss_enabled=True
            ),
            # Mid game (26-50)
            (26, 50): LevelConfig(
                min_groups=3,
                max_groups=5,
                min_aliens=10,
                max_aliens=15,
                alien_types=[f"alien_{i:02d}_{'small' if j < 2 else 'large'}_{k:02d}" 
                           for i in range(7,11) for j in range(3) for k in range(1,3)],
                formations=["line", "v", "circle", "diamond", "wave", "cross", "spiral"],
                movement_patterns=["straight", "wave", "zigzag", "swarm", "circular", "random"],
                entry_points=["top_center", "top_left", "top_right", "left_top", "right_top"],
                difficulty=3,
                boss_enabled=True
            ),
            # Late game (51-75)
            (51, 75): LevelConfig(
                min_groups=4,
                max_groups=6,
                min_aliens=10,
                max_aliens=15,
                alien_types=[f"alien_{i:02d}_{'small' if j < 2 else 'large'}_{k:02d}" 
                           for i in range(11,15) for j in range(3) for k in range(1,3)],
                formations=["line", "v", "circle", "diamond", "wave", "cross", "spiral"],
                movement_patterns=["straight", "wave", "zigzag", "swarm", "circular", "random"],
                entry_points=["top_center", "top_left", "top_right", "left_top", "right_top"],
                difficulty=4,
                boss_enabled=True
            ),
            # Expert game (76-100)
            (76, 100): LevelConfig(
                min_groups=5,
                max_groups=7,
                min_aliens=10,
                max_aliens=20,
                alien_types=[f"alien_{i:02d}_{'small' if j < 2 else 'large'}_{k:02d}" 
                           for i in range(15,18) for j in range(3) for k in range(1,3)],
                formations=["line", "v", "circle", "diamond", "wave", "cross", "spiral"],
                movement_patterns=["straight", "wave", "zigzag", "swarm", "circular", "random", "chase"],
                entry_points=["top_center", "top_left", "top_right", "left_top", "right_top"],
                difficulty=5,
                boss_enabled=True
            ),
            # Master game (101-150)
            (101, 150): LevelConfig(
                min_groups=6,
                max_groups=8,
                min_aliens=15,
                max_aliens=25,
                alien_types=[f"alien_{i:02d}_{'small' if j < 2 else 'large'}_{k:02d}" 
                           for i in range(18,22) for j in range(3) for k in range(1,3)],
                formations=["line", "v", "circle", "diamond", "wave", "cross", "spiral"],
                movement_patterns=["straight", "wave", "zigzag", "swarm", "circular", "random", "chase"],
                entry_points=["top_center", "top_left", "top_right", "left_top", "right_top"],
                difficulty=6,
                boss_enabled=True
            ),
            # Legend game (151-200)
            (151, 200): LevelConfig(
                min_groups=7,
                max_groups=10,
                min_aliens=20,
                max_aliens=30,
                alien_types=[f"alien_{i:02d}_{'small' if j < 2 else 'large'}_{k:02d}" 
                           for i in range(22,26) for j in range(3) for k in range(1,3)],
                formations=["line", "v", "circle", "diamond", "wave", "cross", "spiral", "star"],
                movement_patterns=["straight", "wave", "zigzag", "swarm", "circular", "random", "chase", "teleport"],
                entry_points=["top_center", "top_left", "top_right", "left_top", "right_top"],
                difficulty=7,
                boss_enabled=True
            )
        }

    def generate_path(self, entry_point: str, complexity: int) -> List[Dict]:
        """Generate a movement path for an alien group."""
        path = []
        points = random.randint(3, 5 + complexity)
        
        # Starting point based on entry point
        if entry_point == "top_center":
            start_x = 0.5
            start_y = 0.1
        elif entry_point == "top_left":
            start_x = 0.2
            start_y = 0.1
        elif entry_point == "top_right":
            start_x = 0.8
            start_y = 0.1
        elif entry_point == "left_top":
            start_x = 0.1
            start_y = 0.1
        elif entry_point == "right_top":
            start_x = 0.9
            start_y = 0.1
        else:
            start_x = 0.5
            start_y = 0.1

        path.append({
            "x": start_x,
            "y": start_y,
            "wait_time": 0,
            "shoot": False
        })

        # Generate middle points
        for _ in range(points - 2):
            path.append({
                "x": random.uniform(0.1, 0.9),
                "y": random.uniform(0.2, 0.6),
                "wait_time": random.uniform(0.5, 2.0),
                "shoot": random.random() > 0.5
            })

        # End point (return to top)
        path.append({
            "x": random.uniform(0.2, 0.8),
            "y": 0.1,
            "wait_time": 0,
            "shoot": False
        })

        return path

    def generate_alien_group(self, config: LevelConfig) -> Dict:
        """Generate a single alien group configuration."""
        count = random.randint(config.min_aliens, config.max_aliens)
        formation = random.choice(config.formations)
        
        # Use formation-specific spacing
        formation_config = self.formation_spacing[formation]
        spacing = formation_config["min_spacing"]
        group_behavior_chance = formation_config["group_behavior_chance"]

        entry_point = random.choice(config.entry_points)
        
        return {
            "alien_type": random.choice(config.alien_types),
            "count": count,
            "formation": formation,
            "spacing": spacing,
            "entry_point": entry_point,
            "path": self.generate_path(entry_point, config.difficulty),
            "movement_pattern": random.choice(config.movement_patterns),
            "speed": random.uniform(1.5, 2.5),
            "health": random.randint(1, config.difficulty + 1),
            "shoot_interval": random.uniform(1.5, 3.0),
            "group_behavior": random.random() < group_behavior_chance
        }

    def generate_boss_data(self, level_number: int) -> Dict:
        """Generate boss configuration for milestone levels."""
        return {
            "type": f"boss_{(level_number // 25):02d}",
            "health": 100 + (level_number // 25) * 50,
            "speed": 1.0,
            "attack_patterns": ["pattern1", "pattern2", "pattern3"],
            "phase_count": 3
        }

    def generate_level(self, level_number: int) -> Dict:
        """Generate a complete level configuration."""
        # Find the appropriate difficulty config for this level
        config = next((conf for (start, end), conf in self.difficulty_configs.items() 
                        if start <= level_number <= end), None)
        
        if not config:
            raise ValueError(f"No configuration found for level {level_number}")

        # Generate groups
        group_count = random.randint(config.min_groups, config.max_groups)
        alien_groups = [self.generate_alien_group(config) for _ in range(group_count)]

        # Determine if this is a boss level
        is_boss_level = config.boss_enabled and level_number % 25 == 0
        boss_data = self.generate_boss_data(level_number) if is_boss_level else None

        return {
            "level_number": level_number,
            "name": f"Level {level_number}",
            "difficulty": config.difficulty,
            "alien_groups": alien_groups,
            "boss_data": boss_data,
            "background_speed": 1.0 + (level_number // 25) * 0.2,
            "music_track": f"level{(level_number // 25) + 1}.mp3",
            "special_effects": [],
            "power_up_frequency": 0.2,
            "minimum_clear_time": 30.0
        }

    def generate_all_levels(self, start_level: int = 1, end_level: int = 100):
        """Generate all level files."""
        output_dir = os.path.join("assets", "levels")
        os.makedirs(output_dir, exist_ok=True)

        for level in range(start_level, end_level + 1):
            try:
                level_data = self.generate_level(level)
                filename = os.path.join(output_dir, f"{level:03d}.json")
                
                with open(filename, 'w') as f:
                    json.dump(level_data, f, indent=2)
                    
                logger.info(f"Generated level {level}")
            except Exception as e:
                logger.error(f"Error generating level {level}: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generator = LevelGenerator()
    
    # Generate first 200 levels by default
    generator.generate_all_levels(1, 200) 
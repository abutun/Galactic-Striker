import json
import random
import math
import os
import sys

# Add the src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from level.level_data import *
from enemy.alien_types import AlienCategory, AlienSubType, AlienType

class LevelGenerator:
    def __init__(self):
        self.difficulty_progression = {
            # Level ranges and their difficulty settings
            (1, 25): {"diff_range": (1, 3), "alien_types": (1, 5)},
            (26, 50): {"diff_range": (2, 4), "alien_types": (4, 8)},
            (51, 100): {"diff_range": (3, 5), "alien_types": (7, 12)},
            (101, 150): {"diff_range": (4, 7), "alien_types": (10, 15)},
            (151, 200): {"diff_range": (6, 8), "alien_types": (13, 20)},
            (201, 250): {"diff_range": (7, 10), "alien_types": (15, 25)}
        }
        
        # Ensure the levels directory exists
        os.makedirs(os.path.join(os.path.dirname(__file__), "../../assets/levels"), exist_ok=True)

    def generate_path(self, entry_point: EntryPoint, complexity: int) -> List[PathPoint]:
        paths = []
        screen_width = 1.0  # Using relative coordinates (0-1)
        screen_height = 1.0

        if entry_point == EntryPoint.TOP:
            start_x = random.random()
            paths.append(PathPoint(start_x, 0, 0, False))
        elif entry_point == EntryPoint.TOP_LEFT:
            paths.append(PathPoint(0, 0, 0, False))
        elif entry_point == EntryPoint.TOP_RIGHT:
            paths.append(PathPoint(1, 0, 0, False))

        # Generate middle points based on complexity
        for _ in range(complexity):
            x = random.random()
            y = random.random() * 0.7  # Keep in top 70% of screen
            wait = random.random() * 2  # 0-2 seconds wait
            shoot = random.random() < 0.3  # 30% chance to shoot
            paths.append(PathPoint(x, y, wait, shoot))

        # Add return path to top
        paths.append(PathPoint(random.random(), 0, 0, False))
        return paths

    def create_alien_group(self, type_num: int, category: AlienCategory, 
                          count: int, difficulty: int) -> AlienGroup:
        alien_type = AlienType(type_num, category)
        entry_point = self._get_strategic_entry_point(difficulty)
        
        # Get base name without extension and frame number
        base_name = f"alien_{type_num:02d}_{category.value}" if category != AlienCategory.BOSS else f"boss_{type_num:02d}"
        
        # Define formation first so we can use it in group_behavior calculation
        formation = random.choice(["line", "v", "circle", "diamond", "wave"])
        
        return AlienGroup(
            alien_type=base_name,
            count=count,
            formation=formation,  # Use the selected formation
            spacing=random.randint(30, 50),
            entry_point=entry_point,
            path=self._generate_strategic_path(entry_point, difficulty),
            movement_pattern=self._get_appropriate_pattern(category, difficulty),
            speed=self._calculate_speed(category, difficulty),
            health=alien_type.health,
            shoot_interval=self._calculate_shoot_interval(category, difficulty),
            group_behavior=self._should_use_group_behavior(formation, difficulty)  # Now formation is defined
        )

    def _get_strategic_entry_point(self, difficulty: int) -> EntryPoint:
        """Choose entry point based on difficulty and strategy."""
        if difficulty > 7:
            # More complex entry points for higher difficulties
            return random.choice([EntryPoint.TOP_LEFT, EntryPoint.TOP_RIGHT])
        return random.choice(list(EntryPoint))

    def generate_level(self, level_number: int) -> LevelData:
        """Generate a level with appropriate difficulty and alien types."""
        # Find appropriate difficulty settings
        settings = next((config for (start, end), config in self.difficulty_progression.items() 
                        if start <= level_number <= end), None)
        
        if not settings:
            raise ValueError(f"Invalid level number: {level_number}")

        difficulty = random.randint(*settings["diff_range"])
        alien_type_range = settings["alien_types"]
        
        # Determine if this is a boss or bonus level
        is_boss_level = level_number % 25 == 0
        is_bonus_level = level_number % 10 == 0 and not is_boss_level

        alien_groups = []

        if is_boss_level:
            # Create boss level
            boss_num = level_number // 25
            boss_type = AlienType(boss_num, AlienCategory.BOSS)
            
            alien_groups.append(AlienGroup(
                alien_type=f"boss_{boss_num:02d}",
                count=1,
                formation="single",
                spacing=0,
                entry_point=EntryPoint.TOP,
                path=self._generate_strategic_path(EntryPoint.TOP, difficulty),
                movement_pattern=MovementPattern.BOSS,
                speed=0.8,
                health=boss_type.health,
                shoot_interval=1.0,
                group_behavior=False
            ))
            
            # Add some small support enemies
            for _ in range(2):
                type_num = random.randint(*alien_type_range)
                alien_groups.append(self.create_alien_group(
                    type_num, AlienCategory.SMALL, 
                    random.randint(2, 4), difficulty
                ))

        else:
            # Regular or bonus level
            group_count = random.randint(2, 4 + difficulty)
            points_multiplier = 3 if is_bonus_level else 1

            for _ in range(group_count):
                type_num = random.randint(*alien_type_range)
                category = random.choice([AlienCategory.SMALL, AlienCategory.LARGE])
                
                count = random.randint(3, 8 + difficulty)
                if category == AlienCategory.LARGE:
                    count = count // 2  # Fewer large enemies
                
                alien_groups.append(self.create_alien_group(
                    type_num, category, count, difficulty
                ))

        return LevelData(
            level_number=level_number,
            name=f"Level {level_number}",
            difficulty=difficulty,
            alien_groups=alien_groups,
            boss_data=None if not is_boss_level else {
                "type": f"boss_{level_number // 25}",
                "health": 50 + (level_number // 25) * 25,
                "patterns": random.randint(2, 4 + (level_number // 50))
            },
            background_speed=1.0 + (difficulty * 0.1),
            music_track=f"level_{random.randint(1,5)}.mp3",
            special_effects=["bonus_multiplier"] if is_bonus_level else []
        )

    def generate_all_levels(self):
        """Generate all 250 levels."""
        for level in range(1, 251):
            level_data = self.generate_level(level)
            # Update path to be relative to script location
            level_path = os.path.join(os.path.dirname(__file__), 
                                    f"../../assets/levels/{level:03d}.json")
            with open(level_path, "w") as f:
                json.dump(level_data.__dict__, f, indent=2, 
                         default=lambda x: x.value if isinstance(x, Enum) else x.__dict__)

    def _generate_strategic_path(self, entry_point: EntryPoint, difficulty: int) -> List[PathPoint]:
        """Generate a strategic path based on entry point and difficulty."""
        paths = []
        screen_width = 1.0
        screen_height = 1.0

        # Starting point based on entry point
        if entry_point == EntryPoint.TOP:
            start_x = random.random()
            paths.append(PathPoint(start_x, 0, 0, False))
        elif entry_point == EntryPoint.TOP_LEFT:
            paths.append(PathPoint(0, 0, 0, False))
        elif entry_point == EntryPoint.TOP_RIGHT:
            paths.append(PathPoint(1, 0, 0, False))
        elif entry_point == EntryPoint.LEFT:
            start_y = random.random() * 0.3  # Top third of screen
            paths.append(PathPoint(0, start_y, 0, False))
        elif entry_point == EntryPoint.RIGHT:
            start_y = random.random() * 0.3
            paths.append(PathPoint(1, start_y, 0, False))

        # Number of waypoints increases with difficulty
        num_points = 2 + difficulty // 2

        # Generate strategic waypoints
        for i in range(num_points):
            x = random.random()
            y = random.random() * 0.7  # Keep in top 70% of screen
            
            # Higher difficulty means more complex paths
            if difficulty > 5:
                # Add more waiting points and shooting opportunities
                wait = random.random() * (difficulty * 0.5)  # More waiting time
                shoot = random.random() < (0.2 + difficulty * 0.05)  # More shooting
            else:
                wait = random.random() * 2
                shoot = random.random() < 0.3
                
            paths.append(PathPoint(x, y, wait, shoot))

        # Add exit point
        paths.append(PathPoint(random.random(), 0, 0, False))
        return paths

    def _get_appropriate_pattern(self, category: AlienCategory, difficulty: int) -> MovementPattern:
        """Choose appropriate movement pattern based on alien type and difficulty."""
        if category == AlienCategory.BOSS:
            return MovementPattern.BOSS
        
        # Available patterns based on difficulty
        patterns = [MovementPattern.STRAIGHT]
        if difficulty > 3:
            patterns.extend([MovementPattern.ZIGZAG, MovementPattern.WAVE])
        if difficulty > 5:
            patterns.extend([MovementPattern.CIRCULAR, MovementPattern.SWARM])
        if difficulty > 7:
            patterns.append(MovementPattern.RANDOM)
            
        return random.choice(patterns)

    def _calculate_speed(self, category: AlienCategory, difficulty: int) -> float:
        """Calculate appropriate speed based on alien type and difficulty."""
        base_speed = 1.0
        
        # Category modifiers
        speed_modifiers = {
            AlienCategory.SMALL: 1.2,
            AlienCategory.LARGE: 0.8,
            AlienCategory.BOSS: 0.6
        }
        
        # Apply category modifier
        base_speed *= speed_modifiers[category]
        
        # Apply difficulty scaling
        difficulty_bonus = 0.1 * difficulty
        
        return base_speed + difficulty_bonus

    def _calculate_shoot_interval(self, category: AlienCategory, difficulty: int) -> float:
        """Calculate shooting interval based on alien type and difficulty."""
        base_interval = 3.0
        
        # Category modifiers
        interval_modifiers = {
            AlienCategory.SMALL: 1.0,
            AlienCategory.LARGE: 0.8,
            AlienCategory.BOSS: 0.5
        }
        
        # Apply category modifier
        base_interval *= interval_modifiers[category]
        
        # Reduce interval with difficulty (faster shooting)
        difficulty_reduction = 0.2 * difficulty
        
        return max(0.5, base_interval - difficulty_reduction)

    def _should_use_group_behavior(self, formation: str, difficulty: int) -> bool:
        """Determine if aliens should move as a group."""
        # Group behavior more likely with certain formations
        formation_weights = {
            "line": 0.4,
            "v": 0.6,
            "circle": 0.7,
            "diamond": 0.8,
            "wave": 0.5
        }
        
        base_chance = formation_weights.get(formation, 0.3)
        difficulty_bonus = difficulty * 0.05
        
        return random.random() < (base_chance + difficulty_bonus)

if __name__ == "__main__":
    # Print current directory and Python path for debugging
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    generator = LevelGenerator()
    generator.generate_all_levels() 
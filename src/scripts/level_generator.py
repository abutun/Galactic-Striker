import json
import random
import os
import sys
import logging

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

class LevelGenerator:
    def __init__(self):
        self.difficulty_progression = LEVEL_PROGRESSION
        
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

    def validate_alien_type(self, type_num: int, category: AlienCategory, 
                           subtype: AlienSubType) -> bool:
        """Validate alien type combination."""
        try:
            # Check type number range
            if not 1 <= type_num <= 25:
                logger.error(f"Invalid type number: {type_num}")
                return False

            # Check category/subtype combination
            if category == AlienCategory.BOSS and subtype is not None:
                logger.error(f"Boss aliens should not have subtypes")
                return False
            
            if category != AlienCategory.BOSS and subtype not in [AlienSubType.TYPE1, AlienSubType.TYPE2]:
                logger.error(f"Invalid subtype for non-boss alien: {subtype}")
                return False

            # Verify asset exists
            asset_path = os.path.join("assets/aliens", 
                f"alien_{type_num:02d}_{category.value}_{subtype.value:02d}.png" 
                if category != AlienCategory.BOSS else f"boss_{type_num:02d}.png")
            
            if not os.path.exists(asset_path):
                logger.error(f"Missing asset file: {asset_path}")
                return False

            return True
        except Exception as e:
            logger.error(f"Error validating alien type: {e}")
            return False

    def create_alien_group(self, type_num: int, category: AlienCategory, 
                          subtype: AlienSubType, count: int, difficulty: int) -> AlienGroup:
        """Create an alien group with validation."""
        # Validate inputs
        if not self.validate_alien_type(type_num, category, subtype):
            raise ValueError(f"Invalid alien type combination: type={type_num}, category={category}, subtype={subtype}")
        
        if count < 1:
            raise ValueError(f"Invalid alien count: {count}")
        
        if difficulty < 1:
            raise ValueError(f"Invalid difficulty: {difficulty}")

        alien_type = AlienType(type_num, category, subtype)
        entry_point = self._get_strategic_entry_point(difficulty)
        
        formation = random.choice(["line", "v", "circle", "diamond", "wave"])
        
        return AlienGroup(
            alien_type=alien_type.base_name,
            count=count,
            formation=formation,
            spacing=random.randint(30, 50),
            entry_point=entry_point,
            path=self._generate_strategic_path(entry_point, difficulty),
            movement_pattern=self._get_appropriate_pattern(category, difficulty),
            speed=self._calculate_speed(category, difficulty),
            health=alien_type.health,
            shoot_interval=self._calculate_shoot_interval(category, difficulty),
            group_behavior=self._should_use_group_behavior(formation, difficulty)
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
            boss_type = AlienType(boss_num, AlienCategory.BOSS, None)
            
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
                    type_num, AlienCategory.SMALL, random.choice([AlienSubType.TYPE1, AlienSubType.TYPE2]), 
                    random.randint(2, 4), difficulty
                ))

        else:
            # Regular or bonus level
            group_count = random.randint(2, 4 + difficulty)
            points_multiplier = 3 if is_bonus_level else 1

            for _ in range(group_count):
                type_num = random.randint(*alien_type_range)
                category = random.choice([AlienCategory.SMALL, AlienCategory.LARGE])
                sub_type = random.choice([AlienSubType.TYPE1, AlienSubType.TYPE2])
                
                count = random.randint(3, 8 + difficulty)
                if category == AlienCategory.LARGE:
                    count = count // 2  # Fewer large enemies
                
                alien_groups.append(self.create_alien_group(
                    type_num, category, sub_type, count, difficulty
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
        speed_modifier = ALIEN_SETTINGS[category.value]["speed_modifier"]
        difficulty_bonus = SPECIAL_EFFECTS["difficulty_scaling"] * difficulty
        return base_speed * speed_modifier + difficulty_bonus

    def _calculate_shoot_interval(self, category: AlienCategory, difficulty: int) -> float:
        """Calculate shooting interval based on alien type and difficulty."""
        base_interval = ALIEN_SETTINGS[category.value]["shoot_interval"]
        difficulty_reduction = SPECIAL_EFFECTS["difficulty_scaling"] * difficulty
        return max(0.5, base_interval - difficulty_reduction)

    def _should_use_group_behavior(self, formation: str, difficulty: int) -> bool:
        """Determine if aliens should move as a group."""
        base_chance = FORMATIONS[formation]["group_behavior_chance"]
        difficulty_bonus = SPECIAL_EFFECTS["difficulty_scaling"] * difficulty
        return random.random() < (base_chance + difficulty_bonus)

if __name__ == "__main__":
    # Print current directory and Python path for debugging
    print(f"Current directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    generator = LevelGenerator()
    generator.generate_all_levels() 
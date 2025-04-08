from enum import Enum
from dataclasses import dataclass
from typing import Optional, List
import os
import logging

logger = logging.getLogger(__name__)

class AlienCategory(Enum):
    SMALL = "small"
    LARGE = "large"
    BOSS = "boss"

class AlienSubType(Enum):
    TYPE1 = 1
    TYPE2 = 2

@dataclass
class AlienType:
    type_number: int  # 1-25
    category: AlienCategory
    subtype: AlienSubType

    def __post_init__(self):
        """Validate alien type after initialization."""
        if not 1 <= self.type_number <= 25:
            raise ValueError(f"Invalid alien type number: {self.type_number}")
            
        if self.category == AlienCategory.BOSS and self.subtype is not None:
            raise ValueError("Boss aliens should not have subtypes")
            
        if self.category != AlienCategory.BOSS and self.subtype not in [AlienSubType.TYPE1, AlienSubType.TYPE2]:
            raise ValueError(f"Invalid subtype for non-boss alien: {self.subtype}")

    @property
    def sprite_path(self) -> str:
        """Get the path to the sprite file with validation."""
        try:
            path = self._generate_sprite_path()
            if not os.path.exists(path):
                logger.error(f"Sprite file not found: {path}")
                raise FileNotFoundError(f"Missing sprite file: {path}")
            return path
        except Exception as e:
            logger.error(f"Error getting sprite path: {e}")
            raise

    @property
    def sprite_frames(self) -> List[str]:
        """Get list of sprite frames for animation."""
        if self.category == AlienCategory.BOSS:
            return [f"assets/aliens/boss_{self.type_number:02d}.png"]
        else:
            base = f"assets/aliens/alien_{self.type_number:02d}_{self.category.value}_{self.subtype:02d}.png"
            #return [f"{base}_{i:02d}.png" for i in range(1, 3)]

    @property
    def base_name(self) -> str:
        """Get the base name without path and frame number."""
        if self.category == AlienCategory.BOSS:
            return f"boss_{self.type_number:02d}"
        return f"alien_{self.type_number:02d}_{self.category.value}_{self.subtype.value:02d}"

    @property
    def points(self) -> int:
        """Calculate points value for this alien type."""
        base_points = self.type_number * 100
        
        if self.category == AlienCategory.SMALL:
            return base_points
        elif self.category == AlienCategory.LARGE:
            return base_points * 2
        else:  # BOSS
            return base_points * 10

    @property
    def life(self) -> int:
        """Calculate life for this alien type."""
        base_life = self.type_number
        
        if self.category == AlienCategory.SMALL:
            return base_life
        elif self.category == AlienCategory.LARGE:
            return base_life * 2
        else:  # BOSS
            return base_life * 5

    @property
    def fire_pattern(self) -> str:
        """Define how this alien type shoots."""
        if self.category == AlienCategory.BOSS:
            return "multi_directional"
        elif self.category == AlienCategory.LARGE:
            return "spread"
        return "single"
    
    @property
    def special_ability(self) -> Optional[str]:
        """Special abilities based on type."""
        abilities = {
            (AlienCategory.LARGE, 1): "shield",
            (AlienCategory.LARGE, 2): "teleport",
            (AlienCategory.BOSS, None): "summon_minions"
        }
        return abilities.get((self.category, self.type_number))
    
    @property
    def score_multiplier(self) -> float:
        """Dynamic score multiplier based on difficulty."""
        return 1.0 + (self.type_number * 0.1) 

    def _generate_sprite_path(self) -> str:
        """Generate the sprite path based on the type."""
        return f"assets/aliens/{self.base_name}.png" 
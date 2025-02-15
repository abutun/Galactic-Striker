from enum import Enum
from dataclasses import dataclass
from typing import Optional, List

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
    subtype: AlienSubType = None  # Not used in new structure

    @property
    def sprite_path(self) -> str:
        """Get the path to the sprite file."""
        if self.category == AlienCategory.BOSS:
            return f"assets/aliens/boss_{self.type_number:02d}.png"
        else:
            return f"assets/aliens/alien_{self.type_number:02d}_{self.category.value}_1.png"

    @property
    def sprite_frames(self) -> List[str]:
        """Get list of sprite frames for animation."""
        if self.category == AlienCategory.BOSS:
            return [f"assets/aliens/boss_{self.type_number:02d}.png"]
        else:
            base = f"assets/aliens/alien_{self.type_number:02d}_{self.category.value}"
            return [f"{base}_{i}.png" for i in range(1, 3)]

    @property
    def base_name(self) -> str:
        """Get the base name without path and frame number."""
        if self.category == AlienCategory.BOSS:
            return f"boss{self.type_number:02d}"
        return f"type{self.type_number:02d}_{self.category.value}_sub{self.subtype.value}"

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
    def health(self) -> int:
        """Calculate health for this alien type."""
        base_health = self.type_number
        
        if self.category == AlienCategory.SMALL:
            return base_health
        elif self.category == AlienCategory.LARGE:
            return base_health * 2
        else:  # BOSS
            return base_health * 10

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
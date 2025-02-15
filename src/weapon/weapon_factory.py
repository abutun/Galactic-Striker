from typing import Type
from .weapon1 import Weapon1
from .base_weapon import PrimaryWeapon
from .weapon2 import Weapon2
from .weapon3 import Weapon3
from .weapon4 import Weapon4
from .weapon5 import Weapon5
from .weapon6 import Weapon6
from .weapon7 import Weapon7
from .weapon8 import Weapon8
from .weapon9 import Weapon9
import logging

logger = logging.getLogger(__name__)

class WeaponFactory:
    _weapon_classes = {
        1: Weapon1,
        2: Weapon2,
        3: Weapon3,
        4: Weapon4,
        5: Weapon5,
        6: Weapon6,
        7: Weapon7,
        8: Weapon8,
        9: Weapon9
    }
    
    @classmethod
    def create_weapon(cls, weapon_type: int) -> PrimaryWeapon:
        """Create a weapon instance based on weapon type."""
        try:
            weapon_class = cls._weapon_classes.get(weapon_type, Weapon1)
            return weapon_class()
        except Exception as e:
            logger.error(f"Error creating weapon type {weapon_type}: {e}")
            return Weapon1()  # Fallback to basic weapon
            
    @classmethod
    def register_weapon(cls, weapon_type: int, weapon_class: Type[PrimaryWeapon]) -> None:
        """Register a new weapon type."""
        cls._weapon_classes[weapon_type] = weapon_class 

    @staticmethod
    def create_weapon(weapon_type: int) -> PrimaryWeapon:
        if weapon_type == 1:
            return Weapon1()
        # Add more weapon types here
        return Weapon1()  # Default to Weapon1 
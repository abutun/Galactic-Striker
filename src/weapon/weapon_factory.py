from typing import Dict, Type

from src.weapon.base_weapon import PrimaryWeapon
from .weapon1 import Weapon1
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
    _weapons: Dict[str, Type] = {
        'weapon1': Weapon1,
        'weapon2': Weapon2,
        'weapon3': Weapon3,
        'weapon4': Weapon4,
        'weapon5': Weapon5,
        'weapon6': Weapon6,
        'weapon7': Weapon7,
        'weapon8': Weapon8,
        'weapon9': Weapon9
    }
    
    @staticmethod
    def create_weapon(weapon_type, bullet_group):
        if weapon_type == 1:
            return Weapon1(bullet_group)
        elif weapon_type == 2:
            return Weapon2(bullet_group)
        elif weapon_type == 3:
            return Weapon3(bullet_group)
        elif weapon_type == 4:
            return Weapon4(bullet_group)
        elif weapon_type == 5:
            return Weapon5(bullet_group)
        elif weapon_type == 6:
            return Weapon6(bullet_group)
        elif weapon_type == 7:
            return Weapon7(bullet_group)
        else:
            return Weapon1(bullet_group)  # Default to basic weapon

    @classmethod
    def register_weapon(cls, weapon_type: str, weapon_class: Type[PrimaryWeapon]) -> None:
        """Register a new weapon type."""
        cls._weapons[weapon_type] = weapon_class 
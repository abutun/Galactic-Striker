# src/weapon/base_weapon.py

class PrimaryWeapon:
    """Base class for primary weapons."""
    def __init__(self, bullet_group):
        self.bullet_group = bullet_group
        self.level = 1
        self.bullet_speed = 7
        self.bullet_damage = 1
        self.fire_delay = 250
        self.last_fire = 0

    def fire(self, x, y):
        """Fire the weapon. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement fire method")

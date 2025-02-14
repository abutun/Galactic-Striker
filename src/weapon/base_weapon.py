# src/weapon/base_weapon.py

class PrimaryWeapon:
    def fire(self, player, bullet_group):
        """
        Fire method to be implemented by each weapon subclass.
        Should create one or more bullets and add them to bullet_group.
        """
        raise NotImplementedError("Subclasses must implement fire()")

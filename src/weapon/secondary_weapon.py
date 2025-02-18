# src/weapon/secondary_weapon.py
from src.weapon.weapons import Missile

class SecondaryWeapon:
    def fire(self, player, bullet_group):
        if player.rockets > 0:
            rocket = Missile(player.rect.centerx, player.rect.top, -8, damage=10)
            rocket.image.fill((255, 100, 0))
            bullet_group.add(rocket)
            player.rockets = max(player.rockets - 1, 0)

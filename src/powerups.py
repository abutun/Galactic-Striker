from enum import Enum
from dataclasses import dataclass
import random

class PowerUpType(Enum):
    SHIELD = "shield"
    SPEED = "speed"
    SPREAD = "spread"
    RAPID_FIRE = "rapid_fire"
    DAMAGE_UP = "damage_up"
    HEALTH = "health"
    MISSILE = "missile"
    LASER = "laser"

@dataclass
class PowerUpEffect:
    type: PowerUpType
    duration: float  # in seconds, -1 for permanent
    magnitude: float
    
class PowerUpManager:
    def __init__(self, player):
        self.player = player
        self.active_powerups = []
        
    def add_powerup(self, powerup_type):
        effects = {
            PowerUpType.SHIELD: PowerUpEffect(PowerUpType.SHIELD, 10, 50),
            PowerUpType.SPEED: PowerUpEffect(PowerUpType.SPEED, 5, 1.5),
            PowerUpType.SPREAD: PowerUpEffect(PowerUpType.SPREAD, -1, 1),
            PowerUpType.RAPID_FIRE: PowerUpEffect(PowerUpType.RAPID_FIRE, 8, 0.5),
            PowerUpType.DAMAGE_UP: PowerUpEffect(PowerUpType.DAMAGE_UP, 12, 2),
        }
        
        if powerup_type in effects:
            self.active_powerups.append(effects[powerup_type])
            self.apply_effect(effects[powerup_type])
    
    def apply_effect(self, effect):
        if effect.type == PowerUpType.SHIELD:
            self.player.shield += effect.magnitude
        elif effect.type == PowerUpType.SPEED:
            self.player.speed *= effect.magnitude
        # ... other effects 
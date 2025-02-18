from enum import Enum
from dataclasses import dataclass
import json

class Achievement:
    def __init__(self, id, name, description, icon_path, points):
        self.id = id
        self.name = name
        self.description = description
        self.icon_path = icon_path
        self.points = points
        self.unlocked = False
        
class AchievementManager:
    def __init__(self):
        self.achievements = {}
        self.total_points = 0
        self.load_achievements()
        
    def load_achievements(self):
        self.add_achievement("first_blood", "First Blood", 
                           "Destroy your first enemy", "achievements/first_blood.png", 5)
        self.add_achievement("survivor", "Survivor", 
                           "Complete level 10 without dying", "achievements/survivor.png", 20)
        # ... more achievements
        
    def check_achievements(self, game_state):
        # Check various conditions and unlock achievements
        if game_state.enemies_destroyed == 1:
            self.unlock_achievement("first_blood") 
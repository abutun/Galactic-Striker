from .base_bonus import Bonus

class SpeedBoostBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/speed_boost.png", (0, 255, 255), (24, 24))
        
    def apply(self, player, game_context=None):
        if hasattr(player, 'speed'):
            player.speed = min(player.speed + 1, 5)  # Cap at 5
        else:
            player.speed = 2

class TimeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/time_bonus.png", (255, 255, 0), (24, 24))
        
    def apply(self, player, game_context=None):
        if game_context and "time_manager" in game_context:
            game_context["time_manager"].add_time(30)  # Add 30 seconds 
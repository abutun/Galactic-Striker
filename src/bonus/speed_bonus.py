from .base_bonus import Bonus

class ExtraSpeedBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_speed.png", (0, 255, 255), (32, 32))
        
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if hasattr(player, 'speed'):
            player.speed = min(player.speed + 1, 5)  # Cap at 5
        else:
            player.speed = 2

class TimeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_time.png", (255, 255, 0), (32, 32))
        
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "time_manager" in game_context:
            game_context["time_manager"].add_time(30)  # Add 30 seconds 
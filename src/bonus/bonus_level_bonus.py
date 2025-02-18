from .base_bonus import Bonus

class BonusMeteorstormBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/bonus_meteorstorm.png", (192, 192, 192), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "start_meteorstorm" in game_context:
            game_context["start_meteorstorm"]()

class BonusMemorystationBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/bonus_memorystation.png", (128, 128, 128), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "start_memorystation" in game_context:
            game_context["start_memorystation"]()

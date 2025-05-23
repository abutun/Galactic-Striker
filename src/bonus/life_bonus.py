from .base_bonus import Bonus

class ExtraLifeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_life.png", (0, 255, 0), (32, 32))
    def apply(self, player, game_context=None):
        if player.add_life():
            self.sound_manager.play("bonus_reward")
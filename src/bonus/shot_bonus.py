from .base_bonus import Bonus

class SingleShotBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, 
                        image_path="assets/sprites/single_shot.png",
                        fallback_color=(200, 200, 200),
                        size=(24, 24))

    def apply(self, player):
        self.sound_manager.play("bonus_reward")
        player.primary_weapon = 1

class DoubleShotBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, 
                        image_path="assets/sprites/double_shot.png",
                        fallback_color=(200, 200, 200),
                        size=(24, 24))

    def apply(self, player):
        self.sound_manager.play("bonus_reward")
        player.primary_weapon = 2

class TripleShotBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, 
                        image_path="assets/sprites/triple_shot.png",
                        fallback_color=(200, 200, 200),
                        size=(24, 24))

    def apply(self, player):
        self.sound_manager.play("bonus_reward")
        player.primary_weapon = 3

class QuadShotBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, 
                        image_path="assets/sprites/quad_shot.png",
                        fallback_color=(200, 200, 200),
                        size=(24, 24))

    def apply(self, player):
        self.sound_manager.play("bonus_reward")
        player.primary_weapon = 4

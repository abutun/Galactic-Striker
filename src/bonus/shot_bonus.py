from .base_bonus import BaseBonus

class SingleShotBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/single_shot.png", (200, 200, 200), (24, 24))
    def apply(self, player, game_context=None):
        player.shot_count = 1

class DoubleShotBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/double_shot.png", (200, 200, 200), (24, 24))
    def apply(self, player, game_context=None):
        player.shot_count = 2

class TripleShotBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/triple_shot.png", (200, 200, 200), (24, 24))
    def apply(self, player, game_context=None):
        player.shot_count = 3

class QuadShotBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/quad_shot.png", (200, 200, 200), (24, 24))
    def apply(self, player, game_context=None):
        player.shot_count = 4

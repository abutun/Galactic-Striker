from .base_bonus import BaseBonus

class ShipAutofireBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/ship_autofire.png", (255, 192, 203), (24, 24))
    def apply(self, player, game_context=None):
        player.autofire = True

class ShieldBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/shield.png", (0, 0, 255), (24, 24))
    def apply(self, player, game_context=None):
        player.shield_active = True

class AlienScoopBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/alien_scoop.png", (255, 105, 180), (24, 24))
    def apply(self, player, game_context=None):
        player.scoop_active = True

class MoneyBombBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/money_bomb.png", (255, 215, 0), (24, 24))
    def apply(self, player, game_context=None):
        if game_context and "enemy_group" in game_context:
            for enemy in list(game_context["enemy_group"]):
                enemy.kill()
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].add_points(500)

class GemBombBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/gem_bomb.png", (0, 255, 255), (24, 24))
    def apply(self, player, game_context=None):
        if game_context and "enemy_group" in game_context:
            for enemy in list(game_context["enemy_group"]):
                enemy.kill()
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].add_points(100)

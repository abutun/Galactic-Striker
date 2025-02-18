from .base_bonus import Bonus

class ShipAutofireBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/ship_autofire.png", (255, 255, 0), (24, 24))
    def apply(self, player, game_context=None):
        player.autofire = True

class ShieldBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/shield.png", (0, 0, 255), (24, 24))
    def apply(self, player, game_context=None):
        player.shield_active = True

class AlienScoopBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/alien_scoop.png", (0, 255, 0), (24, 24))
    def apply(self, player, game_context=None):
        player.scoop_active = True
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].add_score(500)

class MoneyBombBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/money_bomb.png", (255, 215, 0), (24, 24))
    def apply(self, player, game_context=None):
        player.money += 1000
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].add_score(1000)

class GemBombBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/gem_bomb.png", (147, 112, 219), (24, 24))
    def apply(self, player, game_context=None):
        player.money += 2000
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].add_score(2000)

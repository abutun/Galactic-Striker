from .base_bonus import Bonus

class DecreaseStrengthRedBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/decrease_strength_red.png", (255, 0, 0), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if hasattr(player, 'weapon_level'):
            player.weapon_level = max(1, player.weapon_level - 1)
        player.speed = max(1, player.speed - 1)

class DecreaseStrengthGreenBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/decrease_strength_green.png", (0, 255, 0), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if hasattr(player, 'weapon_level'):
            player.weapon_level = max(1, player.weapon_level - 1)
        if hasattr(player, 'time_stat'):
            player.time_stat = max(1, player.time_stat - 1)

class DecreaseStrengthBlueBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/decrease_strength_blue.png", (0, 0, 255), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if hasattr(player, 'weapon_level'):
            player.weapon_level = max(1, player.weapon_level - 1)
        if hasattr(player, 'bullet_count'):
            player.bullet_count = max(1, player.bullet_count - 1)

class X2ScoreMultiplierBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/x2_multiplier.png", (255, 255, 255), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].activate_multiplier(2, 10)

class X5ScoreMultiplierBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/x5_multiplier.png", (255, 255, 255), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].activate_multiplier(5, 5)

class CashDoublerBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/cash_doubler.png", (255, 215, 0), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if hasattr(player, 'money'):
            if player.money > 500000:
                pass
            else:
                player.money *= 2
        else:
            player.money = 0

class MirrorModeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/mirror_mode.png", (200, 200, 200), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        player.mirror_mode = True

class DrunkModeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/drunk_mode.png", (200, 200, 200), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        player.drunk_mode = True

class FreezeModeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/freeze_mode.png", (173, 216, 230), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "enemy_group" in game_context:
            for enemy in list(game_context["enemy_group"]):
                enemy.freeze = True

class WarpForwardBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/warp_forward.png", (255, 255, 255), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "warp_forward" in game_context:
            game_context["warp_forward"]()

from .base_bonus import Bonus

class ExtraLifeBonus(Bonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_life.png", (0, 255, 0), (24, 24))
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if hasattr(player, 'lives'):
            if player.lives < 4:
                player.lives += 1
            else:
                if hasattr(player, 'armour'):
                    player.armour += 1
                else:
                    player.armour = 1
        else:
            player.lives = 1

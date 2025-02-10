from .base_bonus import BaseBonus

class ExtraSpeedBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_speed.png", (0, 0, 255), (24, 24))
    def apply(self, player, game_context=None):
        player.speed += 2

class ExtraBulletBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_bullet.png", (255, 165, 0), (24, 24))
    def apply(self, player, game_context=None):
        if hasattr(player, 'bullet_count'):
            player.bullet_count += 1
        else:
            player.bullet_count = 1

class ExtraTimeBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_time.png", (0, 255, 0), (24, 24))
    def apply(self, player, game_context=None):
        if hasattr(player, 'time_stat'):
            player.time_stat += 5
        else:
            player.time_stat = 5

class ExtraBulletSpeedBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/extra_bullet_speed.png", (255, 0, 0), (24, 24))
    def apply(self, player, game_context=None):
        if hasattr(player, 'bullet_speed'):
            player.bullet_speed += 2
        else:
            player.bullet_speed = 2

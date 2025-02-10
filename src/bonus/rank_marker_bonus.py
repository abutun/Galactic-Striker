from .base_bonus import BaseBonus

class RankMarkerBonus(BaseBonus):
    def __init__(self, x, y, color):
        image_path = f"assets/sprites/rank_marker_{color}.png"
        super().__init__(x, y, image_path, (128, 128, 128), (24, 24))
        self.color = color
    def apply(self, player, game_context=None):
        if not hasattr(player, 'rank_markers'):
            player.rank_markers = []
        player.rank_markers.append(self.color)

class RankMarkerDarkPurpleBonus(BaseBonus):
    def __init__(self, x, y):
        super().__init__(x, y, "assets/sprites/rank_marker_darkpurple.png", (64, 0, 64), (24, 24))
    def apply(self, player, game_context=None):
        if hasattr(player, 'rank'):
            player.rank = max(0, player.rank - 1)
        else:
            player.rank = 0

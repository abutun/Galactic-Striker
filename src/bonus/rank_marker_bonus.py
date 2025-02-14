from .base_bonus import BaseBonus

class RankMarkerBonus(BaseBonus):
    def __init__(self, x, y, color="red"):
        # Use the provided color (default "red") to construct the filename.
        image_path = f"assets/sprites/rank_marker_{color}.png"
        super().__init__(x, y, image_path, (128, 128, 128), (24, 24))
        self.color = color

    def apply(self, player, game_context=None):
        if not hasattr(player, 'rank_markers'):
            player.rank_markers = []
        player.rank_markers.append(self.color)

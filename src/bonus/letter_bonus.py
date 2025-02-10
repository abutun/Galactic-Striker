from .base_bonus import BaseBonus

class ExtraLetterBonus(BaseBonus):
    def __init__(self, x, y, letter):
        image_path = f"assets/sprites/letter_{letter}.png"
        super().__init__(x, y, image_path, (255, 255, 255), (24, 24))
        self.letter = letter
    def apply(self, player, game_context=None):
        if not hasattr(player, 'letters'):
            player.letters = []
        player.letters.append(self.letter)

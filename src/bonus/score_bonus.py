from .base_bonus import Bonus

class ScoreMultiplierBonus(Bonus):
    def __init__(self, x, y, multiplier=2):
        super().__init__(x, y, f"assets/sprites/x{multiplier}_multiplier.png", (255, 215, 0), (24, 24))
        self.multiplier = multiplier
        
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if game_context and "score_manager" in game_context:
            game_context["score_manager"].set_multiplier(self.multiplier)

class LetterCollectionBonus(Bonus):
    def __init__(self, x, y, letter):
        super().__init__(x, y, f"assets/sprites/letter_{letter}.png", (255, 255, 255), (24, 24))
        self.letter = letter
        
    def apply(self, player, game_context=None):
        self.sound_manager.play("bonus_reward")
        if not hasattr(player, 'collected_letters'):
            player.collected_letters = []
        player.collected_letters.append(self.letter)
        
        # Check for complete words
        if game_context and "score_manager" in game_context:
            if self._check_word_completion(player.collected_letters):
                game_context["score_manager"].add_score(10000)  # Bonus for completing a word
                
    def _check_word_completion(self, letters):
        # Example words to check
        bonus_words = ["BONUS", "EXTRA", "POWER"]
        letters_str = ''.join(letters)
        return any(word in letters_str for word in bonus_words) 
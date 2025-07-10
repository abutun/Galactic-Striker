import random
import logging
from typing import Optional, Dict, List, Tuple, Type

from src.bonus import (
    MoneyBonus10, MoneyBonus50, MoneyBonus100, MoneyBonus200,
    SingleShotBonus, DoubleShotBonus, TripleShotBonus, QuadShotBonus,
    ExtraSpeedBonus, ExtraBulletBonus, ExtraTimeBonus, ExtraBulletSpeedBonus,
    ExtraLifeBonus, ShipAutofireBonus, AlienScoopBonus, MoneyBombBonus,
    GemBombBonus, MirrorModeBonus, DrunkModeBonus, FreezeModeBonus,
    WarpForwardBonus, CashDoublerBonus, DecreaseStrengthRedBonus,
    DecreaseStrengthGreenBonus, DecreaseStrengthBlueBonus,
    X2ScoreMultiplierBonus, X3ScoreMultiplierBonus, X4ScoreMultiplierBonus,
    X5ScoreMultiplierBonus, BonusMeteorstormBonus, BonusMemorystationBonus,
    RankMarker, LetterBonus
)

logger = logging.getLogger(__name__)


class RewardManager:
    """Manages reward spawning and distribution."""
    
    def __init__(self):
        self.reward_groups = self._initialize_reward_groups()
    
    def _initialize_reward_groups(self) -> Dict[Tuple[float, float], List[Tuple[Type, float]]]:
        """Initialize reward groups with probabilities."""
        return {
            # Money bonuses (15%)
            (0, 0.15): [
                (MoneyBonus10, 0.4),     # 6%
                (MoneyBonus50, 0.3),     # 4.5%
                (MoneyBonus100, 0.2),    # 3%
                (MoneyBonus200, 0.1)     # 1.5%
            ],
            # Weapon bonuses (15%)
            (0.15, 0.30): [
                (SingleShotBonus, 0.25),   # 3.75%
                (DoubleShotBonus, 0.25),   # 3.75%
                (TripleShotBonus, 0.25),   # 3.75%
                (QuadShotBonus, 0.25),     # 3.75%
            ],
            # Stat bonuses (15%)
            (0.30, 0.45): [
                (ExtraSpeedBonus, 0.25),       # 3.75%
                (ExtraBulletBonus, 0.25),      # 3.75%
                (ExtraTimeBonus, 0.25),        # 3.75%
                (ExtraBulletSpeedBonus, 0.25)  # 3.75%
            ],
            # Special bonuses (15%)
            (0.45, 0.60): [
                (ShipAutofireBonus, 0.2),    # 3%
                (AlienScoopBonus, 0.2),      # 3%
                (MoneyBombBonus, 0.2),       # 3%
                (GemBombBonus, 0.2),         # 3%
                (ExtraLifeBonus, 0.2)        # 3%
            ],
            # Game mode bonuses (15%)
            (0.60, 0.75): [
                (MirrorModeBonus, 0.2),      # 3%
                (DrunkModeBonus, 0.2),       # 3%
                (FreezeModeBonus, 0.2),      # 3%
                (WarpForwardBonus, 0.2),     # 3%
                (CashDoublerBonus, 0.2)      # 3%
            ],
            # Modifier bonuses (15%)
            (0.75, 0.90): [
                (DecreaseStrengthRedBonus, 0.15),    # 2.25%
                (DecreaseStrengthGreenBonus, 0.15),  # 2.25%
                (DecreaseStrengthBlueBonus, 0.15),   # 2.25%
                (X2ScoreMultiplierBonus, 0.15),      # 2.25%
                (X3ScoreMultiplierBonus, 0.15),      # 2.25%
                (X4ScoreMultiplierBonus, 0.15),      # 2.25%
                (X5ScoreMultiplierBonus, 0.15),      # 2.25%                 
                (BonusMeteorstormBonus, 0.125),      # 1.875%
                (BonusMemorystationBonus, 0.125)     # 1.875%
            ],
            # Collection bonuses (10%)
            (0.90, 1.0): [
                (lambda x, y: RankMarker(x, y, random.choice(['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'dark_purple'])), 0.4),    # 4%
                (lambda x, y: LetterBonus(x, y, random.choice('EXTRA')), 0.6)  # 6%
            ]
        }
    
    def calculate_spawn_chance(self, level: int) -> float:
        """Calculate spawn chance based on level."""
        base_chance = 0.15 + (min(level, 100) * 0.001)  # Max +10% at level 100
        return base_chance
    
    def spawn_reward(self, position: Tuple[int, int], level: int, sound_manager) -> Optional[object]:
        """Spawn a reward at the given position."""
        try:
            # Check if we should spawn a reward
            if random.random() > self.calculate_spawn_chance(level):
                return None
            
            # Select reward group
            chance = random.random()
            for (min_prob, max_prob), rewards in self.reward_groups.items():
                if min_prob <= chance < max_prob:
                    return self._select_reward_from_group(rewards, position, sound_manager)
            
            return None
            
        except Exception as e:
            logger.error(f"Error spawning reward: {e}")
            return None
    
    def _select_reward_from_group(self, rewards: List[Tuple[Type, float]], 
                                 position: Tuple[int, int], sound_manager) -> Optional[object]:
        """Select a specific reward from a group."""
        sub_chance = random.random()
        cumulative = 0
        
        for reward_class, prob in rewards:
            cumulative += prob
            if sub_chance <= cumulative:
                reward = reward_class(position[0], position[1])
                reward.sound_manager = sound_manager
                logger.info(f"Spawned reward: {reward.__class__.__name__} at position {position}")
                return reward
        
        return None 
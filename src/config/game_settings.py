"""Game configuration settings."""

# Level progression and difficulty settings
LEVEL_PROGRESSION = {
    (1, 25): {
        "diff_range": (1, 3),
        "alien_types": (1, 5),
        "description": "Tutorial levels",
        "boss_life": 50,
        "group_size": (2, 4)
    },
    (26, 50): {
        "diff_range": (2, 4),
        "alien_types": (4, 8),
        "description": "Early game",
        "boss_life": 75,
        "group_size": (3, 5)
    },
    (51, 100): {
        "diff_range": (3, 5),
        "alien_types": (7, 12),
        "description": "Mid game",
        "boss_life": 100,
        "group_size": (3, 6)
    },
    (101, 150): {
        "diff_range": (4, 7),
        "alien_types": (10, 15),
        "description": "Late game",
        "boss_life": 150,
        "group_size": (4, 7)
    },
    (151, 200): {
        "diff_range": (6, 8),
        "alien_types": (13, 20),
        "description": "Expert levels",
        "boss_life": 200,
        "group_size": (4, 8)
    },
    (201, 250): {
        "diff_range": (7, 10),
        "alien_types": (15, 25),
        "description": "Master levels",
        "boss_life": 250,
        "group_size": (5, 9)
    }
}

# Alien type settings
ALIEN_SETTINGS = {
    "small": {
        "base_life": 1,
        "base_points": 100,
        "size": (64, 64),
        "speed_modifier": 1.2,
        "shoot_interval": 2.0
    },
    "large": {
        "base_life": 3,
        "base_points": 200,
        "size": (96, 96),
        "speed_modifier": 0.8,
        "shoot_interval": 1.5
    },
    "boss": {
        "base_points": 1000,
        "size": (196, 196),
        "speed_modifier": 0.6,
        "shoot_interval": 1.0,
        "minion_count": (2, 4)
    }
}

# Formation settings
FORMATIONS = {
    "line": {
        "spacing": (30, 50),
        "group_behavior_chance": 0.4
    },
    "v": {
        "spacing": (40, 60),
        "group_behavior_chance": 0.6
    },
    "circle": {
        "spacing": (45, 65),
        "group_behavior_chance": 0.7
    },
    "diamond": {
        "spacing": (35, 55),
        "group_behavior_chance": 0.8
    },
    "wave": {
        "spacing": (25, 45),
        "group_behavior_chance": 0.5
    }
}

# Movement patterns unlocked by difficulty
MOVEMENT_PATTERNS = {
    "straight": {"min_difficulty": 1},
    "zigzag": {"min_difficulty": 3},
    "wave": {"min_difficulty": 3},
    "circular": {"min_difficulty": 5},
    "swarm": {"min_difficulty": 5},
    "random": {"min_difficulty": 7},
    "boss": {"min_difficulty": 1}  # Boss-specific pattern
}

# Special effects and bonuses
SPECIAL_EFFECTS = {
    "bonus_multiplier": 3.0,  # Score multiplier for bonus levels
    "boss_minion_boost": 2,  # life/damage boost for boss minions
    "difficulty_scaling": 0.1  # Per-level scaling factor
}

PLAYER_SETTINGS = {
    "size": (64, 64),
    "speed": 5,
    "life": 3,
    "shield": 0,
    "lives": 3,
    "bullet_speed": 7,
    "animation_speed": 0.2,  # Seconds per frame
    "sprite_sheet": {
        "rows": 3,
        "cols": 3,
        "frame_size": 341  # 1024/3 rounded down
    }
}

# Play area boundaries (percentage of screen width)
PLAY_AREA = {
    "left_boundary": 0.115,  # 11.5% from left
    "right_boundary": 0.885,  # 88.5% from left
    "width_percentage": 0.77,  # 77% of screen width for play area
} 
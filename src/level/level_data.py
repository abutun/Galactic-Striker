from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
import pygame
import json

class Movement(Enum):
    STRAIGHT = "straight"
    ZIGZAG = "zigzag"
    CIRCULAR = "circular"
    WAVE = "wave"
    SWARM = "swarm"
    RANDOM = "random"
    CHASE = "chase"
    TELEPORT = "teleport"

class Formation(Enum):
    LINE = "line"
    V = "v"
    CIRCLE = "circle"
    DIAMOND = "diamond"
    WAVE = "wave"
    CROSS = "cross"
    SPIRAL = "spiral"
    STAR = "star"

class EntryPoint(Enum):
    TOP_CENTER = "top_center"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    LEFT_TOP = "left_top"
    RIGHT_TOP = "right_top"

@dataclass
class PathPoint:
    x: float  # Relative x position (0-1)
    y: float  # Relative y position (0-1)
    wait_time: float = 0  # Time to wait at this point in seconds
    shoot: bool = False  # Whether to shoot at this point

@dataclass
class AlienGroup:
    alien_type: str
    count: int
    formation: Formation
    spacing: int
    entry_point: EntryPoint
    path: List[PathPoint]
    movement_pattern: Movement
    speed: float
    health: int
    shoot_interval: float
    group_behavior: bool = False  # Whether aliens move as a group

@dataclass
class LevelData:
    level_number: int
    name: str
    difficulty: int  # 1-10
    alien_groups: List[AlienGroup]
    boss_data: Optional[Dict] = None
    background_speed: float = 1.0
    music_track: Optional[str] = None
    special_effects: List[str] = None
    
    # Add new fields for better game progression
    power_up_frequency: float = 0.2  # Chance of power-up drops
    minimum_clear_time: float = 30.0  # Minimum time to clear level
    bonus_objectives: List[str] = None  # Optional bonus objectives
    hazard_types: List[str] = None  # Environmental hazards 
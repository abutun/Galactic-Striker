from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Any
import random
import math
import logging

logger = logging.getLogger(__name__)

class NodeStatus(Enum):
    SUCCESS = 1
    FAILURE = 2
    RUNNING = 3

class Node(ABC):
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> NodeStatus:
        pass

class Sequence(Node):
    def __init__(self, children: List[Node]):
        self.children = children
        self.current_child = 0
        
    def execute(self, context: Dict[str, Any]) -> NodeStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].execute(context)
            
            if status == NodeStatus.FAILURE:
                self.current_child = 0
                return NodeStatus.FAILURE
                
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
                
            self.current_child += 1
            
        self.current_child = 0
        return NodeStatus.SUCCESS

class Selector(Node):
    def __init__(self, children: List[Node]):
        self.children = children
        self.current_child = 0
        
    def execute(self, context: Dict[str, Any]) -> NodeStatus:
        while self.current_child < len(self.children):
            status = self.children[self.current_child].execute(context)
            
            if status == NodeStatus.SUCCESS:
                self.current_child = 0
                return NodeStatus.SUCCESS
                
            if status == NodeStatus.RUNNING:
                return NodeStatus.RUNNING
                
            self.current_child += 1
            
        self.current_child = 0
        return NodeStatus.FAILURE

# Concrete behavior nodes
class MoveTowardsPlayer(Node):
    def execute(self, context: Dict[str, Any]) -> NodeStatus:
        try:
            enemy = context.get('enemy')
            player = context.get('player')
            
            if not enemy or not player:
                return NodeStatus.FAILURE
                
            dx = player.rect.centerx - enemy.rect.centerx
            dy = player.rect.centery - enemy.rect.centery
            dist = math.hypot(dx, dy)
            
            if dist < 5:
                return NodeStatus.SUCCESS
                
            speed = enemy.speed
            enemy.rect.x += (dx / dist) * speed
            enemy.rect.y += (dy / dist) * speed
            
            return NodeStatus.RUNNING
            
        except Exception as e:
            logger.error(f"Error in MoveTowardsPlayer: {e}")
            return NodeStatus.FAILURE

class FireAtPlayer(Node):
    def execute(self, context: Dict[str, Any]) -> NodeStatus:
        try:
            enemy = context.get('enemy')
            player = context.get('player')
            
            if not enemy or not player:
                return NodeStatus.FAILURE
                
            if hasattr(enemy, 'fire') and callable(enemy.fire):
                enemy.fire()
                return NodeStatus.SUCCESS
                
            return NodeStatus.FAILURE
            
        except Exception as e:
            logger.error(f"Error in FireAtPlayer: {e}")
            return NodeStatus.FAILURE

class FollowPath(Node):
    def execute(self, context: Dict[str, Any]) -> NodeStatus:
        try:
            enemy = context.get('enemy')
            if not enemy or not enemy.path:
                return NodeStatus.FAILURE
                
            return enemy.follow_path()
            
        except Exception as e:
            logger.error(f"Error in FollowPath: {e}")
            return NodeStatus.FAILURE 
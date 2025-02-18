from typing import List, Tuple, Set
import pygame
import logging

logger = logging.getLogger(__name__)

class QuadTree:
    def __init__(self, boundary: pygame.Rect, capacity: int):
        self.boundary = boundary
        self.capacity = capacity
        self.objects: List[pygame.sprite.Sprite] = []
        self.divided = False
        self.northwest: 'QuadTree' = None
        self.northeast: 'QuadTree' = None
        self.southwest: 'QuadTree' = None
        self.southeast: 'QuadTree' = None
        
    def subdivide(self) -> None:
        """Subdivide this quad into four quads."""
        x, y = self.boundary.x, self.boundary.y
        w, h = self.boundary.width / 2, self.boundary.height / 2
        
        nw = pygame.Rect(x, y, w, h)
        ne = pygame.Rect(x + w, y, w, h)
        sw = pygame.Rect(x, y + h, w, h)
        se = pygame.Rect(x + w, y + h, w, h)
        
        self.northwest = QuadTree(nw, self.capacity)
        self.northeast = QuadTree(ne, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)
        self.divided = True
        
    def insert(self, sprite: pygame.sprite.Sprite) -> bool:
        """Insert a sprite into the quadtree."""
        if not self.boundary.colliderect(sprite.rect):
            return False
            
        if len(self.objects) < self.capacity and not self.divided:
            self.objects.append(sprite)
            return True
            
        if not self.divided:
            self.subdivide()
            
        return (self.northwest.insert(sprite) or
                self.northeast.insert(sprite) or
                self.southwest.insert(sprite) or
                self.southeast.insert(sprite))
                
    def query(self, range_rect: pygame.Rect, found: Set[pygame.sprite.Sprite] = None) -> Set[pygame.sprite.Sprite]:
        """Find all sprites that could collide with the given range."""
        if found is None:
            found = set()
            
        if not self.boundary.colliderect(range_rect):
            return found
            
        for sprite in self.objects:
            if range_rect.colliderect(sprite.rect):
                found.add(sprite)
                
        if self.divided:
            self.northwest.query(range_rect, found)
            self.northeast.query(range_rect, found)
            self.southwest.query(range_rect, found)
            self.southeast.query(range_rect, found)
            
        return found

class CollisionManager:
    def __init__(self, screen_size: Tuple[int, int]):
        self.screen_rect = pygame.Rect(0, 0, *screen_size)
        self.quadtree = None
        
    def update(self, sprite_groups: List[pygame.sprite.Group]) -> None:
        """Update the collision detection system."""
        try:
            # Create new quadtree each frame
            self.quadtree = QuadTree(self.screen_rect, 4)
            
            # Insert all sprites
            for group in sprite_groups:
                for sprite in group:
                    self.quadtree.insert(sprite)
                    
        except Exception as e:
            logger.error(f"Error updating collision system: {e}")
            
    def check_collisions(self, sprite: pygame.sprite.Sprite, group: pygame.sprite.Group) -> List[pygame.sprite.Sprite]:
        """Check collisions between a sprite and a group using spatial partitioning."""
        try:
            if not self.quadtree:
                return []
                
            # Get potential collision candidates
            candidates = self.quadtree.query(sprite.rect)
            
            # Filter candidates to only include sprites from the target group
            collisions = []
            for candidate in candidates:
                if candidate in group and sprite.rect.colliderect(candidate.rect):
                    collisions.append(candidate)
                    
            return collisions
            
        except Exception as e:
            logger.error(f"Error checking collisions: {e}")
            return [] 
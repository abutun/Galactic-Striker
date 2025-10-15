import logging
from typing import List, Type, Optional

logger = logging.getLogger(__name__)


class ObjectPool:
    """Generic object pool for managing reusable game objects."""
    
    def __init__(self, object_class: Type, initial_size: int = 10, max_size: int = 100):
        self.object_class = object_class
        self.max_size = max_size
        self.available_objects: List = []
        self.active_objects: List = []
        
        # Pre-create initial objects
        for _ in range(initial_size):
            self.available_objects.append(object_class())
    
    def get_object(self, *args, **kwargs) -> Optional[object]:
        """Get an object from the pool."""
        if self.available_objects:
            obj = self.available_objects.pop()
            self.active_objects.append(obj)
            # Reset object state
            if hasattr(obj, 'reset'):
                obj.reset(*args, **kwargs)
            return obj
        elif len(self.active_objects) < self.max_size:
            # Create new object if pool not at max capacity
            obj = self.object_class(*args, **kwargs)
            self.active_objects.append(obj)
            return obj
        else:
            logger.warning(f"Object pool for {self.object_class.__name__} is full")
            return None
    
    def return_object(self, obj: object):
        """Return an object to the pool."""
        if obj in self.active_objects:
            self.active_objects.remove(obj)
            self.available_objects.append(obj)
    
    def cleanup_inactive(self):
        """Remove objects that are no longer active."""
        active_copy = self.active_objects.copy()
        for obj in active_copy:
            if hasattr(obj, 'alive') and not obj.alive():
                self.return_object(obj)


class BulletPool(ObjectPool):
    """Specialized pool for bullet objects."""
    
    def __init__(self, bullet_class: Type, initial_size: int = 20):
        super().__init__(bullet_class, initial_size, max_size=200)
    
    def get_bullet(self, x: int, y: int, vx: float, vy: float, damage: int = 1):
        """Get a bullet from the pool with specific parameters."""
        bullet = self.get_object()
        if bullet:
            bullet.rect.x = x
            bullet.rect.y = y
            bullet.vx = vx
            bullet.vy = vy
            bullet.damage = damage
        return bullet


class ParticlePool(ObjectPool):
    """Specialized pool for particle effects."""
    
    def __init__(self, particle_class: Type, initial_size: int = 50):
        super().__init__(particle_class, initial_size, max_size=500)
    
    def create_explosion(self, x: int, y: int, particle_count: int = 10):
        """Create an explosion effect using pooled particles."""
        particles = []
        for _ in range(particle_count):
            particle = self.get_object()
            if particle:
                particle.set_explosion_params(x, y)
                particles.append(particle)
        return particles 
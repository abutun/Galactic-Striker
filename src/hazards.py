class Asteroid:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.rotation = random.random() * 360
        self.speed = random.uniform(50, 100)
        
    def update(self, dt):
        self.y += self.speed * dt
        self.rotation += 45 * dt
        
class SpaceStorm:
    def __init__(self):
        self.particles = []
        self.damage_per_second = 10
        self.slow_factor = 0.7
        
    def affect_player(self, player, dt):
        player.speed *= self.slow_factor
        player.take_damage(self.damage_per_second * dt) 
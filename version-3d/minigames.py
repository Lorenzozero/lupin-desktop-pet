import random
import math

class MiniGame:
    def __init__(self, name):
        self.name = name
        self.active = False
        self.score = 0
        
    def start(self):
        self.active = True
        self.score = 0
        
    def end(self):
        self.active = False
        return self.score
        
class CatchTheIcon(MiniGame):
    """Mini-game: clicca le icone prima che scompaiano"""
    def __init__(self):
        super().__init__("Catch The Icon")
        self.targets = []
        self.time_limit = 30
        self.timer = 0
        
    def start(self):
        super().start()
        self.timer = self.time_limit
        self._spawn_targets()
        
    def _spawn_targets(self, count=5):
        # Genera posizioni casuali per icone
        for _ in range(count):
            self.targets.append({
                "x": random.randint(100, 1920 - 100),
                "y": random.randint(100, 1080 - 100),
                "lifetime": random.uniform(2, 5)
            })
            
    def update(self, dt):
        if not self.active:
            return
            
        self.timer -= dt
        if self.timer <= 0:
            self.end()
            return
            
        # Update targets
        for target in self.targets:
            target["lifetime"] -= dt
            
        self.targets = [t for t in self.targets if t["lifetime"] > 0]
        
        # Spawn nuovi se necessario
        if len(self.targets) < 3:
            self._spawn_targets(2)
            
    def on_click(self, x, y):
        """Controlla se click ha colpito un target"""
        for target in self.targets:
            dist = math.hypot(target["x"] - x, target["y"] - y)
            if dist < 40:
                self.targets.remove(target)
                self.score += 10
                return True
        return False
        
class PetRace(MiniGame):
    """Mini-game: corri dall'inizio alla fine evitando ostacoli"""
    def __init__(self):
        super().__init__("Pet Race")
        self.obstacles = []
        self.finish_line = 1800
        self.player_x = 100
        
    def start(self):
        super().start()
        self.player_x = 100
        self._generate_obstacles()
        
    def _generate_obstacles(self):
        for i in range(10):
            self.obstacles.append({
                "x": 300 + i * 150,
                "y": random.randint(200, 800),
                "radius": random.randint(30, 60)
            })
            
    def update(self, dt, player_vx):
        if not self.active:
            return
            
        self.player_x += player_vx * dt
        
        if self.player_x >= self.finish_line:
            self.score = 100
            self.end()
            
    def check_collision(self, player_y):
        """Controlla collisione con ostacoli"""
        for obs in self.obstacles:
            dist = math.hypot(obs["x"] - self.player_x, obs["y"] - player_y)
            if dist < obs["radius"] + 30:
                self.score -= 10
                return True
        return False
        
class IconMemory(MiniGame):
    """Mini-game: memorizza sequenza di icone"""
    def __init__(self):
        super().__init__("Icon Memory")
        self.sequence = []
        self.player_sequence = []
        self.level = 1
        
    def start(self):
        super().start()
        self.level = 1
        self._generate_sequence()
        
    def _generate_sequence(self):
        self.sequence = [random.randint(0, 7) for _ in range(3 + self.level)]
        self.player_sequence = []
        
    def on_input(self, icon_id):
        """Player clicca un'icona"""
        self.player_sequence.append(icon_id)
        
        if len(self.player_sequence) == len(self.sequence):
            if self.player_sequence == self.sequence:
                self.score += 10 * self.level
                self.level += 1
                self._generate_sequence()
            else:
                self.end()

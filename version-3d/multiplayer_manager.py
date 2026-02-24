import random
import math
from panda3d.core import Vec3

class PetInstance:
    """Istanza di un pet nel multiplayer"""
    def __init__(self, id, name, personality, color, position):
        self.id = id
        self.name = name
        self.personality = personality
        self.color = color
        self.x, self.y = position
        self.vx, self.vy = 0.0, 0.0
        self.stolen = []
        self.state = "idle"
        self.model_node = None
        
class MultiplayerManager:
    """Sistema multiplayer locale (più pet sullo stesso desktop)"""
    
    def __init__(self, sw, sh, render):
        self.sw = sw
        self.sh = sh
        self.render = render
        self.pets = []
        self.max_pets = 4
        
    def spawn_pet(self, name, personality=None, color=None):
        """Spawna un nuovo pet"""
        if len(self.pets) >= self.max_pets:
            print(f"[Multiplayer] Limite raggiunto: {self.max_pets} pet")
            return None
            
        pet_id = len(self.pets)
        
        if not personality:
            personality = random.choice(["aggressive", "playful", "sneaky"])
            
        if not color:
            colors = [
                (0.3, 0.5, 0.9),  # blu
                (0.9, 0.3, 0.3),  # rosso
                (0.3, 0.9, 0.5),  # verde
                (0.9, 0.7, 0.2),  # oro
            ]
            color = colors[pet_id % len(colors)]
            
        # Spawn in posizione casuale
        position = (random.randint(100, self.sw - 100), random.randint(100, self.sh - 100))
        
        pet = PetInstance(pet_id, name, personality, color, position)
        self.pets.append(pet)
        
        print(f"[Multiplayer] Pet '{name}' spawnato (ID: {pet_id}, Personalit\u00e0: {personality})")
        return pet
        
    def remove_pet(self, pet_id):
        """Rimuove un pet"""
        self.pets = [p for p in self.pets if p.id != pet_id]
        print(f"[Multiplayer] Pet {pet_id} rimosso")
        
    def update(self, dt, icons):
        """Update logic per tutti i pet"""
        for pet in self.pets:
            self._update_pet(pet, dt, icons)
            
        # Interazioni tra pet
        self._check_pet_collisions()
        
    def _update_pet(self, pet, dt, icons):
        """Update singolo pet (AI semplificata)"""
        # Movimento casuale
        if random.random() < 0.02:
            pet.vx = random.uniform(-5, 5)
            pet.vy = random.uniform(-5, 5)
            
        pet.x += pet.vx * dt
        pet.y += pet.vy * dt
        
        # Boundary
        pet.x = max(50, min(self.sw - 50, pet.x))
        pet.y = max(50, min(self.sh - 50, pet.y))
        
        # Friction
        pet.vx *= 0.95
        pet.vy *= 0.95
        
        # Aggiorna posizione modello 3D se presente
        if pet.model_node:
            # Converti screen -> world
            pass
            
    def _check_pet_collisions(self):
        """Controlla collisioni tra pet"""
        for i, pet1 in enumerate(self.pets):
            for pet2 in self.pets[i+1:]:
                dist = math.hypot(pet1.x - pet2.x, pet1.y - pet2.y)
                
                if dist < 100:
                    # Bounce
                    dx = pet2.x - pet1.x
                    dy = pet2.y - pet1.y
                    if dist > 0:
                        dx /= dist
                        dy /= dist
                        
                    force = (100 - dist) * 0.5
                    pet1.vx -= dx * force
                    pet1.vy -= dy * force
                    pet2.vx += dx * force
                    pet2.vy += dy * force
                    
                    # Easter egg: se si scontrano mentre hanno icone, le scambiano
                    if pet1.stolen and pet2.stolen and random.random() < 0.1:
                        pet1.stolen, pet2.stolen = pet2.stolen, pet1.stolen
                        print(f"[Multiplayer] {pet1.name} e {pet2.name} hanno scambiato il bottino!")

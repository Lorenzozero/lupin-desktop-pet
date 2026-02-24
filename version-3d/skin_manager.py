import os
import json
from panda3d.core import Vec4, Texture

class Skin:
    def __init__(self, id, name, description, color_scheme, particles, unlock_condition):
        self.id = id
        self.name = name
        self.description = description
        self.color_scheme = color_scheme  # {"primary": Vec4, "secondary": Vec4}
        self.particles = particles  # tipo particelle custom
        self.unlock_condition = unlock_condition
        self.unlocked = False
        
class SkinManager:
    """Sistema customizzazione skin del pet"""
    
    def __init__(self):
        self.skins = {}
        self.current_skin = "default"
        self.save_file = "skins.json"
        self._init_skins()
        self._load_unlocked()
        
    def _init_skins(self):
        # Default
        self.register(Skin(
            "default", "Lupin Classico", "Il ladro originale",
            {"primary": Vec4(0.3, 0.5, 0.9, 1), "secondary": Vec4(0.1, 0.1, 0.1, 1)},
            "gold", None
        ))
        
        # Unlockable
        self.register(Skin(
            "gold", "Re Mida", "Tutto ciò che tocca diventa oro",
            {"primary": Vec4(1.0, 0.84, 0.0, 1), "secondary": Vec4(0.8, 0.6, 0.0, 1)},
            "gold_sparkle", "master_thief"
        ))
        
        self.register(Skin(
            "rainbow", "Arcobaleno", "Colori che cambiano dinamicamente",
            {"primary": Vec4(1, 0, 0, 1), "secondary": Vec4(0, 0, 1, 1)},
            "rainbow", "hoarder"
        ))
        
        self.register(Skin(
            "ghost", "Fantasma", "Semi-trasparente e spettrale",
            {"primary": Vec4(0.8, 0.8, 1.0, 0.5), "secondary": Vec4(0.5, 0.5, 0.8, 0.5)},
            "ghost_trail", "ninja"
        ))
        
        self.register(Skin(
            "fire", "Infernale", "Tracce di fuoco",
            {"primary": Vec4(1.0, 0.3, 0.0, 1), "secondary": Vec4(0.8, 0.0, 0.0, 1)},
            "fire", "combo_master"
        ))
        
        self.register(Skin(
            "ice", "Glaciale", "Congelato nel tempo",
            {"primary": Vec4(0.5, 0.8, 1.0, 1), "secondary": Vec4(0.7, 0.9, 1.0, 1)},
            "ice_crystal", "untouchable"
        ))
        
        self.register(Skin(
            "neon", "Cyber", "Estetica cyberpunk",
            {"primary": Vec4(0.0, 1.0, 1.0, 1), "secondary": Vec4(1.0, 0.0, 1.0, 1)},
            "neon_glow", "speedrun"
        ))
        
    def register(self, skin):
        self.skins[skin.id] = skin
        if skin.unlock_condition is None:
            skin.unlocked = True
            
    def unlock_skin(self, skin_id):
        if skin_id in self.skins:
            self.skins[skin_id].unlocked = True
            print(f"[Skins] ✨ Skin '{self.skins[skin_id].name}' sbloccata!")
            self._save_unlocked()
            
    def set_skin(self, skin_id):
        if skin_id in self.skins and self.skins[skin_id].unlocked:
            self.current_skin = skin_id
            print(f"[Skins] Skin cambiata: {self.skins[skin_id].name}")
            return True
        return False
        
    def get_current(self):
        return self.skins[self.current_skin]
        
    def apply_to_model(self, model_node):
        """Applica skin al modello 3D"""
        skin = self.get_current()
        
        # Applica colori
        model_node.setColor(skin.color_scheme["primary"])
        
        # Se skin rainbow, attiva animazione colore
        if skin.id == "rainbow":
            # Implementa con LerpColorInterval
            pass
            
        # Se skin ghost, abbassa alpha
        if skin.id == "ghost":
            model_node.setAlphaScale(0.6)
        else:
            model_node.setAlphaScale(1.0)
            
    def _save_unlocked(self):
        data = {sid: skin.unlocked for sid, skin in self.skins.items()}
        with open(self.save_file, 'w') as f:
            json.dump(data, f)
            
    def _load_unlocked(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                for sid, unlocked in data.items():
                    if sid in self.skins:
                        self.skins[sid].unlocked = unlocked
            except Exception as e:
                print(f"[Skins] Errore caricamento: {e}")

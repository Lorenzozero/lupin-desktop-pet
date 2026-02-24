import json
import os
from datetime import datetime

class Achievement:
    def __init__(self, id, name, description, icon, condition, reward=None):
        self.id = id
        self.name = name
        self.description = description
        self.icon = icon
        self.condition = condition
        self.reward = reward
        self.unlocked = False
        self.unlock_date = None
        self.progress = 0
        self.target = condition.get('target', 1)
        
class AchievementSystem:
    """Sistema achievements con tracking persistente"""
    
    def __init__(self):
        self.achievements = {}
        self.save_file = "achievements.json"
        self._init_achievements()
        self._load_progress()
        
    def _init_achievements(self):
        """Definisce tutti gli achievements"""
        
        # Basic
        self.register(Achievement(
            "first_steal", "Primo Furto", "Ruba la tua prima icona",
            "🎒", {"type": "steal_count", "target": 1}, "unlock_voice_taunt"
        ))
        
        self.register(Achievement(
            "master_thief", "Maestro Ladro", "Ruba 100 icone totali",
            "🏆", {"type": "steal_count", "target": 100}, "unlock_skin_gold"
        ))
        
        # Speed
        self.register(Achievement(
            "speedrun", "Speedrunner", "Ruba 5 icone in meno di 30 secondi",
            "⚡", {"type": "speed_steal", "count": 5, "time": 30}, "unlock_speed_boost"
        ))
        
        # Combo
        self.register(Achievement(
            "combo_master", "Re dei Combo", "Raggiungi un combo x10",
            "🔥", {"type": "max_combo", "target": 10}, "unlock_particle_fire"
        ))
        
        # Stealth
        self.register(Achievement(
            "ninja", "Ninja", "Resta nascosto per 5 minuti senza essere trovato",
            "🥷", {"type": "hide_time", "target": 300}, "unlock_invisibility"
        ))
        
        # Evasion
        self.register(Achievement(
            "untouchable", "Intoccabile", "Evita il cursore per 2 minuti di fila",
            "👻", {"type": "evade_time", "target": 120}, "unlock_teleport"
        ))
        
        # Collection
        self.register(Achievement(
            "hoarder", "Accumulatore", "Ruba tutte le 8 icone in una sessione",
            "📦", {"type": "full_sack", "target": 8}, "unlock_skin_rainbow"
        ))
        
        # Persistence
        self.register(Achievement(
            "marathon", "Maratoneta", "Gioca per 1 ora consecutiva",
            "⏱️", {"type": "playtime", "target": 3600}, "unlock_emote_dance"
        ))
        
        # Easter eggs
        self.register(Achievement(
            "konami_code", "Codice Konami", "Inserisci il codice segreto",
            "🎮", {"type": "secret", "code": "konami"}, "unlock_god_mode"
        ))
        
        self.register(Achievement(
            "midnight_thief", "Ladro di Mezzanotte", "Gioca alle 00:00",
            "🌙", {"type": "time_specific", "hour": 0}, "unlock_moon_particles"
        ))
        
    def register(self, achievement):
        self.achievements[achievement.id] = achievement
        
    def check(self, event_type, value=1, **kwargs):
        """Controlla se evento sblocca achievements"""
        unlocked = []
        
        for ach in self.achievements.values():
            if ach.unlocked:
                continue
                
            cond = ach.condition
            
            if cond["type"] == event_type:
                if event_type in ["steal_count", "max_combo", "playtime", "hide_time", "evade_time"]:
                    ach.progress += value
                    if ach.progress >= ach.target:
                        self._unlock(ach)
                        unlocked.append(ach)
                        
                elif event_type == "full_sack" and value >= cond["target"]:
                    self._unlock(ach)
                    unlocked.append(ach)
                    
                elif event_type == "speed_steal":
                    if kwargs.get("count") >= cond["count"] and kwargs.get("time") <= cond["time"]:
                        self._unlock(ach)
                        unlocked.append(ach)
                        
                elif event_type == "secret" and kwargs.get("code") == cond["code"]:
                    self._unlock(ach)
                    unlocked.append(ach)
                    
                elif event_type == "time_specific":
                    hour = datetime.now().hour
                    if hour == cond["hour"]:
                        self._unlock(ach)
                        unlocked.append(ach)
                        
        self._save_progress()
        return unlocked
        
    def _unlock(self, ach):
        ach.unlocked = True
        ach.unlock_date = datetime.now().isoformat()
        print(f"[Achievement] ✨ {ach.icon} {ach.name} sbloccato!")
        print(f"             {ach.description}")
        if ach.reward:
            print(f"             🎁 Ricompensa: {ach.reward}")
            
    def get_progress(self):
        """Stats completi"""
        total = len(self.achievements)
        unlocked = sum(1 for a in self.achievements.values() if a.unlocked)
        return {
            "total": total,
            "unlocked": unlocked,
            "percentage": (unlocked / total * 100) if total > 0 else 0,
            "achievements": [
                {
                    "id": a.id,
                    "name": a.name,
                    "description": a.description,
                    "icon": a.icon,
                    "unlocked": a.unlocked,
                    "progress": a.progress,
                    "target": a.target,
                    "unlock_date": a.unlock_date,
                }
                for a in self.achievements.values()
            ]
        }
        
    def _save_progress(self):
        data = {
            a.id: {
                "unlocked": a.unlocked,
                "progress": a.progress,
                "unlock_date": a.unlock_date,
            }
            for a in self.achievements.values()
        }
        with open(self.save_file, 'w') as f:
            json.dump(data, f, indent=2)
            
    def _load_progress(self):
        if not os.path.exists(self.save_file):
            return
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
            for aid, progress in data.items():
                if aid in self.achievements:
                    a = self.achievements[aid]
                    a.unlocked = progress.get("unlocked", False)
                    a.progress = progress.get("progress", 0)
                    a.unlock_date = progress.get("unlock_date")
        except Exception as e:
            print(f"[Achievements] Errore caricamento: {e}")

import json
import os
from datetime import datetime, timedelta

class StatsTracker:
    """Statistiche persistenti del giocatore"""
    
    def __init__(self):
        self.save_file = "player_stats.json"
        self.stats = {
            "total_steals": 0,
            "total_caught": 0,
            "total_playtime": 0.0,
            "max_combo": 0,
            "total_distance": 0.0,
            "sessions_played": 0,
            "first_played": None,
            "last_played": None,
            "favorite_personality": {},
            "steals_per_session": [],
            "longest_session": 0.0,
            "fastest_steal": None,
            "total_hides": 0,
            "total_taunts": 0,
        }
        self.session_start = datetime.now()
        self.session_stats = {
            "steals": 0,
            "caught": 0,
            "distance": 0.0,
            "max_combo": 0,
        }
        self._load()
        
    def record_steal(self, time_taken=None):
        self.stats["total_steals"] += 1
        self.session_stats["steals"] += 1
        
        if time_taken and (self.stats["fastest_steal"] is None or time_taken < self.stats["fastest_steal"]):
            self.stats["fastest_steal"] = time_taken
            
    def record_caught(self):
        self.stats["total_caught"] += 1
        self.session_stats["caught"] += 1
        
    def record_combo(self, combo):
        if combo > self.stats["max_combo"]:
            self.stats["max_combo"] = combo
        if combo > self.session_stats["max_combo"]:
            self.session_stats["max_combo"] = combo
            
    def record_distance(self, dist):
        self.stats["total_distance"] += dist
        self.session_stats["distance"] += dist
        
    def record_hide(self):
        self.stats["total_hides"] += 1
        
    def record_taunt(self):
        self.stats["total_taunts"] += 1
        
    def record_personality(self, personality):
        if personality not in self.stats["favorite_personality"]:
            self.stats["favorite_personality"][personality] = 0
        self.stats["favorite_personality"][personality] += 1
        
    def update_playtime(self, dt):
        self.stats["total_playtime"] += dt
        
    def end_session(self):
        session_duration = (datetime.now() - self.session_start).total_seconds()
        
        if session_duration > self.stats["longest_session"]:
            self.stats["longest_session"] = session_duration
            
        self.stats["steals_per_session"].append(self.session_stats["steals"])
        if len(self.stats["steals_per_session"]) > 100:
            self.stats["steals_per_session"] = self.stats["steals_per_session"][-100:]
            
        self.stats["sessions_played"] += 1
        self.stats["last_played"] = datetime.now().isoformat()
        
        if not self.stats["first_played"]:
            self.stats["first_played"] = self.stats["last_played"]
            
        self._save()
        
    def get_summary(self):
        avg_steals = sum(self.stats["steals_per_session"]) / len(self.stats["steals_per_session"]) if self.stats["steals_per_session"] else 0
        
        return {
            "total_steals": self.stats["total_steals"],
            "total_caught": self.stats["total_caught"],
            "success_rate": (self.stats["total_steals"] / (self.stats["total_steals"] + self.stats["total_caught"]) * 100) if (self.stats["total_steals"] + self.stats["total_caught"]) > 0 else 0,
            "total_playtime_hours": self.stats["total_playtime"] / 3600,
            "max_combo": self.stats["max_combo"],
            "total_distance_km": self.stats["total_distance"] / 1000,
            "sessions_played": self.stats["sessions_played"],
            "avg_steals_per_session": avg_steals,
            "longest_session_minutes": self.stats["longest_session"] / 60,
            "fastest_steal_seconds": self.stats["fastest_steal"],
            "session_stats": self.session_stats,
        }
        
    def _save(self):
        with open(self.save_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
            
    def _load(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    loaded = json.load(f)
                self.stats.update(loaded)
            except Exception as e:
                print(f"[Stats] Errore caricamento: {e}")

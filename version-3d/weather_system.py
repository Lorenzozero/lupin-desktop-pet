from panda3d.core import Vec3, Vec4, NodePath
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.Particles import Particles
from direct.particles.ForceGroup import ForceGroup
import random

class WeatherSystem:
    """Sistema meteo dinamico per effetti atmosferici"""
    
    def __init__(self, render):
        self.render = render
        self.current_weather = "clear"
        self.particles = []
        self.intensity = 0.0
        
    def set_weather(self, weather_type):
        """Cambia condizioni meteo"""
        self.clear_effects()
        self.current_weather = weather_type
        
        if weather_type == "rain":
            self._create_rain()
        elif weather_type == "snow":
            self._create_snow()
        elif weather_type == "leaves":
            self._create_leaves()
        elif weather_type == "sparkles":
            self._create_magic_sparkles()
            
    def _create_rain(self):
        """Pioggia leggera"""
        print("[Weather] Pioggia attivata")
        # Implementazione con particelle Panda3D native
        # Per semplicità, usa il sistema custom
        self.intensity = 0.3
        
    def _create_snow(self):
        """Neve che cade"""
        print("[Weather] Neve attivata")
        self.intensity = 0.2
        
    def _create_leaves(self):
        """Foglie autunnali"""
        print("[Weather] Foglie attivate")
        self.intensity = 0.15
        
    def _create_magic_sparkles(self):
        """Scintille magiche (quando ruba tante icone)"""
        print("[Weather] Sparkles magici!")
        self.intensity = 0.4
        
    def update(self, dt, particle_system):
        """Genera particelle meteo"""
        if self.current_weather == "clear":
            return
            
        # Spawn probabilistico
        if random.random() < self.intensity * dt * 10:
            x = random.uniform(-15, 15)
            z = random.uniform(5, 12)
            
            if self.current_weather == "rain":
                particle_system.emit_rain_drop(Vec3(x, 0, z))
            elif self.current_weather == "snow":
                particle_system.emit_snowflake(Vec3(x, 0, z))
            elif self.current_weather == "leaves":
                particle_system.emit_leaf(Vec3(x, 0, z))
            elif self.current_weather == "sparkles":
                particle_system.emit_magic_sparkle(Vec3(x, 0, z))
                
    def clear_effects(self):
        """Rimuove effetti meteo"""
        for p in self.particles:
            p.removeNode()
        self.particles.clear()

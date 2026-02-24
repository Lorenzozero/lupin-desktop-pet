import os
import random
try:
    from pygame import mixer
    SOUND_ENABLED = True
except ImportError:
    SOUND_ENABLED = False
    print("pygame not installed - sounds disabled. Install with: pip install pygame")

class SoundManager:
    def __init__(self):
        self.enabled = SOUND_ENABLED
        self.sounds = {}
        
        if self.enabled:
            try:
                mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
                self._load_sounds()
            except:
                self.enabled = False
                
    def _load_sounds(self):
        sound_dir = "sounds"
        if not os.path.exists(sound_dir):
            os.makedirs(sound_dir)
            return
            
        sound_files = {
            "steal": ["steal1.wav", "steal2.wav", "steal3.wav"],
            "taunt": ["taunt1.wav", "taunt2.wav"],
            "run": ["run.wav"],
            "caught": ["caught.wav"],
            "hide": ["hide.wav"],
        }
        
        for key, files in sound_files.items():
            self.sounds[key] = []
            for fname in files:
                path = os.path.join(sound_dir, fname)
                if os.path.exists(path):
                    try:
                        self.sounds[key].append(mixer.Sound(path))
                    except:
                        pass
                        
    def play(self, sound_type, volume=0.5):
        if not self.enabled or sound_type not in self.sounds:
            return
            
        sounds = self.sounds[sound_type]
        if sounds:
            sound = random.choice(sounds)
            sound.set_volume(volume)
            sound.play()
            
    def play_footstep(self, speed):
        """Genera suono di passi in base alla velocità"""
        if not self.enabled:
            return
        # Frequenza basata su velocità
        # Implementa con tone generator se serve
        pass

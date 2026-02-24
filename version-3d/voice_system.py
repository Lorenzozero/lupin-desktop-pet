import random
try:
    import pyttsx3
    TTS_ENABLED = True
except ImportError:
    TTS_ENABLED = False
    print("pyttsx3 non installato. Installa con: pip install pyttsx3")

class VoiceSystem:
    """Text-to-speech per il pet"""
    
    def __init__(self):
        self.enabled = TTS_ENABLED
        self.engine = None
        
        if self.enabled:
            try:
                self.engine = pyttsx3.init()
                # Voice properties
                voices = self.engine.getProperty('voices')
                # Prova a usare voce italiana se disponibile
                for voice in voices:
                    if 'italian' in voice.name.lower() or 'it' in voice.id.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                        
                self.engine.setProperty('rate', 180)  # Velocità
                self.engine.setProperty('volume', 0.8)
            except Exception as e:
                print(f"[Voice] Errore init TTS: {e}")
                self.enabled = False
                
    def say(self, text, personality="playful"):
        """Pronuncia testo con personalità"""
        if not self.enabled:
            return
            
        # Modifica parametri in base a personalità
        if personality == "aggressive":
            self.engine.setProperty('rate', 200)
            self.engine.setProperty('pitch', 90)  # più basso
        elif personality == "playful":
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('pitch', 110)  # medio-alto
        elif personality == "sneaky":
            self.engine.setProperty('rate', 150)
            self.engine.setProperty('pitch', 95)  # basso sussurro
            
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[Voice] Errore speak: {e}")
            
    def taunt(self, personality="playful"):
        """Frase di scherno casuale"""
        taunts = [
            "Troppo lento!",
            "Non mi prenderai mai!",
            "Ahah! Provaci ancora!",
            "Le tue icone sono mie!",
            "Sono un genio del crimine!",
            "Sei troppo prevedibile!",
        ]
        self.say(random.choice(taunts), personality)
        
    def steal_comment(self):
        """Commento durante furto"""
        comments = [
            "Questa è mia!",
            "Perfetto!",
            "Troppo facile!",
            "Un'altra per la collezione!",
        ]
        self.say(random.choice(comments))
        
    def surrender_comment(self):
        """Commento alla resa"""
        comments = [
            "Va bene, hai vinto!",
            "Ok ok, le restituisco!",
            "Dannazione!",
            "Mi hai preso...",
        ]
        self.say(random.choice(comments))

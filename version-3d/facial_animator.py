from panda3d.core import NodePath, LerpBlendType
from direct.interval.IntervalGlobal import LerpFunc, Sequence, Parallel, Wait, Func
import math

class FacialAnimator:
    """Sistema di facial animation procedurale per espressioni emotive"""
    
    def __init__(self, model_node):
        self.model = model_node
        self.current_emotion = "neutral"
        self.blink_sequence = None
        
        # Cerca morph targets o bones facciali
        self.morphs = {}
        self._find_morph_targets()
        
    def _find_morph_targets(self):
        """Trova morph targets nel modello GLB"""
        # Se il modello ha blend shapes, li trova automaticamente
        # Nomi comuni: eyeBlink, mouthSmile, browRaise, etc.
        try:
            for node in self.model.findAllMatches('**'):
                if hasattr(node, 'getMorphs'):
                    morphs = node.getMorphs()
                    for name in morphs:
                        self.morphs[name] = node
        except:
            pass
            
    def set_emotion(self, emotion):
        """Cambia espressione facciale"""
        self.current_emotion = emotion
        
        if emotion == "happy":
            self._expression_happy()
        elif emotion == "angry":
            self._expression_angry()
        elif emotion == "surprised":
            self._expression_surprised()
        elif emotion == "smug":
            self._expression_smug()
        elif emotion == "scared":
            self._expression_scared()
        elif emotion == "sad":
            self._expression_sad()
        else:
            self._expression_neutral()
            
    def _expression_happy(self):
        """Sorriso largo"""
        if 'mouthSmile' in self.morphs:
            self.morphs['mouthSmile'].setMorphWeight('mouthSmile', 0.9)
        if 'eyeSquint' in self.morphs:
            self.morphs['eyeSquint'].setMorphWeight('eyeSquint', 0.4)
            
    def _expression_angry(self):
        """Arrabbiato"""
        if 'browDown' in self.morphs:
            self.morphs['browDown'].setMorphWeight('browDown', 0.8)
        if 'mouthFrown' in self.morphs:
            self.morphs['mouthFrown'].setMorphWeight('mouthFrown', 0.6)
            
    def _expression_surprised(self):
        """Sorpreso"""
        if 'browRaise' in self.morphs:
            self.morphs['browRaise'].setMorphWeight('browRaise', 1.0)
        if 'mouthOpen' in self.morphs:
            self.morphs['mouthOpen'].setMorphWeight('mouthOpen', 0.7)
            
    def _expression_smug(self):
        """Smug/saccente"""
        if 'mouthSmile' in self.morphs:
            self.morphs['mouthSmile'].setMorphWeight('mouthSmile', 0.5)
        if 'eyeLidClose' in self.morphs:
            self.morphs['eyeLidClose'].setMorphWeight('eyeLidClose', 0.3)
            
    def _expression_scared(self):
        """Spaventato"""
        if 'browRaise' in self.morphs:
            self.morphs['browRaise'].setMorphWeight('browRaise', 0.9)
        if 'mouthOpen' in self.morphs:
            self.morphs['mouthOpen'].setMorphWeight('mouthOpen', 0.5)
            
    def _expression_sad(self):
        """Triste"""
        if 'browDown' in self.morphs:
            self.morphs['browDown'].setMorphWeight('browDown', 0.6)
        if 'mouthFrown' in self.morphs:
            self.morphs['mouthFrown'].setMorphWeight('mouthFrown', 0.8)
            
    def _expression_neutral(self):
        """Reset a neutro"""
        for morph_node in self.morphs.values():
            try:
                for name in morph_node.getMorphs():
                    morph_node.setMorphWeight(name, 0.0)
            except:
                pass
                
    def blink(self):
        """Blink procedurale"""
        if 'eyeBlink' in self.morphs:
            def set_blink(t):
                self.morphs['eyeBlink'].setMorphWeight('eyeBlink', t)
            
            self.blink_sequence = Sequence(
                LerpFunc(set_blink, 0.0, 1.0, 0.08),
                Wait(0.05),
                LerpFunc(set_blink, 1.0, 0.0, 0.08)
            )
            self.blink_sequence.start()

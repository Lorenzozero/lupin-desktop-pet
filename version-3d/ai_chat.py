import random
import os

try:
    import openai
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False

class AIChatSystem:
    """Sistema AI per risposte dinamiche del pet"""
    
    def __init__(self, personality="playful"):
        self.enabled = AI_ENABLED and os.getenv("OPENAI_API_KEY")
        self.personality = personality
        self.history = []
        
        if not self.enabled:
            print("[AI] OpenAI non disponibile. Usando risposte pregenerate.")
            
        self.fallback_responses = {
            "greeting": [
                "Ciao! Pronto a giocare?",
                "Ehilà! Oggi ruberò tutto!",
                "Salve! Sono Lupin, il ladro più elegante!",
            ],
            "taunt": [
                "Non mi prenderai mai!",
                "Troppo lento, amico!",
                "Le tue icone sono già mie!",
            ],
            "caught": [
                "Ok, questa volta hai vinto tu...",
                "Dannazione! Sei stato veloce!",
                "Bravo... ma tornerò!",
            ],
        }
        
    def get_response(self, context):
        """Genera risposta in base al contesto"""
        if self.enabled:
            return self._ai_response(context)
        else:
            return self._fallback_response(context)
            
    def _ai_response(self, context):
        """Risposta da OpenAI"""
        try:
            system_prompt = f"""Sei Lupin, un ladro gentiluomo elegante e giocoso che ruba icone dal desktop.
Personalità: {self.personality}
Rispondi in modo breve (max 10 parole), spiritoso e in italiano."""
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": context}
                ],
                max_tokens=30,
                temperature=0.9,
            )
            
            text = response.choices[0].message.content.strip()
            self.history.append({"context": context, "response": text})
            return text
            
        except Exception as e:
            print(f"[AI] Errore: {e}")
            return self._fallback_response(context)
            
    def _fallback_response(self, context):
        """Risposta pre-generata"""
        if "taunt" in context.lower():
            return random.choice(self.fallback_responses["taunt"])
        elif "caught" in context.lower():
            return random.choice(self.fallback_responses["caught"])
        else:
            return random.choice(self.fallback_responses["greeting"])

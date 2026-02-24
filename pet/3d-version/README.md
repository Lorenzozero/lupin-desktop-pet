# 🎩 Lupin Desktop Pet - 3D Version

Versione avanzata con rendering **3D real-time** (Panda3D), modelli GLB, achievements, multiplayer locale e mini-games.

## 🚀 Installazione

```bash
cd pet/3d-version
pip install -r requirements.txt
python main.py
```

## 🎮 Modello GLB

Metti il tuo modello 3D in `models/lupin.glb` con animazioni:
- idle, walk, run, grab, taunt, crouch, surrender

Senza GLB, usa fallback procedurale 3D.

## ✨ Advanced Features

### Rendering 3D
- Luci dinamiche (ambient, key, fill, rim)
- Particelle 3D billboarded
- Squash/stretch fisico
- Ombre proiettate

### Gameplay Systems
- **Achievements** (10+): sblocchi con ricompense
- **Stats Tracker**: statistiche persistenti
- **Multiplayer**: fino a 4 pet contemporanei
- **Skin System**: 7 skin unlockable
- **Mini-Games**: 3 giochi integrati

### AI & Voice
- **Facial Animator**: espressioni facciali (morph targets)
- **Voice System**: text-to-speech con personalità
- **Weather System**: pioggia, neve, foglie, sparkles
- **AI Chat**: OpenAI integration per risposte dinamiche

## ⌨️ Comandi

- Click: cattura pet
- ESC: chiude
- A: achievements
- S: stats
- M: spawna secondo pet
- G: mini-game
- K: Konami code

## 📚 Vedi file sorgenti per dettagli implementazione

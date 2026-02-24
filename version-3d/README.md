# 🎩 Lupin Desktop Pet — Versione 3D

Versione avanzata con rendering **3D real-time** basata su **Panda3D** + **GLB/GLTF**.
Supporta modelli 3D animati, luci dinamiche, sistema particelle 3D, squash/stretch fisico e ombre proiettate.

---

## 🚀 Installazione

```bash
cd version-3d
pip install -r requirements.txt
python main.py
```

---

## 🎮 Modello 3D Custom (GLB)

Per usare il tuo modello 3D di Lupin:

1. Crea o scarica un modello `.glb` (Blender, Sketchfab, Mixamo)
2. Il modello deve avere queste **armature/animazioni** incluse nel file GLB:
   - `idle` → respirazione passiva
   - `walk` → camminata
   - `run` → corsa veloce
   - `grab` → animazione furto
   - `taunt` → linguaccia / derisione
   - `crouch` → nascondersi
   - `surrender` → resa
3. Salva come `models/lupin.glb`

### Come creare il modello in Blender

```
1. Modella il personaggio (low-poly consigliato: 5-10k triangoli)
2. Rigga con armatura
3. Crea le NLA Actions con i nomi esatti sopra
4. Export > GLTF 2.0 (.glb) con opzione "Include Animations" attiva
5. Copia in version-3d/models/lupin.glb
```

### Asset gratuiti consigliati

- [Sketchfab](https://sketchfab.com/3d-models?features=downloadable&q=chibi+thief) - Cerca "chibi thief" o "gentleman"
- [Mixamo](https://www.mixamo.com) - Animazioni free su qualsiasi mesh
- [Kenney.nl](https://kenney.nl) - Asset low-poly CC0

---

## 🎨 Features 3D

### Rendering
- **3 luci dinamiche**: Ambient, Key, Fill + Rim light che segue il pet
- **Ombra blob proiettata** con pulsazione
- **Transparenza per-pixel** tramite Win32 `SetLayeredWindowAttributes`
- **Squash & Stretch fisico**: deformazione del modello 3D in base alla velocità
- **Tilt dinamico**: il modello si inclina in corsa
- **Breath animation**: oscillazione passiva in idle

### Sistema Particelle 3D
- Particelle **quad billboarded** (sempre verso la camera)
- **Gravità fisica** per sparkle e confetti
- **Smoke ascendente** per dust trail in corsa
- **Cuori** che fluttuano in surrender
- **Alpha decay** per dissolvenza naturale
- **Spin individuale** per ogni particella

### Animazioni
- Transizione automatica tra clip animate del GLB
- Squash/stretch applicato sul nodo 3D
- Rotazione di tilt in corsa

---

## 🎮 Advanced Systems

### 🏆 Achievements (10+ sblocchi)
- **First Steal**: ruba la prima icona
- **Master Thief**: 100 furti totali → sblocca skin Gold
- **Speedrunner**: 5 icone in 30s → speed boost
- **Combo Master**: combo x10 → particelle fuoco
- **Ninja**: nascosto 5min → invisibilità
- **Untouchable**: evadi cursore 2min → teleport
- **Marathon**: 1h di gioco → emote dance
- **Konami Code**: inserisci codice segreto → god mode
- **Midnight Thief**: gioca alle 00:00 → moon particles

### 📊 Stats Tracker
Traccia persistentemente:
- Furti totali / catture
- Playtime totale
- Combo massimo
- Distanza percorsa (km)
- Sessioni giocate
- Personalità preferita
- Record velocità

### 👥 Multiplayer Locale
Spawna fino a **4 pet contemporanei** sullo stesso desktop:
```python
multi = MultiplayerManager(sw, sh, render)
multi.spawn_pet("Lupin Jr.", personality="playful")
multi.spawn_pet("Shadow", personality="sneaky")
```
- Interagiscono tra loro (bounce, scambio bottino)
- Colori diversi per distinguerli
- AI indipendente per ognuno

### 🎨 Skin System (7 skin)
- **Default**: Lupin classico
- **Gold**: Re Mida (tutto oro) → unlock: 100 furti
- **Rainbow**: Colori dinamici → unlock: sacco pieno
- **Ghost**: Semi-trasparente → unlock: ninja achievement
- **Fire**: Tracce di fuoco → unlock: combo master
- **Ice**: Glaciale → unlock: untouchable
- **Neon**: Cyberpunk → unlock: speedrun

### 🎮 Mini-Games
3 mini-giochi integrati:

1. **Catch The Icon**: Clicca icone prima che scompaiano (30s)
2. **Pet Race**: Corri evitando ostacoli fino al traguardo
3. **Icon Memory**: Memorizza sequenza di icone (stile Simon Says)

Attivabili con comando speciale o dopo tot furti.

### 🌟 Easter Eggs
- **Konami Code** (↑↑↓↓←→←→BA): God mode
- **Midnight spawn**: Effetti speciali se avviato a mezzanotte
- **Collision scambio**: Due pet che si scontrano scambiano il bottino
- **Weather trigger**: Pioggia se rubate tutte le icone

---

## 🛠️ Architettura

```
version-3d/
├── main.py                   # Entry point
├── pet3d_app.py              # Core Panda3D
├── pet3d_brain.py            # State machine AI
├── particle_system3d.py      # Particelle + weather
├── facial_animator.py        # Espressioni facciali
├── voice_system.py           # Text-to-speech
├── weather_system.py         # Meteo dinamico
├── ai_chat.py                # OpenAI integration
├── achievements.py           # Sistema achievements
├── stats_tracker.py          # Statistiche persistenti
├── multiplayer_manager.py    # Multiplayer locale
├── skin_manager.py           # Sistema skin
├── minigames.py              # Mini-giochi
├── desktop_hooks.py          # Win32 API
├── requirements.txt
└── models/
    └── lupin.glb                # Modello 3D
```

---

## ⌨️ Comandi

| Tasto | Azione |
|---|---|
| Click sinistro | Cattura Lupin |
| ESC | Chiude e ripristina |
| A | Apri pannello achievements |
| S | Mostra statistiche |
| M | Spawna secondo pet (multiplayer) |
| G | Avvia mini-game casuale |
| K | Inserisci Konami Code |

---

## 📊 Stats & Progress

Tutti i dati sono salvati localmente in JSON:
- `achievements.json` - progress achievements
- `player_stats.json` - statistiche giocatore
- `skins.json` - skin sbloccate

---

*Il desktop pet più completo mai creato.* 🎩✨🎮

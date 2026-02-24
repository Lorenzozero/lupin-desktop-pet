# 🎩 Lupin Desktop Pet

> *"Se mi prendi ti ridò il tuo desktop esattamente com'era!"*

Un desktop pet in stile **Arsène Lupin** che ruba le icone del desktop Windows e ti sfida a catturarlo.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🔥 Due Versioni Disponibili

### 🎨 [2D Version](./2d-version/) - Classica
Versione leggera con PyQt5, sprite 2D animati e particelle avanzate.

**Features:**
- Sistema particelle (sparkle, smoke, cuori)
- Sound effects
- Combo system
- Cursor attention
- Motion trail
- 3 personalità

**Performance:** ~2% CPU

```bash
cd pet/2d-version
pip install -r requirements.txt
python main.py
```

### 🎮 [3D Version](./3d-version/) - Advanced
Versione completa con Panda3D, modelli GLB/GLTF 3D, achievements e multiplayer.

**Features:**
- Rendering 3D con luci dinamiche
- Modelli GLB animati
- Sistema achievements (10+)
- Stats tracker persistente
- Multiplayer locale (4 pet)
- 7 skin unlockable
- 3 mini-games
- Facial expressions
- Text-to-speech
- Weather system
- OpenAI chat integration

**Performance:** ~5-10% CPU + GPU

```bash
cd pet/3d-version
pip install -r requirements.txt
python main.py
```

---

## 🎯 Come Funziona

1. **Idle**: Passeggia per il desktop
2. **Steal**: Si avvicina alle icone e le ruba
3. **Taunt**: Centro schermo, ti prende in giro
4. **Run**: Scappa dal cursore con movimenti evasivi
5. **Hide**: Si nasconde dietro finestre
6. **Surrender**: Restituisce tutto quando lo catturi

---

## 🛠️ Requisiti

- **Windows 10/11**
- **Python 3.8+**

### 2D Version
```bash
pip install PyQt5 pywin32 pygame
```

### 3D Version
```bash
pip install panda3d panda3d-gltf pywin32 pyttsx3
```

---

## 🎨 Personalizzazione

### Sprite 2D Custom
Crea cartella `pet/2d-version/sprites/` con PNG 90x90px:
- `idle.png`, `stealing.png`, `taunting.png`, etc.

### Modello 3D Custom
Salva il tuo modello GLB con animazioni in:
- `pet/3d-version/models/lupin.glb`

Animazioni richieste: idle, walk, run, grab, taunt, crouch, surrender

**Dove trovare modelli:**
- [Sketchfab](https://sketchfab.com) (chibi thief, gentleman)
- [Mixamo](https://mixamo.com) (animazioni gratis)
- [Kenney.nl](https://kenney.nl) (low-poly CC0)

---

## 📊 Confronto Versioni

| Feature | 2D | 3D |
|---|:---:|:---:|
| Sprite/Modelli | PNG | GLB 3D |
| Particelle | 2D QPainter | 3D billboarded |
| Luci | Gradiente statico | 3 luci dinamiche |
| Animazioni | Frame sprite | Skeletal |
| Achievements | ❌ | ✅ 10+ |
| Stats tracking | ❌ | ✅ |
| Multiplayer | ❌ | ✅ 4 pet |
| Skin system | ❌ | ✅ 7 skin |
| Mini-games | ❌ | ✅ 3 giochi |
| Voice TTS | ❌ | ✅ |
| AI Chat | ❌ | ✅ OpenAI |
| CPU | ~2% | ~5-10% |
| Setup | Facile | Medio |

---

## ⌨️ Comandi Base

### 2D Version
- **Click sinistro**: Cattura
- **ESC**: Chiude

### 3D Version
- **Click sinistro**: Cattura
- **ESC**: Chiude
- **A**: Achievements panel
- **S**: Statistiche
- **M**: Spawna secondo pet
- **G**: Mini-game casuale
- **K**: Inserisci Konami code

---

## 🐛 Troubleshooting

### Icone non ripristinate
- Premi **ESC** o chiudi il pet
- Refresh desktop: **F5**

### Performance lag (3D)
- Riduci particelle nel codice
- Usa modello low-poly (<10k triangoli)

### Finestra non trasparente (3D)
- Abilita Aero/GPU rendering in Windows
- Esegui come amministratore

---

## 🚀 Roadmap Future

- [ ] System tray controls
- [ ] Multi-monitor support
- [ ] Integrazione Ollama (AI locale)
- [ ] Cloud sync achievements
- [ ] Steam Workshop skins
- [ ] VR mode (!)

---

## 📜 License

MIT License - Modifica e condividi liberamente!

---

## 👤 Author

**Lorenzo Garoffolo**  
🌐 [lorenzo-garoffolo-cyber.netlify.app](https://lorenzo-garoffolo-cyber.netlify.app/)  
💼 Full Stack Developer & Cybersecurity Specialist  
📧 [GitHub: @Lorenzozero](https://github.com/Lorenzozero)

---

*Costruito con carisma, determinazione e un motore 3D degno di un AAA game.* 🎩✨🎮

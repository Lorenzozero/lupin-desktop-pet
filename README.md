# 🎩 Lupin Desktop Pet

> *"Se mi prendi ti ridò il tuo desktop esattamente com'era!"*

Un desktop pet in stile **Arsène Lupin** con **fisica realistica**, **particelle dinamiche**, **ombre proiettate** e **animazioni fluide**. Ruba le icone del tuo desktop Windows, le infila nel sacco e ti sfida a catturarlo mentre corre per lo schermo.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Advanced Features

### 🎨 Visual Effects
- **Sistema Particellare**: Esplosioni dorate quando ruba, scie di polvere in corsa, cuori quando si arrende
- **Ombre Dinamiche**: Ombre proiettate radiali che seguono il pet
- **Motion Trail**: Scia fantasma durante la corsa ad alta velocità
- **Screen Shake**: Vibrazione dello schermo durante eventi drammatici
- **Flash Effect**: Flash bianco al momento del furto
- **Squash & Stretch**: Deformazione realistica del corpo durante movimento veloce

### 🎭 Animazioni Avanzate
- **Smooth Physics**: Sistema di accelerazione/decelerazione con velocity-based movement
- **Evasive Maneuvers**: Movimenti laterali imprevedibili durante la fuga
- **Pop-in Animations**: Fumetti che crescono con easing elastico
- **Bounce Effect**: Sacco che rimbalza sopra la testa
- **Blink System**: Occhi che si chiudono casualmente per realismo

### 🧠 Sistema di Personalità
Ogni sessione, Lupin assume una personalità casuale che influenza il comportamento:

- **Aggressive** 😈: Ruba più icone (90% probabilità), distanza di fuga ridotta (250px), veloce
- **Playful** 😜: Equilibrato (70% probabilità), distanza media (350px), comportamento standard
- **Sneaky** 🤫: Più cauto (50% probabilità), distanza elevata (450px), timing più lungo

---

## 🎮 Features Core

- **Furto Dinamico**: Si avvicina alle icone, le "ruba" e le nasconde fuori dallo schermo
- **Inseguimento Intelligente**: Scappa dal cursore con movimenti evasivi
- **Nascondimento**: Si nasconde dietro finestre aperte mostrando solo un angolino
- **Interazione Completa**: Cliccalo per restituire tutte le icone
- **Overlay Trasparente**: Finestra borderless che non interferisce con il desktop

---

## 🚀 Installazione

### Requisiti
- **Windows 10/11**
- **Python 3.8+**

### Setup

```bash
# Clona il repository
git clone https://github.com/Lorenzozero/lupin-desktop-pet.git
cd lupin-desktop-pet

# Installa le dipendenze
pip install -r requirements.txt

# Avvia Lupin
python main.py
```

---

## 🎯 Come Funziona

### Architettura

```
lupin-desktop-pet/
├── main.py              # Entry point
├── pet_window.py        # PyQt5 window + advanced rendering + particle system
├── desktop_hooks.py     # Win32 API hooks per manipolare icone
├── pet_brain.py         # State machine + personality system + smooth physics
└── sprites/             # (opzionale) PNG custom per animazioni
```

### Stati Comportamentali

1. **IDLE**: Passeggia lentamente, personalità influenza timing di attacco
2. **APPROACHING**: Si avvicina a un'icona con accelerazione fluida
3. **STEALING**: Animazione furto → particelle dorate + screen shake + flash
4. **TAUNTING**: Centro schermo, fumetto animato, linguaccia
5. **RUNNING**: Fuga con evasive maneuvers + motion trail + dust particles
6. **HIDING**: Si nasconde dietro finestre, solo angolino visibile
7. **SURRENDER**: Particelle cuore, restituzione icone

### Effetti Visivi Dettagliati

**Particle System**
- Gravità fisica su ogni particella
- Alpha decay per dissolvenza
- 3 tipi: esplosioni (oro), polvere (grigio), cuori (rosa)

**Motion Trail**
- Buffer di 8 posizioni precedenti
- Alpha gradient per effetto fantasma
- Attivo solo durante corsa veloce

**Squash & Stretch**
- Deformazione proporzionale alla velocità
- Rotazione dinamica basata su sin wave
- Ritorna a forma normale quando fermo

---

## 🎨 Personalizzazione

### Sprite Custom

1. Crea cartella `sprites/`
2. Aggiungi PNG 90×90px:
   - `idle.png`, `stealing.png`, `taunting.png`
   - `running.png`, `hiding.png`, `surrender.png`

### Configurazione Comportamento

**pet_brain.py**
```python
class LupinBrain:
    MAX_STEAL = 8  # Numero massimo icone
    
    # Modifica valori personalità
    "aggressive": 0.9,  # % probabilità rubare altra icona
    flee_dist: 250      # distanza di fuga in pixel
```

**pet_window.py**
```python
# Intensità particelle
for _ in range(20):  # numero particelle per esplosione
    
# Durata effetti
self.shake_intensity = 8  # intensità screen shake
self.flash_alpha = 255    # intensità flash
```

---

## ⌨️ Comandi

- **Click sinistro su Lupin**: Costringe resa immediata + particelle blu
- **ESC**: Chiude applicazione + ripristino icone immediato

---

## 🛠️ Tecnologie

- **PyQt5**: Finestra trasparente, rendering avanzato, smooth transforms
- **pywin32**: Win32 API per manipolazione icone desktop
- **ctypes**: Memoria processo per lettura/scrittura coordinate
- **Custom Physics Engine**: Sistema velocità/accelerazione per movimento naturale

---

## 🔧 Performance

- **60 FPS cap**: Timer a 16ms per fluidità
- **Particle pooling**: Max ~50 particelle contemporanee
- **Lazy icon refresh**: Update posizioni ogni 200 frame
- **Hardware acceleration**: QT smooth transform rendering

---

## 🐛 Troubleshooting

### Lag o stuttering
- Riduci numero particelle in `pet_window.py` (linea esplosione: `range(20)` → `range(10)`)
- Disabilita motion trail commentando sezione rendering trail

### Le icone non vengono ripristinate
- Premi **ESC** per forzare ripristino
- Refresh desktop: F5 o riavvia `explorer.exe`

### Pet non cliccabile
- Il click-through è dinamico. Assicurati cursore sia esattamente sopra sprite
- Prova durante fase TAUNTING quando è fermo al centro

---

## 📊 Statistiche Progetto

- **Linee di codice**: ~600
- **Stati AI**: 7
- **Tipi particelle**: 3
- **Personalità**: 3
- **FPS target**: 60
- **Max icone rubabili**: 8

---

## 🚀 Possibili Estensioni

- [ ] **Integrazione Ollama**: AI locale decide comportamento in real-time
- [ ] **Sound FX**: Effetti sonori comici (pygame)
- [ ] **System Tray**: Controlli pause/config/exit
- [ ] **Multi-monitor**: Supporto setup multipli
- [ ] **Custom Triggers**: Alert su eventi (Wazuh, VirusTotal, prezzi)
- [ ] **Multiplayer**: Più pet che interagiscono
- [ ] **Achievements**: Sistema unlock skin/comportamenti

---

## 📜 License

MIT License - Modifica, estendi, condividi liberamente!

---

## 👤 Author

**Lorenzo Garoffolo**  
🌐 [lorenzo-garoffolo-cyber.netlify.app](https://lorenzo-garoffolo-cyber.netlify.app/)  
💼 Full Stack Developer & Cybersecurity Specialist  
📧 [GitHub: @Lorenzozero](https://github.com/Lorenzozero)

---

*Costruito con carisma, determinazione e un sistema particellare degno di un AAA game.* 🎩✨

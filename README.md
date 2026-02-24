# 🎩 Lupin Desktop Pet

> *"Se mi prendi ti ridò il tuo desktop esattamente com'era!"*

Un desktop pet in stile **Arsène Lupin** che ruba le icone del tuo desktop Windows, le infila nel sacco e ti sfida a catturarlo mentre corre per lo schermo e si nasconde dietro le finestre.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🎮 Features

- **Furto Dinamico**: Lupin si avvicina alle icone del desktop, le "ruba" e le nasconde fuori dallo schermo
- **Animazioni Realistiche**: Gravità, movimento fluido, sprite che cambiano in base allo stato
- **Inseguimento Intelligente**: Scappa dal cursore quando ti avvicini, rendendo difficile catturarlo
- **Nascondimento**: Si nasconde dietro le finestre aperte mostrando solo un angolino
- **Interazione Completa**: Cliccalo per costringerlo a restituire tutte le icone alle posizioni originali
- **Overlay Trasparente**: Finestra borderless che non interferisce con il normale utilizzo del desktop

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
pip install PyQt5 pywin32

# Avvia Lupin
python main.py
```

---

## 🎯 Come Funziona

### Architettura

Il progetto è strutturato in 4 moduli principali:

```
lupin-desktop-pet/
├── main.py              # Entry point
├── pet_window.py        # Finestra trasparente PyQt5 + rendering
├── desktop_hooks.py     # Win32 API per manipolare icone desktop
├── pet_brain.py         # State machine e AI comportamentale
└── sprites/             # (opzionale) PNG custom per animazioni
```

### Stati Comportamentali

1. **IDLE**: Lupin passeggia lentamente per lo schermo
2. **APPROACHING**: Si avvicina a un'icona target
3. **STEALING**: Animazione del furto → l'icona sparisce nel sacco
4. **TAUNTING**: Si ferma al centro, zooma la faccia e ti provoca
5. **RUNNING**: Scappa dal cursore in modo intelligente
6. **HIDING**: Si nasconde dietro una finestra, mostrando solo un angolino
7. **SURRENDER**: Restituisce tutte le icone rubate

### Tecnologie Utilizzate

- **PyQt5**: Finestra trasparente, rendering sprite, input handling
- **pywin32**: Accesso diretto alle Win32 API per:
  - Trovare l'handle di `SysListView32` (il componente che gestisce le icone del desktop)
  - Leggere le posizioni originali (`LVM_GETITEMPOSITION`)
  - Spostare le icone (`LVM_SETITEMPOSITION`)
  - Enumerare finestre aperte (`EnumWindows`, `GetWindowRect`)
- **ctypes**: Manipolazione memoria processo per lettura/scrittura coordinate icone

---

## 🎨 Personalizzazione

### Sprite Custom

Per sostituire i placeholder colorati con sprite reali:

1. Crea una cartella `sprites/` nella root del progetto
2. Aggiungi i seguenti file PNG (90×90px):
   - `idle.png`
   - `stealing.png`
   - `taunting.png`
   - `running.png`
   - `hiding.png`
   - `surrender.png`

### Configurazione Comportamento

Modifica `pet_brain.py` per personalizzare:

```python
class LupinBrain:
    MAX_STEAL = 6  # Numero massimo di icone da rubare
    # Altri parametri: velocità, distanza di fuga, timer, ecc.
```

---

## ⌨️ Comandi

- **Click sinistro su Lupin**: Durante la fase di fuga/nascondimento, lo costringe a restituire le icone
- **ESC**: Chiude l'applicazione e ripristina immediatamente tutte le icone

---

## 🛠️ Possibili Estensioni

- [ ] **Integrazione AI**: Collegare a Ollama/LLM locale per decisioni comportamentali dinamiche
- [ ] **Suoni**: Effetti sonori comici durante furto e linguaccia
- [ ] **Tray Icon**: Controlli da system tray (pausa, configurazione, exit)
- [ ] **Multi-monitor**: Supporto per setup con più schermi
- [ ] **Modalità Produttività**: Trasforma gli scherzi in alert utili (security, notifiche, timer Pomodoro)

---

## 🐛 Troubleshooting

### Le icone non vengono ripristinate
- Premi **ESC** per forzare il ripristino immediato
- Se il problema persiste, fai refresh del desktop (F5) o riavvia `explorer.exe`

### Il pet non è cliccabile
- Il click-through è gestito dinamicamente. Assicurati che il cursore sia esattamente sopra lo sprite di Lupin

### Errore: "cannot find SysListView32"
- Alcune configurazioni di Windows 11 nascondono le icone del desktop in modo diverso. Il codice include un fallback su `WorkerW`, ma potrebbero servire ulteriori adattamenti per setup particolari

---

## 📜 License

MIT License - Sentiti libero di modificare, estendere e condividere!

---

## 👤 Author

**Lorenzo Garoffolo**  
🌐 [lorenzo-garoffolo-cyber.netlify.app](https://lorenzo-garoffolo-cyber.netlify.app/)  
💼 Full Stack Developer & Cybersecurity Specialist  
📧 [GitHub: @Lorenzozero](https://github.com/Lorenzozero)

---

*Costruito con carisma e determinazione. Perché anche il codice può avere stile.* 🎩✨

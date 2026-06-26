# 🎩 Lupin Desktop Pet

> *"Se mi prendi ti ridò il tuo desktop esattamente com'era!"*

Un desktop pet **Lupin III** disegnato proceduralmente che vive sul tuo schermo Windows, ruba le icone, fa dispetti, beve birre e insulta in italiano satirico quando lo colpisci.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-lightgrey.svg)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🚀 Avvio rapido

```bash
pip install PyQt5 pywin32 pygame-ce

# Avvio silenzioso (no finestra CMD):
start launch.vbs
# Oppure direttamente:
pythonw main.py
```

**ESC** per chiudere e ripristinare tutte le icone.

---

## 🎮 Funzionalità

### Movimento & Fisica
| Feature | Dettaglio |
|---|---|
| **Movimento smooth** | Velocità + accelerazione, inerzia fisica |
| **Salto con gravità** | `jump_z` + `jump_vel`, gravità 1.4/frame |
| **Wrap-around schermo** | Esce da un lato, rientra dall'altro |
| **Dual monitor** | Schermo virtuale Win32 — si muove su tutti i monitor |
| **Freeze durante speech** | Non si muove mentre ha la bolla di testo |
| **Schiacciamento** | Corpo si deforma durante la corsa |
| **Body rotation** | Rotazione durante la corsa veloce |

### Stati & Comportamenti (23 stati)
| Stato | Descrizione |
|---|---|
| `IDLE` | Vaga su tutto lo schermo, salta occasionalmente |
| `SLEEPING` | Si addormenta dopo 40s di cursore fermo, Zzz… |
| `CURIOUS` | Si avvicina al cursore, si spaventa se troppo vicino |
| `FOLLOWING` | Segue il cursore saltellando |
| `WAVING` | Saluta con animazione braccio + cuori |
| `DANCING` | Balla con saltelli ritmici e note musicali |
| `HANGING` | Si appende a un'icona del desktop |
| `LEANING` | Si appoggia fisicamente al bordo — braccio tocca il muro |
| `CORNER` | Si nasconde in un angolo con braccia conserte |
| `SITTING` | Si siede su un'icona e chiacchiera |
| `EXHAUSTED` | Si accascia dopo una lunga fuga, ansima con fiatone |
| `DRINKING` | Beve una birra 🍺, testa che si inclina, poi rutta |
| `VOLUME_TRICK` | Alza il volume del PC con animazione + barra visiva |
| `APPROACHING` | Corre verso un'icona con maschera da ladro |
| `STEALING` | Ruba l'icona (Win32 LVM32) — esce da un buco nero |
| `TAUNTING` | Si prende gioco di te con refurtiva orbitante 👑💎🏅 |
| `RUNNING` | Fuga con wrap-around e gocce di sudore |
| `HIDING` | Si nasconde dietro finestre aperte |
| `SURRENDER` | Si arrende se cliccato — nessuna lacrima, solo resa |
| `CELEBRATING` | Festeggia con coriandoli e cuori |
| `PRANK` | Dispetto: icone a cerchio o caos totale |

### Interazione con Desktop (Win32)
| Feature | Dettaglio |
|---|---|
| **Furto icone** | `LVM_SETITEMPOSITION32` via `WriteProcessMemory` (32-bit safe) |
| **Nome icona** | `LVM_GETITEMTEXT` via `ReadProcessMemory` — legge il titolo reale |
| **Icona nascosta** | Durante CARRYING la vera icona è off-screen: si vede solo la replica |
| **Auto-arrange off** | Disabilita `LVS_AUTOARRANGE` all'avvio |
| **Spinta fisica** | Muove icona 2.5px/frame, rimbalza sui bordi |
| **Trasporto in testa** | Replica visiva sopra la testa con nome reale + emoji tipo |
| **Click → ripristino** | Clicca Lupin mentre trasporta → "scusa!" + icona torna al posto |
| **Auto-ripristino** | Dopo 2 minuti: "Per stavolta sistemo io…" + ripristino |
| **Scatter cerchio** | Icone disposte in ellisse attorno al centro |
| **Scatter caos** | Icone in posizioni casuali visibili |
| **Portale buco nero** | Animazione vortice viola all'entrata/uscita del ladro |

### Icona Trasportata
| Feature | Dettaglio |
|---|---|
| **Nome reale** | Titolo letto da Explorer (`LVM_GETITEMTEXT`) mostrato in pill scura |
| **Emoji adattiva** | 📁 cartella / 🐍 Python / 🌐 browser / 🎮 giochi / ⚙️ .exe / 🗑️ cestino… |
| **Alone pulsante** | Glow dorato animato con oscillazione sinusoidale |
| **Nascosta durante carrying** | L'originale va a -300,-300; al rilascio torna alla posizione salvata |

### Sistema Colpi (Click su Lupin)
| Combo | Reazione + Particelle |
|---|---|
| ×1 | 💢 pugno + 😮 + stelle + "Ow! Che maleducato! 😤" |
| ×2 | 💥 pugno grande + 😠 + scintille + "BASTARDO! Non colpirmi! 😡" |
| ×3 | 🤛 + 😡 + onde d'urto + shake schermo + "Chiamo i Carabinieri! 🚔" |
| ×4 | 👊 + 🤬 + flash + "Articolo 581 cp! 📜" |
| ×5+ | 💥 + 💀 + flash schermo + "Ti denuncio a 8 tribunali!" |
| Esausto | "VIGLIACCO! Colpisci un esausto!" |

> **Click detection**: `GetAsyncKeyState(VK_LBUTTON)` poll ogni frame — nessun hook globale, nessun blocco del mouse. Raggio di rilevamento: ±65px orizzontale, ±90px verticale dal centro Lupin.

### Effetti Visivi
| Feature | Dettaglio |
|---|---|
| **Particelle** | 10 tipi: sparkle, smoke, heart, note, zzz, confetti, star, sweat, dust, emoji_pain |
| **Maschera da ladro** | Striscia nera in APPROACHING/STEALING |
| **Refurtiva orbitante** | 👑💎🏅✨🪙💍 con alone dorato |
| **Barra volume** | HUD animato verde→giallo→rosso + 🔊 |
| **Toast notifications** | Slide-in da destra con countdown |
| **Speech bubble** | Bolla con scale-in, coda, word-wrap |
| **Screen shake** | Intensità proporzionale al combo colpi |
| **Trail corsa** | Scia ellissoidale semi-trasparente |
| **Shadow dinamica** | Si rimpicciolisce con l'altezza del salto |
| **Dust particelle** | Nuvole di polvere durante corsa/caduta |

### Animazioni Corpo
| Parte | Animazione |
|---|---|
| **Testa** | Bob sinusoidale + respirazione + tilt mentre beve |
| **Occhi** | Tracking cursore con pupille, blink casuale |
| **Bocca** | Sorriso, O-sorpresa, smorfia, ansimante, linguaccia animata |
| **Maschera** | Striscia nera da ladro in APPROACHING/STEALING |
| **Braccia** | Pose per ogni stato: saluto, ballo, trasporto, spinta, appoggio, birra |
| **Gambe** | Corsa alternata, seduto disteso, accasciato esausto |
| **Guance** | Rossore per stati felici/eccitati |
| **Cappello** | Lupin III con tesa, corpo e fascetta rossa |

### Personalità
| Tipo | Aggressività | Distanza fuga | Avidità |
|---|---|---|---|
| 😤 Aggressive | Alta | 280px | 85% |
| 🎮 Playful | Media | 380px | 65% |
| 🥷 Sneaky | Bassa | 480px | 45% |

### Audio
| Feature | Dettaglio |
|---|---|
| **pygame-ce** | Community edition, pre-built per Python 3.14 |
| **Suoni facoltativi** | Graceful fallback se pygame non disponibile |

---

## 📁 Struttura Progetto

```
lupin-desktop-pet/
├── main.py              # Entry point
├── pet_brain.py         # State machine (23 stati, fisica, AI comportamentale)
├── pet_window.py        # PyQt5 overlay + renderer procedurale Lupin
├── desktop_hooks.py     # Win32 API — LVM_SETITEMPOSITION32, LVM_GETITEMTEXT
├── sound_manager.py     # Audio pygame-ce
├── launch.vbs           # Avvio silenzioso (no CMD)
└── requirements.txt
```

---

## 🔧 Requisiti

```
PyQt5>=5.15
pywin32
pygame-ce>=2.5   # opzionale — audio
```

---

## 👤 Author

**Lorenzo Garoffolo**  
🌐 [lorenzo-garoffolo-cyber.netlify.app](https://lorenzo-garoffolo-cyber.netlify.app/)  
📧 [GitHub: @Lorenzozero](https://github.com/Lorenzozero)

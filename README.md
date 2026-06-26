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
| **Movimento smart** | Si orienta verso le icone del desktop — 50% probabilità di sceglierle come meta |
| **Salto con gravità** | `jump_z` + `jump_vel`, gravità 1.4/frame |
| **Wrap-around Pac-Man** | Esce da **qualsiasi** bordo (sinistra/destra **e** alto/basso) e rientra dall'opposto — copie "fantasma" ai bordi così non si vede mai mezzo personaggio |
| **Multi-monitor reale** | Si muove su **tutti** i monitor disponibili (virtual screen Win32); coordinate locali `[0, sw]×[0, sh]` allineate alle icone del desktop |
| **Evita il cursore** | In IDLE si allontana se il mouse si avvicina (<180px) e scappa di scatto se troppo vicino (<85px) |
| **Schiacciamento** | Corpo si deforma durante la corsa |
| **Body rotation** | Rotazione durante la corsa veloce |
| **Boost velocità** | Ogni colpo ricevuto in fuga lo fa accelerare |

### Stati & Comportamenti (24 stati)
| Stato | Descrizione |
|---|---|
| `IDLE` | Vaga notando le icone vicine, le commenta, salta occasionalmente |
| `SLEEPING` | Si addormenta dopo 40s (20s di notte) — dondola lentamente mentre sogna |
| `CURIOUS` | Si avvicina al cursore, si spaventa se troppo vicino |
| `FOLLOWING` | Segue il cursore saltellando |
| `WAVING` | Saluta con animazione braccio + cuori |
| `DANCING` | Balla con saltelli ritmici e note musicali |
| `HANGING` | Si appende a un'icona del desktop |
| `PUSHING` | Spinge fisicamente un'icona attraverso il desktop |
| `CARRYING` | Porta un'icona sopra la testa — la originale sparisce, replica visiva animata |
| `SITTING` | Si siede su un'icona e chiacchiera |
| `LEANING` | Si appoggia al bordo schermo — appare un lampione procedurale |
| `CORNER` | Si nasconde in un angolo con braccia conserte |
| `EXHAUSTED` | Si accascia dopo una lunga fuga, ansima con fiatone |
| `DRINKING` | Beve una birra 🍺, testa che si inclina, poi rutta |
| `VOLUME_TRICK` | Alza il volume del PC con animazione + barra visiva |
| `PHONE` | Chiama i complici (Jigen/Goemon/Fujiko) — telefono disegnato, conversazione a bolle |
| `APPROACHING` | Corre verso un'icona con maschera da ladro |
| `STEALING` | Si appoggia **dietro** l'icona e la **spinge fisicamente** sul desktop (icona reale che scivola), poi la afferra: sparisce e va sopra la testa col **titolo reale** |
| `TAUNTING` | Si prende gioco di te con refurtiva orbitante 👑💎🏅 |
| `RUNNING` | Fuga con wrap-around, gocce di sudore, velocità crescente se colpito |
| `HIDING` | Si nasconde dietro finestre aperte |
| `SURRENDER` | Si arrende solo se cliccato durante TAUNTING — mai durante la fuga |
| `CELEBRATING` | Festeggia con coriandoli e cuori |
| `PRANK` | Dispetto: icone a cerchio o caos totale |

### Interazione con Desktop (Win32)
| Feature | Dettaglio |
|---|---|
| **Furto icone** | `LVM_SETITEMPOSITION32` via `WriteProcessMemory` (32-bit safe) |
| **Nome icona** | `LVM_GETITEMTEXTW` (Unicode) via `ReadProcessMemory` — legge il titolo reale dell'oggetto |
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

### Interazione Mouse
| Click | Effetto |
|---|---|
| **Clic sinistro su Lupin** | Pugno + particelle + insulto (escalation combo) |
| **Doppio click su Lupin** | Reazione drammatica potenziata + flash schermo |
| **Clic destro su Lupin** | Lupin viene accarezzato — cuori, scintille, reazione imbarazzata |

### Sistema Colpi — Stato Normale
| Combo | Reazione + Particelle |
|---|---|
| ×1 | 💢 pugno + 😮 + stelle + *"Ow! Che maleducato! 😤"* |
| ×2 | 💥 pugno grande + 😠 + scintille + *"BASTARDO! Non colpirmi! 😡"* |
| ×3 | 🤛 + 😡 + onde d'urto + shake + *"Chiamo i Carabinieri! 🚔"* → scappa |
| ×5+ | 💥 + 💀 + flash schermo + *"Ti denuncio a 8 tribunali!"* |
| Esausto | *"VIGLIACCO! Colpisci un esausto!"* — salto debolissimo |

### Sistema Colpi — Durante la Fuga
Lupin **non si arrende mai** durante la fuga — reagisce progressivamente e accelera:

| Colpo | Reazione |
|---|---|
| 1° | Restituisce **una** icona rubata · *"Ok ok LA RIDÒ! Ricordati la mia faccia! 😤"* |
| 2°–3° | Impreca · *"BASTARDO! Smettila! 💢"* · velocità +1.0 |
| 4°–5° | *"CHIAMO LA POLIZIA! 113! 📞"* · velocità +3.0 |
| 6°–7° | *"Sono già sparito! 💨"* · velocità massima (18px/frame) |
| 8°+ | Crolla esausto — non ce la fa più fisicamente |

> **Click detection**: `GetAsyncKeyState(VK_LBUTTON/RBUTTON)` bit 15 con edge-detection — nessun hook globale, nessun blocco del mouse. La posizione di Lupin è convertita in coordinate schermo con `mapToGlobal` e confrontata con `QCursor.pos()` (stesso sistema di coordinate Qt → corretto anche con monitor a sinistra/offset negativi e DPI). Raggio: ±115px orizzontale, ±135px verticale.

### Comportamenti Temporali
| Ora | Comportamento |
|---|---|
| **23:00 – 06:00** | Si addormenta dopo 20s (invece di 40s), telefonate più frequenti |
| **12:00 – 14:00** | Beve più birre (pausa pranzo) |
| **Ogni 8–12 minuti** | Commenta l'ora con battute tematiche (mattina/pranzo/sera/notte) |

### Effetti Visivi
| Feature | Dettaglio |
|---|---|
| **Particelle** | 10 tipi: sparkle, smoke, heart, note, zzz, confetti, star, sweat, dust, emoji_pain |
| **Lampione procedurale** | Palo metallico + braccio curvo + lanterna pulsante in LEANING su bordo schermo |
| **Telefono disegnato** | Braccio alzato + rettangolo nero con schermo blu in stato PHONE |
| **Maschera da ladro** | Striscia nera in APPROACHING/STEALING |
| **Refurtiva orbitante** | 👑💎🏅✨🪙💍 con alone dorato |
| **Barra volume** | HUD animato verde→giallo→rosso + 🔊 |
| **Toast notifications** | Slide-in da destra con countdown |
| **Speech bubble** | Bolla con scale-in, drop shadow, bordo scuro, font emoji |
| **Screen shake** | Intensità proporzionale al combo colpi |
| **Trail corsa** | Scia ellissoidale semi-trasparente |
| **Shadow dinamica** | Si rimpicciolisce con l'altezza del salto |
| **Portale buco nero** | Vortice viola con scintille orbitanti |

### Animazioni Corpo
| Parte | Animazione |
|---|---|
| **Testa** | Bob sinusoidale + respirazione + tilt mentre beve |
| **Occhi** | Tracking cursore con pupille, blink casuale |
| **Bocca** | Sorriso, O-sorpresa, smorfia, ansimante, linguaccia animata |
| **Maschera** | Striscia nera da ladro in APPROACHING/STEALING |
| **Braccia** | Pose per ogni stato: saluto, ballo, trasporto, spinta, appoggio, birra, telefono |
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
├── pet_brain.py         # State machine (24 stati, fisica, AI comportamentale)
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

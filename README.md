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

# Versione 2D (root)
start launch.vbs
# oppure:
pythonw main.py

# Versione 3D (pseudo-3D renderer)
start version-3d\launch3d.vbs
# oppure:
cd version-3d && pythonw main.py
```

**ESC** per chiudere e ripristinare tutte le icone.  
**S** (versione 3D) per mostrare/nascondere il pannello statistiche.

---

## 🎮 Versione 2D — Funzionalità

### Movimento & Fisica
| Feature | Dettaglio |
|---|---|
| **Movimento smooth** | Velocità + accelerazione, inerzia fisica |
| **Salto con gravità** | `jump_z` + `jump_vel`, gravità 1.4/frame |
| **Wrap-around schermo** | Esce da un lato, rientra dall'altro |
| **Dual monitor** | Riconosce lo schermo virtuale, si muove su tutti i monitor |
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
| `STEALING` | Ruba l'icona (Win32 LVM32) esce da un buco nero |
| `TAUNTING` | Si prende gioco di te con refurtiva orbitante |
| `RUNNING` | Fuga con wrap-around e gocce di sudore |
| `HIDING` | Si nasconde dietro finestre aperte |
| `SURRENDER` | Si arrende se cliccato — nessuna lacrima, solo resa |
| `CELEBRATING` | Festeggia con coriandoli e cuori |
| `PRANK` | Dispetto: icone a cerchio o caos totale |

### Interazione con Desktop (Win32)
| Feature | Dettaglio |
|---|---|
| **Furto icone** | `LVM_SETITEMPOSITION32` via `WriteProcessMemory` (32-bit safe) |
| **Auto-arrange off** | Disabilita `LVS_AUTOARRANGE` all'avvio |
| **Spinta fisica** | Muove icona 2.5px/frame, rimbalza sui bordi |
| **Trasporto in testa** | Icona segue la testa di Lupin frame-by-frame |
| **Click → ripristino** | Clicca Lupin mentre spinge/trasporta → icona torna al posto |
| **Auto-ripristino** | Dopo 2 minuti: "Per stavolta sistemo io…" + ripristino |
| **Scatter cerchio** | Icone disposte in ellisse attorno al centro |
| **Scatter caos** | Icone in posizioni casuali visibili |
| **Portale buco nero** | Animazione vortice viola all'entrata/uscita del ladro |

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

### Sistema Colpi (Click Combo)
| Combo | Reazione |
|---|---|
| ×1 | "Ow! Che maleducato! 😤" |
| ×2 | "BASTARDO! Non colpirmi! 😡" |
| ×3 | "Chiamo i Carabinieri! 🚔" — inizia a scappare |
| ×4 | "Articolo 581 cp! 📜" — fuga con shake |
| ×5+ | "Ti denuncio a 8 tribunali!" — flash + fuga |
| Esausto | "VIGLIACCO! Colpisci un esausto!" |

### Personalità
| Tipo | Aggressività | Distanza fuga | Avidità |
|---|---|---|---|
| 😤 Aggressive | Alta | 280px | 85% |
| 🎮 Playful | Media | 380px | 65% |
| 🥷 Sneaky | Bassa | 480px | 45% |

---

## 🧊 Versione 3D — `version-3d/`

Riscritta completamente su **PyQt5** con rendering pseudo-3D procedurale — nessuna dipendenza da Panda3D o modelli 3D.

### Rendering 3D Procedurale
| Tecnica | Dettaglio |
|---|---|
| **Depth extrusion** | Ogni shape ha layer "lato" (scuro, offset) + "fronte" (lit) |
| **Sphere gradient head** | Radial gradient con specular highlight bianco |
| **Cylinder arms** | Segmenti con QPen a doppio strato — ombra + lit |
| **Perspective shadow** | Ellisse radiale proiettata sul "pavimento" |
| **3D hat** | Tesa ellittica + corona con gradient laterale |
| **Body squash/stretch** | Deformazione proporzionale alla velocità |
| **Z-depth particles** | Particelle con z-velocity e size proporzionale alla profondità |

### Sistemi Esclusivi (3D)
| Sistema | Dettaglio |
|---|---|
| **Achievements** | 10+ achievement con tracking JSON persistente in `achievements.json` |
| **Stats lifetime** | Furti, sessioni, distanza, combo record in `player_stats.json` |
| **Achievement toasts** | Notifiche animate slide-in con icona + nome |
| **Stats HUD** | Pannello live (tasto S): personalità, furti, achievements, sessione |
| **3D ParticleSystem** | Sparkle, smoke, confetti, heart, sweat, star con z-physics |

### Stati (7 core)
| Stato | Descrizione |
|---|---|
| `IDLE` | Vagabonda con breath animation |
| `APPROACHING` | Corre con lean-forward |
| `STEALING` | Burst sparkle dorato + screen shake |
| `TAUNTING` | Bounce + confetti |
| `RUNNING` | Squash/stretch + smoke trail |
| `HIDING` | Accovacciato dietro finestre |
| `SURRENDER` | Mani alzate + cuori |

### Achievement disponibili
| Achievement | Condizione | Ricompensa |
|---|---|---|
| 🎒 Primo Furto | Prima icona rubata | `unlock_voice_taunt` |
| 🏆 Maestro Ladro | 100 furti totali | `unlock_skin_gold` |
| ⚡ Speedrunner | 5 icone in 30s | `unlock_speed_boost` |
| 🔥 Re dei Combo | Combo ×10 | `unlock_particle_fire` |
| 🥷 Ninja | Nascosto 5 minuti | `unlock_invisibility` |
| 👻 Intoccabile | Evita cursore 2 min | `unlock_teleport` |
| 📦 Accumulatore | 8 icone in sessione | `unlock_skin_rainbow` |
| ⏱️ Maratoneta | 1 ora di gioco | `unlock_emote_dance` |
| 🌙 Ladro di Mezzanotte | Gioca alle 00:00 | `unlock_moon_particles` |
| 🎮 Codice Konami | Input segreto | `unlock_god_mode` |

---

## 📁 Struttura Progetto

```
lupin-desktop-pet/
├── main.py                 # Entry point 2D
├── pet_brain.py            # State machine 2D (23 stati, fisica, AI)
├── pet_window.py           # PyQt5 overlay + renderer 2D procedurale
├── desktop_hooks.py        # Win32 API per icone desktop (LVM_SETITEMPOSITION32)
├── sound_manager.py        # Audio pygame-ce
├── launch.vbs              # Avvio silenzioso 2D (no CMD)
├── requirements.txt
└── version-3d/             # Versione pseudo-3D — PyQt5
    ├── main.py             # Entry point 3D
    ├── pet3d_app.py        # Renderer pseudo-3D volumetrico + HUD
    ├── pet3d_brain.py      # State machine 3D (7 stati)
    ├── particle_system3d.py# Particelle 3D con z-physics (PyQt5)
    ├── desktop_hooks.py    # Win32 API (shared con 2D)
    ├── achievements.py     # 10+ achievement con persistenza JSON
    ├── stats_tracker.py    # Statistiche lifetime persistenti
    ├── skin_manager.py     # Sistema skin (estendibile)
    ├── ai_chat.py          # Risposte AI (estendibile con OpenAI)
    ├── voice_system.py     # TTS (estendibile con pyttsx3)
    ├── weather_system.py   # Sistema meteo (estendibile)
    ├── minigames.py        # Mini-giochi (estendibile)
    ├── launch3d.vbs        # Avvio silenzioso 3D (no CMD)
    └── models/             # Placeholder modelli 3D futuri (.glb/.bam)
```

---

## 🔧 Requisiti

```bash
# Versione 2D + 3D
pip install PyQt5 pywin32

# Audio (opzionale, solo 2D)
pip install pygame-ce
```

Nessuna dipendenza da Panda3D — la versione 3D usa esclusivamente PyQt5.

---

## 👤 Author

**Lorenzo Garoffolo**  
🌐 [lorenzo-garoffolo-cyber.netlify.app](https://lorenzo-garoffolo-cyber.netlify.app/)  
📧 [GitHub: @Lorenzozero](https://github.com/Lorenzozero)

# 🎩 Lupin Desktop Pet

> *"Se mi prendi ti ridò il tuo desktop esattamente com'era!"*

<p align="center">
  <img src="assets/demo.gif" alt="Lupin ruba le icone del desktop" width="640">
</p>

Lupin III vive sul tuo desktop. Cammina tra i monitor, **ruba davvero le icone**
spingendole via e portandole sopra la testa, fa telefonate ai complici, beve
birre, balla, dorme — e se provi a cliccarlo scappa impaurito **insultandoti in
italiano**. Non si arrende mai durante la fuga: più lo colpisci, più corre forte
e più si arrabbia, finché non chiama la polizia o crolla esausto.

È disegnato **interamente a codice** (nessuno sprite): ogni capello, la giacca
rossa, il cappello con la fascetta, le animazioni di corsa e le pose sono
generate frame per frame con `QPainter`. Gira come overlay trasparente a tutto
schermo su Windows, senza mai rubarti i click sul desktop sotto.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Platform](https://img.shields.io/badge/Windows-10%2F11-lightgrey.svg)
![PyQt5](https://img.shields.io/badge/UI-PyQt5-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🚀 Avvio

```bash
pip install PyQt5 pywin32 pygame-ce
start launch.vbs      # avvio silenzioso (no finestra CMD)
# oppure:  pythonw main.py
```

Premi **ESC** per chiudere e rimettere tutte le icone al loro posto.

---

## 🎮 Cosa fa

**Ruba le icone sul serio.** Si avvicina con la maschera da ladro, si appoggia
dietro un'icona e la **spinge fisicamente** sul desktop (la vedi scivolare via),
poi la afferra: l'icona sparisce e ne compare una replica sopra la sua testa, col
**titolo reale** dell'oggetto. Tutto via Win32 (`LVM_SETITEMPOSITION32`,
`LVM_GETITEMTEXTW`). Quando lo catturi, rimette ogni cosa esattamente dov'era.

**Reagisce ai tuoi click.** Avvicini il mouse e si allontana; ti avvicini troppo
e scatta in fuga. Se riesci a colpirlo parte l'escalation di insulti — *"Ehi
STRONZO!"* → *"BASTARDO, smettila!"* → *"CHIAMO LA POLIZIA! 113!"* — e durante la
fuga accelera a ogni colpo invece di fermarsi. Click destro per accarezzarlo
(cuori e imbarazzo), doppio click per una reazione drammatica.

**Vive di vita sua.** Ha 24 stati e una personalità casuale (aggressivo /
giocherellone / furtivo) che cambia quanto è avido e quanto scappa lontano. Vaga
notando le icone, dorme se lo lasci in pace (prima di notte), telefona ai
complici, balla, beve birre a pranzo, e commenta l'ora con battute a tema.

**Gira su tutti i monitor.** Si muove sull'intero virtual screen e fa
**wrap-around stile Pac-Man**: esce da un lato e rientra dall'altro, attraversando
gli schermi senza soluzione di continuità.

---

## 🧠 Come è fatto

| File | Ruolo |
|---|---|
| `main.py` | Entry point |
| `pet_brain.py` | State machine: 24 stati, fisica, IA comportamentale, personalità |
| `pet_window.py` | Overlay PyQt5 + renderer procedurale di Lupin (zero sprite) |
| `desktop_hooks.py` | Win32: legge/sposta le icone reali del desktop |
| `sound_manager.py` | Audio opzionale (pygame-ce, fallback silenzioso) |

Un paio di dettagli tecnici di cui vado fiero: i click sono rilevati con
`GetAsyncKeyState` senza hook globali (niente mouse bloccato), e la posizione di
Lupin è convertita con `mapToGlobal` per funzionare anche con monitor a sinistra
(offset negativi) e DPI scaling. Le coordinate del cervello sono locali alla
finestra e allineate a quelle delle icone del desktop, così furto e spinta sono
precisi su qualsiasi configurazione di schermi.

---

## 📋 Tutte le funzionalità interattive

### Interazione col mouse
| Azione | Reazione di Lupin |
|---|---|
| **Mouse si avvicina** (<180px) | Si allontana lentamente, a disagio |
| **Mouse troppo vicino** (<85px) | Scatta in fuga impaurito |
| **Click sinistro su Lupin** | Pugno + particelle + insulto (escalation a combo) |
| **Doppio click** | Reazione drammatica potenziata + flash schermo |
| **Click destro** (carezza) | Cuori, scintille, reazione imbarazzata |
| **Click mentre trasporta un'icona** | *"Scusa!"* → rimette l'icona al suo posto |
| **Click mentre schernisce/prank** | Si arrende → ripristina tutto il desktop |
| **ESC** | Chiude e ripristina ogni icona |

### Sistema colpi — stato normale
| Combo | Reazione |
|---|---|
| ×1 | *"Ehi STRONZO! Attento!"* — pugno + stelle |
| ×2 | *"BASTARDO! Non colpirmi!"* — scintille |
| ×3 | *"CHIAMO LA POLIZIA! 113!"* — shake + scappa |
| ×5 | *"Ti denuncio a 8 tribunali!"* — flash + fuga |
| esausto | *"VIGLIACCO! Colpisci un esausto!"* — salto debolissimo |

### Sistema colpi — durante la fuga *(non si arrende mai)*
| Colpo | Reazione |
|---|---|
| 1° | Restituisce **una** icona rubata · *"Ok LA RIDÒ!"* |
| 2°–3° | Impreca e accelera · *"BASTARDO, smettila!"* |
| 4°–5° | Minaccia · *"CHIAMO LA POLIZIA!"* · più veloce |
| 6°–7° | *"Sono già sparito!"* · velocità massima |
| 8°+ | Crolla esausto — non ce la fa più |

### I 24 stati
| Stato | Cosa fa |
|---|---|
| `IDLE` | Vaga notando le icone, le commenta, salta |
| `SLEEPING` | Si addormenta (prima di notte) e dondola sognando |
| `CURIOUS` / `FOLLOWING` | Si avvicina / segue il cursore saltellando |
| `WAVING` / `DANCING` | Saluta con cuori / balla con note musicali |
| `HANGING` / `PUSHING` | Si appende a un'icona / la spinge sul desktop |
| `APPROACHING` / `STEALING` | Corre con la maschera / spinge e ruba l'icona |
| `CARRYING` | Porta l'icona sopra la testa col titolo reale |
| `TAUNTING` | Si prende gioco di te con la refurtiva |
| `RUNNING` / `HIDING` | Fuga con wrap-around / si nasconde vicino a una finestra |
| `EXHAUSTED` | Si accascia ansimando dopo una lunga fuga |
| `SURRENDER` / `CELEBRATING` | Si arrende / festeggia con coriandoli |
| `SITTING` / `LEANING` / `CORNER` | Si siede / si appoggia (con lampione) / sta in un angolo |
| `DRINKING` / `PHONE` / `VOLUME_TRICK` | Beve una birra e rutta / chiama i complici / alza il volume |
| `PRANK` | Sparpaglia le icone in cerchio o nel caos |

### Comportamenti temporali
| Quando | Cosa cambia |
|---|---|
| **23:00 – 06:00** | Si addormenta prima, telefonate più frequenti |
| **12:00 – 14:00** | Beve più birre (pausa pranzo) |
| **Ogni 8–12 min** | Commenta l'ora con battute a tema |

### Personalità *(casuale a ogni avvio)*
| Tipo | Aggressività | Distanza fuga | Avidità |
|---|---|---|---|
| 😤 Aggressive | Alta | 280px | 85% |
| 🎮 Playful | Media | 380px | 65% |
| 🥷 Sneaky | Bassa | 480px | 45% |

---

## 👤 Autore

**Lorenzo Garoffolo** · [Portfolio](https://lorenzo-garoffolo-cyber.netlify.app/) · [GitHub @Lorenzozero](https://github.com/Lorenzozero)

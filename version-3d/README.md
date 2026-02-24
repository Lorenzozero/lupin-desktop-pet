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

## 🛠️ Architettura

```
version-3d/
├── main.py               # Entry point Panda3D
├── pet3d_app.py          # ShowBase: rendering, camera, lighting, tasks
├── pet3d_brain.py        # State machine con physics-based movement
├── particle_system3d.py  # Sistema particelle 3D billboarded
├── desktop_hooks.py      # Win32 API icone desktop
├── requirements.txt
└── models/
    └── lupin.glb            # ← Metti qui il tuo modello 3D!
```

---

## ⌨️ Comandi

| Tasto | Azione |
|---|---|
| Click sinistro | Cattura Lupin (se ha icone) |
| ESC | Chiude e ripristina icone |

---

## 🔧 Troubleshooting

### Finestra non trasparente
- Assicurati di avere **Aero abilitato** (Windows 10/11 con GPU discreta)
- Prova ad eseguire come **Amministratore**

### GLB non si carica
```bash
pip install panda3d-gltf
```
Se il modello non viene trovato, il sistema usa automaticamente un **fallback geometrico 3D procedurale**

### Performance
- Riduci `count` nelle chiamate `burst_sparkle()` in `pet3d_app.py`
- Abbassa la risoluzione delle texture del modello in Blender prima dell'export

---

## 📊 Differenze vs Versione 2D

| Feature | 2D (PyQt5) | 3D (Panda3D) |
|---|---|---|
| Modello | PNG sprite 90x90 | GLB mesh con armatura |
| Animazioni | Framesheet PNG | Skeletal animation clip |
| Luci | Gradiente statico | 3 luci dinamiche real-time |
| Particelle | QPainter 2D | Quad billboarded 3D |
| Ombra | Ellisse gradiente | Blob shadow 3D |
| Performance | ≈ 2% CPU | ≈ 5-10% CPU + GPU |
| Setup | pip install 2 pkg | pip install 3 pkg + modello |

---

*Costruito per chi vuole un desktop pet degno di un game AAA.* 🎩✨

import math, random, win32api
from datetime import datetime
from enum import Enum, auto

class S(Enum):
    IDLE         = auto()
    SLEEPING     = auto()
    CURIOUS      = auto()
    FOLLOWING    = auto()
    WAVING       = auto()
    DANCING      = auto()
    HANGING      = auto()
    PUSHING      = auto()
    CARRYING     = auto()
    SITTING      = auto()
    LEANING      = auto()
    CORNER       = auto()
    EXHAUSTED    = auto()
    VOLUME_TRICK = auto()
    DRINKING     = auto()   # beve una birra
    APPROACHING  = auto()
    STEALING     = auto()
    TAUNTING     = auto()
    RUNNING      = auto()
    HIDING       = auto()
    SURRENDER    = auto()
    CELEBRATING  = auto()
    PRANK        = auto()

FRIENDLY_STATES = {S.IDLE, S.SLEEPING, S.CURIOUS, S.FOLLOWING,
                   S.WAVING, S.DANCING, S.HANGING, S.CELEBRATING,
                   S.PUSHING, S.CARRYING, S.SITTING, S.LEANING, S.CORNER,
                   S.EXHAUSTED, S.DRINKING}

# Battute italiane per ogni situazione
JOKES = {
    "taunt":      ["Non ci arriverai mai! 😝",
                   "Le tue icone? ORA SONO MIE! 😎",
                   "Presto come una lumaca! 🐌",
                   "Corri corri... ma non abbastanza! 😜",
                   "Il tuo desktop è diventato arte moderna 🎨",
                   "Ho visto tartarughe più veloci! 🐢"],
    "caught":     ["Ok, stavolta hai vinto tu... 😤",
                   "Patta! Ma tornerò! 🤜",
                   "Ugh... ti concedo la vittoria. PER ORA.",
                   "Bravo! Ma era un piano... forse.",
                   "Questa non me la dimentico! 😒"],
    "waving":     ["Ciao! Sono il tuo nuovo problema 👋",
                   "Buongiorno! Pronto a divertirti? 😄",
                   "Ehi! Non ignorarmi! 👀",
                   "Sono tornato! Ti mancavo? 😏"],
    "dancing":    ["🎵 La la la la!",
                   "Dai, balla con me! 🕺",
                   "Sentilo il ritmo! ♪♫",
                   "Lupin balla, tu guardi! 💃"],
    "prank_circle":["Icone in cerchio! Arte! 🎨",
                    "Ecco il mio capolavoro! 🖼️",
                    "Fibonacci? No, Lupin! 🌀",
                    "Un po' di ordine... circolare! ⭕"],
    "prank_chaos": ["CAOS TOTALE! 🌪️",
                    "Il desktop era troppo noioso! 😂",
                    "Ti ho ridato la creatività! 🎲",
                    "Benvenuto nel mio mondo! 😈"],
    "hanging":    ["Ciao dall'alto! 😎",
                   "Ottima vista da quassù! 🏔️",
                   "Appeso come un pipistrello! 🦇",
                   "Mi faccio un giro!"],
    "curious":    ["Cosa stai facendo? 🤔",
                   "Hmm... interessante!",
                   "Mi avvicino... piano piano 🐱",
                   "Chi sei straniero? 👀"],
    "wakeup":     ["Ah! Sei tornato! 😃",
                   "Svegliami ancora... ti prego! 😴",
                   "Dormivo così bene! 😤"],
    "celebrating":["LIBERO! 🎉",
                   "Ok ok, patta! 🤝",
                   "Rivincita alle 15:00! ⏰",
                   "Mi hai beccato... stavolta! 😏"],
    "following":  ["Dove vai senza di me?! 🏃",
                   "Aspettami! 😅",
                   "Ti seguo ovunque! 👣"],
    "hit_1":      ["Ow! Che maleducato! 😤",
                   "Ehi! Attento! 😠",
                   "Cosa ti ho fatto?!",
                   "Non ho fatto nulla! 😇",
                   "Questo è bullismo! 📢"],
    "hit_2":      ["BASTARDO! Non colpirmi! 😡",
                   "Smettila o chiamo mia nonna! 👵",
                   "Sei una persona orribile! 😤",
                   "Mi stai facendo male, psicopatico!",
                   "Il tuo karma sarà terribile! ☠️"],
    "hit_3":      ["BASTA! Chiamo i Carabinieri! 🚔",
                   "Questo è reato! Articolo 581 cp! 📜",
                   "Denuncia depositata! ⚖️",
                   "Violenza su animale virtuale! VERGOGNA!",
                   "Sei peggio del mio avvocato!"],
    "hit_escape": ["SCAPPO! Tornerò con gli avvocati! 😤",
                   "VIGLIACCO! Ti denuncio a 8 tribunali!",
                   "Non ti perdonerò mai, MOSTRO! 💢",
                   "Codardo! Colpire chi non si difende!",
                   "Me la pagherai! Con gli interessi! 😈"],
    "hit_taunt":  ["Neanche sento! Sono di gomma! 😝",
                   "Troppo lento! Manco mi tocchi!",
                   "Haha! Le tue dita fanno solletico! 😂",
                   "Potresti almeno provarci seriamente?"],
    "surrender":  ["Ok le restituisco... 😒",
                   "Tutte qui? Ne mancava una! 😇",
                   "Trattativa conclusa! 🤝"],
    "pushing":    ["Via via via! Spostati! 💪",
                   "Un po' di ordine! 🧹",
                   "Questa icona va QUI! 😤",
                   "Su! Muoviti pesante! 🏋️",
                   "Ridecoro il tuo desktop! 🎨"],
    "carrying":   ["Consegne a domicilio! 📦",
                   "Porto questo in giro! 😏",
                   "L'ho preso in prestito... 😇",
                   "Giro giro tondo! 🚶",
                   "Trovatore d'icone al lavoro!"],
    "leaning":    ["Bella finestra! 😎",
                   "Chill mode: ON 😌",
                   "Da qui vedo tutto il desktop!",
                   "Mi appoggio un attimo... 🧱",
                   "Questo muro è comodo!",
                   "Ho trovato il posto migliore 😏"],
    "leaning_lamp":["Bella seratina... quante borse ho fregato 🌙",
                    "Il lampione non parla. A differenza dei testimoni. 🤫",
                    "Ho rubato in 47 paesi. Mai preso. 🌍",
                    "Stanotte ho un colpo da 3 icone... tecnicamente. 🎩",
                    "Chi ha inventato le icone non ha mai incontrato me 😈",
                    "La luna mi copre. Il lampione illumina gli altri. 🕯️",
                    "Ogni grande ladro ha il suo lampione preferito! 😎",
                    "Pensiero: rubare è come scaricare file. Veloce e indolore. 💾",
                    "Il mio avvocato dice che tecnicamente non è furto se ridi mentre lo fai 😂",
                    "Quante rapine ho fatto? Non si conta. Si celebra! 🥂"],
    "wakeup_yawn":["*Sbadiglio* Già mattina? 😪",
                   "Zzz... ah! Chi c'è?! 😲",
                   "Dormivo così bene... 😴",
                   "Mi hai svegliato sul più bello! 😤"],
    "idle_stretch":["Aaahh! Mi scricchiola tutto! 😌",
                    "Stiracchiata mattutina... 🙆",
                    "Creeeek... eccellente! 💪"],
    "idle_look":   ["...cosa c'è là? 🤔",
                    "Hmm... qualcosa non quadra.",
                    "Sto pianificando qualcosa. Non chiedere. 😏"],
    "corner":     ["Nessuno mi trova qui! 😏",
                   "Il mio angolo segreto! 🤫",
                   "Voi umani non capite gli angoli.",
                   "Qui mi sento a casa! 🏠",
                   "L'angolo perfetto per complottare! 😈"],
    "exhausted":      ["...sto... riprendendo fiato... 😮‍💨",
                       "Non ce la... faccio più... 🥵",
                       "Un momento... servo... ossigeno... 😵",
                       "Gambe a pezzi... cuore a pezzi... 💀",
                       "Mamma mia che fatica! Aspetta! 😤",
                       "Il mio cuore sta esplodendo! 💔"],
    "hit_exhausted":  ["VIGLIACCO! Colpisci un esausto! 😤",
                       "Noooo! Aspetta che... riprendo fiato! 😡",
                       "Ma sei umano?! MOSTRO! 🤬",
                       "Non ho forze... però ricordo tutto! 💢",
                       "Questo è accanimento! Chiamo Amnesty! 📞",
                       "Aspetta che mi riprendo... poi ti denuncio in 12 stati! ⚖️",
                       "Sto avendo un infarto... per colpa TUA! 😵",
                       "Vile! Colpire chi non si difende... VERGOGNA! 😠",
                       "Non hai un minimo di pietà?! BARBARO! 🤮",
                       "Ok questo è bullismo virtuale! Ti segnalo! 🚨"],
    "volume_trick":   ["VOLUME AL MASSIMO! 🔊",
                       "Sentitemi TUTTI nel palazzo! 📢",
                       "Il desktop ora suona! 🎵",
                       "DJ Lupin on air! 🎧",
                       "Alzate il volume, è un ordine! 🔉"],
    "drinking":       ["Salute! 🍺",
                       "Una birretta ci vuole! 🍻",
                       "Ah, il meritato riposo del ladro! 🍺",
                       "Cin cin! 🥂",
                       "Al tuo desktop! 😄🍺"],
    "auto_restore":   ["Per stavolta sistemo io... 😒",
                       "Ok ok... rimetto tutto a posto! NON perché mi dispiace! 😤",
                       "Le vostre icone? Le ho sistemate io. Prego. 🙄",
                       "Buonanima delle icone... eccole qui! 😇",
                       "Stavolta sistemo io. Ma solo stavolta! 😈"],
    "click_restore":  ["Ehi! Ok, la rimetto! 😤",
                       "Va bene, va bene... la riporto! 😒",
                       "Stai bene attento! La rimetto a posto... 😑"],
    "scusa_carrying": ["Scusa scusa! La rimetto a posto! 🙏",
                       "Ok ok, mi sono fatto prendere la mano! 😅",
                       "Aaah! Eccola qua, tieni! 😤",
                       "Non ero io! ...Okay ero io. Scusa. 😇"],
    "burp":           ["BRUUUAP! 🤢",
                       "Scusate... la birra sale! 🍺",
                       "BRUAP! Eccellente qualità! 🤣",
                       "*BUURP* — Pardon! 😅",
                       "BRUAAAP! Tre stelle Michelin! 🌟"],
    "linguaccia":     ["Bleah! 😛",
                       "Neanche ti vedo! 👅",
                       "Pffff! 😜",
                       "Ta-da! 👅",
                       "Questo per te! 😝"],
    "wifi_trick":     ["Addio internet! 📵",
                       "WiFi? Non esisteva! 🚫",
                       "Ora lavori DAVVERO! 💼",
                       "Riconnettiti se ci riesci! 😝"],
    "sitting":    ["Bella questa scrivania! 😌",
                   "Da qui vedo tutto! 👀",
                   "Comodo eh? È MIO ora. 😎",
                   "Shhh... sto guardando i tuoi file 🤫",
                   "Non disturbarmi, sto meditando 🧘",
                   "Ah, un po' di relax! ☕",
                   "Questo posto è mio! 😤",
                   "Quanti file inutili hai... 🗂️",
                   "Potrei stare qui per ore! 😴"],
}

class LupinBrain:
    MAX_STEAL = 6

    def __init__(self, sw, sh, hooks, vx=0, vy=0):
        self.sw, self.sh = sw, sh
        self.vx_off = vx   # offset origine virtual screen (per dual monitor)
        self.vy_off = vy
        self.hooks = hooks
        self.x, self.y = vx + sw // 2, vy + sh // 2
        self.tx, self.ty = self.x, self.y
        self.vx, self.vy = 0.0, 0.0
        self.state = S.WAVING
        self.timer = 0
        self.global_timer = 0
        self.direction = 1
        self.stolen = []
        self.target_icon = None
        self.hide_rect = None
        self.peek_side = "right"
        self.anim_frame = 0
        self.anim_tick = 0
        self.personality = random.choice(["aggressive", "playful", "sneaky"])

        # Cursor idle tracking — soglia alta: 40 secondi a ~60fps
        self.last_cursor = win32api.GetCursorPos()
        self.cursor_idle_frames = 0

        self.mood = "happy"
        self.total_steals = 0
        self.times_caught = 0
        self.prank_count = 0
        self.dance_phase = 0.0

        # Salto fisico
        self.jump_z = 0.0
        self.jump_vel = 0.0
        self.is_jumping = False

        # Wrap-around
        self.just_wrapped = False

        self.steal_cooldown = 60

        # Hanging
        self.hang_target = None

        # Pushing
        self.push_icon_idx = None
        self.push_dir = (1.0, 0.0)

        # Carrying
        self.carry_icon_idx  = None
        self.carry_icon_pos  = (0, 0)   # posizione fake per il disegno
        self.carry_icon_name = ""       # nome dell'icona trasportata

        # Idle micro-behaviors
        self.idle_look_dir   = 0        # -1 sinistra, 0 centro, 1 destra
        self.idle_look_timer = 0        # timer per cambio direzione sguardo
        self.idle_micro      = None     # "stretch" | "look" | None

        # Leaning
        self.lean_is_screen  = False    # True se appoggiato a bordo schermo (lampione)

        # Sitting
        self.sit_target    = None
        self._sit_duration = 0

        # Leaning (appoggiato a bordo finestra)
        self.lean_wall_x   = 0     # x del muro
        self.lean_wall_y   = 0     # y del punto di appoggio
        self.lean_side     = "right"  # "left"/"right"/"bottom" - da che lato è il muro

        # Corner
        self.corner_x = 0
        self.corner_y = 0

        self.current_joke = ""

        # Sistema colpi
        self.hit_combo      = 0
        self.last_hit_timer = -999
        self.hit_reaction   = ""

        # Esaurimento
        self._exhausted_rest_pos = None
        self._volume_presses     = 0
        self._icons = {}

        # Freeze movimento durante speech
        self.frozen = False
        self._last_steal_global = 0   # frame in cui è avvenuto l'ultimo furto
        self._auto_restore_said = False

        # Linguaccia timer
        self.tongue_timer = 0
        self.burp_pending = False

    # ── helpers movimento ────────────────────────────────────

    def _cursor(self):
        return win32api.GetCursorPos()

    def _dist_cursor(self):
        cx, cy = self._cursor()
        return math.hypot(self.x - cx, self.y - cy)

    def _move_smooth(self, tx, ty, spd, accel=0.35, wrap=False, margin=25):
        if self.frozen:
            self.vx *= 0.5;  self.vy *= 0.5
            return False
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        if d < 6:
            self.x, self.y = tx, ty
            self.vx *= 0.65
            self.vy *= 0.65
            return True
        self.vx += ((dx / d) * spd - self.vx) * accel
        self.vy += ((dy / d) * spd - self.vy) * accel
        self.x += self.vx
        self.y += self.vy
        if wrap:
            self._wrap_position()
        else:
            self.x = max(self.vx_off + margin, min(self.vx_off + self.sw - margin, self.x))
            self.y = max(self.vy_off + margin, min(self.vy_off + self.sh - 60, self.y))
        self.direction = 1 if self.vx > 0.5 else -1 if self.vx < -0.5 else self.direction
        return False

    def _flee_smart(self, spd=12):
        cx, cy = self._cursor()
        dx, dy = self.x - cx, self.y - cy
        d = math.hypot(dx, dy) or 1
        perp = math.sin(self.timer * 0.22) * 4
        self.vx += (dx / d * spd - dy / d * perp - self.vx) * 0.38
        self.vy += (dy / d * spd + dx / d * perp - self.vy) * 0.38
        spd_now = math.hypot(self.vx, self.vy)
        if spd_now > spd:
            self.vx = self.vx / spd_now * spd
            self.vy = self.vy / spd_now * spd
        self.x += self.vx
        self.y += self.vy
        # Wrap ai bordi durante la fuga
        self._wrap_position()
        self.direction = 1 if self.vx > 0 else -1

    def _wrap_position(self):
        """Esce da un lato e rientra dall'altro (dual-monitor aware)."""
        self.just_wrapped = False
        left  = self.vx_off - 30
        right = self.vx_off + self.sw + 30
        if self.x < left:
            self.x = right - 50
            self.just_wrapped = True
        elif self.x > right:
            self.x = left + 50
            self.just_wrapped = True
        floor = self.vy_off + self.sh + 10 if self.state == S.EXHAUSTED else self.vy_off + self.sh - 80
        top   = self.vy_off + 40
        if self.y < top:
            self.y = top
            self.vy = abs(self.vy) * 0.5
        elif self.y > floor:
            self.y = floor
            self.vy = -abs(self.vy) * 0.5

    def _jump(self, force=18):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_vel = -force

    def _update_jump(self):
        if self.is_jumping:
            self.jump_z += self.jump_vel
            self.jump_vel += 1.4  # gravità
            if self.jump_z >= 0:
                self.jump_z = 0
                self.jump_vel = 0
                self.is_jumping = False

    def _transition(self, state):
        self.state = state
        self.timer = 0
        self.just_wrapped = False

    def _track_cursor(self):
        cx, cy = self._cursor()
        lx, ly = self.last_cursor
        if math.hypot(cx - lx, cy - ly) > 10:
            self.cursor_idle_frames = 0
            self.last_cursor = (cx, cy)
        else:
            self.cursor_idle_frames += 1

    def say(self, key):
        self.current_joke = random.choice(JOKES.get(key, ["..."]))
        return self.current_joke

    # ── update principale ────────────────────────────────────

    def update(self, icons):
        self._icons = icons
        self.anim_tick += 1
        if self.anim_tick >= 8:
            self.anim_frame = (self.anim_frame + 1) % 4
            self.anim_tick = 0
        self.timer += 1
        self.global_timer += 1
        if self.tongue_timer > 0:
            self.tongue_timer -= 1
        self.dance_phase += 0.14
        self._track_cursor()
        self._update_jump()
        if self.steal_cooldown > 0:
            self.steal_cooldown -= 1

        # Auto-restore dopo ~2 minuti (7200 frame) con icone ancora in giro
        if (self.stolen and not self._auto_restore_said
                and self.global_timer - self._last_steal_global > 7200
                and self.state not in (S.RUNNING, S.HIDING, S.SURRENDER, S.STEALING,
                                       S.APPROACHING, S.TAUNTING)):
            self._auto_restore_said = True
            self.say("auto_restore")
            self.hooks.restore_icons()
            self.stolen.clear()
            self.steal_cooldown = 600
            self._jump(10)

        {
            S.IDLE:        lambda: self._idle(icons),
            S.SLEEPING:    lambda: self._sleeping(),
            S.CURIOUS:     lambda: self._curious(),
            S.FOLLOWING:   lambda: self._following(),
            S.WAVING:      lambda: self._waving(),
            S.DANCING:     lambda: self._dancing(),
            S.HANGING:     lambda: self._hanging(icons),
            S.PUSHING:     lambda: self._pushing(icons),
            S.CARRYING:    lambda: self._carrying(),
            S.SITTING:     lambda: self._sitting(),
            S.LEANING:       lambda: self._leaning(),
            S.CORNER:        lambda: self._corner(),
            S.EXHAUSTED:     lambda: self._exhausted(),
            S.VOLUME_TRICK:  lambda: self._volume_trick(),
            S.DRINKING:      lambda: self._drinking(),
            S.APPROACHING:   lambda: self._approaching(),
            S.STEALING:    lambda: self._stealing(icons),
            S.TAUNTING:    lambda: self._taunting(),
            S.RUNNING:     lambda: self._running(),
            S.HIDING:      lambda: self._hiding(),
            S.SURRENDER:   lambda: self._surrender(),
            S.CELEBRATING: lambda: self._celebrating(),
            S.PRANK:       lambda: self._prank(icons),
        }[self.state]()

    # ── stati ────────────────────────────────────────────────

    def _idle(self, icons):
        self.mood = "happy"

        # Sonno dopo ~40 secondi di cursore fermo
        if self.cursor_idle_frames > 2400:
            self._transition(S.SLEEPING)
            return

        # Vagabondaggio su tutto il virtual screen
        if self.timer % 50 == 0:
            self.tx = random.randint(self.vx_off + 30, self.vx_off + self.sw - 30)
            self.ty = random.randint(self.vy_off + 30, self.vy_off + self.sh - 90)

        self._move_smooth(self.tx, self.ty, 5, 0.28)

        # Salto casuale durante il vagabondaggio
        if not self.is_jumping and self.timer % 140 == 0 and random.random() < 0.4:
            self._jump(16)

        # Micro-comportamenti idle: guarda in giro, stiracchia
        self.idle_look_timer += 1
        if self.idle_look_timer > random.randint(180, 360):
            self.idle_look_timer = 0
            self.idle_look_dir = random.choice([-1, 0, 0, 1])
            if random.random() < 0.25:
                self.idle_micro = "stretch"
                self.say("idle_stretch")
            elif random.random() < 0.2:
                self.idle_micro = "look"
                if random.random() < 0.3:
                    self.say("idle_look")
            else:
                self.idle_micro = None
        # Reset micro-behavior dopo un po'
        if self.idle_micro and self.idle_look_timer > 80:
            self.idle_micro = None

        dist = self._dist_cursor()

        # Curiosità verso il cursore
        if dist < 200 and self.timer > 40 and random.random() < 0.015:
            self._transition(S.CURIOUS)
            return

        # Comportamenti casuali con icone
        visible = {k: v for k, v in icons.items()
                   if self.vx_off <= v[0] <= self.vx_off + self.sw
                   and self.vy_off <= v[1] <= self.vy_off + self.sh - 80}
        if self.timer > 80:
            r = random.random()
            if r < 0.003:
                self._transition(S.DANCING)
                return
            if r < 0.005:
                self._transition(S.WAVING)
                return
            if r < 0.007 and visible:
                idx = random.choice(list(visible.keys()))
                self.hang_target = visible[idx]
                self.tx, self.ty = self.hang_target
                self._transition(S.HANGING)
                return
            if r < 0.009 and visible:
                # Spinge un'icona in direzione casuale
                idx = random.choice(list(visible.keys()))
                self.push_icon_idx = idx
                angle = random.uniform(0, 2 * math.pi)
                self.push_dir = (math.cos(angle), math.sin(angle))
                self.tx, self.ty = visible[idx]
                self.say("pushing")
                self._transition(S.PUSHING)
                return
            if r < 0.013 and visible:
                # Si siede su un'icona (più frequente)
                idx = random.choice(list(visible.keys()))
                self.sit_target = visible[idx]
                self._sit_duration = random.randint(500, 1200)
                self.say("sitting")
                self._transition(S.SITTING)
                return
            if r < 0.016 and visible:
                # Raccoglie un'icona e la porta in giro
                idx = random.choice(list(visible.keys()))
                self.carry_icon_idx = idx
                self.carry_icon_name = self.hooks.get_icon_name(idx)
                # Nasconde l'icona reale off-screen (solo la replica disegnata è visibile)
                self.hooks.set_icon_position(idx, -300, -300)
                self.say("carrying")
                self._transition(S.CARRYING)
                return
            if r < 0.019:
                # Angolo schermo
                corners = [(30, 30), (self.sw - 30, 30),
                           (30, self.sh - 90), (self.sw - 30, self.sh - 90)]
                self.corner_x, self.corner_y = random.choice(corners)
                self.say("corner")
                self._transition(S.CORNER)
                return
            if r < 0.022:
                spot = self._find_lean_spot()
                if spot:
                    self.lean_wall_x, self.lean_wall_y, self.lean_side, self.lean_is_screen = spot
                    joke_key = "leaning_lamp" if self.lean_is_screen else "leaning"
                    self.say(joke_key)
                    self._transition(S.LEANING)
                    return
            if r < 0.025:
                self.say("volume_trick")
                self._volume_presses = 0
                self._transition(S.VOLUME_TRICK)
                return
            if r < 0.028:
                # Beve una birra
                self.say("drinking")
                self._transition(S.DRINKING)
                return
            # Linguaccia casuale (senza cambiare stato)
            if r < 0.031 and self.tongue_timer == 0:
                self.say("linguaccia")
                self.tongue_timer = 55
            # Rutto casuale
            if r < 0.034 and self.tongue_timer == 0:
                self.say("burp")
                self.burp_pending = True
                self.tongue_timer = 40

        if self.steal_cooldown > 0:
            return

        available = {k: v for k, v in icons.items() if k not in self.stolen and v[0] < self.sw}
        threshold = {"aggressive": 160, "playful": 220, "sneaky": 300}[self.personality]
        if self.timer > threshold and available:
            # 20% chance di fare un dispetto invece di rubare
            if random.random() < 0.20:
                self._transition(S.PRANK)
                return
            idx = random.choice(list(available.keys()))
            self.target_icon = idx
            self.tx, self.ty = available[idx]
            self._transition(S.APPROACHING)

    def _sleeping(self):
        self.mood = "sleepy"
        # Dondola lentamente avanti e indietro mentre dorme
        cx = self.vx_off + self.sw // 2
        cy = self.vy_off + self.sh - 200
        drift_x = math.sin(self.timer * 0.018) * 28
        drift_y = math.sin(self.timer * 0.011) * 12
        self._move_smooth(cx + drift_x, cy + drift_y, 0.9, 0.03)
        if self.cursor_idle_frames == 0:
            self.mood = "happy"
            self.say("wakeup_yawn")
            self._jump(10)
            self._transition(S.WAVING)

    def _curious(self):
        self.mood = "curious"
        cx, cy = self._cursor()
        dist = self._dist_cursor()
        if dist > 130:
            self._move_smooth(cx, cy, 3.5, 0.18)
        if dist < 60:
            self.mood = "scared"
            self._jump(20)
            self._transition(S.RUNNING)
            return
        if dist > 600 and self.timer > 60:
            self.say("following")
            self._transition(S.FOLLOWING)
            return
        if self.timer > 420:
            self._transition(S.IDLE)

    def _following(self):
        self.mood = "happy"
        cx, cy = self._cursor()
        dist = self._dist_cursor()
        if dist > 120:
            self._move_smooth(cx, cy, 6, 0.25, wrap=False)
        # Saltellare mentre segue
        if not self.is_jumping and self.timer % 100 == 0:
            self._jump(14)
        if dist < 65:
            self.mood = "scared"
            self._transition(S.RUNNING)
            return
        if self.timer > 550:
            self._transition(S.IDLE)

    def _waving(self):
        self.mood = "happy"
        self._move_smooth(self.sw // 2, self.sh // 2, 5, 0.25)
        if self.timer > 160:
            self._transition(S.IDLE)

    def _dancing(self):
        self.mood = "excited"
        if self.timer % 60 == 0:
            spread = 90
            self.tx = max(120, min(self.sw - 120, int(self.x) + random.randint(-spread, spread)))
            self.ty = max(120, min(self.sh - 200, int(self.y) + random.randint(-30, 30)))
        self._move_smooth(self.tx, self.ty, 4, 0.12)
        # Saltelli ritmici durante il ballo
        if not self.is_jumping and self.timer % 50 == 0:
            self._jump(12)
        if self.timer > 480:
            self.mood = "happy"
            self._transition(S.IDLE)

    def _hanging(self, icons):
        """Lupin si avvicina a un'icona e si appende (simula)."""
        self.mood = "happy"
        if self.hang_target is None:
            self._transition(S.IDLE)
            return
        reached = self._move_smooth(self.hang_target[0], self.hang_target[1] - 20, 6, 0.35)
        # Oscilla un po' mentre è "appeso"
        if reached or self.timer > 60:
            # Appeso: oscillazione laterale piccola
            if self.timer > 60:
                osc = math.sin(self.timer * 0.2) * 8
                self.x += osc * 0.15
        if self.timer > 220:
            # Cade/salta via
            self._jump(22)
            self.hang_target = None
            self._transition(S.IDLE)

    def _pushing(self, icons):
        """Spinge fisicamente un'icona attraverso il desktop."""
        self.mood = "happy"
        if self.push_icon_idx is None:
            self._transition(S.IDLE)
            return

        all_pos = self.hooks.get_all_positions()
        if self.push_icon_idx not in all_pos:
            self._transition(S.IDLE)
            return

        ix, iy = all_pos[self.push_icon_idx]

        # Fase 1: avvicinati all'icona
        dist_to_icon = math.hypot(self.x - ix, self.y - iy)
        if dist_to_icon > 50 and self.timer < 80:
            self._move_smooth(ix, iy, 6, 0.3)
            return

        # Fase 2: spinge – icona si muove nella push_dir, Lupin segue da dietro
        dx, dy = self.push_dir
        speed = 2.5
        new_ix = ix + dx * speed
        new_iy = iy + dy * speed

        # Rimbalza sui bordi
        margin = 80
        taskbar = 70
        bounced = False
        if new_ix < margin:
            new_ix = margin;  self.push_dir = (-dx, dy);  bounced = True
        elif new_ix > self.sw - margin:
            new_ix = self.sw - margin;  self.push_dir = (-dx, dy);  bounced = True
        if new_iy < margin:
            new_iy = margin;  self.push_dir = (dx, -dy);  bounced = True
        elif new_iy > self.sh - taskbar:
            new_iy = self.sh - taskbar;  self.push_dir = (dx, -dy);  bounced = True

        if self.timer % 3 == 0:
            self.hooks.set_icon_position(self.push_icon_idx, int(new_ix), int(new_iy))

        # Lupin si posiziona dietro l'icona nella direzione di spinta
        lupin_tx = new_ix - dx * 45
        lupin_ty = new_iy - dy * 45
        self._move_smooth(lupin_tx, lupin_ty, 5, 0.3)
        self.direction = 1 if dx > 0 else -1 if dx < 0 else self.direction

        if self.timer > 400:
            self.push_icon_idx = None
            self._transition(S.IDLE)

    def _carrying(self):
        """Porta un'icona sopra la testa mentre passeggia.
        L'icona reale è nascosta off-screen; solo la replica disegnata è visibile.
        """
        self.mood = "happy"
        if self.carry_icon_idx is None:
            self._transition(S.IDLE)
            return

        # Aggiorna solo la posizione fake per il rendering — l'icona reale è off-screen
        head_x = max(50, min(self.sw - 50, int(self.x)))
        head_y = max(50, min(self.sh - 80, int(self.y) - 85))
        self.carry_icon_pos = (head_x, head_y)

        # Cammina in giro
        if self.timer % 90 == 0:
            self.tx = random.randint(160, self.sw - 160)
            self.ty = random.randint(160, self.sh - 200)
        self._move_smooth(self.tx, self.ty, 4.5, 0.22)

        if not self.is_jumping and self.timer % 110 == 0:
            self._jump(13)

        # Ogni tanto commenta
        if self.timer % 220 == 110:
            self.say("carrying")

        if self.timer > 600:
            # Ripristina l'icona alla posizione originale salvata
            orig = self.hooks._saved_positions.get(self.carry_icon_idx)
            if orig:
                self.hooks.set_icon_position(self.carry_icon_idx, *orig)
            else:
                self.hooks.set_icon_position(self.carry_icon_idx, int(self.x), int(self.y) + 50)
            self.carry_icon_idx = None
            self.carry_icon_name = ""
            self._transition(S.CELEBRATING)

    def _sitting(self):
        """Si siede su un'icona e chiacchiera."""
        self.mood = "happy"
        if self.sit_target is None:
            self._transition(S.IDLE)
            return

        sx, sy = self.sit_target
        # Si avvicina e si siede (si ferma SOPRA l'icona)
        self._move_smooth(sx, sy - 10, 5, 0.28)

        # Battute periodiche mentre è seduto
        if self.timer % 260 == 60:
            self.say("sitting")

        # Piccolo dondolio (aggiornato tramite info)
        if self.timer > self._sit_duration:
            self._sit_duration = 0
            self.sit_target = None
            self._jump(18)
            self._transition(S.IDLE)

    def _find_lean_spot(self):
        """Trova il bordo di una finestra aperta o del bordo schermo.

        lean_side="right" → muro a DESTRA di Lupin, braccio destro teso verso dx.
                             Lupin.x ≈ muro_x - 60 (mano a muro_x - 60 + 45 ≈ muro_x).
        lean_side="left"  → muro a SINISTRA, braccio sinistro teso verso sx.
                             Lupin.x ≈ muro_x + 60.
        """
        wins = self.hooks.get_open_windows()
        taskbar_y = self.sh - 60
        mid_y = random.randint(self.sh // 4, 3 * self.sh // 4)
        ARM_REACH = 58   # pixel dal centro di Lupin alla mano tesa

        candidates = []
        for r in wins:
            x1, y1, x2, y2 = r
            wy = max(self.sh // 4, min(taskbar_y - 80, (y1 + y2) // 2))
            # Bordo SINISTRO finestra: muro a dx di Lupin
            if x1 > ARM_REACH + 10:
                candidates.append((x1 - ARM_REACH, wy, "right"))
            # Bordo DESTRO finestra: muro a sx di Lupin
            if x2 < self.sw - ARM_REACH - 10:
                candidates.append((x2 + ARM_REACH, wy, "left"))

        # Bordi dello schermo (sempre candidati) — LAMPIONE
        screen_candidates = [
            (self.vx_off + ARM_REACH,           mid_y, "left"),
            (self.vx_off + self.sw - ARM_REACH, mid_y, "right"),
        ]
        candidates += screen_candidates

        wx, wy, side = random.choice(candidates)
        is_screen = (wx, wy, side) in screen_candidates
        wx = max(self.vx_off + ARM_REACH, min(self.vx_off + self.sw - ARM_REACH, wx))
        wy = max(self.vy_off + 60, min(self.vy_off + taskbar_y - 60, wy))
        return wx, wy, side, is_screen

    def _leaning(self):
        """Cammina fino al bordo e si appoggia con un braccio."""
        self.mood = "happy"
        self._move_smooth(self.lean_wall_x, self.lean_wall_y, 6, 0.3, margin=15)
        dist = math.hypot(self.x - self.lean_wall_x, self.y - self.lean_wall_y)

        # Direzione verso il muro (lean_side = lato dove c'è il muro)
        self.direction = 1 if self.lean_side == "right" else -1

        # Battute periodiche mentre è appoggiato
        if dist < 40 and self.timer % 280 == 60:
            self.say("leaning_lamp" if self.lean_is_screen else "leaning")

        # Piccolo dondolio alla parete
        if dist < 40 and not self.is_jumping and self.timer % 200 == 0:
            self._jump(8)

        # Se cursore troppo vicino → se ne va
        if self._dist_cursor() < 100 and self.timer > 60:
            self._transition(S.RUNNING)
            return

        if self.timer > random.randint(700, 1800):
            self._transition(S.IDLE)

    def _corner(self):
        """Staziona in un angolo, chiacchiera, guarda in giro."""
        self.mood = "happy"
        self._move_smooth(self.corner_x, self.corner_y, 6, 0.3, margin=10)

        # Direzione verso il centro (guarda verso lo schermo)
        self.direction = 1 if self.corner_x < self.sw // 2 else -1

        if self.timer % 300 == 80:
            self.say("corner")

        if self._dist_cursor() < 80 and self.timer > 60:
            self._jump(20)
            self._transition(S.RUNNING)
            return

        if self.timer > random.randint(600, 1400):
            self._transition(S.IDLE)

    def _approaching(self):
        self.mood = "excited"
        # Piccolo salto prima di rubare
        if self.timer == 10:
            self._jump(10)
        if self._move_smooth(self.tx, self.ty, 9, 0.42):
            self._transition(S.STEALING)

    def _stealing(self, icons=None):
        self.mood = "excited"
        if self.timer == 25:
            self.hooks.steal_icon(self.target_icon)
            self.stolen.append(self.target_icon)
            self.total_steals += 1
            self._last_steal_global = self.global_timer
            self._auto_restore_said = False
            self._jump(14)
        if self.timer > 50:
            if len(self.stolen) < self.MAX_STEAL:
                all_pos = self.hooks.get_all_positions()
                remaining = {k: v for k, v in all_pos.items()
                             if k not in self.stolen and v[0] < self.sw}
                greed = {"aggressive": 0.85, "playful": 0.65, "sneaky": 0.45}[self.personality]
                if remaining and random.random() < greed:
                    idx = random.choice(list(remaining.keys()))
                    self.target_icon = idx
                    self.tx, self.ty = remaining[idx]
                    self._transition(S.APPROACHING)
                    return
            self.tx, self.ty = self.sw // 2, self.sh // 2
            self.say("taunt")
            self._transition(S.TAUNTING)

    def _taunting(self):
        self.mood = "smug"
        self._move_smooth(self.tx, self.ty, 6, 0.3)
        # Saltello di scherno
        if self.timer == 30:
            self._jump(18)
        if self.timer > 240:
            self._transition(S.RUNNING)

    def _running(self):
        self.mood = "scared"
        dist = self._dist_cursor()
        flee_dist = {"aggressive": 280, "playful": 380, "sneaky": 480}[self.personality]
        if dist < flee_dist:
            self._flee_smart(13 if self.personality == "aggressive" else 11)
        else:
            if self.timer % 70 == 0:
                self.tx = random.randint(80, self.sw - 80)
                self.ty = random.randint(80, self.sh - 120)
            self._move_smooth(self.tx, self.ty, 6, 0.28, wrap=True)

        # Saltello di paura ogni tanto
        if not self.is_jumping and self.timer % 80 == 0 and random.random() < 0.5:
            self._jump(16)

        # Dopo ~500 frame si stanca e si accascia
        if self.timer > 500 and random.random() < 0.005:
            # Scegli posizione di riposo: icona desktop o centro-basso schermo
            visible_icons = {k: v for k, v in self._icons.items()
                             if v[0] < self.sw - 60 and v[1] < self.sh - 60}
            if visible_icons:
                self._exhausted_rest_pos = random.choice(list(visible_icons.values()))
            else:
                self._exhausted_rest_pos = (self.sw // 2, self.sh - 90)
            self.say("exhausted")
            self._transition(S.EXHAUSTED)
            return

        if self.timer > 300 and random.random() < 0.004:
            wins = self.hooks.get_open_windows()
            if wins:
                r = random.choice(wins)
                self.hide_rect = r
                self.peek_side = "right" if self.x < (r[0] + r[2]) // 2 else "left"
                self.tx = r[2] - 15 if self.peek_side == "right" else r[0] + 15
                self.ty = max(30, min(self.sh - 80, r[1] + 50))
                self._transition(S.HIDING)

    def _hiding(self):
        self.mood = "scared"
        self._move_smooth(self.tx, self.ty, 9, 0.5)
        if self._dist_cursor() < 150:
            self._transition(S.RUNNING)
        elif self.timer > 500:
            self._transition(S.RUNNING)

    def _exhausted(self):
        """Lupin si accascia, respira a fatica, poi si riprende."""
        self.mood = "sad"
        if self._exhausted_rest_pos:
            ex, ey = self._exhausted_rest_pos
            # Movimento molto lento verso la posizione di riposo
            self._move_smooth(ex, ey, 1.8, 0.09)

        # Piccolo oscillio laterale da stanchezza
        if self.timer % 180 == 90 and not self.is_jumping:
            self._jump(5)   # saltellino stanco

        # Battute occasionali
        if self.timer % 300 == 120:
            self.say("exhausted")

        # Se il cursore si avvicina troppo, scappa un po' (ma lentamente)
        if self._dist_cursor() < 80 and self.timer > 120:
            self.vx += random.uniform(-2, 2)
            self.vy += random.uniform(-1, 1)

        # Dopo ~400 frame si riprende
        if self.timer > random.randint(300, 500):
            self._exhausted_rest_pos = None
            self._jump(12)
            self._transition(S.IDLE)

    def _volume_trick(self):
        """Lupin alza il volume premendo tasti virtuali."""
        import win32api, win32con
        self.mood = "smug"
        # Cammina verso centro-alto schermo
        self._move_smooth(self.sw // 2, self.sh // 4, 6, 0.28)

        # Preme VK_VOLUME_UP (0xAF) ripetutamente nel tempo
        if 40 < self.timer < 200 and self.timer % 12 == 0 and self._volume_presses < 15:
            try:
                win32api.keybd_event(0xAF, 0, 0, 0)        # VK_VOLUME_UP down
                win32api.keybd_event(0xAF, 0, win32con.KEYEVENTF_KEYUP, 0)  # up
                self._volume_presses += 1
            except Exception:
                pass

        if not self.is_jumping and self.timer % 55 == 0:
            self._jump(14)

        if self.timer == 80:
            self.say("volume_trick")

        if self.timer > 280:
            self.say("taunt")
            self._transition(S.TAUNTING)

    def _drinking(self):
        """Lupin si ferma e beve una birra."""
        self.mood = "happy"
        # Rimane fermo (non chiama _move_smooth)
        self.vx *= 0.6;  self.vy *= 0.6

        if self.timer == 100:
            # Finita la birra: rutto!
            self.say("burp")
            self.burp_pending = True
            self.tongue_timer = 50

        if self.timer > 120:
            self._jump(12)
            self._transition(S.IDLE)

    def _surrender(self):
        self.mood = "sad"
        if self.timer > 80:
            self.hooks.restore_icons()
            self.stolen.clear()
            self.times_caught += 1
            self.steal_cooldown = 400
            self.say("celebrating")
            self._transition(S.CELEBRATING)

    def _celebrating(self):
        self.mood = "happy"
        self._move_smooth(self.sw // 2, self.sh // 2, 5, 0.25)
        if self.timer == 20:
            self._jump(24)
        if self.timer > 300:
            self._transition(S.IDLE)

    def _prank(self, icons):
        """Dispetto: 50/50 cerchio o caos totale."""
        self.mood = "smug"
        # Avvicinati al centro
        if self.timer < 35:
            self._move_smooth(self.sw // 2, self.sh // 2, 7, 0.3)
        elif self.timer == 35:
            self._jump(20)
            if random.random() < 0.5:
                self.hooks.scatter_circle()
                self.say("prank_circle")
                self._prank_type = "circle"
            else:
                self.hooks.scatter_chaos()
                self.say("prank_chaos")
                self._prank_type = "chaos"
            self.prank_count += 1
        elif self.timer < 260:
            # Schernisce in giro
            if self.timer % 100 == 0:
                self.tx = random.randint(200, self.sw - 200)
                self.ty = random.randint(200, self.sh - 200)
            self._move_smooth(self.tx, self.ty, 5, 0.22)
            if not self.is_jumping and self.timer % 70 == 0:
                self._jump(14)
        else:
            # Ripristina (il "perdono")
            self.hooks.restore_icons()
            self._transition(S.TAUNTING)

    # ── input ────────────────────────────────────────────────

    def on_click(self):
        # ── Click durante PUSHING o CARRYING → restituisce l'icona ──
        if self.state == S.PUSHING and self.push_icon_idx is not None:
            orig = self.hooks._saved_positions.get(self.push_icon_idx)
            if orig:
                self.hooks.set_icon_position(self.push_icon_idx, *orig)
            self.push_icon_idx = None
            self.hit_reaction = self.say("click_restore")
            self._jump(14)
            self._transition(S.IDLE)
            self.hit_combo = 0
            return

        if self.state == S.CARRYING and self.carry_icon_idx is not None:
            orig = self.hooks._saved_positions.get(self.carry_icon_idx)
            if orig:
                self.hooks.set_icon_position(self.carry_icon_idx, *orig)
            else:
                self.hooks.set_icon_position(self.carry_icon_idx, int(self.x), int(self.y) + 60)
            self.carry_icon_idx = None
            self.carry_icon_name = ""
            self.hit_reaction = self.say("scusa_carrying")
            self._jump(14)
            self._transition(S.IDLE)
            self.hit_combo = 0
            return

        # ── Resa se catturato mentre scappa ──────────────────
        if self.state in (S.RUNNING, S.HIDING, S.TAUNTING, S.PRANK):
            self.say("caught")
            self._transition(S.SURRENDER)
            self.hit_combo = 0
            return

        # ── Click mentre esausto: insulti speciali, non riesce a scappare ──
        if self.state == S.EXHAUSTED:
            gap = self.global_timer - self.last_hit_timer
            self.last_hit_timer = self.global_timer
            if gap < 90:
                self.hit_combo += 1
            else:
                self.hit_combo = 1
            self.hit_reaction = self.say("hit_exhausted")
            self._jump(max(4, 18 - self.timer // 60))  # salto debolissimo
            # Dopo abbastanza colpi scappa comunque (con quel poco di energia rimasta)
            if self.hit_combo >= 4:
                self._exhausted_rest_pos = None
                self._transition(S.RUNNING)
            return

        # ── Sistema colpi: click ravvicinati = combo ──────────
        gap = self.global_timer - self.last_hit_timer
        self.last_hit_timer = self.global_timer

        if gap < 90:
            self.hit_combo += 1
        else:
            self.hit_combo = 1

        # Scala le reazioni in base al combo
        if self.hit_combo >= 5:
            self.hit_reaction = self.say("hit_escape")
            self._jump(26)
            self._transition(S.RUNNING)
        elif self.hit_combo >= 3:
            self.hit_reaction = self.say("hit_3")
            self._jump(22)
            if self.state not in (S.RUNNING, S.HIDING):
                self._transition(S.RUNNING)
        elif self.hit_combo == 2:
            self.hit_reaction = self.say("hit_2")
            self._jump(18)
        else:
            if self.state in FRIENDLY_STATES:
                self.hit_reaction = self.say("hit_1")
                self._jump(14)
            elif self.state == S.TAUNTING:
                self.hit_reaction = self.say("hit_taunt")

    # ── info ─────────────────────────────────────────────────

    @property
    def info(self):
        h = datetime.now().hour
        return dict(
            state=self.state,
            x=int(self.x), y=int(self.y),
            direction=self.direction,
            anim_frame=self.anim_frame,
            sack_count=len(self.stolen),
            mood=self.mood,
            jump_z=int(self.jump_z),
            is_jumping=self.is_jumping,
            just_wrapped=self.just_wrapped,
            is_taunting=(self.state == S.TAUNTING and self.timer < 220) or
                        (self.state == S.PRANK and 35 < self.timer < 260),
            is_hiding=self.state == S.HIDING,
            is_surrender=self.state == S.SURRENDER and self.timer < 60,
            is_waving=self.state == S.WAVING,
            is_dancing=self.state == S.DANCING,
            is_sleeping=self.state == S.SLEEPING,
            is_celebrating=self.state == S.CELEBRATING,
            is_curious=self.state == S.CURIOUS,
            is_following=self.state == S.FOLLOWING,
            is_hanging=self.state == S.HANGING,
            is_pushing=self.state == S.PUSHING,
            is_carrying=self.state == S.CARRYING,
            is_sitting=self.state == S.SITTING,
            carry_icon_pos=self.carry_icon_pos,
            carry_icon_name=self.carry_icon_name,
            push_dir=self.push_dir,
            sit_target=self.sit_target,
            is_prank=self.state == S.PRANK,
            is_leaning=self.state == S.LEANING,
            is_corner=self.state == S.CORNER,
            is_exhausted=self.state == S.EXHAUSTED,
            is_volume_trick=self.state == S.VOLUME_TRICK,
            is_drinking=self.state == S.DRINKING,
            volume_presses=self._volume_presses,
            tongue_timer=self.tongue_timer,
            burp_pending=self.burp_pending,
            lean_side=self.lean_side,
            lean_wall_x=self.lean_wall_x,
            lean_wall_y=self.lean_wall_y,
            lean_is_screen=self.lean_is_screen,
            idle_look_dir=self.idle_look_dir,
            idle_micro=self.idle_micro,
            hit_combo=self.hit_combo,
            hit_reaction=self.hit_reaction,
            peek_side=self.peek_side,
            dance_phase=self.dance_phase,
            timer=self.timer,
            global_timer=self.global_timer,
            personality=self.personality,
            total_steals=self.total_steals,
            times_caught=self.times_caught,
            prank_count=self.prank_count,
            hour=h,
            current_joke=self.current_joke,
            hang_target=self.hang_target,
        )

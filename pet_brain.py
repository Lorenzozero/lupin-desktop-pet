import math, random, win32api
from enum import Enum, auto

class S(Enum):
    IDLE       = auto()
    APPROACHING = auto()
    STEALING   = auto()
    TAUNTING   = auto()
    RUNNING    = auto()
    HIDING     = auto()
    SURRENDER  = auto()

class LupinBrain:
    MAX_STEAL = 6  # Quante icone vuole rubare

    def __init__(self, sw, sh, hooks):
        self.sw, self.sh = sw, sh
        self.hooks = hooks
        self.x, self.y = sw // 2, sh // 2
        self.tx, self.ty = self.x, self.y
        self.state = S.IDLE
        self.timer = 0
        self.direction = 1     # 1=destra, -1=sinistra
        self.stolen = []       # Lista indici icone rubate
        self.target_icon = None
        self.hide_rect = None
        self.peek_side = "right"
        self.anim_frame = 0
        self.anim_tick = 0

    # ── Helpers ──────────────────────────────────────────

    def _cursor(self):
        p = win32api.GetCursorPos()
        return p[0], p[1]

    def _dist_cursor(self):
        cx, cy = self._cursor()
        return math.hypot(self.x - cx, self.y - cy)

    def _move_to(self, tx, ty, spd):
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        if d < spd:
            self.x, self.y = tx, ty
            return True
        self.x += dx / d * spd
        self.y += dy / d * spd
        self.direction = 1 if dx > 0 else -1
        return False

    def _flee_cursor(self, spd=9):
        cx, cy = self._cursor()
        dx, dy = self.x - cx, self.y - cy
        d = math.hypot(dx, dy) or 1
        self.x = max(60, min(self.sw - 60, self.x + dx / d * spd))
        self.y = max(60, min(self.sh - 60, self.y + dy / d * spd))
        self.direction = 1 if dx > 0 else -1

    def _transition(self, state):
        self.state = state
        self.timer = 0

    # ── Tick principale ───────────────────────────────────

    def update(self, icons):
        self.anim_tick += 1
        if self.anim_tick >= 8:
            self.anim_frame = (self.anim_frame + 1) % 4
            self.anim_tick = 0
        self.timer += 1
        {
            S.IDLE:        lambda: self._idle(icons),
            S.APPROACHING: lambda: self._approaching(icons),
            S.STEALING:    lambda: self._stealing(icons),
            S.TAUNTING:    lambda: self._taunting(),
            S.RUNNING:     lambda: self._running(),
            S.HIDING:      lambda: self._hiding(),
            S.SURRENDER:   lambda: self._surrender(),
        }[self.state]()

    def _idle(self, icons):
        # Passeggia lentamente
        if self.timer % 90 == 0:
            self.tx = random.randint(100, self.sw - 100)
            self.ty = random.randint(100, self.sh - 100)
        self._move_to(self.tx, self.ty, 2)

        # Dopo 4s inizia il furto
        available = {k: v for k, v in icons.items()
                     if k not in self.stolen and v[0] < self.sw}
        if self.timer > 240 and available:
            idx = random.choice(list(available.keys()))
            self.target_icon = idx
            self.tx, self.ty = available[idx]
            self._transition(S.APPROACHING)

    def _approaching(self, icons=None):
        reached = self._move_to(self.tx, self.ty, 6)
        if reached:
            self._transition(S.STEALING)

    def _stealing(self, icons=None):
        if self.timer == 25:  # A metà animazione, l'icona sparisce nel sacco
            self.hooks.steal_icon(self.target_icon)
            self.stolen.append(self.target_icon)

        if self.timer > 50:
            # Vuole altre icone?
            if len(self.stolen) < self.MAX_STEAL:
                all_pos = self.hooks.get_all_positions()
                remaining = {k: v for k, v in all_pos.items()
                             if k not in self.stolen and v[0] < self.sw}
                if remaining and random.random() < 0.7:
                    idx = random.choice(list(remaining.keys()))
                    self.target_icon = idx
                    self.tx, self.ty = remaining[idx]
                    self._transition(S.APPROACHING)
                    return
            # Vai al centro a canzonare
            self.tx, self.ty = self.sw // 2, self.sh // 2
            self._transition(S.TAUNTING)

    def _taunting(self):
        self._move_to(self.tx, self.ty, 4)
        if self.timer > 220:
            self._transition(S.RUNNING)

    def _running(self):
        if self._dist_cursor() < 350:
            self._flee_cursor()
        else:
            self._move_to(self.tx, self.ty, 5)
            if self.timer % 60 == 0:
                self.tx = random.randint(100, self.sw - 100)
                self.ty = random.randint(100, self.sh - 100)

        # Dopo 6s tenta di nascondersi dietro una finestra
        if self.timer > 360:
            wins = self.hooks.get_open_windows()
            if wins:
                r = random.choice(wins)
                self.hide_rect = r
                self.peek_side = "right" if self.x < (r[0] + r[2]) // 2 else "left"
                if self.peek_side == "right":
                    self.tx = r[2] - 15   # Sporge solo l'angolino dal bordo destro
                    self.ty = r[1] + 50
                else:
                    self.tx = r[0] + 15
                    self.ty = r[1] + 50
                self._transition(S.HIDING)

    def _hiding(self):
        self._move_to(self.tx, self.ty, 7)
        # Scappa se il cursore si avvicina troppo
        if self._dist_cursor() < 180:
            self._transition(S.RUNNING)
        # Riposiziona in un'altra finestra ogni tanto
        elif self.timer > 400:
            self._transition(S.RUNNING)

    def _surrender(self):
        if self.timer > 80:
            self.hooks.restore_icons()
            self.stolen.clear()
            self._transition(S.IDLE)

    # ── Evento click ─────────────────────────────────────

    def on_click(self):
        if self.state in (S.RUNNING, S.HIDING, S.TAUNTING) and self.stolen:
            self._transition(S.SURRENDER)

    @property
    def info(self):
        return dict(
            state=self.state, x=int(self.x), y=int(self.y),
            direction=self.direction, anim_frame=self.anim_frame,
            sack_count=len(self.stolen),
            is_taunting=self.state == S.TAUNTING and self.timer < 200,
            is_hiding=self.state == S.HIDING,
            is_surrender=self.state == S.SURRENDER and self.timer < 60,
            peek_side=self.peek_side,
        )

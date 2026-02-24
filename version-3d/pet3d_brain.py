import math
import random
import win32api
from enum import Enum, auto

class S(Enum):
    IDLE        = auto()
    APPROACHING = auto()
    STEALING    = auto()
    TAUNTING    = auto()
    RUNNING     = auto()
    HIDING      = auto()
    SURRENDER   = auto()

class LupinBrain3D:
    MAX_STEAL = 8

    def __init__(self, sw, sh, hooks):
        self.sw, self.sh = sw, sh
        self.hooks = hooks
        self.x, self.y = sw // 2, sh // 2
        self.tx, self.ty = self.x, self.y
        self.vx, self.vy = 0.0, 0.0
        self.state = S.IDLE
        self.timer = 0
        self.direction = 1
        self.stolen = []
        self.target_icon = None
        self.hide_rect = None
        self.peek_side = "right"
        self.speed = 0.0
        self.personality = random.choice(["aggressive", "playful", "sneaky"])
        print(f"[Brain3D] Personalit\u00e0: {self.personality}")

    def _cursor(self):
        p = win32api.GetCursorPos()
        return float(p[0]), float(p[1])

    def _dist_cursor(self):
        cx, cy = self._cursor()
        return math.hypot(self.x - cx, self.y - cy)

    def _move_smooth(self, tx, ty, spd, accel=0.35):
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        if d < 4:
            self.x, self.y = tx, ty
            self.vx *= 0.6
            self.vy *= 0.6
            self.speed = math.hypot(self.vx, self.vy)
            return True

        target_vx = (dx / d) * spd
        target_vy = (dy / d) * spd
        self.vx += (target_vx - self.vx) * accel
        self.vy += (target_vy - self.vy) * accel
        self.x += self.vx
        self.y += self.vy
        self.x = max(60, min(self.sw - 60, self.x))
        self.y = max(60, min(self.sh - 60, self.y))
        self.direction = 1 if self.vx > 0.1 else (-1 if self.vx < -0.1 else self.direction)
        self.speed = math.hypot(self.vx, self.vy)
        return False

    def _flee_smart(self, spd=12):
        cx, cy = self._cursor()
        dx, dy = self.x - cx, self.y - cy
        d = math.hypot(dx, dy) or 1
        perp = math.sin(self.timer * 0.18) * 4
        self.vx += (dx / d * spd - dy / d * perp - self.vx) * 0.35
        self.vy += (dy / d * spd + dx / d * perp - self.vy) * 0.35
        max_spd = spd
        curr = math.hypot(self.vx, self.vy)
        if curr > max_spd:
            self.vx = (self.vx / curr) * max_spd
            self.vy = (self.vy / curr) * max_spd
        self.x = max(60, min(self.sw - 60, self.x + self.vx))
        self.y = max(60, min(self.sh - 60, self.y + self.vy))
        self.direction = 1 if self.vx > 0 else -1
        self.speed = math.hypot(self.vx, self.vy)

    def _transition(self, state):
        self.state = state
        self.timer = 0

    def update(self, icons, dt=0.016):
        self.timer += 1
        {
            S.IDLE:        lambda: self._idle(icons),
            S.APPROACHING: lambda: self._approaching(),
            S.STEALING:    lambda: self._stealing(icons),
            S.TAUNTING:    lambda: self._taunting(),
            S.RUNNING:     lambda: self._running(),
            S.HIDING:      lambda: self._hiding(),
            S.SURRENDER:   lambda: self._surrender(),
        }[self.state]()

    def _idle(self, icons):
        if self.timer % 100 == 0:
            self.tx = random.randint(100, self.sw - 100)
            self.ty = random.randint(100, self.sh - 100)
        self._move_smooth(self.tx, self.ty, 2.5, 0.15)
        threshold = {"aggressive": 150, "playful": 200, "sneaky": 280}[self.personality]
        available = {k: v for k, v in icons.items() if k not in self.stolen and v[0] < self.sw}
        if self.timer > threshold and available:
            idx = random.choice(list(available.keys()))
            self.target_icon = idx
            self.tx, self.ty = available[idx]
            self._transition(S.APPROACHING)

    def _approaching(self):
        if self._move_smooth(self.tx, self.ty, 9, 0.4):
            self._transition(S.STEALING)

    def _stealing(self, icons):
        if self.timer == 25:
            self.hooks.steal_icon(self.target_icon)
            self.stolen.append(self.target_icon)
        if self.timer > 55:
            greed = {"aggressive": 0.92, "playful": 0.65, "sneaky": 0.45}[self.personality]
            if len(self.stolen) < self.MAX_STEAL:
                all_pos = self.hooks.get_all_positions()
                remaining = {k: v for k, v in all_pos.items() if k not in self.stolen and v[0] < self.sw}
                if remaining and random.random() < greed:
                    idx = random.choice(list(remaining.keys()))
                    self.target_icon = idx
                    self.tx, self.ty = remaining[idx]
                    self._transition(S.APPROACHING)
                    return
            self.tx, self.ty = self.sw // 2, self.sh // 2
            self._transition(S.TAUNTING)

    def _taunting(self):
        self._move_smooth(self.tx, self.ty, 5, 0.25)
        if self.timer > 220:
            self._transition(S.RUNNING)

    def _running(self):
        flee_dist = {"aggressive": 260, "playful": 360, "sneaky": 480}[self.personality]
        if self._dist_cursor() < flee_dist:
            self._flee_smart(13)
        else:
            if self.timer % 70 == 0:
                self.tx = random.randint(80, self.sw - 80)
                self.ty = random.randint(80, self.sh - 80)
            self._move_smooth(self.tx, self.ty, 5, 0.2)
        if self.timer > 360 and random.random() < 0.003:
            wins = self.hooks.get_open_windows()
            if wins:
                r = random.choice(wins)
                self.hide_rect = r
                self.peek_side = "right" if self.x < (r[0] + r[2]) // 2 else "left"
                self.tx = r[2] - 15 if self.peek_side == "right" else r[0] + 15
                self.ty = r[1] + 50
                self._transition(S.HIDING)

    def _hiding(self):
        self._move_smooth(self.tx, self.ty, 8, 0.5)
        if self._dist_cursor() < 160:
            self._transition(S.RUNNING)
        elif self.timer > 450:
            self._transition(S.RUNNING)

    def _surrender(self):
        if self.timer > 90:
            self.hooks.restore_icons()
            self.stolen.clear()
            self._transition(S.IDLE)

    def on_click(self):
        if self.state in (S.RUNNING, S.HIDING, S.TAUNTING) and self.stolen:
            self._transition(S.SURRENDER)

    @property
    def info(self):
        return dict(
            state=self.state,
            x=int(self.x), y=int(self.y),
            direction=self.direction,
            speed=self.speed,
            sack_count=len(self.stolen),
            is_taunting=self.state == S.TAUNTING and self.timer < 200,
            is_hiding=self.state == S.HIDING,
            is_surrender=self.state == S.SURRENDER and self.timer < 60,
            peek_side=self.peek_side,
        )

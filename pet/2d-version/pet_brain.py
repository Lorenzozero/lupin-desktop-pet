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
    MAX_STEAL = 8  # Più icone per più sfida

    def __init__(self, sw, sh, hooks):
        self.sw, self.sh = sw, sh
        self.hooks = hooks
        self.x, self.y = sw // 2, sh // 2
        self.tx, self.ty = self.x, self.y
        self.vx, self.vy = 0.0, 0.0  # velocity per smooth movement
        self.state = S.IDLE
        self.timer = 0
        self.direction = 1
        self.stolen = []
        self.target_icon = None
        self.hide_rect = None
        self.peek_side = "right"
        self.anim_frame = 0
        self.anim_tick = 0
        self.personality = random.choice(["aggressive", "playful", "sneaky"])  # varia comportamento

    def _cursor(self):
        p = win32api.GetCursorPos()
        return p[0], p[1]

    def _dist_cursor(self):
        cx, cy = self._cursor()
        return math.hypot(self.x - cx, self.y - cy)

    def _move_to_smooth(self, tx, ty, spd, accel=0.3):
        """Movimento con accelerazione e decelerazione"""
        dx, dy = tx - self.x, ty - self.y
        d = math.hypot(dx, dy)
        
        if d < 5:
            self.x, self.y = tx, ty
            self.vx *= 0.7
            self.vy *= 0.7
            return True
            
        # Accelerazione verso target
        target_vx = (dx / d) * spd if d > 0 else 0
        target_vy = (dy / d) * spd if d > 0 else 0
        
        self.vx += (target_vx - self.vx) * accel
        self.vy += (target_vy - self.vy) * accel
        
        self.x += self.vx
        self.y += self.vy
        
        self.x = max(50, min(self.sw - 50, self.x))
        self.y = max(50, min(self.sh - 50, self.y))
        
        self.direction = 1 if self.vx > 0 else -1 if self.vx < 0 else self.direction
        return False

    def _flee_cursor_smart(self, spd=10):
        """Fuga intelligente con evasive maneuvers"""
        cx, cy = self._cursor()
        dx, dy = self.x - cx, self.y - cy
        d = math.hypot(dx, dy) or 1
        
        # Aggiungi movimento laterale per essere imprevedibile
        perpendicular = math.sin(self.timer * 0.2) * 3
        
        flee_x = dx / d * spd - dy / d * perpendicular
        flee_y = dy / d * spd + dx / d * perpendicular
        
        self.vx += flee_x * 0.4
        self.vy += flee_y * 0.4
        
        # Limita velocità massima
        speed = math.hypot(self.vx, self.vy)
        if speed > spd:
            self.vx = (self.vx / speed) * spd
            self.vy = (self.vy / speed) * spd
        
        self.x += self.vx
        self.y += self.vy
        
        self.x = max(60, min(self.sw - 60, self.x))
        self.y = max(60, min(self.sh - 60, self.y))
        
        self.direction = 1 if self.vx > 0 else -1

    def _transition(self, state):
        self.state = state
        self.timer = 0

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
        if self.timer % 120 == 0:
            self.tx = random.randint(100, self.sw - 100)
            self.ty = random.randint(100, self.sh - 100)
        self._move_to_smooth(self.tx, self.ty, 3, 0.2)

        available = {k: v for k, v in icons.items() if k not in self.stolen and v[0] < self.sw}
        
        # Personalità influenza timing
        threshold = {"aggressive": 180, "playful": 240, "sneaky": 300}[self.personality]
        
        if self.timer > threshold and available:
            idx = random.choice(list(available.keys()))
            self.target_icon = idx
            self.tx, self.ty = available[idx]
            self._transition(S.APPROACHING)

    def _approaching(self, icons=None):
        reached = self._move_to_smooth(self.tx, self.ty, 8, 0.4)
        if reached:
            self._transition(S.STEALING)

    def _stealing(self, icons=None):
        if self.timer == 25:
            self.hooks.steal_icon(self.target_icon)
            self.stolen.append(self.target_icon)

        if self.timer > 50:
            if len(self.stolen) < self.MAX_STEAL:
                all_pos = self.hooks.get_all_positions()
                remaining = {k: v for k, v in all_pos.items() if k not in self.stolen and v[0] < self.sw}
                
                # Personalità influenza avidità
                greed = {"aggressive": 0.9, "playful": 0.7, "sneaky": 0.5}[self.personality]
                
                if remaining and random.random() < greed:
                    idx = random.choice(list(remaining.keys()))
                    self.target_icon = idx
                    self.tx, self.ty = remaining[idx]
                    self._transition(S.APPROACHING)
                    return
                    
            self.tx, self.ty = self.sw // 2, self.sh // 2
            self._transition(S.TAUNTING)

    def _taunting(self):
        self._move_to_smooth(self.tx, self.ty, 6, 0.3)
        if self.timer > 200:
            self._transition(S.RUNNING)

    def _running(self):
        dist = self._dist_cursor()
        
        # Distanza di fuga varia per personalità
        flee_dist = {"aggressive": 250, "playful": 350, "sneaky": 450}[self.personality]
        
        if dist < flee_dist:
            self._flee_cursor_smart(12 if self.personality == "aggressive" else 10)
        else:
            if self.timer % 80 == 0:
                self.tx = random.randint(100, self.sw - 100)
                self.ty = random.randint(100, self.sh - 100)
            self._move_to_smooth(self.tx, self.ty, 5, 0.25)

        if self.timer > 400 and random.random() < 0.3:
            wins = self.hooks.get_open_windows()
            if wins:
                r = random.choice(wins)
                self.hide_rect = r
                self.peek_side = "right" if self.x < (r[0] + r[2]) // 2 else "left"
                if self.peek_side == "right":
                    self.tx, self.ty = r[2] - 15, r[1] + 50
                else:
                    self.tx, self.ty = r[0] + 15, r[1] + 50
                self._transition(S.HIDING)

    def _hiding(self):
        self._move_to_smooth(self.tx, self.ty, 8, 0.5)
        if self._dist_cursor() < 150:
            self._transition(S.RUNNING)
        elif self.timer > 500:
            self._transition(S.RUNNING)

    def _surrender(self):
        if self.timer > 80:
            self.hooks.restore_icons()
            self.stolen.clear()
            self._transition(S.IDLE)

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

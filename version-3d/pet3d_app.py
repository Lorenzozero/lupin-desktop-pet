"""
Lupin Desktop Pet — Versione 3D (PyQt5 pseudo-3D renderer)
Rendering volumetrico procedurale: depth extrusion, ombre prospettiche,
specular highlights, 3D particle system, achievements HUD.
"""
import sys, os, math, random, time

from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QTimer, QPointF, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QPen, QBrush,
    QRadialGradient, QLinearGradient,
    QTransform, QPainterPath, QFont, QFontMetrics
)

import win32api, win32gui, win32con

sys.path.insert(0, os.path.dirname(__file__))
from desktop_hooks import DesktopHooks
from pet3d_brain import LupinBrain3D, S
from achievements import AchievementSystem
from stats_tracker import StatsTracker
from particle_system3d import ParticleSystem3D

# ── Palette 3D ────────────────────────────────────────────────────
SKIN        = QColor(255, 218, 168)
SKIN_LIT    = QColor(255, 235, 200)
SKIN_DARK   = QColor(195, 145, 105)
SKIN_SHD    = QColor(150, 100, 75)
SUIT_F      = QColor(58, 115, 205)
SUIT_L      = QColor(90, 150, 245)
SUIT_D      = QColor(28, 65, 140)
SUIT_SHD    = QColor(20, 45, 100)
HAT_F       = QColor(22, 22, 22)
HAT_D       = QColor(8, 8, 8)
HAT_RIM     = QColor(185, 20, 30)
HAIR_F      = QColor(28, 18, 12)
HAIR_D      = QColor(15, 8, 5)
EYE_W       = QColor(245, 245, 250)
EYE_P       = QColor(22, 18, 80)
SHOE_F      = QColor(28, 18, 10)
SHOE_D      = QColor(12, 8, 4)
SACK_F      = QColor(180, 130, 60)
SACK_D      = QColor(120, 85, 35)

# ── Scale factor (3D version = 40% bigger) ───────────────────────
SC = 1.4

def _e(x): return int(x * SC)

# ── Achievement toast ─────────────────────────────────────────────
class AchToast:
    def __init__(self, text, icon, sw):
        self.text = text
        self.icon = icon
        self.sw = sw
        self.life = 220
        self.max_life = 220

    def draw(self, p):
        alpha_f = min(1.0, self.life / 40, (self.max_life - self.life) / 40 * 4)
        alpha = int(255 * alpha_f)
        if alpha <= 0:
            return
        w, h = 280, 54
        x = self.sw - w - 16
        y = 60
        # bg
        bg = QColor(20, 20, 30, int(200 * alpha_f))
        border = QColor(255, 200, 50, alpha)
        p.save()
        p.setPen(QPen(border, 2))
        p.setBrush(QBrush(bg))
        p.drawRoundedRect(x, y, w, h, 10, 10)
        # icon
        p.setFont(QFont("Segoe UI Emoji", 18))
        p.setPen(QPen(QColor(255, 255, 255, alpha)))
        p.drawText(x + 10, y + 36, self.icon)
        # text
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.setPen(QPen(QColor(255, 215, 0, alpha)))
        p.drawText(x + 46, y + 18, "Achievement!")
        p.setFont(QFont("Segoe UI", 9))
        p.setPen(QPen(QColor(220, 220, 220, alpha)))
        p.drawText(x + 46, y + 36, self.text)
        p.restore()


class LupinPet3D(QWidget):
    def __init__(self):
        super().__init__()
        self.sw = win32api.GetSystemMetrics(78)   # virtual width
        self.sh = win32api.GetSystemMetrics(79)   # virtual height
        self.vx = win32api.GetSystemMetrics(76)   # virtual origin x
        self.vy = win32api.GetSystemMetrics(77)   # virtual origin y

        self._setup_window()

        self.hooks = DesktopHooks()
        self.hooks.save_positions()
        self.icons = self.hooks.get_all_positions()

        self.brain = LupinBrain3D(self.sw, self.sh, self.hooks)
        self.particles = ParticleSystem3D()
        self.achievements = AchievementSystem()
        self.stats = StatsTracker()

        self.stats.record_personality(self.brain.personality)

        self._timer_tick = 0
        self._icon_tick = 0
        self._last_state = self.brain.state
        self._ach_toasts = []
        self._show_stats = False
        self._prev_steal_count = 0
        self._hide_timer = 0
        self._evade_timer = 0
        self._session_start = time.time()
        self._last_state_time = time.time()

        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(16)

    def _setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnBottomHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setGeometry(self.vx, self.vy, self.sw, self.sh)
        self.setCursor(Qt.ArrowCursor)

    # ── Main loop ──────────────────────────────────────────────────

    def _tick(self):
        self._timer_tick += 1
        self._icon_tick += 1

        if self._icon_tick >= 180:
            self.icons = self.hooks.get_all_positions()
            self._icon_tick = 0

        prev_state = self.brain.state
        self.brain.update(self.icons)
        nfo = self.brain.info

        self._emit_state_particles(nfo, prev_state)
        self._check_achievements(nfo)
        self._tick_toasts()
        self.particles.update()

        self.stats.update_playtime(0.016)
        self.update()

    def _emit_state_particles(self, nfo, prev_state):
        x, y = nfo["x"], nfo["y"]

        if nfo["state"] == S.STEALING and self.brain.timer == 25:
            self.particles.burst_sparkle(x, y - _e(20), count=25, color=QColor(255, 215, 0))
            for _ in range(8):
                self.particles.emit_star(x + random.randint(-30, 30), y - 20)

        if nfo["state"] == S.RUNNING and self._timer_tick % 5 == 0:
            self.particles.emit_smoke(x - nfo["direction"] * _e(20), y + _e(30))

        if nfo["state"] == S.TAUNTING and self._timer_tick % 12 == 0:
            for _ in range(4):
                self.particles.emit_confetti(x, y - _e(40))

        if nfo["state"] == S.SURRENDER and self._timer_tick % 8 == 0:
            self.particles.emit_heart(x + random.randint(-20, 20), y - _e(40))

    def _check_achievements(self, nfo):
        steal_count = nfo.get("sack_count", 0)
        state = nfo["state"]

        # Track steals
        if steal_count > self._prev_steal_count:
            self.stats.record_steal()
            unlocked = self.achievements.check("steal_count", 1)
            for a in unlocked:
                self._ach_toasts.append(AchToast(a.name, a.icon, self.sw))
            if steal_count >= 8:
                unlocked2 = self.achievements.check("full_sack", steal_count)
                for a in unlocked2:
                    self._ach_toasts.append(AchToast(a.name, a.icon, self.sw))
        self._prev_steal_count = steal_count

        # Midnight check
        import datetime
        if datetime.datetime.now().hour == 0:
            self.achievements.check("time_specific", hour=0)

        # Hide tracking
        if state == S.HIDING:
            self._hide_timer += 1
            if self._hide_timer % 60 == 0:
                self.achievements.check("hide_time", 1)
        else:
            self._hide_timer = 0

    def _tick_toasts(self):
        for t in self._ach_toasts:
            t.life -= 1
        self._ach_toasts = [t for t in self._ach_toasts if t.life > 0]

    # ── Paint ──────────────────────────────────────────────────────

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        nfo = self.brain.info
        x, y = nfo["x"], nfo["y"]
        direction = nfo["direction"]
        state = nfo["state"]
        speed = nfo.get("speed", 0)
        sack = nfo.get("sack_count", 0)

        # Floor shadow (3D perspective ellipse)
        self._draw_floor_shadow(p, x, y)

        # Particles behind character
        self.particles.draw(p)

        # Character (pseudo-3D)
        p.save()
        if direction == -1:
            # Flip horizontally around character center
            t = QTransform()
            t.translate(x, 0)
            t.scale(-1, 1)
            t.translate(-x, 0)
            p.setTransform(t)
        self._draw_lupin_3d(p, x, y, direction, state, speed, self._timer_tick, sack)
        p.restore()

        # Loot sack icon above head
        if sack > 0:
            self._draw_sack_3d(p, x, y, sack)

        # Achievement toasts
        for toast in self._ach_toasts:
            toast.draw(p)

        # Stats HUD
        if self._show_stats:
            self._draw_stats_hud(p)

        # Speech bubble
        key = nfo.get("speech_key")
        if key:
            msg = self._speech_for(key, state)
            if msg:
                self._draw_speech(p, x, y, msg)

        p.end()

    # ── 3D Character renderer ──────────────────────────────────────

    def _draw_lupin_3d(self, p, x, y, direction, state, speed, t, sack):
        """Render Lupin with pseudo-3D volumetric shading."""
        run_bob = 0
        breathe = math.sin(t * 0.06) * 2
        leg_swing = math.sin(t * 0.3) * 22

        is_running = state == S.RUNNING
        is_crouch  = state in (S.HIDING, S.SURRENDER)
        is_steal   = state in (S.STEALING, S.APPROACHING)
        is_taunt   = state == S.TAUNTING

        if is_running:
            run_bob = math.sin(t * 0.5) * 4
            speed_squash = min(1.0, speed / 12.0)
            body_sx = 1.0 - speed_squash * 0.12
            body_sy = 1.0 + speed_squash * 0.15
        else:
            body_sx = body_sy = 1.0

        cy = y + run_bob + breathe

        # ── Legs ──────────────────────────────────────────────────
        p.save()
        if is_running:
            self._draw_leg_3d(p, x - _e(8), cy + _e(30), leg_swing, SUIT_F, SUIT_D)
            self._draw_leg_3d(p, x + _e(8), cy + _e(30), -leg_swing, SUIT_F, SUIT_D)
        elif is_crouch:
            self._draw_leg_3d(p, x - _e(10), cy + _e(22), 60, SUIT_F, SUIT_D)
            self._draw_leg_3d(p, x + _e(10), cy + _e(22), -60, SUIT_F, SUIT_D)
        else:
            self._draw_leg_3d(p, x - _e(9), cy + _e(30), 8, SUIT_F, SUIT_D)
            self._draw_leg_3d(p, x + _e(9), cy + _e(30), -8, SUIT_F, SUIT_D)
        p.restore()

        # ── Body (3D pill) ────────────────────────────────────────
        p.save()
        p.translate(x, cy)
        p.scale(body_sx, body_sy)
        self._draw_body_3d(p, state, t)
        p.restore()

        # ── Arms ──────────────────────────────────────────────────
        p.save()
        self._draw_arms_3d(p, x, cy, state, t)
        p.restore()

        # ── Head ──────────────────────────────────────────────────
        head_tilt = 0
        if state == S.TAUNTING:
            head_tilt = math.sin(t * 0.18) * 12
        elif is_running:
            head_tilt = nfo_direction_sign(direction) * min(speed * 1.2, 18)
        elif is_crouch:
            head_tilt = -15

        p.save()
        p.translate(x, cy - _e(28))
        p.rotate(head_tilt)
        self._draw_head_3d(p, state, t, sack > 0)
        p.restore()

    def _draw_body_3d(self, p, state, t):
        """3D body: extrusion side + lit front."""
        bw, bh = _e(22), _e(30)
        is_crouch = state in (S.HIDING, S.SURRENDER)
        if is_crouch:
            bh = _e(22)

        # Shadow/extrusion (right-bottom offset = depth illusion)
        depth = _e(5)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(SUIT_SHD))
        p.drawRoundedRect(-bw + depth, -bh//2 + depth, bw*2, bh, _e(10), _e(10))

        # Front face with gradient
        grad = QLinearGradient(-bw, -bh//2, bw, bh//2)
        grad.setColorAt(0.0, SUIT_L)
        grad.setColorAt(0.4, SUIT_F)
        grad.setColorAt(1.0, SUIT_D)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(-bw, -bh//2, bw*2, bh, _e(10), _e(10))

        # Tie/chest detail
        tie = QLinearGradient(0, -_e(10), 0, _e(10))
        tie.setColorAt(0, QColor(180, 30, 30))
        tie.setColorAt(1, QColor(100, 15, 15))
        p.setBrush(QBrush(tie))
        p.drawRoundedRect(-_e(4), -_e(12), _e(8), _e(18), _e(3), _e(3))

        # Suit outline
        p.setPen(QPen(SUIT_SHD, 1.5))
        p.setBrush(Qt.NoBrush)
        p.drawRoundedRect(-bw, -bh//2, bw*2, bh, _e(10), _e(10))

    def _draw_leg_3d(self, p, lx, ly, angle, col_f, col_d):
        """3D leg: cylinder with shading."""
        p.save()
        p.translate(lx, ly)
        p.rotate(angle)
        lw, lh = _e(7), _e(22)

        # Side extrusion
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(col_d))
        p.drawRoundedRect(-lw//2 + 3, -lh//4, lw, lh, _e(4), _e(4))

        # Front
        grad = QLinearGradient(-lw//2, 0, lw//2, 0)
        grad.setColorAt(0, col_f)
        grad.setColorAt(0.6, col_d)
        p.setBrush(QBrush(grad))
        p.drawRoundedRect(-lw//2, -lh//4, lw, lh, _e(4), _e(4))

        # Shoe
        p.setBrush(QBrush(SHOE_D))
        p.drawRoundedRect(-_e(6) + 2, lh - _e(4), _e(13), _e(7), _e(3), _e(3))
        p.setBrush(QBrush(SHOE_F))
        p.drawRoundedRect(-_e(6), lh - _e(6), _e(13), _e(7), _e(3), _e(3))

        p.restore()

    def _draw_arms_3d(self, p, x, cy, state, t):
        """Arms with 3D shading per stato."""
        if state == S.SURRENDER:
            # Hands up
            self._draw_arm_seg(p, x - _e(24), cy - _e(8), x - _e(32), cy - _e(35))
            self._draw_arm_seg(p, x + _e(24), cy - _e(8), x + _e(32), cy - _e(35))
        elif state == S.TAUNTING:
            bob = math.sin(t * 0.2) * 10
            self._draw_arm_seg(p, x - _e(24), cy - _e(4), x - _e(38), cy + _e(10) + bob)
            self._draw_arm_seg(p, x + _e(24), cy - _e(4), x + _e(44), cy - _e(18) + bob)
        elif state in (S.STEALING, S.APPROACHING):
            self._draw_arm_seg(p, x - _e(24), cy, x - _e(14), cy + _e(18))
            self._draw_arm_seg(p, x + _e(24), cy, x + _e(46), cy - _e(8))
        elif state == S.RUNNING:
            swing = math.sin(t * 0.3) * 22
            self._draw_arm_seg(p, x - _e(22), cy, x - _e(36), cy + _e(swing * 0.5))
            self._draw_arm_seg(p, x + _e(22), cy, x + _e(36), cy - _e(swing * 0.5))
        elif state == S.HIDING:
            self._draw_arm_seg(p, x - _e(24), cy, x - _e(22), cy + _e(28))
            self._draw_arm_seg(p, x + _e(24), cy, x + _e(22), cy + _e(28))
        else:
            wave = math.sin(t * 0.1) * 6
            self._draw_arm_seg(p, x - _e(24), cy, x - _e(32), cy + _e(20) + wave)
            self._draw_arm_seg(p, x + _e(24), cy, x + _e(32), cy + _e(20) - wave)

    def _draw_arm_seg(self, p, x1, y1, x2, y2):
        """Cylindrical arm segment with 3D shading."""
        # Shadow arm
        pen_shd = QPen(SKIN_SHD, _e(9))
        pen_shd.setCapStyle(Qt.RoundCap)
        p.setPen(pen_shd)
        p.drawLine(QPointF(x1 + 2, y1 + 2), QPointF(x2 + 2, y2 + 2))

        # Lit arm
        pen_lit = QPen(SKIN, _e(8))
        pen_lit.setCapStyle(Qt.RoundCap)
        p.setPen(pen_lit)
        p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

        # Hand knuckle
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(SKIN_LIT))
        p.drawEllipse(QPointF(x2, y2), _e(5), _e(5))
        p.setBrush(QBrush(SKIN_DARK))
        p.drawEllipse(QPointF(x2 + 1, y2 + 1), _e(3.5), _e(3.5))
        p.setBrush(QBrush(SKIN_LIT))
        p.drawEllipse(QPointF(x2 - 1, y2 - 1), _e(2), _e(2))

    def _draw_head_3d(self, p, state, t, has_sack):
        """Sphere-like head with specular highlight."""
        r = _e(18)

        is_running = state == S.RUNNING
        is_hide    = state == S.HIDING
        is_surrnd  = state == S.SURRENDER

        # 3D extrusion
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(SKIN_SHD))
        p.drawEllipse(QPointF(_e(3), _e(3)), r, r)

        # Sphere gradient
        grad = QRadialGradient(-r * 0.3, -r * 0.4, r * 0.3, 0, 0, r)
        grad.setColorAt(0.0, SKIN_LIT)
        grad.setColorAt(0.5, SKIN)
        grad.setColorAt(1.0, SKIN_DARK)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(0, 0), r, r)

        # Specular highlight
        p.setBrush(QBrush(QColor(255, 255, 255, 80)))
        p.drawEllipse(QPointF(-r * 0.28, -r * 0.35), r * 0.22, r * 0.15)

        # Eyes
        blink = (t % 200 < 8)
        self._draw_eye_3d(p, -_e(7), -_e(3), state, blink, t)
        self._draw_eye_3d(p, +_e(7), -_e(3), state, blink, t)

        # Mouth
        self._draw_mouth_3d(p, state, t)

        # Hair
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(HAIR_D))
        p.drawEllipse(QPointF(2, -r + 2), r * 0.85, r * 0.5)
        p.setBrush(QBrush(HAIR_F))
        p.drawEllipse(QPointF(0, -r), r * 0.85, r * 0.5)

        # Hat
        self._draw_hat_3d(p, r)

    def _draw_eye_3d(self, p, ex, ey, state, blink, t):
        """3D eye: white sclera + shaded iris + pupil + spec."""
        rw, rh = _e(6), _e(7)
        p.setPen(Qt.NoPen)

        if blink or state == S.HIDING:
            # Blink line
            p.setPen(QPen(SKIN_DARK, 2))
            p.drawLine(QPointF(ex - rw, ey), QPointF(ex + rw, ey))
            return

        # Sclera shadow
        p.setBrush(QBrush(QColor(180, 180, 190)))
        p.drawEllipse(QPointF(ex + 1, ey + 1), rw, rh)
        # Sclera
        p.setBrush(QBrush(EYE_W))
        p.drawEllipse(QPointF(ex, ey), rw, rh)

        # Iris gradient
        iris_grad = QRadialGradient(ex - 1, ey - 2, 2, ex, ey, _e(4))
        iris_grad.setColorAt(0, QColor(80, 60, 180))
        iris_grad.setColorAt(1, EYE_P)
        p.setBrush(QBrush(iris_grad))
        p.drawEllipse(QPointF(ex, ey), _e(4), _e(5))

        # Pupil
        p.setBrush(QBrush(QColor(5, 5, 20)))
        p.drawEllipse(QPointF(ex, ey), _e(2), _e(2.5))

        # Specular dot
        p.setBrush(QBrush(QColor(255, 255, 255, 220)))
        p.drawEllipse(QPointF(ex - _e(1.5), ey - _e(2)), _e(1.5), _e(1.5))

        # Outline
        p.setPen(QPen(SKIN_DARK, 1))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(ex, ey), rw, rh)

    def _draw_mouth_3d(self, p, state, t):
        """Expressive mouth per stato."""
        p.setPen(Qt.NoPen)
        if state == S.SURRENDER:
            # Sad
            path = QPainterPath()
            path.moveTo(-_e(8), _e(8))
            path.quadTo(0, _e(14), _e(8), _e(8))
            p.setPen(QPen(SKIN_SHD, 2))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
        elif state == S.TAUNTING:
            # Big grin
            path = QPainterPath()
            path.moveTo(-_e(10), _e(6))
            path.quadTo(0, _e(16), _e(10), _e(6))
            p.setPen(QPen(SKIN_SHD, 2.5))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
            # Teeth
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(240, 240, 240)))
            p.drawRoundedRect(-_e(7), _e(7), _e(14), _e(5), 2, 2)
        elif state == S.STEALING:
            # Determined smirk
            path = QPainterPath()
            path.moveTo(-_e(8), _e(7))
            path.quadTo(-_e(2), _e(11), _e(8), _e(7))
            p.setPen(QPen(SKIN_SHD, 2))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)
        elif state == S.RUNNING:
            # Open mouth panting
            p.setPen(QPen(SKIN_SHD, 1.5))
            p.setBrush(QBrush(QColor(180, 60, 60)))
            p.drawEllipse(QPointF(0, _e(9)), _e(6), _e(4))
        else:
            # Neutral smile
            path = QPainterPath()
            path.moveTo(-_e(6), _e(7))
            path.quadTo(0, _e(12), _e(6), _e(7))
            p.setPen(QPen(SKIN_SHD, 1.8))
            p.setBrush(Qt.NoBrush)
            p.drawPath(path)

    def _draw_hat_3d(self, p, head_r):
        """3D Lupin hat: brim disc + cylindrical crown."""
        p.setPen(Qt.NoPen)

        # Brim shadow
        p.setBrush(QBrush(HAT_D))
        p.drawEllipse(QPointF(2, -head_r - _e(2) + 2), _e(24), _e(8))
        # Brim front
        brim_grad = QLinearGradient(-_e(24), 0, _e(24), 0)
        brim_grad.setColorAt(0.0, QColor(50, 50, 50))
        brim_grad.setColorAt(0.5, QColor(80, 80, 80))
        brim_grad.setColorAt(1.0, QColor(30, 30, 30))
        p.setBrush(QBrush(brim_grad))
        p.drawEllipse(QPointF(0, -head_r - _e(2)), _e(24), _e(8))

        # Crown side (depth)
        p.setBrush(QBrush(HAT_D))
        p.drawRoundedRect(-_e(16) + 3, -head_r - _e(28) + 3, _e(32), _e(26), _e(3), _e(3))
        # Crown front gradient
        crown_grad = QLinearGradient(-_e(16), 0, _e(16), 0)
        crown_grad.setColorAt(0.0, QColor(60, 60, 60))
        crown_grad.setColorAt(0.45, QColor(35, 35, 35))
        crown_grad.setColorAt(1.0, QColor(15, 15, 15))
        p.setBrush(QBrush(crown_grad))
        p.drawRoundedRect(-_e(16), -head_r - _e(28), _e(32), _e(26), _e(3), _e(3))

        # Red hatband
        p.setBrush(QBrush(HAT_RIM))
        p.drawRect(-_e(16), -head_r - _e(4), _e(32), _e(4))

        # Hat specular
        p.setBrush(QBrush(QColor(120, 120, 120, 60)))
        p.drawEllipse(QPointF(-_e(6), -head_r - _e(22)), _e(8), _e(4))

    def _draw_floor_shadow(self, p, x, y):
        """Perspective ellipse shadow on virtual floor."""
        sw_x = _e(55)
        sw_y = _e(14)
        shadow_grad = QRadialGradient(x, y + _e(40), sw_x)
        shadow_grad.setColorAt(0.0, QColor(0, 0, 0, 90))
        shadow_grad.setColorAt(0.6, QColor(0, 0, 0, 40))
        shadow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(shadow_grad))
        p.drawEllipse(QPointF(x, y + _e(40)), sw_x, sw_y)

    def _draw_sack_3d(self, p, x, y, count):
        """3D loot sack above head."""
        sx, sy = x, y - _e(75)
        r = _e(18)

        # Sack shadow
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(SACK_D))
        p.drawEllipse(QPointF(sx + 3, sy + 3), r, r)

        # Sack body gradient
        grad = QRadialGradient(sx - r * 0.3, sy - r * 0.3, r * 0.4, sx, sy, r)
        grad.setColorAt(0, QColor(220, 175, 95))
        grad.setColorAt(0.5, SACK_F)
        grad.setColorAt(1, SACK_D)
        p.setBrush(QBrush(grad))
        p.drawEllipse(QPointF(sx, sy), r, r)

        # Rope tie
        p.setPen(QPen(QColor(100, 70, 30), 3))
        p.drawLine(QPointF(sx - _e(6), sy - r), QPointF(sx + _e(6), sy - r))
        p.setPen(QPen(QColor(80, 50, 20), 2))
        p.drawLine(QPointF(sx, sy - r - _e(4)), QPointF(sx, sy - r - _e(10)))

        # Count text
        p.setPen(QPen(QColor(40, 20, 5), 1))
        p.setFont(QFont("Arial", _e(10), QFont.Bold))
        p.drawText(QRectF(sx - r, sy - _e(8), r * 2, _e(16)), Qt.AlignCenter, f"×{count}")

    def _draw_speech(self, p, x, y, text):
        """3D-style speech bubble."""
        font = QFont("Segoe UI", 9)
        p.setFont(font)
        fm = QFontMetrics(font)
        tw = fm.horizontalAdvance(text) + 24
        th = 36
        bx = min(x - tw // 2, self.sw - tw - 10)
        by = y - _e(90) - th

        # Bubble shadow
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(0, 0, 0, 60)))
        p.drawRoundedRect(bx + 3, by + 3, tw, th, 10, 10)

        # Bubble bg
        p.setBrush(QBrush(QColor(255, 255, 240, 230)))
        p.setPen(QPen(QColor(80, 60, 40), 1.5))
        p.drawRoundedRect(bx, by, tw, th, 10, 10)

        # Tail
        path = QPainterPath()
        path.moveTo(x - 6, by + th)
        path.lineTo(x + 6, by + th)
        path.lineTo(x, by + th + 12)
        p.setBrush(QBrush(QColor(255, 255, 240, 230)))
        p.setPen(QPen(QColor(80, 60, 40), 1.5))
        p.drawPath(path)

        # Text
        p.setPen(QPen(QColor(30, 20, 10)))
        p.drawText(QRectF(bx, by, tw, th), Qt.AlignCenter, text)

    def _draw_stats_hud(self, p):
        """Bottom-left stats overlay."""
        summary = self.stats.get_summary()
        ach_prog = self.achievements.get_progress()
        lines = [
            f"🎭 {self.brain.personality.capitalize()}",
            f"🔑 Furti totali: {summary['total_steals']}",
            f"🏆 Achievement: {ach_prog['unlocked']}/{ach_prog['total']}",
            f"⏱  Sessione: {int((time.time() - self._session_start) / 60)}m",
            f"📦 Sack: {summary['session_stats']['steals']} questa sessione",
        ]
        x, y0 = 14, self.sh - 160
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(QColor(0, 0, 0, 160)))
        p.drawRoundedRect(x - 8, y0 - 6, 220, len(lines) * 22 + 12, 8, 8)
        p.setFont(QFont("Segoe UI", 9))
        for i, line in enumerate(lines):
            p.setPen(QPen(QColor(200, 230, 255)))
            p.drawText(x, y0 + i * 22 + 14, line)

    @staticmethod
    def _speech_for(key, state):
        library = {
            "first_steal": ["Eccola! 🤌", "Affare fatto! ✨"],
            "taunting":    ["Troppo lento! 😈", "Hahaha! 🎩"],
            "surrender":   ["Ok ok, mi arrendo 🏳️", "Ecco le tue icone 😤"],
            "running":     ["Non mi prenderai mai!", "Ahahah! 🏃"],
        }
        return random.choice(library.get(key, [])) if key in library else ""

    # ── Input ──────────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.brain.on_click()
            self.stats.record_caught()
            self.achievements.check("max_combo", 1)
            self.particles.burst_sparkle(e.x(), e.y(), 15, QColor(255, 80, 80))

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hooks.restore_icons()
            self.stats.end_session()
            QApplication.quit()
        elif e.key() == Qt.Key_S:
            self._show_stats = not self._show_stats


def nfo_direction_sign(d):
    return 1 if d >= 0 else -1


def main():
    app = QApplication(sys.argv)
    win = LupinPet3D()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

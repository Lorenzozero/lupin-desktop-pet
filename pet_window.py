import os, sys, math, random
import win32gui, win32con, win32api

from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, QRectF
from PyQt5.QtGui import (
    QPainter, QColor, QFont, QBrush, QPen,
    QPainterPath, QPixmap, QCursor,
    QRadialGradient, QLinearGradient,
)

from desktop_hooks import DesktopHooks
from pet_brain import LupinBrain, S, FRIENDLY_STATES
from sound_manager import SoundManager

SIZE = 110   # bounding box logico

# ─────────────────────────────────────────────────────────
#  Particelle
# ─────────────────────────────────────────────────────────

class Particle:
    def __init__(self, x, y, color, size=5, vx=None, vy=None, ptype="default"):
        self.x, self.y = float(x), float(y)
        self.vx = vx if vx is not None else random.uniform(-3, 3)
        self.vy = vy if vy is not None else random.uniform(-6, -2)
        self.life = 1.0
        self.color = color
        self.size = float(size)
        self.type = ptype
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-12, 12)

    def update(self):
        if self.type == "sparkle":
            self.vy += 0.18;  self.vx *= 0.97;  self.life -= 0.022
        elif self.type == "smoke":
            self.vy -= 0.12;  self.vx *= 0.94;  self.size += 0.25;  self.life -= 0.013
        elif self.type == "heart":
            self.vy -= 0.5;  self.vx *= 0.96;  self.life -= 0.016
        elif self.type == "note":
            self.vy -= 0.4;  self.vx += math.sin(self.life * 8) * 0.4;  self.life -= 0.013
        elif self.type == "zzz":
            self.vy -= 0.4;  self.vx += math.sin(self.life * 5) * 0.3
            self.size += 0.1;  self.life -= 0.011
        elif self.type == "confetti":
            self.vy += 0.4;  self.rotation += self.spin;  self.life -= 0.014
        elif self.type == "star":
            self.vy += 0.2;  self.rotation += self.spin;  self.life -= 0.018
        elif self.type == "emoji_pain":
            self.vy -= 0.25;  self.vx *= 0.94;  self.life -= 0.010
        elif self.type == "sweat":
            self.vy += 0.8;  self.vx *= 0.90;  self.life -= 0.035
        elif self.type == "dust":
            self.vy -= 0.05;  self.size += 0.15;  self.life -= 0.02
        else:
            self.vy += 0.3;  self.life -= 0.022
        self.x += self.vx;  self.y += self.vy
        return self.life > 0


class Toast:
    def __init__(self, text, color=None):
        self.text = text
        self.color = color or QColor(255, 215, 0)
        self.life = 1.0
        self.y_off = 0.0

    def update(self):
        self.life -= 1 / 220
        self.y_off = min(self.y_off + 1.8, 44)
        return self.life > 0


class Portal:
    """Buco nero da cui Lupin emerge o in cui scompare."""
    OPEN   = "open"
    HOLD   = "hold"
    CLOSE  = "close"

    def __init__(self, x, y, mode="emerge"):
        self.x, self.y = float(x), float(y)
        self.mode   = mode      # "emerge" | "vanish"
        self.phase  = self.OPEN
        self.radius = 2.0
        self.angle  = 0.0      # per la rotazione del vortice
        self.life   = 1.0
        self.done   = False
        self._hold  = 0

    def update(self):
        self.angle = (self.angle + 5) % 360
        if self.phase == self.OPEN:
            target = 80 if self.mode == "emerge" else 55
            self.radius += (target - self.radius) * 0.14
            if self.radius > target - 3:
                self.phase = self.HOLD
        elif self.phase == self.HOLD:
            self._hold += 1
            if self._hold > (30 if self.mode == "emerge" else 18):
                self.phase = self.CLOSE
        else:
            self.radius *= 0.82
            self.life   -= 0.06
            if self.life < 0.05:
                self.done = True
        return not self.done


# ─────────────────────────────────────────────────────────
#  PetWindow
# ─────────────────────────────────────────────────────────

BODY_COLOR   = QColor(200, 45,  45)   # giacca rossa
SKIN_COLOR   = QColor(240, 195, 145)
HAIR_COLOR   = QColor(25,  20,  20)
PANTS_COLOR  = QColor(30,  30,  30)
SHOE_COLOR   = QColor(55,  35,  15)
SHIRT_COLOR  = QColor(240, 240, 240)
TIE_COLOR    = QColor(30,  30,  120)
HAT_COLOR    = QColor(18,  18,  18)
HATBAND_CLR  = QColor(180, 20,  20)
OUTLINE      = QColor(30,  20,  10)

class PetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Dual monitor: usa il virtual screen che copre tutti i monitor
        vx = win32api.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
        vy = win32api.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
        self.sw = win32api.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        self.sh = win32api.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        self._vx = vx;  self._vy = vy        # offset origine (negativo con monitor a sinistra)

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setGeometry(vx, vy, self.sw, self.sh)

        self.hooks = DesktopHooks()
        self.hooks.save_positions()
        self.icons = self.hooks.get_all_positions()

        # Brain usa coordinate assolute virtual screen (sw/sh totali, origine in _vx/_vy)
        self.brain = LupinBrain(self.sw, self.sh, self.hooks,
                                vx=self._vx, vy=self._vy)
        self.sound = SoundManager()

        self.particles = []
        self.toasts    = []
        self.portals   = []

        self.shake_off  = (0.0, 0.0)
        self.shake_int  = 0.0
        self.squash     = 1.0
        self.body_rot   = 0.0
        self.trail      = []
        self.dust_t     = 0

        self.blink_t    = 0
        self.eye_state  = "open"
        self.flash_a    = 0
        self.cursor_att = 0.0

        self.combo      = 0
        self.last_steal_t = 0

        # Speech
        self.speech_text  = ""
        self.speech_scale = 0.0
        self.speech_active= False
        self.speech_timer = 0

        # Greeting once
        self.greeted = False

        self._prev_hit_reaction = ""

        self._icon_tick = 0
        self._loop_timer = QTimer()
        self._loop_timer.timeout.connect(self._loop)
        self._loop_timer.start(16)
        self._set_passthrough(True)
        self.show()

    # ── Win32 ────────────────────────────────────────────────

    def _set_passthrough(self, on):
        hwnd = int(self.winId())
        ex = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if on: ex |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
        else:  ex &= ~win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex)

    # ── Main loop ────────────────────────────────────────────

    def _loop(self):
        self._icon_tick += 1
        if self._icon_tick >= 200:
            self.icons = self.hooks.get_all_positions()
            self._icon_tick = 0

        prev_x, prev_y = self.brain.x, self.brain.y
        prev_state = self.brain.state
        # Freeze movimento mentre parla
        self.brain.frozen = self.speech_active
        self.brain.update(self.icons)
        nfo = self.brain.info
        state = nfo["state"]
        t = nfo["timer"]

        entered = state != prev_state

        # ── Transizioni di stato ─────────────────────────────
        if entered:
            if state == S.APPROACHING:
                # Buco nero di uscita: Lupin emerge dal portale
                self.portals.append(Portal(nfo["x"], nfo["y"], mode="emerge"))
            elif state == S.TAUNTING and prev_state in (S.STEALING, S.APPROACHING):
                # Dopo il furto: scompare in un buco nero
                self.portals.append(Portal(nfo["x"], nfo["y"], mode="vanish"))
            if state == S.STEALING:
                self.sound.play("steal", 0.4)
            if state == S.TAUNTING:
                self.sound.play("taunt", 0.5)
                self._say(nfo["current_joke"] or "Non mi prenderai mai! 😝")
            elif state == S.SURRENDER:
                self.sound.play("caught", 0.6)
                self._say(nfo["current_joke"] or "Ok... hai vinto 😤", 240)
            elif state == S.WAVING:
                if not self.greeted:
                    h = nfo["hour"]
                    msg = ("Buongiorno! ☀️" if h < 12 else
                           "Buon pomeriggio! 😊" if h < 19 else "Buonasera! 🌙")
                    self._say(msg + " Sono Lupin! 👋")
                    self.greeted = True
                else:
                    self._say(nfo["current_joke"] or "Ciao! 👋")
                self._spawn_hearts(nfo["x"], nfo["y"], 10)
            elif state == S.DANCING:
                self._say(nfo["current_joke"] or "🎵 La la la!")
            elif state == S.CELEBRATING:
                self._say(nfo["current_joke"] or "LIBERO! 🎉")
                self.toasts.append(Toast(f"🎯 Catturato ×{nfo['times_caught']}!", QColor(255, 200, 50)))
                self._spawn_confetti(nfo["x"], nfo["y"], 30)
            elif state == S.CURIOUS:
                self._say(nfo["current_joke"] or "Cosa stai facendo? 🤔", 180)
            elif state == S.FOLLOWING:
                self._say(nfo["current_joke"] or "Aspettami! 🏃", 160)
            elif state == S.HANGING:
                self._say(nfo["current_joke"] or "Ciao dall'alto! 😎", 160)
            elif state == S.LEANING:
                self._say(nfo["current_joke"] or "Bella finestra! 😎", 240)
            elif state == S.CORNER:
                self._say(nfo["current_joke"] or "Nessuno mi trova qui! 😏", 220)
            elif state == S.PUSHING:
                self._say(nfo["current_joke"] or "Via via! Spostati! 💪", 200)
            elif state == S.CARRYING:
                self._say(nfo["current_joke"] or "Consegne a domicilio! 📦", 200)
            elif state == S.SITTING:
                self._say(nfo["current_joke"] or "Bella questa scrivania! 😌", 250)
            elif state == S.PRANK:
                pass
            elif state == S.SLEEPING:
                self._say("Zzz... 💤", 300)
            elif state == S.EXHAUSTED:
                self._say(nfo["current_joke"] or "...sto... riprendendo fiato... 😮‍💨", 280)
            elif state == S.VOLUME_TRICK:
                self._say(nfo["current_joke"] or "VOLUME AL MASSIMO! 🔊", 260)
            elif state == S.DRINKING:
                self._say(nfo["current_joke"] or "Salute! 🍺", 240)

        # Auto-restore speech (brain setta current_joke e lo consuma)
        if nfo.get("current_joke") and "sistemo" in nfo["current_joke"] and not self.speech_active:
            self._say(nfo["current_joke"], 340)
            self._spawn_confetti(nfo["x"], nfo["y"], 15)

        # Battuta del prank al momento giusto
        if state == S.PRANK and t == 36:
            self._say(nfo["current_joke"] or "CAOS TOTALE! 🌪️", 240)
            self.shake_int = 14
            self.flash_a = 180
            self._spawn_confetti(nfo["x"], nfo["y"], 25)

        # ── Effetti per stato ─────────────────────────────────
        if state == S.STEALING and t == 25:
            n = 22 + self.combo * 5
            for _ in range(n):
                self.particles.append(Particle(
                    nfo["x"], nfo["y"], QColor(255, 215, 0), 6, ptype="star"))
            self.shake_int = 9 + self.combo * 2
            self.flash_a   = 180
            self.combo = self.combo + 1 if t - self.last_steal_t < 140 else 1
            self.last_steal_t = t

        if state == S.RUNNING:
            self.dust_t += 1
            if self.dust_t % 5 == 0:
                for _ in range(2):
                    self.particles.append(Particle(
                        nfo["x"], nfo["y"] + 40,
                        QColor(200, 190, 170, 140), 9,
                        random.uniform(-2, 2), random.uniform(-1, 0.3), "dust"))
            spd = math.hypot(nfo["x"] - prev_x, nfo["y"] - prev_y)
            self.squash  = 1.0 - min(spd * 0.022, 0.32)
            self.body_rot = math.sin(self.brain.global_timer * 0.28) * 7
            # Gocce di sudore se cursore vicino
            cx, cy = win32api.GetCursorPos()
            if math.hypot(nfo["x"]-cx, nfo["y"]-cy) < 230 and t % 28 == 0:
                for _ in range(2):
                    self.particles.append(Particle(
                        nfo["x"] + random.randint(-15, 15), nfo["y"] - 30,
                        QColor(100, 180, 255, 220), 7,
                        random.uniform(-0.4, 0.4), 0.0, "sweat"))
        else:
            self.squash  = 1.0
            self.body_rot = 0.0

        if state == S.DANCING and t % 22 == 0:
            self.particles.append(Particle(
                nfo["x"] + random.randint(-35, 35), nfo["y"] - 40,
                QColor(255, 220, 60), 18,
                random.uniform(-1.5, 1.5), random.uniform(-2.5, -0.5), "note"))

        # Linguaccia / rutto
        if nfo.get("burp_pending"):
            self.brain.burp_pending = False
            self._say(nfo["current_joke"] or "BRUUAP! 🤢", 200)
            # Particella rutto (bolle verdi)
            for _ in range(6):
                self.particles.append(Particle(
                    nfo["x"] + random.randint(-15, 15), nfo["y"] - 50,
                    QColor(100, 220, 80, 200), random.randint(10, 18),
                    random.uniform(-1.5, 1.5), random.uniform(-3, -1), "smoke"))
            self.shake_int = max(self.shake_int, 5)

        if nfo.get("tongue_timer", 0) == 50 and not nfo.get("burp_pending"):
            self._say(nfo["current_joke"] or "Bleah! 😛", 160)

        # EXHAUSTED: sudore leggero (meno particelle)
        if state == S.EXHAUSTED:
            if t % 45 == 0:
                self.particles.append(Particle(
                    nfo["x"] + random.randint(-12, 12), nfo["y"] - 42,
                    QColor(100, 180, 255, 180), 7,
                    random.uniform(-0.4, 0.4), random.uniform(-1.2, -0.3), "sweat"))
            if t % 80 == 0:
                self.particles.append(Particle(
                    nfo["x"] + random.randint(-6, 6), nfo["y"] - 32,
                    QColor(200, 200, 220, 80), 10,
                    random.uniform(-0.3, 0.3), -0.5, "smoke"))
            if t % 300 == 120 and not self.speech_active:
                self._say(nfo["current_joke"] or "Non ce la faccio... 🥵", 220)

        # VOLUME_TRICK: note musicali e particelle volume
        if state == S.VOLUME_TRICK and t % 14 == 0 and 40 < t < 220:
            self.particles.append(Particle(
                nfo["x"] + random.randint(-20, 30), nfo["y"] - random.randint(30, 70),
                QColor(255, 220, 60), 18,
                random.uniform(-2, 2), random.uniform(-3, -1), "note"))

        if state == S.SLEEPING and t % 80 == 0:
            self.particles.append(Particle(
                nfo["x"] + 28, nfo["y"] - 60,
                QColor(180, 160, 255), 15 + (t // 80 % 3) * 5,
                random.uniform(-0.2, 0.2), -0.5, "zzz"))

        if state == S.CELEBRATING:
            if t % 18 == 0:
                self.particles.append(Particle(
                    nfo["x"] + random.randint(-45, 45), nfo["y"] - 20,
                    QColor(255, 80, 140), 16, ptype="heart"))

        # Speech periodici per stati "in posa"
        if state == S.LEANING and t % 280 == 60 and not self.speech_active:
            self._say(nfo["current_joke"] or "Chill mode: ON 😌", 230)
        if state == S.CORNER and t % 300 == 80 and not self.speech_active:
            self._say(nfo["current_joke"] or "L'angolo perfetto! 😏", 220)
        if state == S.SITTING and t % 260 == 60 and not self.speech_active:
            self._say(nfo["current_joke"] or "Comodo! 😌", 240)

        # Carrying: particella polvere icona
        if state == S.CARRYING and t % 40 == 0:
            cx_i, cy_i = nfo.get("carry_icon_pos", (nfo["x"], nfo["y"] - 85))
            self.particles.append(Particle(
                cx_i + random.randint(-10, 10), cy_i,
                QColor(255, 220, 100, 180), 8, ptype="sparkle"))

        if state == S.WAVING and t % 28 == 0:
            self.particles.append(Particle(
                nfo["x"] + random.randint(-28, 28), nfo["y"] - random.randint(20, 55),
                QColor(255, 120, 160), 14, ptype="heart"))

        # Wrap flash
        if nfo["just_wrapped"]:
            self.flash_a = max(self.flash_a, 80)

        # Trail
        self.trail.append((prev_x, prev_y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        # Cursor attention
        cx, cy = win32api.GetCursorPos()
        if math.hypot(nfo["x"]-cx, nfo["y"]-cy) < 220 and state in FRIENDLY_STATES:
            self.cursor_att = min(1.0, self.cursor_att + 0.06)
        else:
            self.cursor_att = max(0.0, self.cursor_att - 0.04)

        # Blink
        self.blink_t += 1
        if self.blink_t > random.randint(130, 360):
            self.eye_state = "closed";  self.blink_t = 0
        elif self.blink_t > 5:
            self.eye_state = "open"

        # Speech
        if self.speech_active:
            self.speech_timer -= 1
            self.speech_scale = min(self.speech_scale + 0.15, 1.0)
            if self.speech_timer <= 0:
                self.speech_active = False
        else:
            self.speech_scale = max(0.0, self.speech_scale - 0.20)

        # Shake decay
        if self.shake_int > 0.4:
            self.shake_int *= 0.86
            self.shake_off = (
                random.uniform(-self.shake_int, self.shake_int),
                random.uniform(-self.shake_int, self.shake_int))
        else:
            self.shake_int = 0;  self.shake_off = (0, 0)

        self.flash_a = max(0, self.flash_a - 25)

        # Particles / toasts / portals
        self.particles = [p for p in self.particles if p.update()]
        self.toasts    = [t for t in self.toasts    if t.update()]
        self.portals   = [p for p in self.portals   if p.update()]

        # Passthrough
        pr = QRect(int(nfo["x"]) - SIZE//2 - 20, int(nfo["y"]) - SIZE//2 - 30, SIZE+40, SIZE+60)
        self._set_passthrough(not pr.contains(QCursor.pos()))
        self.update()

    def _say(self, text, dur=220):
        self.speech_text   = text
        self.speech_active = True
        self.speech_timer  = dur
        self.speech_scale  = 0.0

    def _spawn_hearts(self, x, y, n):
        for _ in range(n):
            self.particles.append(Particle(
                x + random.randint(-35, 35), y + random.randint(-30, 10),
                QColor(255, 100, 150), 15, ptype="heart"))

    def _spawn_confetti(self, x, y, n):
        for _ in range(n):
            self.particles.append(Particle(
                x + random.randint(-60, 60), y - random.randint(0, 80),
                QColor(random.randint(100,255), random.randint(100,255), random.randint(50,200)),
                9, ptype="confetti"))

    # ── Paint ────────────────────────────────────────────────

    def paintEvent(self, _):
        nfo = self.brain.info
        px, py = nfo["x"], nfo["y"]
        jz = nfo["jump_z"]
        state = nfo["state"]
        t_global = nfo["global_timer"]

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)

        # 1. Dust trail during running
        if state == S.RUNNING and len(self.trail) > 2:
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int(20 * i / len(self.trail))
                p.setOpacity(alpha / 255)
                p.setBrush(QBrush(QColor(200, 190, 170, 80)))
                p.setPen(Qt.NoPen)
                p.drawEllipse(int(tx) - 12, int(ty) + 30, 24, 12)
        p.setOpacity(1.0)

        # 2. Portali (buchi neri) — prima dei personaggi
        for portal in self.portals:
            self._draw_portal(p, portal)

        # 2b. Particles
        self._paint_particles(p)

        # 3. Shadow (si riduce con l'altezza del salto)
        sh_y = py + SIZE // 2 + 10 + jz * 0.1
        sh_scale = max(0.3, 1.0 - abs(jz) / 120)
        sh_r = (SIZE // 2) * sh_scale
        shadow = QRadialGradient(px, sh_y, sh_r * 1.4)
        shadow.setColorAt(0, QColor(0, 0, 0, int(80 * sh_scale)))
        shadow.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(shadow));  p.setPen(Qt.NoPen)
        p.drawEllipse(int(px - sh_r * 1.4), int(sh_y) - 6, int(sh_r * 2.8), 14)

        # 4. Lupin character
        draw_y = py + jz

        p.save()
        ox, oy = self.shake_off
        p.translate(px + ox, draw_y + oy)
        p.rotate(self.body_rot)

        if nfo["is_hiding"]:
            peek_w = SIZE // 3
            if nfo["peek_side"] == "right":
                p.setClipRect(QRect(SIZE//2 - peek_w, -SIZE, peek_w, SIZE * 2))
            else:
                p.setClipRect(QRect(-SIZE//2, -SIZE, peek_w, SIZE * 2))

        self._draw_lupin(p, nfo, t_global)
        p.restore()

        # 5a. Icona trasportata (carrying) – replica visiva sopra la testa
        if nfo.get("is_carrying") and nfo.get("carry_icon_pos"):
            cx_i, cy_i = nfo["carry_icon_pos"]
            icon_name = nfo.get("carry_icon_name", "")
            sway = math.sin(t_global * 0.18) * 6
            bob  = math.sin(t_global * 0.22) * 3
            ix = int(cx_i + sway)
            iy = int(cy_i + bob)
            p.save()
            p.translate(ix, iy)
            # Alone luminoso pulsante
            glow_r = 46 + math.sin(t_global * 0.14) * 6
            glow = QRadialGradient(0, 0, glow_r)
            glow.setColorAt(0, QColor(255, 220, 60, 120))
            glow.setColorAt(1, QColor(255, 220, 60, 0))
            p.setBrush(QBrush(glow)); p.setPen(Qt.NoPen)
            p.drawEllipse(int(-glow_r), int(-glow_r), int(glow_r*2), int(glow_r*2))
            # Ombra riquadro
            p.setBrush(QBrush(QColor(0, 0, 0, 50)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(-27, -27, 60, 60, 12, 12)
            # Riquadro icona
            p.setBrush(QBrush(QColor(255, 252, 215, 240)))
            p.setPen(QPen(QColor(200, 160, 30), 2))
            p.drawRoundedRect(-30, -30, 60, 60, 12, 12)
            # Emoji: determina tipo in base al nome (folder se non riconosciuto)
            name_lower = icon_name.lower()
            if any(k in name_lower for k in ("python", ".py")): emoji = "🐍"
            elif any(k in name_lower for k in ("chrome", "browser", "edge", "firefox")): emoji = "🌐"
            elif any(k in name_lower for k in ("music", "spotify", "audio", "mp3")): emoji = "🎵"
            elif any(k in name_lower for k in ("foto", "photo", "image", "img", ".jpg", ".png")): emoji = "🖼️"
            elif any(k in name_lower for k in ("video", ".mp4", ".avi", "vlc")): emoji = "🎬"
            elif any(k in name_lower for k in ("doc", "word", ".docx", ".pdf", "text")): emoji = "📄"
            elif any(k in name_lower for k in ("trash", "recycle", "cestino")): emoji = "🗑️"
            elif any(k in name_lower for k in ("game", "steam", "epic")): emoji = "🎮"
            elif any(k in name_lower for k in (".exe", "setup", "install")): emoji = "⚙️"
            else: emoji = "📁"
            p.setFont(QFont("Segoe UI Emoji", 26))
            p.setPen(QColor(60, 40, 0))
            p.drawText(QRect(-28, -30, 56, 56), Qt.AlignCenter, emoji)
            # Nome icona sotto il riquadro
            if icon_name:
                label = icon_name if len(icon_name) <= 16 else icon_name[:14] + "…"
                # Sfondo etichetta
                p.setFont(QFont("Segoe UI", 8, QFont.Bold))
                fm = p.fontMetrics()
                lw = fm.horizontalAdvance(label) + 10
                p.setPen(Qt.NoPen)
                p.setBrush(QBrush(QColor(0, 0, 0, 140)))
                p.drawRoundedRect(-lw//2, 34, lw, 18, 5, 5)
                # Testo
                p.setPen(QPen(QColor(255, 255, 255)))
                p.drawText(QRect(-lw//2, 34, lw, 18), Qt.AlignCenter, label)
            p.restore()

        # 5b. Sitting: disegna l'icona sotto di lui (piano)
        if nfo.get("is_sitting") and nfo.get("sit_target"):
            sx, sy = nfo["sit_target"]
            p.save()
            p.translate(int(sx), int(sy))
            p.setBrush(QBrush(QColor(255, 240, 200, 180)))
            p.setPen(QPen(QColor(180, 140, 40), 2))
            p.drawRoundedRect(-24, -24, 48, 48, 10, 10)
            p.setFont(QFont("Segoe UI Emoji", 22))
            p.setPen(QColor(80, 60, 0))
            p.drawText(-14, 13, "📁")
            p.restore()

        # 5c. Pushing: freccia direzionale davanti all'icona spinta
        if nfo.get("is_pushing") and nfo.get("push_dir"):
            dx_p, dy_p = nfo["push_dir"]
            # L'icona spinta è davanti a Lupin
            arrow_x = int(px + dx_p * 60)
            arrow_y = int(draw_y + dy_p * 60)
            p.save()
            p.translate(arrow_x, arrow_y)
            p.rotate(math.degrees(math.atan2(dy_p, dx_p)))
            p.setPen(QPen(QColor(255, 100, 50, 180), 3))
            p.drawLine(0, 0, 28, 0)
            p.drawLine(22, -6, 28, 0);  p.drawLine(22, 6, 28, 0)
            p.restore()

        # 5. Sack
        if nfo["sack_count"] > 0:
            self._draw_sack(p, px, draw_y, nfo, t_global)

        # 5d. Volume trick: barra volume visiva
        if nfo.get("is_volume_trick") and t > 30:
            self._draw_volume_bar(p, nfo["volume_presses"], t)

        # 6. Speech bubble
        if self.speech_scale > 0.05 and self.speech_text:
            flip = nfo["direction"]
            bx = px + (80 if flip > 0 else -80)
            self._draw_bubble(p, bx, draw_y - 55, self.speech_text, self.speech_scale)

        # 7. Combo
        if self.combo > 2 and self.brain.timer - self.last_steal_t < 70:
            sc = 1.0 + math.sin(t_global * 0.35) * 0.18
            p.save();  p.translate(px, draw_y - SIZE - 30);  p.scale(sc, sc)
            p.setFont(QFont("Arial Black", 15, QFont.Bold))
            p.setPen(QPen(QColor(255, 30, 30), 3))
            p.drawText(QRect(-60, -16, 120, 32), Qt.AlignCenter, f"COMBO ×{self.combo}!")
            p.restore()

        # 8. Flash
        if self.flash_a > 0:
            from PyQt5.QtGui import QRadialGradient as RG
            g = RG(px, draw_y, 320)
            g.setColorAt(0, QColor(255, 255, 200, self.flash_a))
            g.setColorAt(1, QColor(255, 255, 255, 0))
            p.fillRect(0, 0, self.sw, self.sh, QBrush(g))

        # 9. Toasts
        self._draw_toasts(p)

        # 10. HUD mini
        self._draw_hud(p, nfo)

        p.end()

    # ── Lupin character drawing ───────────────────────────────

    def _draw_lupin(self, p, nfo, t):
        state  = nfo["state"]
        flip   = nfo["direction"]
        phase  = nfo["dance_phase"]
        timer  = nfo["timer"]

        # Respirazione idle
        breath = math.sin(t * 0.055) * 2

        # ── Gambe ────────────────────────────────────────────
        run_anim      = state in (S.RUNNING, S.APPROACHING, S.FOLLOWING)
        dance_anim    = state == S.DANCING
        push_anim     = state == S.PUSHING
        sit_anim      = state == S.SITTING
        exhaust_anim  = state == S.EXHAUSTED

        leg_swing = (math.sin(t * (0.30 if state == S.RUNNING else 0.20)) * 18 if run_anim else
                     math.sin(phase * 1.2) * 12 if dance_anim else
                     math.sin(t * 0.28) * 14 if push_anim else 0)

        if exhaust_anim:
            # Gambe piegate, accasciato — respiro rapido
            exhaust_bob = math.sin(t * 0.22) * 4  # oscillazione stanchezza
            p.setPen(QPen(PANTS_COLOR, 9, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(-10, 22, int(-26 + exhaust_bob), int(48))
            p.drawLine( 10, 22, int( 26 - exhaust_bob), int(48))
            p.setBrush(QBrush(SHOE_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(int(-34 + exhaust_bob), 45, 18, 8)
            p.drawEllipse(int( 18 - exhaust_bob), 45, 18, 8)
        elif sit_anim:
            # Gambe distese in avanti (seduto)
            rock = math.sin(t * 0.06) * 4
            p.setPen(QPen(PANTS_COLOR, 9, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(-10, 22, int(-32 + rock), 45)
            p.drawLine( 10, 22, int( 32 - rock), 45)
            p.setBrush(QBrush(SHOE_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(int(-42 + rock), 43, 20, 8)
            p.drawEllipse(int( 24 - rock), 43, 20, 8)
        else:
            p.setPen(QPen(PANTS_COLOR, 9, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(-10, 22, int(-13 - leg_swing), 52)
            p.drawLine( 10, 22, int( 13 + leg_swing), 52)
            p.setBrush(QBrush(SHOE_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(int(-22 - leg_swing), 50, 22, 9)
            p.drawEllipse(int(  3 + leg_swing), 50, 22, 9)

        # ── Corpo / giacca rossa ─────────────────────────────
        jacket_g = QLinearGradient(-22, -30, 22, 25)
        jacket_g.setColorAt(0, BODY_COLOR.lighter(125))
        jacket_g.setColorAt(1, BODY_COLOR.darker(120))

        body_path = QPainterPath()
        body_path.moveTo(-21, -28)
        body_path.lineTo( 21, -28)
        body_path.cubicTo(23, 0, 23, 20, 22, 25)
        body_path.lineTo(-22, 25)
        body_path.cubicTo(-23, 20, -23, 0, -21, -28)
        p.setBrush(QBrush(jacket_g));  p.setPen(QPen(OUTLINE, 1.5))
        p.drawPath(body_path)

        # Risvolti della giacca (V-shape bianco)
        collar_path = QPainterPath()
        collar_path.moveTo(-9, -26)
        collar_path.lineTo( 0, -12)
        collar_path.lineTo( 9, -26)
        p.setBrush(QBrush(SHIRT_COLOR));  p.setPen(Qt.NoPen)
        p.drawPath(collar_path)

        # Cravatta
        tie_path = QPainterPath()
        tie_path.moveTo(-4, -18);  tie_path.lineTo(4, -18)
        tie_path.lineTo(3, 2);     tie_path.lineTo(0, 8)
        tie_path.lineTo(-3, 2)
        p.setBrush(QBrush(TIE_COLOR))
        p.drawPath(tie_path)

        # Bottoni giacca
        p.setBrush(QBrush(QColor(255, 215, 0)))
        for by in [5, 14]:
            p.drawEllipse(-2, by, 4, 4)

        # ── Braccia ── (save/restore per isolare pen/brush) ──
        p.save()
        arm_g = QColor(BODY_COLOR.red()-15, BODY_COLOR.green(), BODY_COLOR.blue())
        pen_arm = QPen(arm_g, 8, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen_arm);  p.setBrush(Qt.NoBrush)

        if state == S.WAVING:
            wave_a = math.sin(t * 0.30) * 22
            p.drawLine(19, -20, 44, int(-45 + wave_a))   # braccio attivo su
            p.drawLine(-19, -20, -30, 8)                  # altro giù
            # Mano
            p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(38, int(-52 + wave_a), 12, 12)

        elif state == S.DANCING:
            da = math.sin(phase) * 20
            p.drawLine(-19, -18, int(-42), int(-20 + da))
            p.drawLine( 19, -18, int( 42), int(-20 - da))

        elif state == S.SLEEPING:
            p.drawLine(-19, -15, -28, 18)
            p.drawLine( 19, -15,  28, 18)

        elif state == S.CELEBRATING:
            bounce = math.sin(t * 0.4) * 10
            p.drawLine(-19, -20, -42, int(-48 + bounce))
            p.drawLine( 19, -20,  42, int(-48 - bounce))

        elif state in (S.TAUNTING, S.PRANK):
            tilt = math.sin(t * 0.15) * 10
            p.drawLine(-19, -18, -35, int(8 + tilt))
            p.drawLine( 19, -18,  35, int(8 - tilt))

        elif state == S.RUNNING:
            ra = math.sin(t * 0.30) * 24
            p.drawLine(-19, -18, int(-38 + ra), int(-5))
            p.drawLine( 19, -18, int( 38 - ra), int(12))

        elif state == S.CURIOUS:
            # Mano al mento
            p.drawLine(-19, -18, -30, 5)
            p.drawLine( 19, -18,  38, -5)
            # Mano al mento (destra)
            p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(32, -11, 11, 11)

        elif state == S.HANGING:
            ha = math.sin(timer * 0.2) * 6
            p.drawLine(-19, -20, int(-38), int(-55 + ha))
            p.drawLine( 19, -20, int( 38), int(-55 - ha))

        elif state == S.PUSHING:
            # Braccia estese in avanti nella direzione di spinta
            dx = nfo.get("push_dir", (1, 0))[0]
            ext = 1 if dx >= 0 else -1
            lean = math.sin(timer * 0.22) * 4
            p.drawLine(-19, -18, int(-19 + ext * 40), int(-5 + lean))
            p.drawLine( 19, -18, int( 19 + ext * 40), int(-5 - lean))
            # Mani
            p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(int(-19 + ext * 34), int(-11 + lean), 11, 11)
            p.drawEllipse(int( 19 + ext * 34), int(-11 - lean), 11, 11)

        elif state == S.CARRYING:
            # Braccia alzate a sorreggere l'icona sopra la testa
            sway = math.sin(timer * 0.18) * 8
            p.drawLine(-19, -20, int(-32 + sway), -60)
            p.drawLine( 19, -20, int( 32 + sway), -60)
            # Mani aperte
            p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(int(-38 + sway), -66, 12, 12)
            p.drawEllipse(int( 26 + sway), -66, 12, 12)

        elif state == S.SITTING:
            rock = math.sin(timer * 0.06) * 5
            p.drawLine(-19, -15, -38, int(5 + rock))
            p.drawLine( 19, -15,  38, int(5 - rock))

        elif state == S.EXHAUSTED:
            exhaust_bob = math.sin(timer * 0.22) * 4
            p.drawLine(-19, -8, int(-24 + exhaust_bob), int(30))
            p.drawLine( 19, -8, int( 24 - exhaust_bob), int(30))
            p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(int(-30 + exhaust_bob), 26, 11, 11)
            p.drawEllipse(int( 18 - exhaust_bob), 26, 11, 11)

        elif state == S.VOLUME_TRICK:
            vol_wave = math.sin(timer * 0.25) * 10
            p.drawLine( 19, -22,  48, int(-48 + vol_wave))
            p.drawLine(-19, -18, -26, 12)
            p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(42, int(-55 + vol_wave), 12, 12)

        elif state == S.DRINKING:
            # Braccio destro alzato con bottiglia
            drink_prog = min(timer / 80.0, 1.0)  # 0→1 mentre beve
            arm_y = int(-20 - drink_prog * 22)    # braccio sale
            p.drawLine( 19, -18,  44, arm_y)
            p.drawLine(-19, -18, -28, 14)
            p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
            p.drawEllipse(38, arm_y - 8, 12, 12)
            # Bottiglia di birra 🍺 in mano
            p.setFont(QFont("Segoe UI Emoji", 18))
            p.setPen(Qt.NoPen)
            p.drawText(35, arm_y - 14, "🍺")

        elif state == S.LEANING:
            # Un braccio alzato contro il muro, l'altro rilassato
            lean = nfo.get("lean_side", "right")
            wall = math.sin(timer * 0.04) * 3   # micro-dondolio
            if lean == "right":
                # muro a destra: braccio destro alzato
                p.drawLine( 19, -22,  45, int(-40 + wall))
                p.drawLine(-19, -18, -28, int(10 + wall))
                p.setBrush(QBrush(SKIN_COLOR)); p.setPen(QPen(OUTLINE,1))
                p.drawEllipse(39, int(-47+wall), 12, 12)
            else:
                # muro a sinistra: braccio sinistro alzato
                p.drawLine(-19, -22, -45, int(-40 + wall))
                p.drawLine( 19, -18,  28, int(10 + wall))
                p.setBrush(QBrush(SKIN_COLOR)); p.setPen(QPen(OUTLINE,1))
                p.drawEllipse(-51, int(-47+wall), 12, 12)

        elif state == S.CORNER:
            # Braccia conserte / rilassate in angolo
            cross = math.sin(timer * 0.05) * 4
            p.drawLine(-19, -18, -10, int(-5 + cross))
            p.drawLine( 19, -18,  10, int(-5 - cross))
            # mani incrociate sul petto
            p.setBrush(QBrush(SKIN_COLOR)); p.setPen(QPen(OUTLINE,1))
            p.drawEllipse(-14, int(-8+cross), 10, 10)
            p.drawEllipse(  4, int(-8-cross), 10, 10)

        elif state == S.SURRENDER:
            p.drawLine(-19, -18, -25, 22)
            p.drawLine( 19, -18,  25, 22)

        else:
            bd = breath
            p.drawLine(-19, -18, -28, int(16 + bd))
            p.drawLine( 19, -18,  28, int(16 + bd))

        p.restore()   # fine sezione braccia — pen/brush resettati

        # ── Testa ────────────────────────────────────────────
        bob = math.sin(t * 0.10) * 2 + breath * 0.5
        head_tilt = 0.0
        if state == S.DRINKING:
            drink_prog = min(timer / 80.0, 1.0)
            head_tilt = drink_prog * 28
        hy = int(-58 + bob)

        # Collo + eventuale tilt testa (save sempre, rotate opzionale)
        p.save()
        if head_tilt != 0.0:
            p.translate(0, -44)
            p.rotate(head_tilt)
            p.translate(0, 44)
        p.setBrush(QBrush(SKIN_COLOR));  p.setPen(QPen(OUTLINE, 1))
        p.drawRect(-6, -44, 12, 17)

        # Viso
        face_g = QRadialGradient(-4, hy - 10, 30)
        face_g.setColorAt(0, SKIN_COLOR.lighter(108))
        face_g.setColorAt(1, SKIN_COLOR.darker(115))
        p.setBrush(QBrush(face_g));  p.setPen(QPen(OUTLINE, 1.5))
        p.drawEllipse(-26, hy - 24, 52, 46)

        # Capelli
        hair_path = QPainterPath()
        hair_path.moveTo(-26, hy - 8)
        hair_path.cubicTo(-32, hy - 45, -5, hy - 52, 10, hy - 40)
        hair_path.cubicTo(24, hy - 28, 26, hy - 12, 26, hy - 8)
        hair_path.cubicTo(16, hy - 40, -10, hy - 42, -26, hy - 8)
        p.setBrush(QBrush(HAIR_COLOR));  p.setPen(Qt.NoPen)
        p.drawPath(hair_path)

        # ── Cappello ─────────────────────────────────────────
        hat_y = hy - 26
        p.setBrush(QBrush(HAT_COLOR));  p.setPen(QPen(OUTLINE, 1.5))
        p.drawEllipse(-30, hat_y + 8, 60, 13)         # tesa
        p.drawRect(-19, hat_y - 18, 38, 28)            # corpo
        p.setBrush(QBrush(HATBAND_CLR));  p.setPen(Qt.NoPen)
        p.drawRect(-19, hat_y + 6, 38, 5)              # banda
        # Fiocco
        p.setBrush(QBrush(QColor(200, 200, 200)))
        p.drawEllipse(10, hat_y + 5, 8, 8)

        # ── Occhi ────────────────────────────────────────────
        ey = hy - 6    # y centro occhi

        exhausted_eyes = state == S.EXHAUSTED
        closed = (self.eye_state == "closed" or state == S.SLEEPING)
        happy  = state in (S.TAUNTING, S.DANCING, S.CELEBRATING, S.WAVING)
        sad    = state == S.SURRENDER
        smug   = state in (S.TAUNTING, S.PRANK) and timer > 10

        if exhausted_eyes:
            # Occhi mezzi chiusi droopy + sopracciglia tristi
            p.setPen(QPen(QColor(80, 50, 30), 2.5))
            p.setBrush(Qt.NoBrush)
            # Metà cerchio in basso = occhi pesanti
            p.drawArc(-20, ey, 14, 10, 0 * 16,  180 * 16)  # occhio sin
            p.drawArc(  6, ey, 14, 10, 0 * 16,  180 * 16)  # occhio des
            # Sopracciglia cadenti (stanchezza)
            p.setPen(QPen(HAIR_COLOR, 2.5, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(-22, ey - 5, -8, ey - 1)
            p.drawLine(  6, ey - 1, 20, ey - 5)
        elif closed:
            p.setPen(QPen(QColor(80, 50, 30), 2.5))
            p.setBrush(Qt.NoBrush)
            p.drawArc(-20, ey + 2, 14, 7, 0,  180 * 16)
            p.drawArc(  6, ey + 2, 14, 7, 0,  180 * 16)
        elif happy:
            p.setPen(QPen(QColor(80, 50, 30), 2.5))
            p.setBrush(Qt.NoBrush)
            p.drawArc(-20, ey, 14, 9, 180 * 16, 180 * 16)   # ^ occhi
            p.drawArc(  6, ey, 14, 9, 180 * 16, 180 * 16)
        elif sad:
            p.setBrush(QBrush(Qt.white));  p.setPen(QPen(OUTLINE, 1.2))
            p.drawEllipse(-22, ey - 2, 16, 14);  p.drawEllipse(6, ey - 2, 16, 14)
            p.setBrush(QBrush(QColor(30, 20, 15)));  p.setPen(Qt.NoPen)
            p.drawEllipse(-17, ey + 2, 6, 6);  p.drawEllipse(11, ey + 2, 6, 6)
            # sopracciglia tristi (no lacrime)
            p.setPen(QPen(HAIR_COLOR, 2.5, Qt.SolidLine, Qt.RoundCap))
            p.drawLine(-22, ey - 4, -8, ey - 7)
            p.drawLine(  6, ey - 7, 20, ey - 4)
        else:
            # Occhi normali
            p.setBrush(QBrush(Qt.white));  p.setPen(QPen(OUTLINE, 1.2))
            p.drawEllipse(-22, ey - 2, 16, 15);  p.drawEllipse(6, ey - 2, 16, 15)

            # Pupille con tracking cursore
            px_off = py_off = 0.0
            if self.cursor_att > 0.1:
                cx, cy = win32api.GetCursorPos()
                dx = (cx - nfo["x"]) * flip
                dy = cy - nfo["y"]
                d = math.hypot(dx, dy) or 1
                px_off = dx / d * 3 * self.cursor_att
                py_off = dy / d * 2.5 * self.cursor_att

            p.setBrush(QBrush(QColor(25, 18, 12)));  p.setPen(Qt.NoPen)
            p.drawEllipse(int(-17 + px_off), int(ey + 2 + py_off), 8, 8)
            p.drawEllipse(int( 11 + px_off), int(ey + 2 + py_off), 8, 8)
            # Lucide
            p.setBrush(QBrush(QColor(255, 255, 255, 210)))
            p.drawEllipse(int(-15 + px_off), int(ey + 2 + py_off), 3, 3)
            p.drawEllipse(int( 13 + px_off), int(ey + 2 + py_off), 3, 3)

            # Sopracciglia espressive
            p.setPen(QPen(HAIR_COLOR, 2.5, Qt.SolidLine, Qt.RoundCap))
            if smug:
                p.drawLine(-22, ey - 4,  -8, ey - 2)   # sopr. smug
                p.drawLine(  6, ey - 2,  20, ey - 4)
            elif state == S.RUNNING:
                p.drawLine(-22, ey - 3,  -8, ey - 6)
                p.drawLine(  6, ey - 6,  20, ey - 3)
            else:
                p.drawLine(-22, ey - 4,  -8, ey - 4)
                p.drawLine(  6, ey - 4,  20, ey - 4)

        # ── Naso ─────────────────────────────────────────────
        p.setPen(QPen(QColor(190, 130, 85), 1.8))
        p.setBrush(Qt.NoBrush)
        p.drawArc(-4, ey + 8, 8, 6, 0, -180 * 16)

        # ── Bocca ─────────────────────────────────────────────
        my = ey + 17
        p.setPen(QPen(QColor(150, 60, 55), 2))
        p.setBrush(Qt.NoBrush)

        tongue_out = nfo.get("tongue_timer", 0) > 0

        if state == S.EXHAUSTED:
            pant = abs(math.sin(timer * 0.22)) * 6
            p.setBrush(QBrush(QColor(60, 30, 30)))
            p.setPen(QPen(QColor(150, 60, 55), 1.5))
            p.drawEllipse(-8, my, 16, int(6 + pant))
            p.setBrush(QBrush(QColor(255, 100, 100)));  p.setPen(Qt.NoPen)
            p.drawEllipse(-4, my + 2, 8, int(5 + pant * 0.5))
        elif tongue_out:
            # Linguaccia! Bocca aperta + lingua lunga che pende
            p.setBrush(QBrush(QColor(60, 30, 30)))
            p.setPen(QPen(QColor(150, 60, 55), 1.5))
            p.drawArc(-12, my, 24, 12, 0, -180 * 16)
            tongue_len = int(10 + abs(math.sin(timer * 0.25)) * 6)
            tongue_path = QPainterPath()
            tongue_path.moveTo(-6, my + 6)
            tongue_path.lineTo( 6, my + 6)
            tongue_path.lineTo( 5, my + 6 + tongue_len)
            tongue_path.cubicTo(5, my+6+tongue_len+6, -5, my+6+tongue_len+6,
                                -5, my+6+tongue_len)
            tongue_path.lineTo(-6, my + 6)
            p.setBrush(QBrush(QColor(255, 80, 100)));  p.setPen(Qt.NoPen)
            p.drawPath(tongue_path)
        elif state in (S.TAUNTING, S.PRANK):
            # Grin + lingua
            p.drawArc(-13, my, 26, 13, 0, -180 * 16)
            p.setBrush(QBrush(QColor(255, 100, 100)));  p.setPen(Qt.NoPen)
            tongue_path = QPainterPath()
            tongue_path.addEllipse(-7, my + 6, 14, 10)
            p.drawPath(tongue_path)
        elif state == S.SURRENDER:
            p.drawArc(-10, my + 4, 20, 10, 0, 180 * 16)
        elif state in (S.CELEBRATING, S.WAVING, S.DANCING):
            p.drawArc(-13, my, 26, 14, 0, -180 * 16)
            # Denti
            p.setBrush(QBrush(QColor(255, 255, 240)))
            p.setPen(Qt.NoPen)
            p.drawRect(-10, my + 1, 20, 7)
        elif state == S.CURIOUS:
            # O di sorpresa
            p.setBrush(QBrush(QColor(60, 30, 30)))
            p.drawEllipse(-5, my + 1, 10, 9)
        else:
            p.drawArc(-9, my + 2, 18, 9, 0, -180 * 16)

        # ── Maschera da ladro (APPROACHING / STEALING) ───────
        if state in (S.APPROACHING, S.STEALING):
            # Striscia nera sugli occhi, arrotondata
            mask_path = QPainterPath()
            mask_path.addRoundedRect(-26, ey - 5, 52, 16, 5, 5)
            p.setBrush(QBrush(QColor(10, 10, 10, 230)))
            p.setPen(QPen(QColor(50, 50, 50), 1))
            p.drawPath(mask_path)
            # Fori bianchi per gli occhi — stile cartoon
            p.setBrush(QBrush(QColor(255, 255, 255)))
            p.setPen(Qt.NoPen)
            p.drawEllipse(-19, ey - 2, 12, 10)
            p.drawEllipse(  7, ey - 2, 12, 10)
            # Pupille
            p.setBrush(QBrush(QColor(20, 15, 10)))
            p.drawEllipse(-16, ey, 7, 7)
            p.drawEllipse(  10, ey, 7, 7)

        # ── Guance rosse ─────────────────────────────────────
        if state in (S.CELEBRATING, S.WAVING, S.DANCING, S.CURIOUS, S.DRINKING):
            ba = int(90 + 30 * math.sin(t * 0.09))
            p.setBrush(QBrush(QColor(255, 150, 150, ba)));  p.setPen(Qt.NoPen)
            p.drawEllipse(-26, ey + 9, 12, 7)
            p.drawEllipse(14,  ey + 9, 12, 7)

        p.restore()   # fine sezione testa

    # ── Refurtino orbitante ───────────────────────────────────

    LOOT_ICONS = ["👑", "💎", "🏅", "✨", "🪙", "💍"]

    def _draw_sack(self, p, px, py, nfo, t):
        count = nfo["sack_count"]
        # Orbita: ogni oggetto ruota attorno a Lupin a raggio crescente
        for i in range(count):
            icon = self.LOOT_ICONS[i % len(self.LOOT_ICONS)]
            speed  = 0.028 + i * 0.005
            radius = 55 + (i % 3) * 20
            angle  = t * speed + i * (2 * math.pi / max(count, 1))
            ix = int(px + math.cos(angle) * radius)
            iy = int(py - 30 + math.sin(angle) * radius * 0.45)
            # Scintilla sotto l'oggetto
            glow_r = QRadialGradient(ix, iy, 22)
            glow_r.setColorAt(0, QColor(255, 215, 0, 90 + int(50 * math.sin(t * 0.1 + i))))
            glow_r.setColorAt(1, QColor(255, 215, 0, 0))
            p.setBrush(QBrush(glow_r));  p.setPen(Qt.NoPen)
            p.drawEllipse(ix - 22, iy - 22, 44, 44)
            # Emoji
            p.setFont(QFont("Segoe UI Emoji", 16 + (i % 2) * 4))
            p.setPen(Qt.NoPen)
            p.drawText(ix - 12, iy + 10, icon)
        # Contatore in alto a destra
        p.setFont(QFont("Arial Black", 11, QFont.Bold))
        p.setPen(QPen(QColor(30, 20, 0), 3))
        p.drawText(int(px + 46), int(py - 65), f"×{count}")
        p.setPen(QColor(255, 215, 0))
        p.drawText(int(px + 45), int(py - 66), f"×{count}")

    # ── Volume bar ───────────────────────────────────────────

    def _draw_volume_bar(self, p, presses, t):
        """Disegna una barra del volume animata al centro-alto schermo."""
        bw, bh = 220, 48
        bx = self.sw // 2 - bw // 2
        by = 30
        pulse = 1.0 + math.sin(t * 0.30) * 0.06
        fill_frac = min(presses / 15.0, 1.0)

        p.setOpacity(0.88)
        # Sfondo
        bg = QPainterPath();  bg.addRoundedRect(bx, by, bw, bh, 10, 10)
        p.fillPath(bg, QBrush(QColor(28, 28, 28, 220)))
        p.setPen(QPen(QColor(255, 215, 0, 180), 1.5));  p.drawPath(bg)

        # Testo icona
        p.setFont(QFont("Segoe UI Emoji", 16))
        p.setPen(QColor(255, 255, 255, 220))
        p.drawText(bx + 8, by + 32, "🔊")

        # Barra riempimento
        fill_w = int((bw - 54) * fill_frac * pulse)
        fill_rect = QPainterPath()
        fill_rect.addRoundedRect(bx + 44, by + 12, fill_w, bh - 24, 5, 5)
        fill_g = QLinearGradient(bx + 44, 0, bx + 44 + fill_w, 0)
        fill_g.setColorAt(0, QColor(100, 220, 100))
        fill_g.setColorAt(0.7, QColor(255, 200, 50))
        fill_g.setColorAt(1.0, QColor(255, 60, 60))
        p.fillPath(fill_rect, QBrush(fill_g))

        # Bordo interno barra
        bar_bg = QPainterPath()
        bar_bg.addRoundedRect(bx + 44, by + 12, bw - 54, bh - 24, 5, 5)
        p.setPen(QPen(QColor(80, 80, 80, 160), 1));  p.drawPath(bar_bg)

        p.setOpacity(1.0)

    # ── Portal / buco nero ───────────────────────────────────

    def _draw_portal(self, p, portal):
        r  = portal.radius
        cx, cy = int(portal.x), int(portal.y) + 45   # a livello dei piedi
        alpha = int(255 * portal.life)
        p.save()
        p.setOpacity(portal.life * 0.92)
        p.translate(cx, cy)

        # Alone esterno viola/blu che pulsa
        for i, (col, scale) in enumerate([
            (QColor(80, 0, 140, 60),  2.2),
            (QColor(120, 0, 200, 90), 1.7),
            (QColor(40,  0,  80, 120), 1.35),
        ]):
            rg = QRadialGradient(0, 0, int(r * scale))
            rg.setColorAt(0,   col)
            rg.setColorAt(1,   QColor(0, 0, 0, 0))
            p.setBrush(QBrush(rg));  p.setPen(Qt.NoPen)
            p.drawEllipse(int(-r*scale), int(-r*scale*0.45),
                          int(r*scale*2), int(r*scale*0.9))

        # Nucleo nero centrale
        core_g = QRadialGradient(0, 0, int(r))
        core_g.setColorAt(0,   QColor(0, 0, 0, alpha))
        core_g.setColorAt(0.7, QColor(5, 0, 20, alpha))
        core_g.setColorAt(1,   QColor(60, 0, 120, 0))
        p.setBrush(QBrush(core_g));  p.setPen(Qt.NoPen)
        p.drawEllipse(int(-r), int(-r*0.42), int(r*2), int(r*0.84))

        # Bordi vorticosi: linee curte che ruotano
        p.setPen(QPen(QColor(160, 80, 255, int(200 * portal.life)), 2))
        num_arms = 8
        for i in range(num_arms):
            ang = math.radians(portal.angle + i * (360 / num_arms))
            r_in  = r * 0.55
            r_out = r * 0.95
            p.drawLine(
                int(math.cos(ang) * r_in),  int(math.sin(ang) * r_in  * 0.42),
                int(math.cos(ang) * r_out), int(math.sin(ang) * r_out * 0.42))

        # Scintille orbit
        p.setPen(Qt.NoPen)
        for i in range(6):
            ang = math.radians(portal.angle * 2.5 + i * 60)
            sx = math.cos(ang) * r * 1.05
            sy = math.sin(ang) * r * 0.45
            spark_c = QColor(200, 120, 255, int(180 * portal.life))
            p.setBrush(QBrush(spark_c))
            p.drawEllipse(int(sx)-3, int(sy)-3, 6, 6)

        p.restore()

    # ── Speech bubble ─────────────────────────────────────────

    def _draw_bubble(self, p, cx, cy, text, scale):
        bw, bh = 270, 62
        bx, by = -bw // 2, -bh - 15
        p.save()
        p.translate(cx, cy)
        p.scale(scale, scale)
        # Shadow
        for i in range(3):
            sp = QPainterPath()
            sp.addRoundedRect(bx + 2 + i, by + 2 + i, bw, bh, 12, 12)
            p.fillPath(sp, QBrush(QColor(0, 0, 0, 12)))
        # Fill
        g = QLinearGradient(0, by, 0, by + bh)
        g.setColorAt(0, QColor(255, 255, 252));  g.setColorAt(1, QColor(255, 248, 215))
        path = QPainterPath();  path.addRoundedRect(bx, by, bw, bh, 12, 12)
        p.fillPath(path, QBrush(g))
        p.setPen(QPen(QColor(120, 120, 120), 2));  p.drawPath(path)
        # Tail
        tail = [QPoint(-9, by + bh), QPoint(9, by + bh), QPoint(-14, by + bh + 14)]
        p.setBrush(QBrush(QColor(255, 248, 215)));  p.setPen(QPen(QColor(120, 120, 120), 2))
        p.drawPolygon(*tail)
        # Text
        p.setFont(QFont("Segoe UI", 10, QFont.Bold))
        p.setPen(QColor(200, 200, 200))
        p.drawText(QRect(bx + 11, by + 9, bw - 20, bh - 14), Qt.AlignCenter | Qt.TextWordWrap, text)
        p.setPen(QColor(30, 30, 30))
        p.drawText(QRect(bx + 10, by + 8, bw - 20, bh - 14), Qt.AlignCenter | Qt.TextWordWrap, text)
        p.restore()

    # ── Particles paint ───────────────────────────────────────

    def _paint_particles(self, p):
        for part in self.particles:
            p.setOpacity(part.life * 0.88)
            c = QColor(part.color)
            c.setAlpha(int(255 * part.life))
            p.save()
            p.translate(part.x, part.y)
            pt = part.type
            if pt == "sparkle" or pt == "star":
                p.rotate(part.rotation)
                p.setBrush(QBrush(c));  p.setPen(Qt.NoPen)
                s = part.size
                p.drawRect(int(-s//2), -1, int(s), 2)
                p.drawRect(-1, int(-s//2), 2, int(s))
            elif pt == "heart":
                p.setFont(QFont("Segoe UI Emoji", max(8, int(part.size))))
                p.setPen(c);  p.drawText(-9, 9, "❤")
            elif pt == "note":
                p.setFont(QFont("Segoe UI Emoji", max(8, int(part.size))))
                p.setPen(c);  p.drawText(-7, 7, "♪")
            elif pt == "zzz":
                p.setFont(QFont("Arial", max(9, int(part.size)), QFont.Bold))
                p.setPen(c);  p.drawText(0, 0, "Z")
            elif pt == "confetti":
                p.rotate(part.rotation)
                p.setBrush(QBrush(c));  p.setPen(Qt.NoPen)
                p.drawRect(-4, -2, 8, 4)
            elif pt == "sweat":
                p.setBrush(QBrush(QColor(100, 180, 255, int(200 * part.life))))
                p.setPen(Qt.NoPen)
                path = QPainterPath()
                path.moveTo(0, -5);  path.cubicTo(-4, -1, -4, 4, 0, 6)
                path.cubicTo(4, 4, 4, -1, 0, -5)
                p.drawPath(path)
            elif pt == "emoji_pain":
                emoji = getattr(part, "_emoji", "💢")
                sz = max(12, int(part.size * part.life + 10))
                p.setFont(QFont("Segoe UI Emoji", sz))
                p.setPen(QColor(255, 60, 60, int(255 * part.life)))
                p.drawText(-sz // 2, sz // 2, emoji)
            elif pt in ("smoke", "dust"):
                p.setBrush(QBrush(c));  p.setPen(Qt.NoPen)
                r = int(part.size // 2)
                p.drawEllipse(-r, -r, r*2, r*2)
            else:
                p.setBrush(QBrush(c));  p.setPen(Qt.NoPen)
                r = int(part.size // 2)
                p.drawEllipse(-r, -r, r*2, r*2)
            p.restore()
        p.setOpacity(1.0)

    # ── Toasts ────────────────────────────────────────────────

    def _draw_toasts(self, p):
        for i, toast in enumerate(self.toasts):
            a = int(255 * min(toast.life * 3, 1.0))
            y = 30 + i * 54 - int(toast.y_off)
            x = self.sw - 320
            p.setOpacity(a / 255)
            bp = QPainterPath();  bp.addRoundedRect(x, y, 300, 42, 10, 10)
            p.fillPath(bp, QBrush(QColor(28, 28, 28, 230)))
            p.setPen(QPen(toast.color, 1.5));  p.drawPath(bp)
            p.setFont(QFont("Segoe UI", 11, QFont.Bold))
            p.setPen(QColor(255, 255, 255, a))
            p.drawText(QRect(x + 12, y + 4, 276, 34), Qt.AlignVCenter, toast.text)
        p.setOpacity(1.0)

    # ── HUD mini ──────────────────────────────────────────────

    def _draw_hud(self, p, nfo):
        pers = nfo["personality"]
        ei = {"aggressive": "😤", "playful": "🎮", "sneaky": "🥷"}.get(pers, "")
        p.setFont(QFont("Segoe UI Emoji", 11))
        p.setOpacity(0.45)
        p.setPen(QColor(255, 255, 255))
        p.drawText(14, self.sh - 14,
                   f"{ei} Lupin  ·  Furti: {nfo['total_steals']}  ·  Catturato: {nfo['times_caught']}  ·  [ESC] esci")
        p.setOpacity(1.0)

    # ── Input ─────────────────────────────────────────────────

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return

        prev_combo = self.brain.hit_combo
        self.brain.on_click()
        nfo = self.brain.info
        combo = nfo["hit_combo"]
        mx, my = e.x(), e.y()
        px, py = nfo["x"], nfo["y"]

        # ── Particelle colpo ─────────────────────────────────
        # Stelle/impact
        impact_count = 8 + combo * 6
        for _ in range(impact_count):
            self.particles.append(Particle(
                mx + random.randint(-12, 12),
                my + random.randint(-12, 12),
                QColor(255, random.randint(100, 220), 0), 7, ptype="star"))

        # Emoji dolore fluttuanti (tipo fumetto)
        pain_emojis = {1: "😮", 2: "😠", 3: "😡", 4: "🤬", 5: "💀"}
        emoji = pain_emojis.get(min(combo, 5), "💢")
        self.particles.append(Particle(
            px + random.randint(-20, 20), py - 60,
            QColor(255, 60, 60), 26,
            random.uniform(-1.5, 1.5), random.uniform(-4, -2), "emoji_pain"))
        # Salva l'emoji nel particle per usarla nel draw
        self.particles[-1]._emoji = emoji

        # Scintille colorate
        for _ in range(6):
            self.particles.append(Particle(
                mx, my,
                QColor(random.randint(200, 255), random.randint(50, 150), 50),
                5, ptype="sparkle"))

        # Combo alto: onde d'urto e più particelle
        if combo >= 3:
            for _ in range(10):
                ang = random.uniform(0, 6.28)
                spd = random.uniform(4, 9)
                self.particles.append(Particle(
                    px, py,
                    QColor(255, 80, 30), 8,
                    math.cos(ang) * spd, math.sin(ang) * spd - 3, "star"))
            self.shake_int = max(self.shake_int, 10 + combo * 3)

        if combo >= 5:
            self.flash_a = max(self.flash_a, 120)

        # ── Speech bubble reazione ───────────────────────────
        reaction = nfo.get("hit_reaction", "")
        if reaction and reaction != self._prev_hit_reaction:
            self._say(reaction, 200)
            self._prev_hit_reaction = reaction

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.hooks.restore_icons()
            self.close()

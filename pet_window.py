import os, sys, win32gui, win32con
import win32api, math, random
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import (QPainter, QColor, QFont, QBrush, QPen,
                         QPainterPath, QPixmap, QTransform, QCursor, QRadialGradient)

from desktop_hooks import DesktopHooks
from pet_brain import LupinBrain, S

SIZE = 90

class Particle:
    def __init__(self, x, y, color, size=4):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-6, -2)
        self.life = 1.0
        self.color = color
        self.size = size
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # gravity
        self.life -= 0.02
        return self.life > 0

class PetWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        scr = QApplication.primaryScreen().geometry()
        self.sw, self.sh = scr.width(), scr.height()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setGeometry(0, 0, self.sw, self.sh)

        self.hooks = DesktopHooks()
        self.hooks.save_positions()
        self.icons = self.hooks.get_all_positions()

        self.brain = LupinBrain(self.sw, self.sh, self.hooks)
        self.sprites = self._load_sprites()
        
        # Advanced UX
        self.particles = []
        self.shake_offset = (0, 0)
        self.shake_intensity = 0
        self.squash = 1.0  # squash/stretch animation
        self.rotation = 0
        self.trail_positions = []  # motion trail
        self.dust_timer = 0
        self.blink_timer = 0
        self.eye_state = "open"
        self.speech_bubble_scale = 0.0
        self.flash_alpha = 0

        self._icon_tick = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._loop)
        self.timer.start(16)
        self._set_passthrough(True)
        self.show()

    def _set_passthrough(self, on: bool):
        hwnd = int(self.winId())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if on:
            style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
        else:
            style &= ~win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

    def _load_sprites(self):
        mapping = {
            S.IDLE: ("idle", QColor(120, 160, 240)),
            S.APPROACHING: ("idle", QColor(120, 160, 240)),
            S.STEALING: ("stealing", QColor(220, 60, 60)),
            S.TAUNTING: ("taunting", QColor(50, 200, 80)),
            S.RUNNING: ("running", QColor(240, 140, 40)),
            S.HIDING: ("hiding", QColor(160, 160, 160)),
            S.SURRENDER: ("surrender", QColor(240, 220, 50)),
        }
        result = {}
        for state, (fname, color) in mapping.items():
            path = os.path.join("sprites", f"{fname}.png")
            if os.path.exists(path):
                px = QPixmap(path).scaled(SIZE, SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                px = self._placeholder(color)
            result[state] = px
        return result

    def _placeholder(self, color):
        px = QPixmap(SIZE, SIZE)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Corpo con gradiente
        grad = QRadialGradient(SIZE//2, SIZE//2 + 10, SIZE//2)
        grad.setColorAt(0, color.lighter(120))
        grad.setColorAt(1, color)
        p.setBrush(QBrush(grad))
        p.setPen(QPen(color.darker(150), 2))
        p.drawEllipse(15, 20, SIZE - 30, SIZE - 30)
        
        # Cappello Lupin con bordo
        p.setBrush(QBrush(QColor(30, 30, 30)))
        p.setPen(QPen(QColor(10, 10, 10), 1))
        p.drawRect(20, 5, SIZE - 40, 14)
        p.drawRect(28, 2, SIZE - 56, 8)
        
        # Occhi bianchi
        p.setBrush(QBrush(Qt.white))
        p.setPen(QPen(QColor(50, 50, 50), 1))
        p.drawEllipse(26, 28, 14, 14)
        p.drawEllipse(SIZE - 40, 28, 14, 14)
        
        # Pupille
        p.setBrush(QBrush(Qt.black))
        p.setPen(Qt.NoPen)
        p.drawEllipse(30, 32, 6, 6)
        p.drawEllipse(SIZE - 36, 32, 6, 6)
        
        # Riflessi negli occhi
        p.setBrush(QBrush(QColor(255, 255, 255, 180)))
        p.drawEllipse(32, 33, 3, 3)
        p.drawEllipse(SIZE - 34, 33, 3, 3)
        
        p.end()
        return px

    def _loop(self):
        self._icon_tick += 1
        if self._icon_tick >= 200:
            self.icons = self.hooks.get_all_positions()
            self._icon_tick = 0

        prev_x, prev_y = self.brain.x, self.brain.y
        prev_state = self.brain.state
        
        self.brain.update(self.icons)
        nfo = self.brain.info
        
        # Motion trail
        self.trail_positions.append((prev_x, prev_y))
        if len(self.trail_positions) > 8:
            self.trail_positions.pop(0)
        
        # Effetti dinamici per stato
        if nfo["state"] == S.STEALING and self.brain.timer == 25:
            # Esplosione particelle quando ruba
            for _ in range(20):
                self.particles.append(Particle(nfo["x"], nfo["y"], QColor(255, 215, 0)))
            self.shake_intensity = 8
            self.flash_alpha = 255
            
        if nfo["state"] == S.RUNNING:
            # Dust trail mentre corre
            self.dust_timer += 1
            if self.dust_timer % 3 == 0:
                self.particles.append(Particle(nfo["x"], nfo["y"] + 30, QColor(180, 180, 180, 150), 6))
            
            # Squash stretch in corsa
            speed = math.hypot(nfo["x"] - prev_x, nfo["y"] - prev_y)
            self.squash = 1.0 - min(speed * 0.02, 0.3)
            self.rotation = math.sin(self.brain.timer * 0.3) * 5
        else:
            self.squash = 1.0
            self.rotation = 0
            
        if nfo["state"] == S.TAUNTING:
            # Bubble pop-in animation
            self.speech_bubble_scale = min(self.speech_bubble_scale + 0.08, 1.0)
            # Screen shake quando taunts
            if self.brain.timer < 30:
                self.shake_intensity = 4
        else:
            self.speech_bubble_scale = 0.0
            
        if nfo["state"] == S.SURRENDER:
            # Particelle cuore quando si arrende
            if self.brain.timer % 10 == 0:
                self.particles.append(Particle(nfo["x"], nfo["y"] - 20, QColor(255, 100, 150)))
        
        # Blink casuale
        self.blink_timer += 1
        if self.blink_timer > random.randint(120, 300):
            self.eye_state = "closed"
            self.blink_timer = 0
        elif self.blink_timer > 4:
            self.eye_state = "open"
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Decay effects
        if self.shake_intensity > 0:
            self.shake_intensity *= 0.85
            self.shake_offset = (
                random.uniform(-self.shake_intensity, self.shake_intensity),
                random.uniform(-self.shake_intensity, self.shake_intensity)
            )
        else:
            self.shake_offset = (0, 0)
            
        self.flash_alpha = max(0, self.flash_alpha - 25)

        pet_rect = QRect(nfo["x"] - SIZE // 2, nfo["y"] - SIZE // 2, SIZE, SIZE)
        self._set_passthrough(not pet_rect.contains(QCursor.pos()))
        self.update()

    def paintEvent(self, _):
        nfo = self.brain.info
        px_int, py_int = nfo["x"], nfo["y"]

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Motion trail
        if nfo["state"] == S.RUNNING:
            for i, (tx, ty) in enumerate(self.trail_positions):
                alpha = int(30 * (i / len(self.trail_positions)))
                p.setOpacity(alpha / 255.0)
                trail_sprite = self.sprites[S.RUNNING]
                p.drawPixmap(int(tx - SIZE//2), int(ty - SIZE//2), trail_sprite)
            p.setOpacity(1.0)
        
        # Particles
        for particle in self.particles:
            p.setOpacity(particle.life)
            color = QColor(particle.color)
            color.setAlpha(int(255 * particle.life))
            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawEllipse(int(particle.x - particle.size//2), int(particle.y - particle.size//2), 
                         particle.size, particle.size)
        p.setOpacity(1.0)
        
        # Shadow
        shadow_y = py_int + SIZE // 2 + 5
        shadow = QRadialGradient(px_int, shadow_y, SIZE // 2)
        shadow.setColorAt(0, QColor(0, 0, 0, 80))
        shadow.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(shadow))
        p.setPen(Qt.NoPen)
        p.drawEllipse(px_int - SIZE // 3, shadow_y - 5, SIZE * 2 // 3, 10)
        
        # Transform sprite
        p.save()
        p.translate(px_int + self.shake_offset[0], py_int + self.shake_offset[1])
        p.rotate(self.rotation)
        p.scale(1.0 / self.squash if nfo["direction"] == 1 else -1.0 / self.squash, self.squash)
        
        sprite = self.sprites.get(nfo["state"], self.sprites[S.IDLE])
        
        # Effetto hiding: clip
        if nfo["is_hiding"]:
            peek_w = SIZE // 3
            if nfo["peek_side"] == "right":
                clip = QRect(SIZE - peek_w - SIZE//2, -SIZE//2, peek_w, SIZE)
            else:
                clip = QRect(-SIZE//2, -SIZE//2, peek_w, SIZE)
            p.setClipRect(clip)
        
        p.drawPixmap(-SIZE // 2, -SIZE // 2, sprite)
        p.restore()
        
        # Sacco animato
        if nfo["sack_count"] > 0:
            bounce = math.sin(self.brain.timer * 0.15) * 3
            p.setFont(QFont("Segoe UI Emoji", 16))
            p.setPen(QColor(255, 255, 255))
            p.drawText(px_int + SIZE // 2 - 12, int(py_int - SIZE // 2 + 12 + bounce), 
                      f"🎒")
            p.setFont(QFont("Arial", 10, QFont.Bold))
            p.setPen(QColor(255, 215, 0))
            p.drawText(px_int + SIZE // 2 + 8, int(py_int - SIZE // 2 + 14 + bounce), 
                      f"×{nfo['sack_count']}")
        
        # Fumetti con animazione
        if nfo["is_taunting"] and self.speech_bubble_scale > 0.1:
            p.save()
            p.translate(px_int, py_int - 80)
            p.scale(self.speech_bubble_scale, self.speech_bubble_scale)
            self._draw_bubble(p, 0, 0, "😝 Se mi prendi ti ridò\nil tuo desktop!")
            p.restore()
            
        if nfo["is_surrender"]:
            self._draw_bubble(p, px_int, py_int, "😤 Ok... hai vinto.")
        
        # Flash effect
        if self.flash_alpha > 0:
            p.fillRect(0, 0, self.sw, self.sh, QColor(255, 255, 255, self.flash_alpha))
        
        p.end()

    def _draw_bubble(self, p, cx, cy, text):
        bw, bh = 280, 70
        bx = -bw // 2
        by = -bh - 20
        
        # Shadow
        p.setBrush(QBrush(QColor(0, 0, 0, 50)))
        p.setPen(Qt.NoPen)
        path_shadow = QPainterPath()
        path_shadow.addRoundedRect(bx + 3, by + 3, bw, bh, 14, 14)
        p.drawPath(path_shadow)
        
        # Bubble
        grad = QRadialGradient(0, by + bh//2, bh)
        grad.setColorAt(0, QColor(255, 255, 240))
        grad.setColorAt(1, QColor(255, 250, 210))
        
        path = QPainterPath()
        path.addRoundedRect(bx, by, bw, bh, 14, 14)
        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor(100, 100, 100), 2))
        p.drawPath(path)
        
        # Tail
        tail = [QPoint(-8, by + bh), QPoint(8, by + bh), QPoint(0, by + bh + 15)]
        p.setBrush(QBrush(QColor(255, 250, 210)))
        p.drawPolygon(*tail)
        
        # Text
        p.setPen(QColor(30, 30, 30))
        p.setFont(QFont("Arial", 10, QFont.Bold))
        p.drawText(QRect(bx + 10, by + 8, bw - 20, bh - 16),
                  Qt.AlignCenter | Qt.TextWordWrap, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.brain.on_click()
            # Particelle al click
            for _ in range(10):
                self.particles.append(Particle(event.x(), event.y(), QColor(100, 200, 255)))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hooks.restore_icons()
            self.close()

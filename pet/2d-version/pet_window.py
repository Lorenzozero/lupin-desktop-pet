import os, sys, win32gui, win32con
import win32api, math, random
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import (QPainter, QColor, QFont, QBrush, QPen,
                         QPainterPath, QPixmap, QTransform, QCursor, QRadialGradient, QLinearGradient)

from desktop_hooks import DesktopHooks
from pet_brain import LupinBrain, S
from sound_manager import SoundManager

SIZE = 90

class Particle:
    def __init__(self, x, y, color, size=4, vx=None, vy=None, particle_type="default"):
        self.x = x
        self.y = y
        self.vx = vx if vx else random.uniform(-3, 3)
        self.vy = vy if vy else random.uniform(-6, -2)
        self.life = 1.0
        self.color = color
        self.size = size
        self.type = particle_type
        self.rotation = random.uniform(0, 360)
        self.spin = random.uniform(-10, 10)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        
        if self.type == "sparkle":
            self.vy += 0.15
            self.vx *= 0.98
        elif self.type == "smoke":
            self.vy -= 0.1  # sale
            self.vx *= 0.95
            self.size += 0.2
        else:
            self.vy += 0.3
            
        self.rotation += self.spin
        self.life -= 0.02 if self.type != "smoke" else 0.015
        return self.life > 0

class IconGhost:
    """Fantasma di un'icona rubata che vola verso il sacco"""
    def __init__(self, start_x, start_y, target_x, target_y):
        self.x = start_x
        self.y = start_y
        self.tx = target_x
        self.ty = target_y
        self.progress = 0.0
        self.size = 32
        
    def update(self):
        self.progress += 0.08
        # Easing cubic out
        t = 1 - pow(1 - self.progress, 3)
        self.x = self.x + (self.tx - self.x) * 0.15
        self.y = self.y + (self.ty - self.y) * 0.15
        # Wobble
        self.x += math.sin(self.progress * 10) * 5
        return self.progress < 1.0

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
        self.sound = SoundManager()
        
        # Advanced UX
        self.particles = []
        self.icon_ghosts = []  # Icone che volano verso il sacco
        self.shake_offset = (0, 0)
        self.shake_intensity = 0
        self.squash = 1.0
        self.rotation = 0
        self.trail_positions = []
        self.dust_timer = 0
        self.blink_timer = 0
        self.eye_state = "open"
        self.speech_bubble_scale = 0.0
        self.flash_alpha = 0
        self.emotion = "neutral"  # neutral, happy, angry, scared, smug
        self.emotion_timer = 0
        self.cursor_attention = 0.0  # Pet guarda il cursore
        self.interaction_prompt = None  # Testo hover
        self.combo_counter = 0  # Combo steal
        self.last_steal_time = 0

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
                px = self._placeholder(color, state)
            result[state] = px
        return result

    def _placeholder(self, color, state):
        px = QPixmap(SIZE, SIZE)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        
        # Corpo con gradiente
        grad = QRadialGradient(SIZE//2, SIZE//2 + 10, SIZE//2)
        grad.setColorAt(0, color.lighter(130))
        grad.setColorAt(0.7, color)
        grad.setColorAt(1, color.darker(120))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(color.darker(150), 2))
        p.drawEllipse(15, 20, SIZE - 30, SIZE - 30)
        
        # Cappello Lupin
        p.setBrush(QBrush(QColor(30, 30, 30)))
        p.setPen(QPen(QColor(10, 10, 10), 1))
        p.drawRect(20, 5, SIZE - 40, 14)
        p.drawRect(28, 2, SIZE - 56, 8)
        
        # Decorazione cappello
        p.setPen(QPen(QColor(200, 50, 50), 2))
        p.drawLine(25, 12, 65, 12)
        
        # Occhi variano per stato
        eye_y = 28
        if state == S.TAUNTING:
            # Occhi chiusi per linguaccia
            p.setPen(QPen(Qt.black, 2))
            p.drawArc(26, eye_y + 5, 14, 8, 0, 180 * 16)
            p.drawArc(SIZE - 40, eye_y + 5, 14, 8, 0, 180 * 16)
        else:
            p.setBrush(QBrush(Qt.white))
            p.setPen(QPen(QColor(50, 50, 50), 1))
            p.drawEllipse(26, eye_y, 14, 14)
            p.drawEllipse(SIZE - 40, eye_y, 14, 14)
            
            # Pupille
            p.setBrush(QBrush(Qt.black))
            p.setPen(Qt.NoPen)
            pupil_offset = 2 if state == S.RUNNING else 0
            p.drawEllipse(30 + pupil_offset, 32, 6, 6)
            p.drawEllipse(SIZE - 36 + pupil_offset, 32, 6, 6)
            
            # Riflessi
            p.setBrush(QBrush(QColor(255, 255, 255, 200)))
            p.drawEllipse(32, 33, 3, 3)
            p.drawEllipse(SIZE - 34, 33, 3, 3)
        
        # Bocca varia
        p.setPen(QPen(Qt.black, 2))
        if state == S.TAUNTING:
            # Linguaccia
            p.setBrush(QBrush(QColor(255, 100, 120)))
            p.drawEllipse(SIZE//2 - 8, 50, 16, 12)
        elif state == S.SURRENDER:
            # Triste
            p.drawArc(SIZE//2 - 8, 52, 16, 8, 0, -180 * 16)
        else:
            # Sorriso
            p.drawArc(SIZE//2 - 8, 48, 16, 8, 0, 180 * 16)
        
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
        if len(self.trail_positions) > 10:
            self.trail_positions.pop(0)
        
        # State transitions con effetti
        if prev_state != nfo["state"]:
            if nfo["state"] == S.STEALING:
                self.emotion = "excited"
                self.sound.play("steal", 0.4)
            elif nfo["state"] == S.TAUNTING:
                self.emotion = "smug"
                self.sound.play("taunt", 0.5)
            elif nfo["state"] == S.RUNNING:
                self.emotion = "scared"
            elif nfo["state"] == S.SURRENDER:
                self.emotion = "sad"
                self.sound.play("caught", 0.6)
        
        # Effetti per stato
        if nfo["state"] == S.STEALING and self.brain.timer == 25:
            # Icona vola verso sacco
            icon_pos = self.icons.get(self.brain.target_icon)
            if icon_pos:
                self.icon_ghosts.append(IconGhost(icon_pos[0], icon_pos[1], nfo["x"], nfo["y"] - 30))
            
            # Combo system
            if self.brain.timer - self.last_steal_time < 120:
                self.combo_counter += 1
            else:
                self.combo_counter = 1
            self.last_steal_time = self.brain.timer
            
            # Particelle potenziate per combo
            particle_count = 20 + self.combo_counter * 5
            for _ in range(particle_count):
                self.particles.append(Particle(nfo["x"], nfo["y"], 
                    QColor(255, 215, 0), 5, particle_type="sparkle"))
            
            self.shake_intensity = 8 + self.combo_counter * 2
            self.flash_alpha = 255
            
        if nfo["state"] == S.RUNNING:
            self.dust_timer += 1
            if self.dust_timer % 5 == 0:
                for _ in range(2):
                    self.particles.append(Particle(nfo["x"], nfo["y"] + 35, 
                        QColor(180, 180, 180, 120), 8, 
                        random.uniform(-2, 2), random.uniform(-1, 0.5),
                        particle_type="smoke"))
            
            speed = math.hypot(nfo["x"] - prev_x, nfo["y"] - prev_y)
            self.squash = 1.0 - min(speed * 0.025, 0.35)
            self.rotation = math.sin(self.brain.timer * 0.25) * 8
        else:
            self.squash = 1.0
            self.rotation = 0
            
        if nfo["state"] == S.TAUNTING:
            self.speech_bubble_scale = min(self.speech_bubble_scale + 0.12, 1.0)
            if self.brain.timer < 40:
                self.shake_intensity = 5
        else:
            self.speech_bubble_scale = max(0, self.speech_bubble_scale - 0.15)
            
        if nfo["state"] == S.SURRENDER:
            if self.brain.timer % 15 == 0:
                self.particles.append(Particle(nfo["x"] + random.randint(-20, 20), 
                    nfo["y"] - 30, QColor(255, 100, 150), 6, 
                    random.uniform(-1, 1), random.uniform(-3, -1),
                    particle_type="sparkle"))
        
        # Cursor attention
        cx, cy = win32api.GetCursorPos()
        dist_cursor = math.hypot(nfo["x"] - cx, nfo["y"] - cy)
        if dist_cursor < 200 and nfo["state"] in (S.IDLE, S.TAUNTING):
            self.cursor_attention = min(1.0, self.cursor_attention + 0.05)
        else:
            self.cursor_attention = max(0, self.cursor_attention - 0.03)
        
        # Blink
        self.blink_timer += 1
        if self.blink_timer > random.randint(150, 400):
            self.eye_state = "closed"
            self.blink_timer = 0
        elif self.blink_timer > 6:
            self.eye_state = "open"
        
        # Update effects
        self.particles = [p for p in self.particles if p.update()]
        self.icon_ghosts = [g for g in self.icon_ghosts if g.update()]
        
        if self.shake_intensity > 0:
            self.shake_intensity *= 0.88
            self.shake_offset = (
                random.uniform(-self.shake_intensity, self.shake_intensity),
                random.uniform(-self.shake_intensity, self.shake_intensity)
            )
        else:
            self.shake_offset = (0, 0)
            
        self.flash_alpha = max(0, self.flash_alpha - 30)
        self.emotion_timer += 1

        pet_rect = QRect(nfo["x"] - SIZE // 2, nfo["y"] - SIZE // 2, SIZE, SIZE)
        self._set_passthrough(not pet_rect.contains(QCursor.pos()))
        self.update()

    def paintEvent(self, _):
        nfo = self.brain.info
        px_int, py_int = nfo["x"], nfo["y"]

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.SmoothPixmapTransform)
        
        # Icon ghosts
        for ghost in self.icon_ghosts:
            p.setOpacity(0.6 * (1 - ghost.progress))
            p.setBrush(QBrush(QColor(255, 255, 150)))
            p.setPen(QPen(QColor(255, 215, 0), 2))
            p.drawRect(int(ghost.x - ghost.size//2), int(ghost.y - ghost.size//2), 
                      ghost.size, ghost.size)
            p.drawText(int(ghost.x - 8), int(ghost.y + 5), "📂")
        p.setOpacity(1.0)
        
        # Motion trail con gradient
        if nfo["state"] == S.RUNNING and len(self.trail_positions) > 3:
            for i in range(len(self.trail_positions) - 1):
                alpha = int(15 * (i / len(self.trail_positions)))
                p.setOpacity(alpha / 255.0)
                tx, ty = self.trail_positions[i]
                trail_sprite = self.sprites[S.RUNNING]
                p.save()
                p.translate(tx, ty)
                p.scale(0.8, 0.8)
                p.drawPixmap(-SIZE//2, -SIZE//2, trail_sprite)
                p.restore()
            p.setOpacity(1.0)
        
        # Particles con rotazione
        for particle in self.particles:
            p.setOpacity(particle.life * 0.8)
            color = QColor(particle.color)
            color.setAlpha(int(255 * particle.life))
            
            p.save()
            p.translate(particle.x, particle.y)
            if particle.type == "sparkle":
                p.rotate(particle.rotation)
                p.setBrush(QBrush(color))
                p.setPen(Qt.NoPen)
                # Star shape
                star_size = particle.size
                p.drawRect(-star_size//2, -1, star_size, 2)
                p.drawRect(-1, -star_size//2, 2, star_size)
            else:
                p.setBrush(QBrush(color))
                p.setPen(Qt.NoPen)
                p.drawEllipse(-particle.size//2, -particle.size//2, particle.size, particle.size)
            p.restore()
        p.setOpacity(1.0)
        
        # Shadow dinamica
        shadow_y = py_int + SIZE // 2 + 8
        shadow_size = SIZE // 2 + abs(math.sin(self.brain.timer * 0.1)) * 5
        shadow = QRadialGradient(px_int, shadow_y, shadow_size)
        shadow.setColorAt(0, QColor(0, 0, 0, 100))
        shadow.setColorAt(1, QColor(0, 0, 0, 0))
        p.setBrush(QBrush(shadow))
        p.setPen(Qt.NoPen)
        p.drawEllipse(int(px_int - shadow_size), shadow_y - 5, int(shadow_size * 2), 12)
        
        # Pet sprite con transform avanzato
        p.save()
        p.translate(px_int + self.shake_offset[0], py_int + self.shake_offset[1])
        p.rotate(self.rotation)
        
        # Pupil tracking cursore
        if self.cursor_attention > 0.1:
            cx, cy = win32api.GetCursorPos()
            look_x = (cx - px_int) * 0.05 * self.cursor_attention
            look_y = (cy - py_int) * 0.05 * self.cursor_attention
            p.translate(look_x, look_y)
        
        scale_x = 1.0 / self.squash if nfo["direction"] == 1 else -1.0 / self.squash
        p.scale(scale_x, self.squash)
        
        sprite = self.sprites.get(nfo["state"], self.sprites[S.IDLE])
        
        if nfo["is_hiding"]:
            peek_w = SIZE // 3
            clip = QRect(SIZE - peek_w - SIZE//2, -SIZE//2, peek_w, SIZE) if nfo["peek_side"] == "right" else QRect(-SIZE//2, -SIZE//2, peek_w, SIZE)
            p.setClipRect(clip)
        
        p.drawPixmap(-SIZE // 2, -SIZE // 2, sprite)
        p.restore()
        
        # Sacco animato ultra
        if nfo["sack_count"] > 0:
            bounce = math.sin(self.brain.timer * 0.18) * 4
            sack_scale = 1.0 + min(nfo["sack_count"] * 0.05, 0.3)
            
            p.save()
            p.translate(px_int + SIZE // 2 - 10, py_int - SIZE // 2 + 10 + bounce)
            p.scale(sack_scale, sack_scale)
            
            # Glow
            if self.combo_counter > 1:
                glow = QRadialGradient(0, 0, 20)
                glow.setColorAt(0, QColor(255, 215, 0, 100))
                glow.setColorAt(1, QColor(255, 215, 0, 0))
                p.setBrush(QBrush(glow))
                p.setPen(Qt.NoPen)
                p.drawEllipse(-15, -15, 30, 30)
            
            p.setFont(QFont("Segoe UI Emoji", 18))
            p.drawText(-10, 5, "🎒")
            p.restore()
            
            # Counter con combo
            p.setFont(QFont("Arial", 11, QFont.Bold))
            if self.combo_counter > 1:
                p.setPen(QColor(255, 100, 50))
                p.drawText(px_int + SIZE // 2 + 12, py_int - SIZE // 2 + 8, f"x{self.combo_counter}!")
            p.setPen(QColor(255, 215, 0))
            p.drawText(px_int + SIZE // 2 + 10, py_int - SIZE // 2 + 18 + bounce, f"×{nfo['sack_count']}")
        
        # Fumetti avanzati
        if nfo["is_taunting"] and self.speech_bubble_scale > 0.1:
            p.save()
            p.translate(px_int, py_int - 90)
            p.scale(self.speech_bubble_scale, self.speech_bubble_scale)
            p.rotate(math.sin(self.brain.timer * 0.1) * 2)
            taunt_texts = [
                "😝 Troppo lento!",
                "😜 Provaci ancora!",
                "😎 Non mi prenderai mai!"
            ]
            text = taunt_texts[self.combo_counter % len(taunt_texts)]
            self._draw_bubble(p, 0, 0, text)
            p.restore()
            
        if nfo["is_surrender"]:
            self._draw_bubble(p, px_int, py_int, f"😤 Ok... {nfo['sack_count']} icone restituite.")
        
        # Combo text
        if self.combo_counter > 2 and self.brain.timer - self.last_steal_time < 60:
            combo_y = py_int - SIZE - 40
            p.setFont(QFont("Arial", 16, QFont.Bold))
            p.setPen(QColor(255, 50, 50))
            combo_scale = 1.0 + math.sin(self.brain.timer * 0.3) * 0.2
            p.save()
            p.translate(px_int, combo_y)
            p.scale(combo_scale, combo_scale)
            p.drawText(-50, 0, 100, 30, Qt.AlignCenter, f"COMBO x{self.combo_counter}!")
            p.restore()
        
        # Flash
        if self.flash_alpha > 0:
            grad = QRadialGradient(px_int, py_int, 300)
            grad.setColorAt(0, QColor(255, 255, 200, self.flash_alpha))
            grad.setColorAt(1, QColor(255, 255, 255, 0))
            p.fillRect(0, 0, self.sw, self.sh, QBrush(grad))
        
        p.end()

    def _draw_bubble(self, p, cx, cy, text):
        bw, bh = 300, 75
        bx = -bw // 2
        by = -bh - 20
        
        # Shadow
        for i in range(4):
            p.setBrush(QBrush(QColor(0, 0, 0, 15)))
            p.setPen(Qt.NoPen)
            path_shadow = QPainterPath()
            path_shadow.addRoundedRect(bx + 2 + i, by + 2 + i, bw, bh, 16, 16)
            p.drawPath(path_shadow)
        
        # Bubble con gradiente
        grad = QLinearGradient(0, by, 0, by + bh)
        grad.setColorAt(0, QColor(255, 255, 250))
        grad.setColorAt(1, QColor(255, 245, 200))
        
        path = QPainterPath()
        path.addRoundedRect(bx, by, bw, bh, 16, 16)
        p.fillPath(path, QBrush(grad))
        p.setPen(QPen(QColor(120, 120, 120), 3))
        p.drawPath(path)
        
        # Tail
        tail = [QPoint(-10, by + bh), QPoint(10, by + bh), QPoint(0, by + bh + 18)]
        p.setBrush(QBrush(QColor(255, 245, 200)))
        p.drawPolygon(*tail)
        
        # Text con ombra
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Arial", 10, QFont.Bold))
        p.drawText(QRect(bx + 11, by + 9, bw - 20, bh - 16), Qt.AlignCenter | Qt.TextWordWrap, text)
        
        p.setPen(QColor(30, 30, 30))
        p.drawText(QRect(bx + 10, by + 8, bw - 20, bh - 16), Qt.AlignCenter | Qt.TextWordWrap, text)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.brain.on_click()
            for _ in range(15):
                self.particles.append(Particle(event.x(), event.y(), 
                    QColor(100, 200, 255), 4, particle_type="sparkle"))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hooks.restore_icons()
            self.close()

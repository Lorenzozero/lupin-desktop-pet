import os, sys, win32gui, win32con
import win32api
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QTimer, QRect, QPoint
from PyQt5.QtGui import (QPainter, QColor, QFont, QBrush, QPen,
                         QPainterPath, QPixmap, QTransform, QCursor)

from desktop_hooks import DesktopHooks
from pet_brain import LupinBrain, S

SIZE = 90  # dimensione sprite px

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

        self._icon_tick = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self._loop)
        self.timer.start(16)
        self._set_passthrough(True)
        self.show()

    # ── Win32 click-through ────────────────────────────────

    def _set_passthrough(self, on: bool):
        hwnd = int(self.winId())
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if on:
            style |= win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
        else:
            style &= ~win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

    # ── Sprites ────────────────────────────────────────────

    def _load_sprites(self):
        """Carica PNG da ./sprites/ o genera placeholder colorati"""
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
                px = QPixmap(path).scaled(SIZE, SIZE, Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)
            else:
                px = self._placeholder(color)
            result[state] = px
        return result

    def _placeholder(self, color):
        px = QPixmap(SIZE, SIZE)
        px.fill(Qt.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.Antialiasing)
        # Corpo
        p.setBrush(QBrush(color))
        p.setPen(Qt.NoPen)
        p.drawEllipse(15, 20, SIZE - 30, SIZE - 30)
        # Cappello Lupin
        p.setBrush(QBrush(QColor(30, 30, 30)))
        p.drawRect(20, 5, SIZE - 40, 14)
        p.drawRect(28, 2, SIZE - 56, 8)
        # Occhi
        p.setBrush(QBrush(Qt.white))
        p.drawEllipse(26, 28, 14, 14)
        p.drawEllipse(SIZE - 40, 28, 14, 14)
        p.setBrush(QBrush(Qt.black))
        p.drawEllipse(30, 32, 6, 6)
        p.drawEllipse(SIZE - 36, 32, 6, 6)
        p.end()
        return px

    # ── Game loop ──────────────────────────────────────────

    def _loop(self):
        self._icon_tick += 1
        if self._icon_tick >= 200:
            self.icons = self.hooks.get_all_positions()
            self._icon_tick = 0

        self.brain.update(self.icons)
        nfo = self.brain.info

        pet_rect = QRect(nfo["x"] - SIZE // 2, nfo["y"] - SIZE // 2, SIZE, SIZE)
        self._set_passthrough(not pet_rect.contains(QCursor.pos()))
        self.update()

    # ── Rendering ─────────────────────────────────────────

    def paintEvent(self, _):
        nfo = self.brain.info
        px_int, py_int = nfo["x"], nfo["y"]

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        sprite = self.sprites.get(nfo["state"], self.sprites[S.IDLE])
        if nfo["direction"] == -1:
            sprite = sprite.transformed(QTransform().scale(-1, 1))

        # Effetto "nascosto": ritaglia solo l'angolino
        if nfo["is_hiding"]:
            p.save()
            peek_w = SIZE // 3
            if nfo["peek_side"] == "right":
                clip = QRect(px_int - SIZE // 2 + (SIZE - peek_w),
                             py_int - SIZE // 2, peek_w, SIZE)
            else:
                clip = QRect(px_int - SIZE // 2, py_int - SIZE // 2, peek_w, SIZE)
            p.setClipRect(clip)

        p.drawPixmap(px_int - SIZE // 2, py_int - SIZE // 2, sprite)

        if nfo["is_hiding"]:
            p.restore()

        # Sacco sopra la testa
        if nfo["sack_count"] > 0:
            p.setFont(QFont("Segoe UI Emoji", 14))
            p.drawText(px_int + SIZE // 2 - 10, py_int - SIZE // 2 + 10,
                       f"🎒×{nfo['sack_count']}")

        # Fumetto canzonatorio
        if nfo["is_taunting"]:
            self._draw_bubble(p, px_int, py_int,
                "😝 Se mi prendi ti ridò il tuo\ndesktop ESATTAMENTE com'era!")

        # Fumetto resa
        if nfo["is_surrender"]:
            self._draw_bubble(p, px_int, py_int,
                "😤 Ok ok... hai vinto.\nEcco le tue icone.")

        p.end()

    def _draw_bubble(self, p, cx, cy, text):
        bw, bh = 300, 75
        bx = max(10, min(cx - bw // 2, self.sw - bw - 10))
        by = cy - bh - 35

        path = QPainterPath()
        path.addRoundedRect(bx, by, bw, bh, 14, 14)
        p.fillPath(path, QBrush(QColor(255, 252, 210, 235)))
        p.setPen(QPen(QColor(80, 80, 80), 2))
        p.drawPath(path)

        # Triangolino
        tail = [QPoint(cx - 10, by + bh),
                QPoint(cx + 10, by + bh),
                QPoint(cx, by + bh + 18)]
        p.setBrush(QBrush(QColor(255, 252, 210, 235)))
        p.drawPolygon(*tail)

        p.setPen(QColor(30, 30, 30))
        p.setFont(QFont("Arial", 9, QFont.Bold))
        p.drawText(QRect(bx + 10, by + 8, bw - 20, bh - 16),
                   Qt.AlignCenter | Qt.TextWordWrap, text)

    # ── Input ──────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.brain.on_click()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hooks.restore_icons()
            self.close()

import math, random
from PyQt5.QtCore import QPointF, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath

class Particle3D:
    def __init__(self, x, y, z, vx, vy, vz, life, color, ptype="sparkle", size=6):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.life = self.max_life = life
        self.color = color
        self.ptype = ptype
        self.size = size
        self.spin = random.uniform(-8, 8)
        self.angle = random.uniform(0, 360)

    def update(self):
        self.vz -= 0.18
        self.x += self.vx
        self.y += self.vy + abs(self.vz) * 0.1
        self.z += self.vz
        self.angle += self.spin
        if self.ptype in ("snow", "leaf"):
            self.x += math.sin(self.life * 0.3) * 0.4
        self.life -= 1
        return self.life > 0

    @property
    def alpha(self):
        return max(0, int(255 * self.life / self.max_life))

    def screen_size(self):
        # Z gives depth scale
        depth = max(0.4, 1.0 + self.z * 0.02)
        return max(2, self.size * depth)


class ParticleSystem3D:
    def __init__(self):
        self.particles = []

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def burst_sparkle(self, x, y, count=20, color=None):
        for _ in range(count):
            c = color or QColor(
                random.randint(200,255), random.randint(180,255), random.randint(50,150))
            self.particles.append(Particle3D(
                x, y, 0,
                random.uniform(-5, 5), random.uniform(-8, -1), random.uniform(1, 6),
                random.randint(20, 45), c, "sparkle", random.randint(4, 10)
            ))

    def emit_smoke(self, x, y):
        c = QColor(random.randint(150, 200), random.randint(150, 200), random.randint(160, 210), 160)
        self.particles.append(Particle3D(
            x + random.uniform(-15, 15), y, 0,
            random.uniform(-0.8, 0.8), random.uniform(-2.5, -1.0), 0,
            random.randint(25, 50), c, "smoke", random.randint(8, 18)
        ))

    def emit_confetti(self, x, y):
        colors = [QColor(255,60,60), QColor(60,220,60), QColor(60,120,255),
                  QColor(255,220,30), QColor(255,60,200)]
        c = random.choice(colors)
        self.particles.append(Particle3D(
            x + random.uniform(-20, 20), y, 0,
            random.uniform(-4, 4), random.uniform(-7, -2), random.uniform(0, 3),
            random.randint(35, 65), c, "confetti", random.randint(5, 10)
        ))

    def emit_heart(self, x, y):
        self.particles.append(Particle3D(
            x + random.uniform(-12, 12), y, 0,
            random.uniform(-1.5, 1.5), random.uniform(-3, -1), 0,
            random.randint(40, 70), QColor(255, 80, 120), "heart", 10
        ))

    def emit_sweat(self, x, y):
        self.particles.append(Particle3D(
            x + random.uniform(-10, 10), y - 20, 0,
            random.uniform(-1, 1), random.uniform(1, 3), 0,
            random.randint(15, 30), QColor(100, 180, 255, 200), "sweat", 5
        ))

    def emit_star(self, x, y):
        c = QColor(255, random.randint(200, 255), 0)
        self.particles.append(Particle3D(
            x, y, 0,
            random.uniform(-3, 3), random.uniform(-5, 0), random.uniform(1, 4),
            random.randint(30, 55), c, "star", random.randint(6, 12)
        ))

    def draw(self, p: QPainter):
        for pt in self.particles:
            alpha = pt.alpha
            if alpha <= 0:
                continue
            c = QColor(pt.color)
            c.setAlpha(alpha)
            sz = pt.screen_size()

            if pt.ptype == "sparkle":
                p.setPen(Qt_NoPen())
                p.setBrush(QBrush(c))
                p.drawEllipse(QPointF(pt.x, pt.y), sz * 0.5, sz * 0.5)

            elif pt.ptype == "smoke":
                grad = QRadialGradient_simple(pt.x, pt.y, sz)
                c2 = QColor(c); c2.setAlpha(0)
                grad.setColorAt(0, c)
                grad.setColorAt(1, c2)
                p.setPen(Qt_NoPen())
                p.setBrush(QBrush(grad))
                p.drawEllipse(QPointF(pt.x, pt.y), sz, sz * 0.7)

            elif pt.ptype == "confetti":
                p.save()
                p.translate(pt.x, pt.y)
                p.rotate(pt.angle)
                p.setPen(Qt_NoPen())
                p.setBrush(QBrush(c))
                p.drawRect(QRectF(-sz/2, -sz/3, sz, sz*0.6))
                p.restore()

            elif pt.ptype == "heart":
                _draw_heart(p, pt.x, pt.y, sz * 0.7, c)

            elif pt.ptype == "sweat":
                p.setPen(Qt_NoPen())
                p.setBrush(QBrush(c))
                p.drawEllipse(QPointF(pt.x, pt.y), sz * 0.4, sz * 0.65)

            elif pt.ptype == "star":
                _draw_star(p, pt.x, pt.y, sz * 0.6, c)

            else:
                p.setPen(Qt_NoPen())
                p.setBrush(QBrush(c))
                p.drawEllipse(QPointF(pt.x, pt.y), sz * 0.5, sz * 0.5)


# ── Helpers ──────────────────────────────────────────────────────

def Qt_NoPen():
    from PyQt5.QtCore import Qt
    return Qt.NoPen

def QRadialGradient_simple(cx, cy, r):
    from PyQt5.QtGui import QRadialGradient
    g = QRadialGradient(cx, cy, r)
    return g

def _draw_heart(p, cx, cy, size, color):
    from PyQt5.QtGui import QPainterPath
    path = QPainterPath()
    s = size * 0.5
    path.moveTo(cx, cy + s * 0.8)
    path.cubicTo(cx - s*2, cy - s*0.5, cx - s*2.5, cy + s*0.5, cx, cy - s*0.8)
    path.cubicTo(cx + s*2.5, cy + s*0.5, cx + s*2, cy - s*0.5, cx, cy + s*0.8)
    p.setPen(Qt_NoPen())
    p.setBrush(QBrush(color))
    p.drawPath(path)

def _draw_star(p, cx, cy, r, color):
    import math
    from PyQt5.QtGui import QPainterPath
    from PyQt5.QtCore import QPointF
    path = QPainterPath()
    n = 5
    for i in range(n * 2):
        angle = math.radians(i * 180 / n - 90)
        rr = r if i % 2 == 0 else r * 0.4
        x = cx + math.cos(angle) * rr
        y = cy + math.sin(angle) * rr
        if i == 0:
            path.moveTo(x, y)
        else:
            path.lineTo(x, y)
    path.closeSubpath()
    p.setPen(Qt_NoPen())
    p.setBrush(QBrush(color))
    p.drawPath(path)

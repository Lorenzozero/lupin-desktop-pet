import math
import random
from panda3d.core import (
    Vec3, Vec4, Point3,
    NodePath, PandaNode,
    GeomNode, Geom, GeomVertexData, GeomVertexFormat,
    GeomVertexWriter, GeomTriangles, GeomPoints,
    TransparencyAttrib, BillboardEffect, LColor
)
from direct.interval.IntervalGlobal import Sequence, LerpPosInterval, LerpScaleInterval, Func

class Particle3D:
    def __init__(self, node, velocity, life, gravity=True):
        self.node = node
        self.vx = velocity[0]
        self.vy = velocity[1]
        self.vz = velocity[2]
        self.life = life
        self.max_life = life
        self.gravity = gravity
        self.spin = random.uniform(-180, 180)

    def update(self, dt):
        if self.gravity:
            self.vz -= 9.8 * dt
        x, y, z = self.node.getPos()
        self.node.setPos(x + self.vx * dt, y + self.vy * dt, z + self.vz * dt)
        self.node.setR(self.node.getR() + self.spin * dt)
        alpha = self.life / self.max_life
        self.node.setAlphaScale(alpha)
        self.life -= dt
        return self.life > 0

class ParticleSystem3D:
    def __init__(self, render):
        self.render = render
        self.particles = []
        self.root = render.attachNewNode("particles")

    def _make_quad(self, size=0.15):
        """Crea un quad billboarded per ogni particella"""
        format = GeomVertexFormat.getV3n3c4t2()
        vdata = GeomVertexData("particle", format, Geom.UHDynamic)
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        color = GeomVertexWriter(vdata, "color")
        texcoord = GeomVertexWriter(vdata, "texcoord")

        s = size / 2
        for vx, vy, vz in [(-s, 0, -s), (s, 0, -s), (s, 0, s), (-s, 0, s)]:
            vertex.addData3(vx, vy, vz)
            normal.addData3(0, -1, 0)
            color.addData4(1, 1, 1, 1)
            texcoord.addData2(0, 0)

        prim = GeomTriangles(Geom.UHStatic)
        prim.addVertices(0, 1, 2)
        prim.addVertices(0, 2, 3)
        prim.closePrimitive()

        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode("pquad")
        node.addGeom(geom)
        np = self.root.attachNewNode(node)
        np.setTransparency(TransparencyAttrib.MAlpha)
        np.setLightOff()
        return np

    def burst_sparkle(self, pos, count=20, color=Vec4(1, 0.85, 0, 1)):
        for _ in range(count):
            quad = self._make_quad(random.uniform(0.1, 0.25))
            quad.setPos(pos)
            quad.setColor(color)
            vx = random.uniform(-5, 5)
            vy = random.uniform(-1, 1)
            vz = random.uniform(2, 8)
            life = random.uniform(0.4, 0.9)
            p = Particle3D(quad, (vx, vy, vz), life, gravity=True)
            self.particles.append(p)

    def emit_smoke(self, pos):
        quad = self._make_quad(random.uniform(0.3, 0.6))
        quad.setPos(pos + Vec3(random.uniform(-0.3, 0.3), 0, 0))
        quad.setColor(0.7, 0.7, 0.7, 0.5)
        p = Particle3D(quad, (random.uniform(-0.5, 0.5), 0, random.uniform(0.5, 1.5)), 
                       random.uniform(0.3, 0.7), gravity=False)
        self.particles.append(p)

    def emit_confetti(self, pos):
        colors = [Vec4(1,0.2,0.2,1), Vec4(0.2,1,0.2,1), Vec4(0.2,0.2,1,1),
                  Vec4(1,1,0.2,1), Vec4(1,0.2,1,1)]
        quad = self._make_quad(0.15)
        quad.setPos(pos + Vec3(random.uniform(-1, 1), 0, random.uniform(0, 1)))
        quad.setColor(random.choice(colors))
        p = Particle3D(quad, (random.uniform(-3, 3), 0, random.uniform(1, 4)),
                       random.uniform(0.6, 1.2))
        self.particles.append(p)

    def emit_heart(self, pos):
        quad = self._make_quad(0.3)
        quad.setPos(pos + Vec3(random.uniform(-0.5, 0.5), 0, 0))
        quad.setColor(1, 0.3, 0.5, 1)
        p = Particle3D(quad, (random.uniform(-1, 1), 0, random.uniform(2, 4)),
                       0.8, gravity=False)
        self.particles.append(p)

    def update(self, dt):
        alive = []
        for p in self.particles:
            if p.update(dt):
                alive.append(p)
            else:
                p.node.removeNode()
        self.particles = alive

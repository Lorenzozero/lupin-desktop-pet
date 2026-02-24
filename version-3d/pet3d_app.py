import sys
import os
import math
import random
import ctypes
import win32gui
import win32con
import win32api

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import Sequence, Parallel, Wait, Func
from panda3d.core import (
    WindowProperties, FrameBufferProperties, GraphicsPipe,
    AmbientLight, DirectionalLight, PointLight,
    Vec3, Vec4, Point3, LColor,
    TransparencyAttrib, ColorAttrib,
    NodePath, PandaNode,
    ClockObject, ConfigVariableString,
    loadPrcFileData
)

# Configurazione pre-init
loadPrcFileData("", """
    window-title Lupin Pet 3D
    undecorated true
    transparent-alpha 1
    framebuffer-alpha true
    sync-video false
    show-frame-rate-meter true
    model-path ./models
""")

from desktop_hooks import DesktopHooks
from pet3d_brain import LupinBrain3D, S
from particle_system3d import ParticleSystem3D

class LupinPet3D(ShowBase):
    def __init__(self):
        super().__init__()

        # ── Risoluzione ───────────────────────────────────
        self.sw = win32api.GetSystemMetrics(0)
        self.sh = win32api.GetSystemMetrics(1)

        # ── Finestra trasparente borderless ───────────────
        props = WindowProperties()
        props.setSize(self.sw, self.sh)
        props.setOrigin(0, 0)
        props.setUndecorated(True)
        props.setForeground(True)
        self.win.requestProperties(props)

        # Patch Win32: sempre in cima + trasparente ai click
        self._patch_window()

        # ── Camera ortho per overlay 2.5D ─────────────────
        self.disableMouse()
        self.camera.setPos(0, -20, 0)
        self.camera.lookAt(Point3(0, 0, 0))
        self.camLens.setFov(30)
        self.camLens.setNearFar(0.1, 1000)

        # ── Background trasparente ────────────────────────
        self.setBackgroundColor(0, 0, 0, 0)
        self.win.setActive(True)

        # ── Luci ─────────────────────────────────────────
        self._setup_lighting()

        # ── Carica modello ────────────────────────────────
        self.pet_node = self._load_model()

        # ── Sistemi ───────────────────────────────────────
        self.hooks = DesktopHooks()
        self.hooks.save_positions()
        self.icons = self.hooks.get_all_positions()

        self.brain = LupinBrain3D(self.sw, self.sh, self.hooks)
        self.particles = ParticleSystem3D(self.render)

        # ── Ombra proiettata ──────────────────────────────
        self.shadow = self._create_shadow()

        # ── State ─────────────────────────────────────────
        self.current_anim = None
        self.icon_tick = 0
        self.shake_offset = Vec3(0, 0, 0)
        self.shake_intensity = 0
        self.speech_visible = False
        self.speech_label = None

        # ── Tasks ─────────────────────────────────────────
        self.taskMgr.add(self._game_loop, "GameLoop")
        self.taskMgr.add(self._update_icons, "UpdateIcons")
        self.taskMgr.add(self._update_effects, "UpdateEffects")

        # ── Input ─────────────────────────────────────────
        self.accept("escape", self._quit)
        self.accept("mouse1", self._on_click)

        print(f"[Lupin3D] Avviato - Schermo: {self.sw}x{self.sh}")
        print(f"[Lupin3D] Personalit\u00e0: {self.brain.personality}")

    # ── Setup ─────────────────────────────────────────────

    def _patch_window(self):
        """Applica stile Win32 per overlay trasparente sempre in cima"""
        hwnd = win32gui.FindWindow(None, "Lupin Pet 3D")
        if not hwnd:
            return

        # Always on top
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, self.sw, self.sh,
                              win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)

        # WS_EX_LAYERED + WS_EX_TRANSPARENT per click-through
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        style |= win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

        # LWA_COLORKEY: rendi il nero puro trasparente
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0x000000, 0, 0x1)

    def _setup_lighting(self):
        # Ambient soffice
        ambient = AmbientLight("ambient")
        ambient.setColor(LColor(0.4, 0.4, 0.5, 1))
        self.render.setLight(self.render.attachNewNode(ambient))

        # Key light (direzionale)
        key = DirectionalLight("key")
        key.setColor(LColor(0.9, 0.85, 0.8, 1))
        key_np = self.render.attachNewNode(key)
        key_np.setHpr(30, -60, 0)
        self.render.setLight(key_np)

        # Fill light
        fill = DirectionalLight("fill")
        fill.setColor(LColor(0.3, 0.35, 0.5, 1))
        fill_np = self.render.attachNewNode(fill)
        fill_np.setHpr(-120, -20, 0)
        self.render.setLight(fill_np)

        # Rim light dinamico
        self.rim_light = PointLight("rim")
        self.rim_light.setColor(LColor(0.5, 0.5, 1.0, 1))
        self.rim_light.setAttenuation(Vec3(0.1, 0, 0.05))
        self.rim_np = self.render.attachNewNode(self.rim_light)
        self.rim_np.setPos(5, -5, 5)
        self.render.setLight(self.rim_np)

    def _load_model(self):
        """Carica il GLB con fallback su forme geometriche"""
        glb_path = "models/lupin.glb"
        bam_path = "models/lupin.bam"

        node = None

        # Tenta caricamento GLB con panda3d-gltf
        if os.path.exists(glb_path):
            try:
                from gltf import GltfSettings, load_model
                print(f"[Lupin3D] Caricando {glb_path}...")
                node = load_model(glb_path)
                node.reparentTo(self.render)
                node.setScale(1.0)
                print("[Lupin3D] GLB caricato!")
            except ImportError:
                print("[Lupin3D] panda3d-gltf non installato. Installa con: pip install panda3d-gltf")
            except Exception as e:
                print(f"[Lupin3D] Errore caricamento GLB: {e}")

        # Fallback su BAM
        if node is None and os.path.exists(bam_path):
            try:
                node = self.loader.loadModel(bam_path)
                node.reparentTo(self.render)
                print("[Lupin3D] BAM caricato")
            except Exception as e:
                print(f"[Lupin3D] Errore BAM: {e}")

        # Fallback su modello procedurale 3D
        if node is None:
            print("[Lupin3D] Usando modello procedurale")
            node = self._build_procedural_lupin()

        node.setTransparency(TransparencyAttrib.MAlpha)
        return node

    def _build_procedural_lupin(self):
        """Modello 3D procedurale se non c'\u00e8 il GLB"""
        root = self.render.attachNewNode("lupin")

        # Corpo
        body = self.loader.loadModel("models/misc/sphere")
        if body:
            body.reparentTo(root)
            body.setScale(0.6, 0.4, 0.7)
            body.setPos(0, 0, 0)
            body.setColor(0.3, 0.5, 0.9, 1)
        else:
            # Fallback su cube se sphere non disponibile
            body = self.loader.loadModel("models/misc/rgbCube")
            if body:
                body.reparentTo(root)
                body.setScale(0.5)
                body.setColor(0.3, 0.5, 0.9, 1)

        # Cappello
        hat_brim = self.loader.loadModel("models/misc/sphere")
        if hat_brim:
            hat_brim.reparentTo(root)
            hat_brim.setScale(0.55, 0.55, 0.08)
            hat_brim.setPos(0, 0, 0.75)
            hat_brim.setColor(0.1, 0.1, 0.1, 1)

            hat_top = self.loader.loadModel("models/misc/sphere")
            if hat_top:
                hat_top.reparentTo(root)
                hat_top.setScale(0.3, 0.3, 0.45)
                hat_top.setPos(0, 0, 1.05)
                hat_top.setColor(0.1, 0.1, 0.1, 1)

        root.setTransparency(TransparencyAttrib.MAlpha)
        return root

    def _create_shadow(self):
        """Blob shadow sotto il pet"""
        try:
            shadow = self.loader.loadModel("models/misc/sphere")
            shadow.reparentTo(self.render)
            shadow.setScale(1.2, 1.2, 0.05)
            shadow.setPos(0, 0, -1.2)
            shadow.setColor(0, 0, 0, 0.4)
            shadow.setTransparency(TransparencyAttrib.MAlpha)
            return shadow
        except:
            return None

    # ── Tasks ──────────────────────────────────────────────

    def _game_loop(self, task):
        dt = globalClock.getDt()

        self.icon_tick += 1
        if self.icon_tick >= 180:
            self.icons = self.hooks.get_all_positions()
            self.icon_tick = 0

        prev_state = self.brain.state
        self.brain.update(self.icons, dt)
        nfo = self.brain.info

        # Converti coordinate schermo -> mondo 3D
        world_x, world_z = self._screen_to_world(nfo["x"], nfo["y"])

        # Posiziona pet con shake
        target_pos = Vec3(world_x + self.shake_offset.x,
                          0,
                          world_z + self.shake_offset.z)
        self.pet_node.setPos(target_pos)

        # Direzione con flip fluido
        if nfo["direction"] == 1:
            self.pet_node.setH(0)
        else:
            self.pet_node.setH(180)

        # Aggiorna ombra
        if self.shadow:
            self.shadow.setPos(world_x, 0, world_z - 1.0)

        # Rim light dinamica (segue il pet)
        self.rim_np.setPos(world_x + 3, -8, world_z + 5)

        # Squash/stretch dinamico
        speed = nfo.get("speed", 0)
        if nfo["state"] == S.RUNNING:
            squash = max(0.7, 1.0 - speed * 0.015)
            stretch = min(1.4, 1.0 + speed * 0.015)
            self.pet_node.setScale(squash, 1.0, stretch)

            # Tilt in base a velocità
            tilt = nfo["direction"] * min(speed * 2, 20)
            self.pet_node.setR(tilt)
        else:
            # Breath animation
            t = globalClock.getRealTime()
            breath = 1.0 + math.sin(t * 1.5) * 0.02
            self.pet_node.setScale(breath, 1.0, breath)
            self.pet_node.setR(0)

        # Cambio animazione
        self._update_animation(nfo["state"], prev_state, nfo)

        # Effetti per stato
        self._state_effects(nfo, prev_state)

        return Task.cont

    def _update_icons(self, task):
        if self.icon_tick % 200 == 0:
            self.icons = self.hooks.get_all_positions()
        return Task.cont

    def _update_effects(self, task):
        # Decay shake
        if self.shake_intensity > 0.01:
            self.shake_intensity *= 0.85
            self.shake_offset = Vec3(
                random.uniform(-self.shake_intensity, self.shake_intensity),
                0,
                random.uniform(-self.shake_intensity, self.shake_intensity)
            )
        else:
            self.shake_intensity = 0
            self.shake_offset = Vec3(0, 0, 0)

        # Update particle system
        self.particles.update(globalClock.getDt())
        return Task.cont

    # ── Animazioni ─────────────────────────────────────────

    def _update_animation(self, state, prev_state, nfo):
        if state == prev_state:
            return

        # Mappa stato -> nome animazione GLB
        anim_map = {
            S.IDLE:        "idle",
            S.APPROACHING: "walk",
            S.STEALING:    "grab",
            S.TAUNTING:    "taunt",
            S.RUNNING:     "run",
            S.HIDING:      "crouch",
            S.SURRENDER:   "surrender",
        }

        anim_name = anim_map.get(state, "idle")

        # Se il modello è un Actor (GLB con armature), usa loop
        try:
            if hasattr(self.pet_node, 'loop'):
                self.pet_node.loop(anim_name)
                self.current_anim = anim_name
                print(f"[Lupin3D] Animazione: {anim_name}")
        except Exception as e:
            print(f"[Lupin3D] Anim error: {e}")

    def _state_effects(self, nfo, prev_state):
        """Effetti 3D al cambio di stato"""
        cx, cz = self._screen_to_world(nfo["x"], nfo["y"])
        pos = Vec3(cx, 0, cz)

        # Furto: esplosione particelle dorate
        if nfo["state"] == S.STEALING and self.brain.timer == 25:
            self.particles.burst_sparkle(pos, count=30, color=Vec4(1, 0.85, 0, 1))
            self.shake_intensity = 0.3

        # Corsa: smoke trail
        if nfo["state"] == S.RUNNING:
            if int(globalClock.getRealTime() * 30) % 4 == 0:
                self.particles.emit_smoke(pos + Vec3(0, 0, -0.5))

        # Taunting: confetti
        if nfo["state"] == S.TAUNTING and nfo["is_taunting"]:
            if int(globalClock.getRealTime() * 20) % 10 == 0:
                for _ in range(5):
                    self.particles.emit_confetti(pos)

        # Resa: cuori
        if nfo["state"] == S.SURRENDER:
            if int(globalClock.getRealTime() * 20) % 8 == 0:
                self.particles.emit_heart(pos)

    # ── Utils ──────────────────────────────────────────────

    def _screen_to_world(self, sx, sy):
        """Converte coordinate pixel -> spazio 3D Panda3D"""
        # Normalizza in [-1, 1]
        nx = (sx / self.sw) * 2 - 1
        ny = 1 - (sy / self.sh) * 2

        # Scala al frustum a distanza y=0
        fov_rad = math.radians(self.camLens.getFov()[0])
        dist = abs(self.camera.getY())
        aspect = self.sw / self.sh
        half_w = math.tan(fov_rad / 2) * dist
        half_h = half_w / aspect

        return nx * half_w, ny * half_h

    # ── Input ──────────────────────────────────────────────

    def _on_click(self):
        self.brain.on_click()
        if self.mouseWatcher.node().hasMouse():
            mx = self.mouseWatcher.node().getMouseX()
            my = self.mouseWatcher.node().getMouseY()
            cx = mx * 8
            cz = my * 5
            for _ in range(12):
                self.particles.burst_sparkle(Vec3(cx, 0, cz), count=1, color=Vec4(0.4, 0.8, 1, 1))

    def _quit(self):
        self.hooks.restore_icons()
        print("[Lupin3D] Icone ripristinate. Bye!")
        self.userExit()

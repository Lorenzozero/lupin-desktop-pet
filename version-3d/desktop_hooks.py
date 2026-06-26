import ctypes, ctypes.wintypes
import win32gui, win32con, win32api
import random, math

LVM_FIRST              = 0x1000
LVM_GETITEMCOUNT       = LVM_FIRST + 4
LVM_GETITEMPOSITION    = LVM_FIRST + 16
LVM_SETITEMPOSITION    = LVM_FIRST + 15
LVM_SETITEMPOSITION32  = LVM_FIRST + 49
LVS_AUTOARRANGE        = 0x0100

# Accessi minimi per WriteProcessMemory
PROC_WRITE = 0x0028   # PROCESS_VM_WRITE | PROCESS_VM_OPERATION
PROC_READ  = 0x0018   # PROCESS_VM_READ  | PROCESS_VM_OPERATION

class DesktopHooks:
    def __init__(self):
        self._lv_hwnd = self._find_listview()
        self._saved_positions = {}
        self._pid = None
        if self._lv_hwnd:
            self._cache_pid()
            self._disable_autoarrange()

    # ── Init ─────────────────────────────────────────────────

    def _find_listview(self):
        progman = win32gui.FindWindow("Progman", None)
        win32gui.SendMessageTimeout(progman, 0x052C, 0, 0, win32con.SMTO_NORMAL, 1000)

        def try_find(parent):
            shell = win32gui.FindWindowEx(parent, 0, "SHELLDLL_DefView", None)
            if shell:
                return win32gui.FindWindowEx(shell, 0, "SysListView32", None)
            return None

        lv = try_find(progman)
        if lv:
            return lv
        result = [None]
        def cb(hwnd, _):
            shell = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
            if shell:
                found = win32gui.FindWindowEx(shell, 0, "SysListView32", None)
                if found:
                    result[0] = found
        win32gui.EnumWindows(cb, None)
        return result[0]

    def _cache_pid(self):
        pid = ctypes.c_ulong(0)
        ctypes.windll.user32.GetWindowThreadProcessId(self._lv_hwnd, ctypes.byref(pid))
        self._pid = pid.value

    def _disable_autoarrange(self):
        try:
            style = win32gui.GetWindowLong(self._lv_hwnd, win32con.GWL_STYLE)
            if style & LVS_AUTOARRANGE:
                win32gui.SetWindowLong(self._lv_hwnd, win32con.GWL_STYLE,
                                       style & ~LVS_AUTOARRANGE)
        except Exception:
            pass

    # ── Memoria processo ──────────────────────────────────────

    def _open_proc(self, access):
        if not self._pid:
            return None
        return ctypes.windll.kernel32.OpenProcess(access, False, self._pid)

    # ── Lettura posizioni ─────────────────────────────────────

    def get_all_positions(self):
        positions = {}
        if not self._lv_hwnd:
            return positions
        count = win32gui.SendMessage(self._lv_hwnd, LVM_GETITEMCOUNT, 0, 0)
        hProc = self._open_proc(PROC_READ)
        if not hProc:
            return positions
        k32 = ctypes.windll.kernel32
        pPt = k32.VirtualAllocEx(hProc, None, ctypes.sizeof(ctypes.wintypes.POINT), 0x3000, 0x40)
        try:
            for i in range(count):
                win32gui.SendMessage(self._lv_hwnd, LVM_GETITEMPOSITION, i, pPt)
                pt = ctypes.wintypes.POINT()
                read = ctypes.c_size_t(0)
                k32.ReadProcessMemory(hProc, pPt, ctypes.byref(pt),
                                      ctypes.sizeof(pt), ctypes.byref(read))
                positions[i] = (pt.x, pt.y)
        finally:
            k32.VirtualFreeEx(hProc, pPt, 0, 0x8000)
            k32.CloseHandle(hProc)
        return positions

    def save_positions(self):
        self._saved_positions = self.get_all_positions()

    # ── Scrittura posizione ───────────────────────────────────

    def set_icon_position(self, idx, x, y):
        """Sposta icona con LVM_SETITEMPOSITION32 (WriteProcessMemory, 32-bit safe).
        Fallback: LVM_SETITEMPOSITION packed 16-bit.
        """
        if not self._lv_hwnd:
            return
        x, y = int(x), int(y)

        # Metodo primario: LVM_SETITEMPOSITION32 via WriteProcessMemory
        hProc = self._open_proc(PROC_WRITE)
        if hProc:
            k32 = ctypes.windll.kernel32
            pt = ctypes.wintypes.POINT(x, y)
            pPt = k32.VirtualAllocEx(hProc, None, ctypes.sizeof(pt), 0x3000, 0x40)
            if pPt:
                try:
                    written = ctypes.c_size_t(0)
                    ok = k32.WriteProcessMemory(hProc, pPt, ctypes.byref(pt),
                                                ctypes.sizeof(pt), ctypes.byref(written))
                    if ok:
                        win32gui.SendMessage(self._lv_hwnd, LVM_SETITEMPOSITION32, idx, pPt)
                finally:
                    k32.VirtualFreeEx(hProc, pPt, 0, 0x8000)
            k32.CloseHandle(hProc)

        # Fallback: metodo packed 16-bit (funziona su schermi < 32768 px)
        if x < 32768 and y < 32768:
            lparam = (y << 16) | (x & 0xFFFF)
            win32gui.SendMessage(self._lv_hwnd, LVM_SETITEMPOSITION, idx, lparam)

        # Forza ridisegno del listview
        win32gui.InvalidateRect(self._lv_hwnd, None, False)

    # ── Azioni sui gruppi ─────────────────────────────────────

    def steal_icon(self, idx):
        sw = win32api.GetSystemMetrics(78)   # SM_CXVIRTUALSCREEN
        sh = win32api.GetSystemMetrics(79)   # SM_CYVIRTUALSCREEN
        ox = win32api.GetSystemMetrics(76)   # SM_XVIRTUALSCREEN
        oy = win32api.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
        margin, taskbar_h = 80, 60
        x = random.randint(ox + margin, ox + sw - margin)
        y = random.randint(oy + margin, oy + sh - taskbar_h - margin)
        orig = self._saved_positions.get(idx)
        if orig:
            attempts = 0
            while abs(x - orig[0]) < 120 and abs(y - orig[1]) < 120 and attempts < 20:
                x = random.randint(ox + margin, ox + sw - margin)
                y = random.randint(oy + margin, oy + sh - taskbar_h - margin)
                attempts += 1
        self.set_icon_position(idx, x, y)

    def scatter_circle(self):
        sw = win32api.GetSystemMetrics(78)
        sh = win32api.GetSystemMetrics(79) - 60
        ox = win32api.GetSystemMetrics(76)
        positions = self.get_all_positions()
        cx, cy = ox + sw // 2, sh // 2
        r = min(sw, sh) // 4
        keys = list(positions.keys())
        for i, idx in enumerate(keys):
            angle = (i / max(len(keys), 1)) * 2 * math.pi
            nx = int(cx + math.cos(angle) * r)
            ny = int(cy + math.sin(angle) * r * 0.65)
            self.set_icon_position(idx, max(ox+60, min(ox+sw-60, nx)), max(60, min(sh-60, ny)))

    def scatter_chaos(self):
        sw = win32api.GetSystemMetrics(78)
        sh = win32api.GetSystemMetrics(79) - 60
        ox = win32api.GetSystemMetrics(76)
        for idx in self.get_all_positions():
            self.set_icon_position(idx, ox + random.randint(40, sw-80), random.randint(40, sh-80))

    def restore_icons(self):
        for idx, (x, y) in self._saved_positions.items():
            self.set_icon_position(idx, x, y)

    def get_open_windows(self):
        rects = []
        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and "Program Manager" not in title:
                    r = win32gui.GetWindowRect(hwnd)
                    w, h = r[2]-r[0], r[3]-r[1]
                    if w > 150 and h > 100:
                        rects.append(r)
        win32gui.EnumWindows(cb, None)
        return rects

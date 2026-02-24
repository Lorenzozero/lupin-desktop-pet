import ctypes
import ctypes.wintypes
import win32gui
import win32con
import win32api

LVM_FIRST = 0x1000
LVM_GETITEMCOUNT    = LVM_FIRST + 4
LVM_GETITEMPOSITION = LVM_FIRST + 16
LVM_SETITEMPOSITION = LVM_FIRST + 15

class DesktopHooks:
    def __init__(self):
        self._lv_hwnd = self._find_listview()
        self._saved_positions = {}

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
                result[0] = win32gui.FindWindowEx(shell, 0, "SysListView32", None)
        win32gui.EnumWindows(cb, None)
        return result[0]

    def get_all_positions(self):
        positions = {}
        if not self._lv_hwnd:
            return positions
        count = win32gui.SendMessage(self._lv_hwnd, LVM_GETITEMCOUNT, 0, 0)
        pid = ctypes.c_ulong(0)
        ctypes.windll.user32.GetWindowThreadProcessId(self._lv_hwnd, ctypes.byref(pid))
        k32 = ctypes.windll.kernel32
        hProc = k32.OpenProcess(0x1F0FFF, False, pid.value)
        if not hProc:
            return positions
        pPt = k32.VirtualAllocEx(hProc, None, ctypes.sizeof(ctypes.wintypes.POINT), 0x3000, 0x40)
        try:
            for i in range(count):
                win32gui.SendMessage(self._lv_hwnd, LVM_GETITEMPOSITION, i, pPt)
                pt = ctypes.wintypes.POINT()
                read = ctypes.c_size_t(0)
                k32.ReadProcessMemory(hProc, pPt, ctypes.byref(pt), ctypes.sizeof(pt), ctypes.byref(read))
                positions[i] = (pt.x, pt.y)
        finally:
            k32.VirtualFreeEx(hProc, pPt, 0, 0x8000)
            k32.CloseHandle(hProc)
        return positions

    def save_positions(self):
        self._saved_positions = self.get_all_positions()

    def set_icon_position(self, idx, x, y):
        if not self._lv_hwnd:
            return
        lparam = (y << 16) | (x & 0xFFFF)
        win32gui.PostMessage(self._lv_hwnd, LVM_SETITEMPOSITION, idx, lparam)

    def steal_icon(self, idx):
        sw = win32api.GetSystemMetrics(0)
        sh = win32api.GetSystemMetrics(1)
        self.set_icon_position(idx, sw + 200 + idx * 10, sh + 200)

    def restore_icons(self):
        for idx, (x, y) in self._saved_positions.items():
            self.set_icon_position(idx, x, y)
        if self._lv_hwnd:
            win32gui.SendMessage(self._lv_hwnd, win32con.WM_SETREDRAW, True, 0)

    def get_open_windows(self):
        rects = []
        def cb(hwnd, _):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title and "Program Manager" not in title and "Lupin" not in title:
                    r = win32gui.GetWindowRect(hwnd)
                    if r[2]-r[0] > 150 and r[3]-r[1] > 100:
                        rects.append(r)
        win32gui.EnumWindows(cb, None)
        return rects

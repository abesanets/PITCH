import sys
import threading
import time
from typing import Callable

_WINDOWS = sys.platform == "win32"

# Global dictionary to track physical states of keys we care about
# (updated by the low-level hook before any events are blocked)
_key_states = {
    'ctrl': False,
    'windows': False,
    'shift': False,
    'alt': False
}

def is_hook_key_pressed(key_name: str) -> bool:
    if not _WINDOWS:
        return False
    name = key_name.lower().strip()
    if 'ctrl' in name or 'control' in name:
        name = 'ctrl'
    elif 'win' in name:
        name = 'windows'
    elif 'shift' in name:
        name = 'shift'
    elif 'alt' in name:
        name = 'alt'
    return _key_states.get(name, False)

class MockEvent:
    def __init__(self, event_type: str, name: str):
        self.event_type = event_type  # "down" or "up"
        self.name = name

class WindowsKeyboardHook:
    def __init__(self, callback: Callable[[MockEvent], None]):
        self.callback = callback
        self.thread = None
        self.hook_id = None
        self.running = False
        self.win_down_blocked = False
        self._hook_proc_ref = None

    def start(self):
        if not _WINDOWS:
            return
        self.running = True
        self.thread = threading.Thread(target=self._run_hook_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if _WINDOWS and self.hook_id:
            import ctypes
            # Post a dummy message to wake up the message loop and unhook
            ctypes.windll.user32.PostThreadMessageW(self.thread.ident, 0, 0, 0)

    def _run_hook_loop(self):
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.WinDLL('user32', use_last_error=True)
        kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

        WH_KEYBOARD_LL = 13
        WM_KEYDOWN = 0x0100
        WM_KEYUP = 0x0101
        WM_SYSKEYDOWN = 0x0104
        WM_SYSKEYUP = 0x0105
        VK_LWIN = 0x5B
        VK_RWIN = 0x5C
        VK_CONTROL = 0x11
        VK_LCONTROL = 0xA2
        VK_RCONTROL = 0xA3
        VK_SHIFT = 0x10
        VK_MENU = 0x12  # Alt

        class KBDLLHOOKSTRUCT(ctypes.Structure):
            _fields_ = [
                ("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_ulonglong)
            ]

        # Define argtypes and restypes for Win32 API calls (critical for 64-bit compatibility)
        kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)

        user32.SetWindowsHookExW.restype = wintypes.HHOOK
        user32.SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]

        user32.CallNextHookEx.restype = ctypes.c_int
        user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]

        user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]

        user32.GetAsyncKeyState.restype = wintypes.SHORT
        user32.GetAsyncKeyState.argtypes = [ctypes.c_int]

        def is_ctrl_pressed() -> bool:
            return bool((user32.GetAsyncKeyState(VK_CONTROL) & 0x8000) or
                        (user32.GetAsyncKeyState(VK_LCONTROL) & 0x8000) or
                        (user32.GetAsyncKeyState(VK_RCONTROL) & 0x8000))

        def hook_callback(nCode, wParam, lParam):
            if nCode >= 0:
                kbd = ctypes.cast(lParam, ctypes.POINTER(KBDLLHOOKSTRUCT)).contents
                vk = kbd.vkCode
                
                is_down = wParam in (WM_KEYDOWN, WM_SYSKEYDOWN)
                is_up = wParam in (WM_KEYUP, WM_SYSKEYUP)
                
                # Map virtual key code to a friendly name for the engine
                key_name = ""
                if vk in (VK_LWIN, VK_RWIN):
                    key_name = "windows"
                elif vk in (VK_CONTROL, VK_LCONTROL, VK_RCONTROL):
                    key_name = "ctrl"
                elif vk in (0x10, 0xA0, 0xA1): # VK_SHIFT, VK_LSHIFT, VK_RSHIFT
                    key_name = "shift"
                elif vk in (0x12, 0xA4, 0xA5): # VK_MENU (Alt), VK_LMENU, VK_RMENU
                    key_name = "alt"
                
                was_windows_pressed = _key_states.get('windows', False) if key_name == 'windows' else False

                # Update our global state tracking
                if key_name and (is_down or is_up):
                    _key_states[key_name] = is_down
                
                # If it's a Windows key event
                if vk in (VK_LWIN, VK_RWIN):
                    if is_down:
                        # If we are already blocking Win or Ctrl is pressed, block it (including auto-repeats)
                        if self.win_down_blocked or is_ctrl_pressed():
                            self.win_down_blocked = True
                            # Notify our app only on the first down event, not auto-repeats
                            if not was_windows_pressed:
                                if key_name:
                                    self.callback(MockEvent("down", key_name))
                            return 1  # Block event propagation
                    elif is_up:
                        # If we previously blocked Win down, block Win up
                        if self.win_down_blocked:
                            self.win_down_blocked = False
                            if key_name:
                                self.callback(MockEvent("up", key_name))
                            return 1  # Block event propagation

                # Notify engine of other key events (without blocking them)
                if key_name and (is_down or is_up):
                    event_type = "down" if is_down else "up"
                    self.callback(MockEvent(event_type, key_name))

            return user32.CallNextHookEx(self.hook_id, nCode, wParam, lParam)

        # Store reference to prevent garbage collection
        self._hook_proc_ref = HOOKPROC(hook_callback)
        
        self.hook_id = user32.SetWindowsHookExW(
            WH_KEYBOARD_LL,
            self._hook_proc_ref,
            kernel32.GetModuleHandleW(None),
            0
        )

        if not self.hook_id:
            print(f"[Хук] Ошибка установки низкоуровневого хука: {ctypes.get_last_error()}")
            return

        # Message loop
        msg = wintypes.MSG()
        while self.running:
            res = user32.GetMessageW(ctypes.byref(msg), 0, 0, 0)
            if res <= 0:
                break
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        # Clean up hook
        user32.UnhookWindowsHookEx(self.hook_id)
        self.hook_id = None

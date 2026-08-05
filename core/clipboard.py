import sys
import time
import keyboard

_WINDOWS = sys.platform == "win32"
if _WINDOWS:
    import ctypes
    _GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState
else:
    _GetAsyncKeyState = None

from .keyboard_hook import is_hook_key_pressed

def is_physical_key_pressed(key_name: str) -> bool:
    """
    Checks if a key is physically pressed. On Windows, uses our keyboard hook state
    to prevent key state desynchronization (stuck keys) for blocked modifiers.
    """
    if _WINDOWS:
        return is_hook_key_pressed(key_name)
    try:
        return keyboard.is_pressed(key_name)
    except Exception:
        return False


class ClipboardManager:
    """
    Manages text pasting via Win32 SendInput.
    """
    MAX_WAIT_MS = 800

    def paste(self) -> None:
        if sys.platform != "win32":
            raise NotImplementedError("ClipboardManager.paste() is only supported on Windows (win32).")

        # Wait for physical modifier keys to be released
        timeout = time.time() + (self.MAX_WAIT_MS / 1000.0)
        while time.time() < timeout:
            if not (is_physical_key_pressed('windows') or 
                    is_physical_key_pressed('alt') or 
                    is_physical_key_pressed('ctrl') or 
                    is_physical_key_pressed('shift')):
                break
            time.sleep(0.05)

        import ctypes
        from ctypes import wintypes
        
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        
        INPUT_KEYBOARD = 1
        KEYEVENTF_KEYUP = 0x0002
        VK_CONTROL = 0x11
        VK_V = 0x56
        
        class KEYBDINPUT(ctypes.Structure):
            _fields_ = (("wVk", wintypes.WORD),
                        ("wScan", wintypes.WORD),
                        ("dwFlags", wintypes.DWORD),
                        ("time", wintypes.DWORD),
                        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong)))
        
        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = (("ki", KEYBDINPUT),
                            ("mi", ctypes.c_byte * 28),
                            ("hi", ctypes.c_byte * 32))
            _anonymous_ = ("_input",)
            _fields_ = (("type", wintypes.DWORD),
                        ("_input", _INPUT))

        inputs = [
            INPUT(INPUT_KEYBOARD, _input=INPUT._INPUT(ki=KEYBDINPUT(VK_CONTROL, 0, 0, 0, None))),
            INPUT(INPUT_KEYBOARD, _input=INPUT._INPUT(ki=KEYBDINPUT(VK_V, 0, 0, 0, None))),
            INPUT(INPUT_KEYBOARD, _input=INPUT._INPUT(ki=KEYBDINPUT(VK_V, 0, KEYEVENTF_KEYUP, 0, None))),
            INPUT(INPUT_KEYBOARD, _input=INPUT._INPUT(ki=KEYBDINPUT(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0, None))),
        ]

        LPINPUT = INPUT * len(inputs)
        pInputs = LPINPUT(*inputs)
        user32.SendInput(len(inputs), pInputs, ctypes.sizeof(INPUT))

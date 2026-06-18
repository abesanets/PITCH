import sys
import time
import keyboard

_WINDOWS = sys.platform == "win32"
if _WINDOWS:
    import ctypes
    _GetAsyncKeyState = ctypes.windll.user32.GetAsyncKeyState
else:
    _GetAsyncKeyState = None

def is_physical_key_pressed(key_name: str) -> bool:
    """
    Checks if a key is physically pressed. On Windows, uses GetAsyncKeyState
    to prevent key state desynchronization (stuck keys) for modifiers.
    """
    if not _WINDOWS or not _GetAsyncKeyState:
        try:
            return keyboard.is_pressed(key_name)
        except Exception:
            return False

    key_clean = key_name.strip().lower()

    # Map key names to Windows Virtual Key codes to read current physical hardware state
    VK_MAP = {
        'ctrl': [0x11],          # VK_CONTROL
        'control': [0x11],
        'left ctrl': [0xA2],     # VK_LCONTROL
        'right ctrl': [0xA3],    # VK_RCONTROL
        'shift': [0x10],         # VK_SHIFT
        'left shift': [0xA0],    # VK_LSHIFT
        'right shift': [0xA1],   # VK_RSHIFT
        'alt': [0x12],           # VK_MENU
        'left alt': [0xA4],      # VK_LMENU
        'right alt': [0xA5],     # VK_RMENU
        'alt gr': [0xA5],
        'windows': [0x5B, 0x5C], # VK_LWIN, VK_RWIN
        'win': [0x5B, 0x5C],
        'left windows': [0x5B],
        'right windows': [0x5C]
    }

    if key_clean in VK_MAP:
        # Most significant bit (0x8000) is set if the key is physically down
        return any(bool(_GetAsyncKeyState(vk) & 0x8000) for vk in VK_MAP[key_clean])

    try:
        return keyboard.is_pressed(key_clean)
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

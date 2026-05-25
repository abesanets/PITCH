import sys
import time
import keyboard

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
            if not (keyboard.is_pressed('windows') or 
                    keyboard.is_pressed('alt') or 
                    keyboard.is_pressed('ctrl') or 
                    keyboard.is_pressed('shift')):
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

import sys
import os

# Ensure working directory is set to application directory
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from core.config_manager import load_config
from core import PitchCore, ClipboardManager, LogRedirector, AudioRecorder
from ui import VoiceAssistant


def main():
    _mutex = ensure_single_instance()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()

    recorder = AudioRecorder()
    clipboard = ClipboardManager()

    core = PitchCore(
        config=config,
        recorder=recorder,
    )

    log_path = os.path.join(os.path.dirname(__file__), "pitch.log")
    redirector = LogRedirector(log_path)
    sys.stdout = redirector
    sys.stderr = redirector

    assistant = VoiceAssistant(core=core, clipboard=clipboard)
    sys.exit(assistant.run())


def ensure_single_instance():
    import ctypes
    MUTEX_NAME = "Global\\PITCHVoiceAssistant_SingleInstance_V3"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, True, MUTEX_NAME)
    last_error = ctypes.windll.kernel32.GetLastError()
    ERROR_ALREADY_EXISTS = 183
    if last_error == ERROR_ALREADY_EXISTS:
        ctypes.windll.user32.MessageBoxW(
            0,
            "PITCH уже запущен.\nПроверьте значок в системном трее.",
            "PITCH — уже запущен",
            0x00000040 | 0x00001000  # MB_ICONINFORMATION | MB_SYSTEMMODAL
        )
        sys.exit(0)
    return mutex


if __name__ == "__main__":
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            print("\nПрограмма корректно завершена (Ctrl+C).")
            sys.exit(0)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception
    main()

import sys
import os

# Disable progress bars globally to prevent tqdm/tkinter crashes in windowed mode
os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"
os.environ["TQDM_DISABLE"] = "1"

# Ensure working directory is set to application directory
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

from core.log_redirector import LogRedirector

# Redirect standard output and error immediately at startup
log_path = os.path.join(os.getcwd(), "pitch.log")
redirector = LogRedirector(log_path)
sys.stdout = redirector
sys.stderr = redirector

import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from core.config_manager import load_config
from core import PitchCore, ClipboardManager, AudioRecorder
from ui import VoiceAssistant


def main():
    _mutex = ensure_single_instance()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    try:
        config = load_config()
        recorder = AudioRecorder()
        clipboard = ClipboardManager()

        core = PitchCore(
            config=config,
            recorder=recorder,
        )

        assistant = VoiceAssistant(core=core, clipboard=clipboard)
        sys.exit(assistant.run())
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"[FATAL ERROR on startup]:\n{err_msg}")
        ctypes.windll.user32.MessageBoxW(
            0,
            f"Ошибка при запуске PITCH:\n\n{e}\n\nПодробности записаны в pitch.log.",
            "PITCH — Ошибка запуска",
            0x00000010 | 0x00001000  # MB_ICONERROR | MB_SYSTEMMODAL
        )
        sys.exit(1)


def ensure_single_instance():
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
        import traceback
        formatted = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"[Unhandled Exception]:\n{formatted}")
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = handle_exception
    main()

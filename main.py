import sys
import os

# Ensure the working directory is set to the application directory (critical for Windows Startup shortcut execution)
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

import time
from PyQt6.QtWidgets import QApplication
from core.config_manager import load_config
from core import PitchCore, ClipboardManager, LogRedirector, AudioRecorder
from ui import VoiceAssistant

def main():
    _mutex = ensure_single_instance()

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = load_config()

    # Create dependencies
    recorder = AudioRecorder()
    clipboard = ClipboardManager()

    # Define Groq client factory referencing core's configuration
    def make_groq_client():
        from groq import Groq
        t_client = time.time()
        client_kwargs = {"api_key": core._config["api_key"]}
        base_url = core._config.get("groq_base_url", "").strip()
        if base_url:
            if base_url.endswith("/openai/v1"):
                base_url = base_url[:-10]
                print(f"[Диагностика] Удалён /openai/v1 из base_url (SDK добавляет автоматически)")
            client_kwargs["base_url"] = base_url
            print(f"[Диагностика] Используем кастомный base_url: {base_url}")
        client = Groq(**client_kwargs)
        print(f"[Диагностика] Groq клиент готов: {time.time() - t_client:.3f}s")
        return client

    # Initialize Core
    core = PitchCore(
        config=config,
        recorder=recorder,
        groq_client_factory=make_groq_client,
    )

    # Redirect stdout/stderr to log file and UI log signal
    log_path = os.path.join(os.path.dirname(__file__), "pitch.log")
    redirector = LogRedirector(core.log_message, log_path)
    sys.stdout = redirector
    sys.stderr = redirector

    # Initialize and run UI/Assistant
    assistant = VoiceAssistant(core=core, clipboard=clipboard)
    assistant.run()

def ensure_single_instance():
    """Prevent multiple instances using a named Windows mutex.
    
    Returns the mutex handle on success (must be kept alive for the process lifetime).
    Exits the process if another instance is already running.
    """
    import ctypes
    MUTEX_NAME = "Global\\PITCHVoiceAssistant_SingleInstance"
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

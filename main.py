import sys
import os

# Ensure the working directory is set to the application directory (critical for Windows Startup shortcut execution)
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
import threading
import time
import pyperclip
import keyboard
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import pyqtSignal, QObject, Qt

from config_manager import load_config, save_config
from audio_recorder import AudioRecorder
from ui import DashboardWindow, OverlayWindow
from groq_client import process_audio_pipeline

class LogRedirector:
    def __init__(self, signal, log_file_path):
        self.signal = signal
        self.log_file_path = log_file_path
        self.stdout = sys.stdout

    def write(self, message):
        if self.stdout is not None:
            self.stdout.write(message)
        if message.strip():
            log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message.strip()}"
            try:
                with open(self.log_file_path, "a", encoding="utf-8") as f:
                    f.write(log_line + "\n")
            except Exception:
                pass
            self.signal.emit(message.strip())

    def flush(self):
        if self.stdout is not None:
            self.stdout.flush()

class WorkerSignals(QObject):
    update_volume = pyqtSignal(float)
    state_changed = pyqtSignal(str)
    processing_done = pyqtSignal(str)
    log_message = pyqtSignal(str)

class VoiceAssistant:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.signals = WorkerSignals()
        
        # Redirect stdout/stderr to log file and UI log signal
        log_file_path = os.path.join(os.path.dirname(__file__), "echo.log")
        self.signals.log_message.connect(self.on_log_message)
        self.redirector = LogRedirector(self.signals.log_message, log_file_path)
        sys.stdout = self.redirector
        sys.stderr = self.redirector
        
        self.config = load_config()
        self.overlay = OverlayWindow()
        self.overlay.set_theme(self.config.get("theme", "dark"))
        self.overlay.apply_config(self.config)
        self.update_startup_registry(self.config.get("run_on_startup", False))
        self.recorder = AudioRecorder()
        
        self.groq_client = None
        self.groq_client_lock = threading.Lock()
        self.warmup_started = False
        self.is_recording = False
        self.is_processing = False
        self.dashboard = None
        
        self.setup_signals()
        self.setup_tray()
        
        if not self.config.get("api_key"):
            self.show_settings()
        
        self.monitor_running = True
        self.monitor_thread = threading.Thread(target=self.hotkey_monitor, daemon=True)
        self.monitor_thread.start()
        self.start_background_warmup()

    def setup_signals(self):
        self.signals.update_volume.connect(self.overlay.set_volume)
        self.signals.state_changed.connect(self.overlay.set_state)
        self.signals.state_changed.connect(self.on_state_changed)
        self.signals.processing_done.connect(self.on_processing_done)

    def on_state_changed(self, state):
        if self.dashboard is not None and self.dashboard.isVisible():
            self.dashboard.set_system_state(state)

    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
        else:
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            painter.drawEllipse(0, 0, 64, 64)
            painter.end()
            self.tray.setIcon(QIcon(pixmap))
            
        self.tray.setVisible(True)
        self.tray.setToolTip("Echo (Hold Ctrl+Win to record)")
        self.tray.activated.connect(self.on_tray_activated)
        
        menu = QMenu()
        
        open_action = menu.addAction("Open Dashboard")
        open_action.triggered.connect(self.show_settings)
        
        menu.addSeparator()
        
        quit_action = menu.addAction("Quit")
        quit_action.triggered.connect(self.quit_app)
        
        self.tray.setContextMenu(menu)

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_settings()

    def show_settings(self):
        if self.dashboard is None:
            self.dashboard = DashboardWindow(self.config, self.on_settings_saved)
            self.dashboard.set_system_state(self.overlay.state)
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def on_settings_saved(self, new_config):
        if new_config.get("api_key") != self.config.get("api_key"):
            with self.groq_client_lock:
                self.groq_client = None  # Пересоздать клиент при смене API ключа
        self.config = new_config
        save_config(self.config)
        self.update_startup_registry(self.config.get("run_on_startup", False))
        self.overlay.set_theme(self.config.get("theme", "dark"))
        self.overlay.apply_config(self.config)
        self.start_background_warmup(force=True)

    def update_startup_registry(self, enabled):
        if sys.platform != "win32":
            return
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "EchoVoiceAssistant"
        
        # Determine executable path
        if getattr(sys, 'frozen', False):
            # Compiled exe mode
            exe_path = f'"{sys.executable}"'
        else:
            # Script development mode
            script_path = os.path.abspath(sys.argv[0])
            exe_path = f'"{sys.executable}" "{script_path}"'
            
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, exe_path)
                print(f"Registry: registered {app_name} at {exe_path} for startup")
            else:
                try:
                    winreg.DeleteValue(key, app_name)
                    print(f"Registry: unregistered {app_name} from startup")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            print(f"Registry: error updating startup: {e}")

    def on_log_message(self, message):
        if self.dashboard is not None and self.dashboard.isVisible():
            self.dashboard.append_log(message)

    def start_background_warmup(self, force=False):
        if self.warmup_started and not force:
            return
        if not self.config.get("api_key"):
            return

        self.warmup_started = True
        threading.Thread(target=self.background_warmup, daemon=True).start()

    def background_warmup(self):
        try:
            self.get_groq_client()
        except Exception as e:
            print(f"[Предупреждение] Не удалось прогреть Groq клиент: {e}")

    def get_groq_client(self):
        with self.groq_client_lock:
            if self.groq_client is None:
                from groq import Groq
                t_client = time.time()
                self.groq_client = Groq(api_key=self.config["api_key"])
                print(f"[Диагностика] Groq клиент готов: {time.time() - t_client:.3f}s")
            return self.groq_client

    def hotkey_monitor(self):
        was_pressed = False
        while self.monitor_running:
            hotkey = self.config.get("hotkey", "ctrl+windows")
            
            # Force replace old hotkeys if they're still in the config
            if hotkey in ["left alt+space", "f8"]:
                hotkey = "ctrl+windows"
                
            try:
                if self.config.get("api_key") and not self.is_processing:
                    hotkey_pressed = keyboard.is_pressed(hotkey)
                    if hotkey_pressed:
                        if not was_pressed:
                            was_pressed = True
                            self.start_recording()
                    else:
                        if was_pressed:
                            was_pressed = False
                            self.stop_recording()
            except Exception as e:
                print(f"Hotkey error: {e}")
            time.sleep(0.05)

    def volume_callback(self, vol):
        self.signals.update_volume.emit(vol)

    def start_recording(self):
        if self.is_recording or self.is_processing: return
        self.is_recording = True
        self.signals.state_changed.emit("recording")
        self.recorder.start_recording(volume_callback=self.volume_callback)

    def stop_recording(self):
        if not self.is_recording: return
        self.is_recording = False
        self.is_processing = True
        self.signals.state_changed.emit("processing")
        
        filename = self.recorder.stop_recording()
        
        if filename:
            model = self.config.get("text_model", "llama-3.3-70b-versatile")
            threading.Thread(target=self.process_audio_thread, args=(filename, model), daemon=True).start()
        else:
            self.signals.state_changed.emit("idle")
            self.is_processing = False

    def process_audio_thread(self, filename, text_model):
        client = self.get_groq_client()
        result = process_audio_pipeline(filename, self.config["api_key"], text_model, client=client)
        if isinstance(result, dict):
            import history_manager
            history_manager.add_history_entry(
                model=text_model,
                raw_text=result["raw_text"],
                cleaned_text=result["text"],
                whisper_latency=result["whisper_latency"],
                llm_latency=result["llm_latency"]
            )
            self.signals.processing_done.emit(result["text"])
        else:
            self.signals.processing_done.emit(result)

    def on_processing_done(self, text):
        self.signals.state_changed.emit("idle")
        self.is_processing = False
        
        if text and not text.startswith("Error:"):
            # Backup to clipboard
            pyperclip.copy(text)
            
            # Wait for physical key release just in case
            timeout = time.time() + 0.8
            while time.time() < timeout:
                if not keyboard.is_pressed('windows') and not keyboard.is_pressed('alt') and not keyboard.is_pressed('ctrl') and not keyboard.is_pressed('shift'):
                    break
                time.sleep(0.05)
            
            self.paste_from_clipboard()

        elif text.startswith("Error:"):
            print(text)

    def paste_from_clipboard(self):
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

    def quit_app(self):
        self.monitor_running = False
        self.recorder.close()
        self.tray.hide()
        self.app.quit()

    def run(self):
        print("\n" + "="*50)
        print("🎙️  Echo: Minimalist Voice Assistant запущен!")
        print("👉  Удерживайте Ctrl+Win для диктовки.")
        print("⚙️   Дважды кликните по иконке в трее, чтобы открыть Dashboard.")
        print("="*50 + "\n")
        
        self.app.exec()

if __name__ == "__main__":
    import sys
    
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            print("\nПрограмма корректно завершена (Ctrl+C).")
            sys.exit(0)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        
    sys.excepthook = handle_exception

    app = VoiceAssistant()
    app.run()

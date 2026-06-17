import sys
import os
import subprocess
import pyperclip
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush
from PyQt6.QtCore import Qt

from core.config_manager import load_config, save_config
from ..visualizer.widgets import OverlayWindow
from .dashboard import DashboardWindow
from core.engine import PitchCore
from core.clipboard import ClipboardManager
from core.startup import update_startup_registry

class VoiceAssistant:
    """UI layer for PITCH: tray, dashboard, and signal bindings."""
    def __init__(self, core: PitchCore, clipboard: ClipboardManager):
        self.app = QApplication.instance()
        self.core = core
        self.clipboard = clipboard
        
        self.config = load_config()
        self.overlay = OverlayWindow()
        self.overlay.set_theme(self.config.get("theme", "dark"))
        self.overlay.apply_config(self.config)
        
        update_startup_registry(self.config.get("run_on_startup", False))
        
        self.dashboard = None
        
        self.setup_signals()
        self.setup_tray()
        
        if not self.config.get("api_key"):
            self.show_settings()
            
        # Optional: trigger background warmup of Groq client
        if self.config.get("api_key"):
            import threading
            threading.Thread(target=self.core._get_groq_client, daemon=True).start()

    def setup_signals(self):
        self.core.volume_changed.connect(self.overlay.set_volume)
        self.core.state_changed.connect(self.overlay.set_state)
        self.core.state_changed.connect(self.on_state_changed)
        self.core.processing_done.connect(self.on_processing_done)
        self.core.log_message.connect(self.on_log_message)

    def on_state_changed(self, state):
        if self.dashboard is not None and self.dashboard.isVisible():
            try:
                self.dashboard.set_system_state(state)
            except Exception:
                pass

    def setup_tray(self):
        self.tray = QSystemTrayIcon()
        
        # Use theme-appropriate icon for tray
        icon_name = "p.jpeg"
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, 'assets', icon_name)
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
        self.tray.setToolTip("PITCH (Hold Ctrl+Win to record)")
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
            # Connect restart signal
            self.dashboard.restart_requested.connect(self.restart_app)
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()

    def on_settings_saved(self, new_config):
        self.config = new_config
        save_config(self.config)
        self.core.update_config(new_config)
        update_startup_registry(self.config.get("run_on_startup", False))
        
        self.overlay.set_theme(self.config.get("theme", "dark"))
        self.overlay.apply_config(self.config)
        
        # Update tray icon when theme changes
        icon_name = "p.jpeg"
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        icon_path = os.path.join(base_dir, 'assets', icon_name)
        if os.path.exists(icon_path):
            self.tray.setIcon(QIcon(icon_path))
            
        if self.config.get("api_key"):
            import threading
            threading.Thread(target=self.core._get_groq_client, daemon=True).start()

    def on_log_message(self, message):
        if self.dashboard is not None and self.dashboard.isVisible():
            try:
                self.dashboard.append_log(message)
            except Exception:
                pass

    def on_processing_done(self, text):
        if text and not text.startswith("Error:"):
            # Backup to clipboard
            pyperclip.copy(text)
            self.clipboard.paste()
        elif text.startswith("Error:"):
            print(text)

    def quit_app(self):
        self.core._monitor_running = False
        self.core._recorder.close()
        self.tray.hide()
        self.app.quit()

    def restart_app(self):
        """Restart the application with the same arguments"""
        print("[Перезапуск] Перезапуск приложения...")
        
        if self.dashboard:
            self.dashboard.close()
        self.tray.hide()
        
        try:
            if getattr(sys, 'frozen', False):
                exe = sys.executable
                subprocess.Popen([exe])
            else:
                script_path = os.path.abspath(sys.argv[0])
                subprocess.Popen([sys.executable, script_path])
            print("[Перезапуск] Новая instance запущена")
        except Exception as e:
            print(f"[Перезапуск] Ошибка запуска: {e}")
        
        self.core._monitor_running = False
        self.core._recorder.close()
        self.app.quit()

    def run(self):
        print("\n" + "="*50)
        print("🎙️  PITCH: Minimalist Voice Assistant запущен!")
        print("👉  Удерживайте Ctrl+Win для диктовки.")
        print("⚙️   Дважды кликните по иконке в трее, чтобы открыть Dashboard.")
        print("="*50 + "\n")
        
        self.app.exec()

import os
import time
import threading
from typing import Callable
import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

from .audio_recorder import AudioRecorder
from .groq_worker import GroqWorker
from . import history_manager

class PitchCore(QObject):
    """
    Core business logic of PITCH. Does not contain any PyQt6 widgets.
    """
    volume_changed = pyqtSignal(float)
    state_changed = pyqtSignal(str)
    processing_done = pyqtSignal(str)

    def __init__(
        self,
        config: dict,
        recorder: AudioRecorder,
        groq_client_factory: Callable,
    ) -> None:
        super().__init__()
        
        if config is None:
            raise TypeError("config is a required parameter")
        if recorder is None:
            raise TypeError("recorder is a required parameter")
        if groq_client_factory is None:
            raise TypeError("groq_client_factory is a required parameter")
            
        self._config = config
        self._recorder = recorder
        self._groq_client_factory = groq_client_factory
        
        self._groq_client = None
        self._groq_client_lock = threading.Lock()
        
        self._is_recording = False
        self._is_processing = False
        self._recording_start_time = None
        self._current_mode = None
        self._active_hotkey = None
        
        # Event-driven keyboard hook
        self.__monitor_running = True
        self._keyboard_hook = keyboard.hook(self._on_keyboard_event)

    @property
    def _monitor_running(self) -> bool:
        return self.__monitor_running

    @_monitor_running.setter
    def _monitor_running(self, value: bool) -> None:
        self.__monitor_running = value
        if not value and hasattr(self, '_keyboard_hook') and self._keyboard_hook is not None:
            try:
                keyboard.unhook(self._keyboard_hook)
                self._keyboard_hook = None
            except Exception:
                pass

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @property
    def is_processing(self) -> bool:
        return self._is_processing

    def start_recording(self, mode: str | None = None) -> None:
        if self._is_recording or self._is_processing:
            return
        self._current_mode = mode
        self._is_recording = True
        self._recording_start_time = time.time()
        self.state_changed.emit("recording")
        self._recorder.start_recording(volume_callback=self._volume_callback)

    def stop_recording(self) -> None:
        if not self._is_recording:
            return
        self._is_recording = False
        
        min_duration = self._config.get("min_recording_duration", 0.5)
        duration = time.time() - (self._recording_start_time or 0)
        self._recorder.stop_recording()

        if duration < min_duration and min_duration > 0:
            print(f"[Запись] Слишком короткая запись ({duration:.2f}s < {min_duration}s), игнорируем.")
            self.state_changed.emit("idle")
            return

        self._is_processing = True
        self.state_changed.emit("processing")

        filename = self._recorder.get_temp_filename()
        if not os.path.exists(filename):
            self.state_changed.emit("idle")
            self._is_processing = False
            return

        # Use the specific mode active during recording, or fallback to the dashboard's current selection
        worker_config = self._config.copy()
        if self._current_mode:
            worker_config["formatting_style"] = self._current_mode
        else:
            # Fallback to the globally selected dashboard style if recording was triggered manually/by other means
            worker_config["formatting_style"] = self._config.get("formatting_style", "default")

        client = self._get_groq_client()
        self._worker = GroqWorker(filename, worker_config, client)
        self._worker.result_ready.connect(self._on_worker_result)
        self._worker.error_occurred.connect(self._on_worker_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def update_config(self, config: dict) -> None:
        # Check if client needs reset
        old_api_key = self._config.get("api_key")
        old_base_url = self._config.get("groq_base_url")
        
        new_api_key = config.get("api_key")
        new_base_url = config.get("groq_base_url")
        
        if old_api_key != new_api_key or old_base_url != new_base_url:
            with self._groq_client_lock:
                self._groq_client = None
                
        self._config = config

    def _get_groq_client(self):
        with self._groq_client_lock:
            if self._groq_client is None:
                self._groq_client = self._groq_client_factory()
            return self._groq_client

    def _volume_callback(self, vol: float) -> None:
        self.volume_changed.emit(vol)

    def _is_hotkey_active(self, hotkey_str: str) -> bool:
        if not hotkey_str:
            return False
        parts = [p.strip().lower() for p in hotkey_str.split('+')]
        if not parts:
            return False
        try:
            for part in parts:
                if not keyboard.is_pressed(part):
                    return False
            
            # Exclusion check for other modifier keys to avoid conflicts
            modifiers = {
                'ctrl': ['ctrl', 'left ctrl', 'right ctrl'],
                'alt': ['alt', 'left alt', 'right alt'],
                'shift': ['shift', 'left shift', 'right shift'],
                'windows': ['windows', 'win', 'left windows', 'right windows']
            }
            
            expected_mods = set()
            for part in parts:
                for mod_name, aliases in modifiers.items():
                    if part in aliases:
                        expected_mods.add(mod_name)
                        break
            
            for mod_name, aliases in modifiers.items():
                if mod_name not in expected_mods:
                    for alias in aliases:
                        if keyboard.is_pressed(alias):
                            return False
            return True
        except Exception:
            return False

    def _on_keyboard_event(self, event) -> None:
        if not self.__monitor_running or not self._config.get("api_key") or self._is_processing:
            return

        h1 = self._config.get("hotkey_1", "ctrl+windows")
        h2_enabled = self._config.get("hotkey_2_enabled", False)
        h2 = self._config.get("hotkey_2", "shift+windows") if h2_enabled else None

        # Run migration compatibility just in case
        if h1 in ["left alt+space", "f8"]:
            h1 = "ctrl+windows"

        try:
            if not self._is_recording:
                # Check if either hotkey is pressed
                if self._is_hotkey_active(h1):
                    self._active_hotkey = 'hotkey_1'
                    mode = self._config.get("mode_1", "default")
                    self.start_recording(mode)
                elif h2 and self._is_hotkey_active(h2):
                    self._active_hotkey = 'hotkey_2'
                    mode = self._config.get("mode_2", "translate_en")
                    self.start_recording(mode)
            else:
                # Recording is active. Check if the triggering hotkey has been released
                target_hotkey_str = h1 if self._active_hotkey == 'hotkey_1' else h2
                if not target_hotkey_str or not self._is_hotkey_active(target_hotkey_str):
                    self.stop_recording()
                    self._active_hotkey = None
        except Exception as e:
            print(f"Hotkey event handler error: {e}")

    def _on_worker_result(self, result: dict) -> None:
        text_model = self._config.get("text_model", "llama-3.3-70b-versatile")
        try:
            history_manager.add_history_entry(
                model=text_model,
                raw_text=result["raw_text"],
                cleaned_text=result["text"],
                whisper_latency=result["whisper_latency"],
                llm_latency=result["llm_latency"]
            )
        except Exception as e:
            print(f"Error saving history: {e}")
            
        self._is_processing = False
        self.state_changed.emit("idle")
        self.processing_done.emit(result["text"])

    def _on_worker_error(self, error: str) -> None:
        self._is_processing = False
        self.state_changed.emit("idle")
        if error.startswith("Error:"):
            self.processing_done.emit(error)
        else:
            self.processing_done.emit(f"Error: {error}")

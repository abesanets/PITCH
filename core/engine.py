import os
import time
import threading
from typing import Callable
import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

from audio_recorder import AudioRecorder
from core.groq_worker import GroqWorker
import history_manager

class PitchCore(QObject):
    """
    Core business logic of PITCH. Does not contain any PyQt6 widgets.
    """
    volume_changed = pyqtSignal(float)
    state_changed = pyqtSignal(str)
    processing_done = pyqtSignal(str)
    log_message = pyqtSignal(str)

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
        
        # Hotkey monitor thread
        self._monitor_running = True
        self._monitor_thread = threading.Thread(target=self._hotkey_monitor, daemon=True)
        self._monitor_thread.start()

    @property
    def is_recording(self) -> bool:
        return self._is_recording

    @property
    def is_processing(self) -> bool:
        return self._is_processing

    def start_recording(self) -> None:
        if self._is_recording or self._is_processing:
            return
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

        client = self._get_groq_client()
        self._worker = GroqWorker(filename, self._config, client)
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

    def _hotkey_monitor(self) -> None:
        was_pressed = False
        while self._monitor_running:
            hotkey = self._config.get("hotkey", "ctrl+windows")
            
            # Force replace old hotkeys if they're still in the config
            if hotkey in ["left alt+space", "f8"]:
                hotkey = "ctrl+windows"
                
            try:
                if self._config.get("api_key") and not self._is_processing:
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

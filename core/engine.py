import time
import sys
from typing import Any
import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

from .audio_recorder import AudioRecorder
from .stt_engine import GigaAMEngine
from .stt_worker import STTWorker
from . import history_manager
from .clipboard import is_physical_key_pressed
from .keyboard_hook import WindowsKeyboardHook


class PitchCore(QObject):
    """
    Core business logic of PITCH using local GigaAM v3 STT.
    """
    volume_changed = pyqtSignal(float)
    state_changed = pyqtSignal(str)
    processing_started = pyqtSignal(float, float)  # audio_duration, avg_rtf
    processing_done = pyqtSignal(str)

    _request_start_recording = pyqtSignal(str)
    _request_stop_recording = pyqtSignal()

    def __init__(
        self,
        config: dict,
        recorder: AudioRecorder,
        stt_engine: GigaAMEngine | None = None,
    ) -> None:
        super().__init__()

        if config is None:
            raise TypeError("config is a required parameter")
        if recorder is None:
            raise TypeError("recorder is a required parameter")

        self._config = config
        self._recorder = recorder
        self._stt_engine = stt_engine or GigaAMEngine(
            model_name=config.get("stt_model", "gigaam-v3-e2e-rnnt"),
        )

        self._is_recording = False
        self._is_processing = False
        self._hook_recording = False
        self._recording_start_time = None
        self._current_mode = None
        self._active_hotkey = None
        self._keyboard_hook: Any = None

        self._request_start_recording.connect(self.start_recording)
        self._request_stop_recording.connect(self.stop_recording)

        self.__monitor_running = True
        if sys.platform == "win32":
            self._keyboard_hook = WindowsKeyboardHook(
                self._on_keyboard_event,
                is_processing_callback=lambda: self._is_processing or self._is_recording,
            )
            self._keyboard_hook.start()
        else:
            self._keyboard_hook = keyboard.hook(self._on_keyboard_event)

    @property
    def _monitor_running(self) -> bool:
        return self.__monitor_running

    @_monitor_running.setter
    def _monitor_running(self, value: bool) -> None:
        self.__monitor_running = value
        if not value and hasattr(self, "_keyboard_hook") and self._keyboard_hook is not None:
            try:
                if sys.platform == "win32":
                    self._keyboard_hook.stop()
                else:
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
        self._hook_recording = False
        if not self._is_recording:
            return
        self._is_recording = False

        min_duration = self._config.get("min_recording_duration", 0.4)
        audio_np, duration = self._recorder.stop_recording()

        if duration < min_duration and min_duration > 0:
            print(f"[Запись] Слишком короткая запись ({duration:.2f}s < {min_duration}s), игнорируем.")
            self.state_changed.emit("idle")
            return

        if audio_np is None or len(audio_np) == 0:
            self.state_changed.emit("idle")
            return

        self._is_processing = True
        self.state_changed.emit("processing")

        try:
            avg_rtf = history_manager.get_cached_avg_rtf()
            if not avg_rtf or avg_rtf <= 0:
                avg_rtf = 0.15
        except Exception:
            avg_rtf = 0.15

        self.processing_started.emit(duration, avg_rtf)

        self._worker = STTWorker(audio_np, duration, self._stt_engine)
        self._worker.result_ready.connect(self._on_worker_result)
        self._worker.error_occurred.connect(self._on_worker_error)
        self._worker.finished.connect(self._worker.deleteLater)
        self._worker.start()

    def update_config(self, config: dict) -> None:
        self._config = config

    def _volume_callback(self, vol: float) -> None:
        self.volume_changed.emit(vol)

    def _is_hotkey_active(self, hotkey_str: str) -> bool:
        if not hotkey_str:
            return False
        parts = [p.strip().lower() for p in hotkey_str.split("+")]
        if not parts:
            return False
        try:
            for part in parts:
                if not is_physical_key_pressed(part):
                    return False
            return True
        except Exception:
            return False

    def cancel_processing(self) -> None:
        if not self._is_processing:
            return
        print("[Отмена] Обработка отменена пользователем (Escape).")
        self._is_processing = False
        if hasattr(self, "_worker") and self._worker is not None:
            try:
                self._worker.cancel()
            except Exception:
                pass
        self.state_changed.emit("idle")

    def _on_keyboard_event(self, event) -> None:
        if not self.__monitor_running:
            return

        if self._is_processing:
            if event.name == "escape" and event.event_type == "down":
                self.cancel_processing()
            return

        h1 = self._config.get("hotkey_1", "ctrl+windows")
        try:
            if not self._hook_recording:
                if self._is_hotkey_active(h1):
                    self._hook_recording = True
                    self._request_start_recording.emit("raw")
            else:
                if not self._is_hotkey_active(h1) or event.event_type == "up":
                    if not self._is_hotkey_active(h1):
                        self._hook_recording = False
                        self._request_stop_recording.emit()
        except Exception as e:
            print(f"Hotkey event handler error: {e}")

    def _on_worker_result(self, result: dict) -> None:
        actual_model = result.get("model_used", "gigaam-v3-e2e-rnnt")
        try:
            history_manager.add_history_entry(
                model=actual_model,
                text=result["text"],
                stt_latency=result["stt_latency"],
                rtf=result.get("rtf", 0.0),
                audio_duration=result.get("audio_duration", 0.0),
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

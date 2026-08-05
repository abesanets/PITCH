from PyQt6.QtCore import QThread, pyqtSignal


class STTWorker(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_data, audio_duration: float, engine):
        super().__init__()
        self.audio_data = audio_data
        self.audio_duration = audio_duration
        self.engine = engine
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        if self._is_cancelled:
            return

        try:
            text, latency = self.engine.transcribe(self.audio_data)
            if self._is_cancelled:
                return

            rtf = round(latency / self.audio_duration, 3) if self.audio_duration > 0 else 0.0

            self.result_ready.emit({
                "text": text,
                "stt_latency": round(latency, 3),
                "audio_duration": round(self.audio_duration, 2),
                "rtf": rtf,
                "model_used": self.engine.model_name,
            })
        except Exception as e:
            if not self._is_cancelled:
                self.error_occurred.emit(str(e))

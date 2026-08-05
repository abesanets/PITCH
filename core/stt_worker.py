from PyQt6.QtCore import QThread, pyqtSignal


class STTWorker(QThread):
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, audio_source, engine):
        super().__init__()
        self.audio_source = audio_source
        self.engine = engine
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        if self._is_cancelled:
            return

        try:
            raw_text, text, latency = self.engine.transcribe(self.audio_source)
            if self._is_cancelled:
                return

            self.result_ready.emit({
                "raw_text": raw_text,
                "text": text,
                "whisper_latency": round(latency, 3),
                "llm_latency": 0.0,
                "model_used": self.engine.model_name,
            })
        except Exception as e:
            if not self._is_cancelled:
                self.error_occurred.emit(str(e))

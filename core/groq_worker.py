from PyQt6.QtCore import QThread, pyqtSignal
from .groq_client import process_audio_pipeline

class GroqWorker(QThread):
    """
    QThread worker for executing the process_audio_pipeline in a separate thread.
    """
    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, file_path: str, config: dict, groq_client, parent=None) -> None:
        super().__init__(parent)
        self.file_path = file_path
        self.config = config
        self.groq_client = groq_client

    def run(self) -> None:
        try:
            text_model = self.config.get("text_model", "llama-3.3-70b-versatile")
            use_raw = self.config.get("use_raw_whisper", False)
            base_url = self.config.get("groq_base_url", "").strip()
            filter_hall = self.config.get("filter_hallucinations", True)
            api_key = self.config.get("api_key", "")
            formatting_style = self.config.get("formatting_style", "default")
            custom_formatting_style = self.config.get("custom_formatting_style", "")
            
            result = process_audio_pipeline(
                self.file_path,
                api_key,
                text_model,
                client=self.groq_client,
                use_raw_whisper=use_raw,
                base_url=base_url,
                filter_hallucinations=filter_hall,
                formatting_style=formatting_style,
                custom_formatting_style=custom_formatting_style
            )
            
            if isinstance(result, dict):
                self.result_ready.emit(result)
            else:
                # If process_audio_pipeline returns a string (e.g. error message),
                # wrap it or emit error depending on its content
                if isinstance(result, str) and result.startswith("Error:"):
                    self.error_occurred.emit(result)
                else:
                    self.result_ready.emit({"text": str(result), "raw_text": str(result), "whisper_latency": 0.0, "llm_latency": 0.0})
        except Exception as e:
            self.error_occurred.emit(str(e))

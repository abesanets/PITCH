import time
from typing import Literal, Any, cast
import numpy as np
import onnx_asr

SampleRates = Literal[8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000]


class GigaAMEngine:
    def __init__(self, model_name: str = "gigaam-v3-e2e-rnnt", sample_rate: SampleRates = 16000):
        self.sample_rate: SampleRates = sample_rate
        self.model_name = model_name

        print(f"[GigaAM Engine] Loading STT model '{model_name}' & Silero VAD...")
        t0 = time.time()
        self.model = onnx_asr.load_model(model_name)
        self.vad = onnx_asr.load_vad("silero")
        self.rec = self.model.with_vad(self.vad)
        print(f"[GigaAM Engine] Loaded in {time.time() - t0:.2f}s.")

        print("[GigaAM Engine] Performing CPU warmup...")
        warmup_audio = np.zeros(self.sample_rate * 2, dtype=np.float32)
        list(self.rec.recognize(cast(Any, warmup_audio), sample_rate=self.sample_rate))
        print("[GigaAM Engine] Warmup complete.")

    def transcribe(self, audio_data: np.ndarray | str) -> tuple[str, float]:
        if audio_data is None:
            return "", 0.0

        t0 = time.time()
        if isinstance(audio_data, str):
            import soundfile as sf
            audio_array, _ = sf.read(audio_data, dtype="float32")
        else:
            audio_array = audio_data

        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)

        segments = list(self.rec.recognize(cast(Any, audio_array), sample_rate=self.sample_rate))
        latency = time.time() - t0

        text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])
        return text, latency

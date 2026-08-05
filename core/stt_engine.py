import time
import numpy as np
import onnx_asr
from .postprocessor import TermPostprocessor


class GigaAMEngine:
    def __init__(self, model_name="gigaam-v3-e2e-rnnt", sample_rate=16000, corrections_path="corrections.json"):
        self.sample_rate = sample_rate
        self.model_name = model_name
        self.postprocessor = TermPostprocessor(corrections_path=corrections_path)

        print(f"[GigaAM Engine] Loading STT model '{model_name}' & Silero VAD...")
        t0 = time.time()
        self.model = onnx_asr.load_model(model_name)
        self.vad = onnx_asr.load_vad("silero")
        self.rec = self.model.with_vad(self.vad)
        print(f"[GigaAM Engine] Loaded in {time.time() - t0:.2f}s.")

        print("[GigaAM Engine] Performing CPU warmup...")
        warmup_audio = np.zeros(self.sample_rate * 2, dtype=np.float32)
        list(self.rec.recognize(warmup_audio, sample_rate=self.sample_rate))
        print("[GigaAM Engine] Warmup complete.")

    def transcribe(self, audio_data) -> tuple[str, str, float]:
        if audio_data is None:
            return "", "", 0.0

        t0 = time.time()
        # Accept either filename str or numpy array
        if isinstance(audio_data, str):
            import soundfile as sf
            audio_array, _ = sf.read(audio_data, dtype="float32")
        else:
            audio_array = audio_data

        if audio_array.dtype != np.float32:
            audio_array = audio_array.astype(np.float32)

        segments = list(self.rec.recognize(audio_array, sample_rate=self.sample_rate))
        latency = time.time() - t0

        raw_text = " ".join([seg.text.strip() for seg in segments if seg.text.strip()])
        final_text = self.postprocessor.process_text(raw_text)

        return raw_text, final_text, latency

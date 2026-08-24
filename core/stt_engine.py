import os
import sys
import time
from pathlib import Path
from typing import Literal, Any, cast
import numpy as np
import onnx_asr

# Disable progress bars globally to avoid TTY/tqdm crashes in GUI mode
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
os.environ.setdefault("TQDM_DISABLE", "1")

SampleRates = Literal[8000, 11025, 16000, 22050, 24000, 32000, 44100, 48000]


def get_local_model_path(folder_name: str) -> Path | None:
    candidates: list[Path] = []

    # 1. PyInstaller bundled data directory (sys._MEIPASS / _internal)
    if hasattr(sys, "_MEIPASS"):
        meipass = Path(sys._MEIPASS)
        candidates.append(meipass / "models" / folder_name)
        candidates.append(meipass / folder_name)

    # 2. Executable base directory and _internal subfolder (if frozen)
    if getattr(sys, "frozen", False):
        exe_dir = Path(sys.executable).resolve().parent
        candidates.append(exe_dir / "_internal" / "models" / folder_name)
        candidates.append(exe_dir / "models" / folder_name)
    else:
        # 3. Source directory (development mode)
        project_root = Path(__file__).resolve().parent.parent
        candidates.append(project_root / "models" / folder_name)

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


class GigaAMEngine:
    def __init__(self, model_name: str = "gigaam-v3-e2e-rnnt", sample_rate: SampleRates = 16000):
        self.sample_rate: SampleRates = sample_rate
        self.model_name = model_name

        local_model_path = get_local_model_path(model_name)
        local_vad_path = get_local_model_path("silero")

        if local_model_path:
            print(f"[GigaAM Engine] Loading STT model from local path: '{local_model_path}'...")
        else:
            print(f"[GigaAM Engine] Loading STT model '{model_name}' (system cache / online)...")

        t0 = time.time()
        self.model = onnx_asr.load_model(model_name, path=local_model_path)

        if local_vad_path:
            print(f"[GigaAM Engine] Loading Silero VAD from local path: '{local_vad_path}'...")
        else:
            print("[GigaAM Engine] Loading Silero VAD (system cache / online)...")

        self.vad = onnx_asr.load_vad("silero", path=local_vad_path)
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

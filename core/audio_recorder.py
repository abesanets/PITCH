import sounddevice as sd
import numpy as np
import threading


class AudioRecorder:
    def __init__(self, samplerate=16000, channels=1):
        self.samplerate = samplerate
        self.channels = channels
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.volume_callback = None
        self.lock = threading.Lock()

    def callback(self, indata, frames, time, status):
        if status:
            pass

        data = indata.copy()
        if self.recording:
            with self.lock:
                self.audio_data.append(data)
            if self.volume_callback:
                volume = np.linalg.norm(indata) / np.sqrt(len(indata))
                volume = min(1.0, volume * 14)
                self.volume_callback(volume)

    def _open_stream(self):
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            callback=self.callback
        )
        self.stream.start()

    def start_recording(self, volume_callback=None):
        self.volume_callback = volume_callback
        with self.lock:
            self.audio_data = []

        self.recording = True

        def _open_async():
            try:
                self._open_stream()
            except Exception:
                try:
                    self.close()
                except Exception:
                    pass
                try:
                    self._open_stream()
                except Exception:
                    self.recording = False
                    return
            if not self.recording:
                self.close()

        threading.Thread(target=_open_async, daemon=True).start()

    def stop_recording(self) -> tuple[np.ndarray | None, float]:
        """
        Stops recording and returns the normalized float32 audio numpy array
        directly in RAM alongside the calculated duration in seconds.
        """
        self.recording = False
        self.close()

        with self.lock:
            audio_chunks = self.audio_data
            self.audio_data = []

        if not audio_chunks:
            return None, 0.0

        audio_np = np.concatenate(audio_chunks, axis=0).flatten()

        max_val = np.max(np.abs(audio_np))
        if max_val > 0.001:
            audio_np = (audio_np / max_val * 0.9).astype(np.float32)

        duration = float(len(audio_np)) / float(self.samplerate)
        return audio_np, duration

    def close(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            finally:
                self.stream = None

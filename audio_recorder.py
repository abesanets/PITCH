import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import tempfile
import os

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
            pass # Handle errors if necessary
            
        data = indata.copy()
        if self.recording:
            with self.lock:
                self.audio_data.append(data)
            if self.volume_callback:
                volume = np.linalg.norm(indata) / np.sqrt(len(indata))
                # Decrease sensitivity further as requested
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

        try:
            self._open_stream()
        except Exception:
            self.close()
            self._open_stream()

        self.recording = True

    def stop_recording(self):
        self.recording = False
        self.close()

        with self.lock:
            audio_chunks = self.audio_data
            self.audio_data = []

        if not audio_chunks:
            return None
            
        audio_np = np.concatenate(audio_chunks, axis=0)
        
        # Normalize audio volume (peak at 0.9) to boost quiet voices and improve Whisper recognition
        max_val = np.max(np.abs(audio_np))
        if max_val > 0.001:
            audio_np = audio_np / max_val * 0.9
            
        temp_dir = tempfile.gettempdir()
        file_path = os.path.join(temp_dir, "voice_assistant_temp.wav")
        
        # Save as standard 16-bit PCM WAV for maximum compatibility and smaller file size
        sf.write(file_path, audio_np, self.samplerate, subtype='PCM_16')
        return file_path

    def get_temp_filename(self):
        return os.path.join(tempfile.gettempdir(), "voice_assistant_temp.wav")

    def close(self):
        if self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            finally:
                self.stream = None

import sys
import time
from PyQt6.QtCore import pyqtBoundSignal

class LogRedirector:
    """
    Redirects sys.stdout and sys.stderr, duplicating output to original stdout,
    writing to a file with timestamps, and emitting a Qt signal without timestamps.
    """
    def __init__(self, signal: pyqtBoundSignal, log_file_path: str) -> None:
        self._signal = signal
        self._log_file_path = log_file_path
        self._original_stdout = sys.stdout

    def write(self, message: str) -> None:
        if self._original_stdout is not None:
            self._original_stdout.write(message)
        
        stripped_message = message.strip()
        if stripped_message:
            log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {stripped_message}"
            try:
                with open(self._log_file_path, "a", encoding="utf-8") as f:
                    f.write(log_line + "\n")
            except Exception:
                pass
            self._signal.emit(stripped_message)

    def flush(self) -> None:
        if self._original_stdout is not None:
            self._original_stdout.flush()

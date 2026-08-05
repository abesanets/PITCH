import sys
import time

import threading

class LogRedirector:
    """
    Redirects sys.stdout and sys.stderr, duplicating output to original stdout,
    and writing to a file with timestamps.
    """
    def __init__(self, log_file_path: str) -> None:
        self._log_file_path = log_file_path
        self._original_stdout = sys.stdout
        self._lock = threading.Lock()

    def write(self, message: str) -> None:
        if self._original_stdout is not None:
            self._original_stdout.write(message)
        
        stripped_message = message.strip()
        if stripped_message:
            log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {stripped_message}"
            with self._lock:
                try:
                    with open(self._log_file_path, "a", encoding="utf-8") as f:
                        f.write(log_line + "\n")
                except Exception:
                    pass

    def flush(self) -> None:
        if self._original_stdout is not None:
            self._original_stdout.flush()

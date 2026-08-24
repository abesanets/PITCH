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

    encoding: str = "utf-8"

    def write(self, message: str) -> int:
        if self._original_stdout is not None:
            try:
                self._original_stdout.write(message)
            except Exception:
                pass

        stripped_message = message.strip()
        if stripped_message:
            log_line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {stripped_message}"
            with self._lock:
                try:
                    with open(self._log_file_path, "a", encoding="utf-8") as f:
                        f.write(log_line + "\n")
                except Exception:
                    pass
        return len(message)

    def flush(self) -> None:
        if self._original_stdout is not None:
            try:
                self._original_stdout.flush()
            except Exception:
                pass

    def isatty(self) -> bool:
        return False

    def readable(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

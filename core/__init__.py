"""Core business logic package for PITCH voice assistant"""

__version__ = "1.53"

from .engine import PitchCore
from .clipboard import ClipboardManager
from .log_redirector import LogRedirector
from .stt_worker import STTWorker
from .audio_recorder import AudioRecorder
from . import config_manager
from . import history_manager

__all__ = [
    "__version__",
    "PitchCore",
    "ClipboardManager",
    "LogRedirector",
    "STTWorker",
    "AudioRecorder",
    "config_manager",
    "history_manager",
]


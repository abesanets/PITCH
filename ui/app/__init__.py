"""App subpackage containing dashboard and assistant windows"""
from .assistant import VoiceAssistant
from .dashboard import DashboardWindow

__all__ = [
    'VoiceAssistant',
    'DashboardWindow',
]

"""UI package for VoiceAssistant"""
from .styles import get_stylesheet, _lerp_color
from .styles_data import ACCENT_PRESETS, VISUALIZER_PRESETS, VISUALIZER_SIZES
from .widgets import ToggleSwitch, SegmentedControl, ColorPresetSelector, ElidedLabel
from .visualizer.widgets import PreviewWidget, OverlayWindow
from .app.dashboard import DashboardWindow
from .app.assistant import VoiceAssistant

__all__ = [
    'get_stylesheet',
    'ACCENT_PRESETS',
    'VISUALIZER_PRESETS', 
    'VISUALIZER_SIZES',
    '_lerp_color',
    'ToggleSwitch',
    'SegmentedControl',
    'ColorPresetSelector',
    'ElidedLabel',
    'PreviewWidget',
    'OverlayWindow',
    'DashboardWindow',
    'VoiceAssistant',
]

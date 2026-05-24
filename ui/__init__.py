"""UI package for VoiceAssistant"""
from .styles import get_stylesheet, _lerp_color
from .styles_data import ACCENT_PRESETS, VISUALIZER_PRESETS, VISUALIZER_SIZES
from .widgets import ToggleSwitch, SegmentedControl, ColorPresetSelector, CustomColorDialog
from .visualizer import PreviewWidget, OverlayWindow
from .dashboard import DashboardWindow

__all__ = [
    'get_stylesheet',
    'ACCENT_PRESETS',
    'VISUALIZER_PRESETS', 
    'VISUALIZER_SIZES',
    '_lerp_color',
    'ToggleSwitch',
    'SegmentedControl',
    'ColorPresetSelector',
    'CustomColorDialog',
    'PreviewWidget',
    'OverlayWindow',
    'DashboardWindow',
]

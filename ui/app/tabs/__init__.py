"""Dashboard tab builder modules."""
from .overview import build_overview_tab
from .visualizer import build_visualizer_tab
from .history import build_history_tab
from .settings import build_settings_tab

__all__ = [
    "build_overview_tab",
    "build_visualizer_tab",
    "build_history_tab",
    "build_settings_tab",
]

"""Color presets and visualizer data"""
from PyQt6.QtGui import QColor

# Visualizer Presets
VISUALIZER_PRESETS = {
    "mono": {
        "name": "Mono",
        "bg_color": {"dark": QColor(17, 17, 21, 245), "light": QColor(17, 17, 21, 245)},
        "waves": [
            {"dark": QColor(240, 240, 245, 255), "light": QColor(240, 240, 245, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(180, 180, 195, 180), "light": QColor(180, 180, 195, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(115, 115, 135, 120), "light": QColor(115, 115, 135, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "matrix": {
        "name": "Matrix",
        "bg_color": {"dark": QColor(10, 24, 16, 245), "light": QColor(10, 24, 16, 245)},
        "waves": [
            {"dark": QColor(0, 230, 118, 255), "light": QColor(0, 230, 118, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(0, 200, 83, 180), "light": QColor(0, 200, 83, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(0, 137, 123, 120), "light": QColor(0, 137, 123, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "cyber": {
        "name": "Cyber",
        "bg_color": {"dark": QColor(8, 20, 36, 245), "light": QColor(8, 20, 36, 245)},
        "waves": [
            {"dark": QColor(0, 229, 255, 255), "light": QColor(0, 229, 255, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(0, 176, 255, 180), "light": QColor(0, 176, 255, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(41, 121, 255, 120), "light": QColor(41, 121, 255, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "amber": {
        "name": "Amber",
        "bg_color": {"dark": QColor(28, 18, 8, 245), "light": QColor(28, 18, 8, 245)},
        "waves": [
            {"dark": QColor(255, 179, 0, 255), "light": QColor(255, 179, 0, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(255, 143, 0, 180), "light": QColor(255, 143, 0, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(255, 111, 0, 120), "light": QColor(255, 111, 0, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "synth": {
        "name": "Synth",
        "bg_color": {"dark": QColor(26, 10, 36, 245), "light": QColor(26, 10, 36, 245)},
        "waves": [
            {"dark": QColor(224, 64, 251, 255), "light": QColor(224, 64, 251, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(124, 77, 255, 180), "light": QColor(124, 77, 255, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(101, 31, 255, 120), "light": QColor(101, 31, 255, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "plasma": {
        "name": "Plasma",
        "bg_color": {"dark": QColor(32, 10, 16, 245), "light": QColor(32, 10, 16, 245)},
        "waves": [
            {"dark": QColor(255, 23, 68, 255), "light": QColor(255, 23, 68, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(245, 0, 87, 180), "light": QColor(245, 0, 87, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(213, 0, 0, 120), "light": QColor(213, 0, 0, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "acid": {
        "name": "Acid",
        "bg_color": {"dark": QColor(18, 28, 8, 245), "light": QColor(18, 28, 8, 245)},
        "waves": [
            {"dark": QColor(198, 255, 0, 255), "light": QColor(198, 255, 0, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(118, 255, 3, 180), "light": QColor(118, 255, 3, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(100, 221, 23, 120), "light": QColor(100, 221, 23, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "ice": {
        "name": "Ice",
        "bg_color": {"dark": QColor(10, 28, 32, 245), "light": QColor(10, 28, 32, 245)},
        "waves": [
            {"dark": QColor(224, 247, 250, 255), "light": QColor(224, 247, 250, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(128, 222, 234, 180), "light": QColor(128, 222, 234, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(38, 198, 218, 120), "light": QColor(38, 198, 218, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "void": {
        "name": "Void",
        "bg_color": {"dark": QColor(20, 14, 36, 245), "light": QColor(20, 14, 36, 245)},
        "waves": [
            {"dark": QColor(179, 136, 255, 255), "light": QColor(179, 136, 255, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(124, 77, 255, 180), "light": QColor(124, 77, 255, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(83, 109, 254, 120), "light": QColor(83, 109, 254, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
}

# Visualizer Sizes
VISUALIZER_SIZES = {
    "xs":     (48,  16),
    "small":  (60,  20),
    "medium": (80,  26),
    "large":  (110, 32),
    "xl":     (140, 40),
}

# Accent Color Presets
ACCENT_PRESETS = {
    "mono": {
        "dark":  {"primary": "#A1A1AA", "secondary": "#52525B", "hover": "#F4F4F5"},
        "light": {"primary": "#18181B", "secondary": "#52525B", "hover": "#3F3F46"},
    },
    "chocolate": {
        "dark":  {"primary": "#DFCEBA", "secondary": "#5A4234", "hover": "#F5ECE3"},
        "light": {"primary": "#5A4234", "secondary": "#4E382B", "hover": "#DFCEBA"},
    },
    "ocean": {
        "dark":  {"primary": "#38BDF8", "secondary": "#0EA5E9", "hover": "#0284C7"},
        "light": {"primary": "#0284C7", "secondary": "#0369A1", "hover": "#38BDF8"},
    },
    "aurora": {
        "dark":  {"primary": "#10B981", "secondary": "#06B6D4", "hover": "#059669"},
        "light": {"primary": "#059669", "secondary": "#0891B2", "hover": "#10B981"},
    },
    "neon": {
        "dark":  {"primary": "#EC4899", "secondary": "#A855F7", "hover": "#DB2777"},
        "light": {"primary": "#BE185D", "secondary": "#7E22CE", "hover": "#EC4899"},
    },
    "sunset": {
        "dark":  {"primary": "#F59E0B", "secondary": "#EF4444", "hover": "#D97706"},
        "light": {"primary": "#D97706", "secondary": "#B91C1C", "hover": "#F59E0B"},
    },
    "lavender": {
        "dark":  {"primary": "#A78BFA", "secondary": "#8B5CF6", "hover": "#7C3AED"},
        "light": {"primary": "#7C3AED", "secondary": "#6D28D9", "hover": "#A78BFA"},
    },
    "rose": {
        "dark":  {"primary": "#F43F5E", "secondary": "#E11D48", "hover": "#BE123C"},
        "light": {"primary": "#BE123C", "secondary": "#9F1239", "hover": "#F43F5E"},
    },
    "forest": {
        "dark":  {"primary": "#22C55E", "secondary": "#10B981", "hover": "#16A34A"},
        "light": {"primary": "#16A34A", "secondary": "#059669", "hover": "#22C55E"},
    },
}

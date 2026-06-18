"""Color presets and visualizer data"""
from PyQt6.QtGui import QColor

# Visualizer Presets
VISUALIZER_PRESETS = {
    "mono": {
        "name": "Mono",
        "bg_color": {"dark": QColor(9, 9, 11, 245), "light": QColor(24, 24, 27, 245)},
        "waves": [
            {"dark": QColor(244, 244, 245, 255), "light": QColor(24, 24, 27, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(161, 161, 170, 160), "light": QColor(113, 113, 122, 140),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(113, 113, 122, 100), "light": QColor(161, 161, 170, 100),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "chocolate": {
        "name": "Chocolate",
        "bg_color": {"dark": QColor(36, 26, 20, 160), "light": QColor(245, 236, 227, 200)},
        "waves": [
            {"dark": QColor(245, 236, 227, 255), "light": QColor(78, 56, 43, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(223, 206, 186, 220), "light": QColor(90, 66, 52, 180),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(109, 81, 65, 140), "light": QColor(212, 197, 185, 120),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "ocean": {
        "name": "Ocean",
        "bg_color": {"dark": QColor(6, 25, 38, 160), "light": QColor(224, 242, 254, 200)},
        "waves": [
            {"dark": QColor(56, 189, 248, 255), "light": QColor(2, 132, 199, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(6, 182, 212, 180), "light": QColor(14, 116, 144, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(34, 211, 238, 120), "light": QColor(8, 145, 178, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "aurora": {
        "name": "Aurora",
        "bg_color": {"dark": QColor(5, 30, 24, 160), "light": QColor(209, 250, 229, 200)},
        "waves": [
            {"dark": QColor(16, 185, 129, 255), "light": QColor(5, 150, 105, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(6, 182, 212, 180), "light": QColor(8, 145, 178, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(132, 204, 22, 120), "light": QColor(101, 163, 13, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "neon": {
        "name": "Neon",
        "bg_color": {"dark": QColor(35, 10, 50, 160), "light": QColor(251, 207, 232, 200)},
        "waves": [
            {"dark": QColor(236, 72, 153, 255), "light": QColor(190, 24, 93, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(168, 85, 247, 180), "light": QColor(126, 34, 206, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(6, 182, 212, 120), "light": QColor(8, 145, 178, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "sunset": {
        "name": "Sunset",
        "bg_color": {"dark": QColor(40, 12, 10, 160), "light": QColor(254, 243, 199, 200)},
        "waves": [
            {"dark": QColor(251, 191, 36, 255), "light": QColor(217, 119, 6, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(249, 115, 22, 180), "light": QColor(234, 88, 12, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(248, 113, 113, 120), "light": QColor(220, 38, 38, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "lavender": {
        "name": "Lavender",
        "bg_color": {"dark": QColor(25, 10, 50, 160), "light": QColor(243, 232, 255, 200)},
        "waves": [
            {"dark": QColor(167, 139, 250, 255), "light": QColor(139, 92, 246, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(192, 132, 252, 180), "light": QColor(167, 139, 250, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(216, 180, 254, 120), "light": QColor(192, 132, 252, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "rose": {
        "name": "Rose",
        "bg_color": {"dark": QColor(45, 8, 18, 160), "light": QColor(255, 228, 230, 200)},
        "waves": [
            {"dark": QColor(244, 63, 94, 255), "light": QColor(225, 29, 72, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(251, 113, 133, 180), "light": QColor(244, 63, 94, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
             {"dark": QColor(253, 164, 175, 120), "light": QColor(251, 113, 133, 110),
              "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "forest": {
        "name": "Forest",
        "bg_color": {"dark": QColor(10, 30, 18, 160), "light": QColor(220, 252, 231, 200)},
        "waves": [
            {"dark": QColor(34, 197, 94, 255), "light": QColor(22, 163, 74, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(16, 185, 129, 180), "light": QColor(5, 150, 105, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(132, 204, 22, 120), "light": QColor(101, 163, 13, 110),
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

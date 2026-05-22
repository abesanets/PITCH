import os
import sys
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox,
                             QStackedWidget, QPlainTextEdit, QFrame, QApplication,
                             QListWidget, QListWidgetItem, QGridLayout,
                             QSizePolicy, QSpacerItem, QScrollArea)
from PyQt6.QtCore import (Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve,
                           pyqtProperty, pyqtSignal, QPointF)
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QIcon, QPixmap,
                          QCursor, QPainterPath, QLinearGradient)

import history_manager

# ──────────────────────────────────────────────
#  Visualizer Presets & Sizes
# ──────────────────────────────────────────────

VISUALIZER_PRESETS = {
    "emerald": {
        "name": "Emerald",
        "waves": [
            {"dark": QColor(250, 250, 250, 255), "light": QColor(24, 24, 27, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(6, 182, 212, 180), "light": QColor(8, 145, 178, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(16, 185, 129, 120), "light": QColor(5, 150, 105, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "arctic": {
        "name": "Arctic",
        "waves": [
            {"dark": QColor(255, 255, 255, 255), "light": QColor(15, 23, 42, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(56, 189, 248, 180), "light": QColor(14, 116, 144, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(125, 211, 252, 120), "light": QColor(8, 145, 178, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "neon": {
        "name": "Neon",
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
        "waves": [
            {"dark": QColor(251, 191, 36, 255), "light": QColor(217, 119, 6, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(249, 115, 22, 180), "light": QColor(234, 88, 12, 160),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(248, 113, 113, 120), "light": QColor(220, 38, 38, 110),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
    "mono": {
        "name": "Mono",
        "waves": [
            {"dark": QColor(244, 244, 245, 255), "light": QColor(24, 24, 27, 255),
             "amp": 1.0, "freq": 0.12, "phase": 1.0, "width": 2.0},
            {"dark": QColor(161, 161, 170, 160), "light": QColor(113, 113, 122, 140),
             "amp": 0.65, "freq": 0.22, "phase": -1.3, "width": 1.5},
            {"dark": QColor(113, 113, 122, 100), "light": QColor(161, 161, 170, 100),
             "amp": 0.35, "freq": 0.08, "phase": 0.7, "width": 1.0},
        ]
    },
}

VISUALIZER_SIZES = {
    "small": (60, 20),
    "medium": (80, 26),
    "large": (120, 34),
}

# ──────────────────────────────────────────────
#  Accent Color Presets & Stylesheet
# ──────────────────────────────────────────────

ACCENT_PRESETS = {
    "emerald": {
        "dark": {
            "primary": "#06B6D4",
            "secondary": "#10B981",
            "hover_primary": "#0891B2",
            "hover_secondary": "#059669",
        },
        "light": {
            "primary": "#0891B2",
            "secondary": "#059669",
            "hover_primary": "#06B6D4",
            "hover_secondary": "#10B981",
        }
    },
    "arctic": {
        "dark": {
            "primary": "#38BDF8",
            "secondary": "#0EA5E9",
            "hover_primary": "#0284C7",
            "hover_secondary": "#0369A1",
        },
        "light": {
            "primary": "#0284C7",
            "secondary": "#0369A1",
            "hover_primary": "#38BDF8",
            "hover_secondary": "#0EA5E9",
        }
    },
    "neon": {
        "dark": {
            "primary": "#EC4899",
            "secondary": "#A855F7",
            "hover_primary": "#DB2777",
            "hover_secondary": "#9333EA",
        },
        "light": {
            "primary": "#BE185D",
            "secondary": "#7E22CE",
            "hover_primary": "#EC4899",
            "hover_secondary": "#A855F7",
        }
    },
    "sunset": {
        "dark": {
            "primary": "#F59E0B",
            "secondary": "#EF4444",
            "hover_primary": "#D97706",
            "hover_secondary": "#DC2626",
        },
        "light": {
            "primary": "#D97706",
            "secondary": "#B91C1C",
            "hover_primary": "#F59E0B",
            "hover_secondary": "#EF4444",
        }
    },
    "mono": {
        "dark": {
            "primary": "#A1A1AA",
            "secondary": "#52525B",
            "hover_primary": "#F4F4F5",
            "hover_secondary": "#71717A",
        },
        "light": {
            "primary": "#18181B",
            "secondary": "#52525B",
            "hover_primary": "#3F3F46",
            "hover_secondary": "#27272A",
        }
    }
}

def get_stylesheet(theme, preset_key="emerald"):
    if preset_key not in ACCENT_PRESETS:
        preset_key = "emerald"
    acc = ACCENT_PRESETS[preset_key][theme]
    primary = acc["primary"]
    secondary = acc["secondary"]
    hover_primary = acc["hover_primary"]
    hover_secondary = acc["hover_secondary"]

    if theme == "light":
        return f"""
            QWidget#DashboardWindow {{
                background-color: #FAFAFA;
            }}
            QFrame#Sidebar {{
                background-color: #FFFFFF;
                border-right: 1px solid #E4E4E7;
            }}
            QLabel {{
                color: #18181B;
                font-family: "Segoe UI", "Segoe UI Variable", -apple-system, sans-serif;
            }}
            QLabel#LogoTitle {{
                font-size: 22px;
                font-weight: 800;
                color: #09090B;
                letter-spacing: 4px;
            }}
            QLabel#LogoSubtitle {{
                font-size: 8px;
                font-weight: 700;
                color: #A1A1AA;
                letter-spacing: 2px;
            }}
            QLabel#SectionTitle {{
                font-size: 17px;
                font-weight: 700;
                color: #09090B;
            }}
            QLabel#StatusHeader {{
                color: #A1A1AA;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#VersionLabel {{
                color: #D4D4D8;
                font-size: 10px;
            }}
            QLabel#CardTitle {{
                font-size: 11px;
                font-weight: 700;
                color: #71717A;
                letter-spacing: 0.5px;
            }}
            QLabel#FieldLabel {{
                font-size: 13px;
                font-weight: 500;
                color: #3F3F46;
            }}

            /* Nav Buttons */
            QPushButton#NavButton, QPushButton#NavButtonActive {{
                text-align: left;
                padding: 10px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
            QPushButton#NavButton {{
                background-color: transparent;
                color: #71717A;
            }}
            QPushButton#NavButton:hover {{
                background-color: #F4F4F5;
                color: #18181B;
            }}
            QPushButton#NavButtonActive {{
                background-color: #F4F4F5;
                color: #09090B;
                border-left: 3px solid qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {primary}, stop:1 {secondary});
            }}

            /* Cards */
            QFrame#Card {{
                background-color: #FFFFFF;
                border: 1px solid #E4E4E7;
                border-radius: 12px;
            }}
            QFrame#LogoAccentLine {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #18181B, stop:0.5 {primary}, stop:1 {secondary});
                border: none; border-radius: 1px;
            }}
            QLabel#StatLabel {{
                color: #A1A1AA; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;
            }}
            QLabel#StatVal {{
                color: #09090B; font-size: 22px; font-weight: 700;
            }}

            /* List Widget */
            QListWidget {{
                background-color: #FFFFFF; border: 1px solid #E4E4E7;
                border-radius: 8px; color: #18181B; outline: 0;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 10px; border-bottom: 1px solid #F4F4F5; border-radius: 4px;
            }}
            QListWidget::item:hover {{ background-color: #F4F4F5; }}
            QListWidget::item:selected {{ background-color: #E4E4E7; color: #09090B; }}

            /* Detail */
            QFrame#DetailPanel {{
                background-color: #FFFFFF; border: 1px solid #E4E4E7; border-radius: 12px;
            }}
            QLabel#DetailLabel {{ font-size: 12px; font-weight: 600; color: #3F3F46; }}
            QPlainTextEdit#DetailText {{
                background-color: #FAFAFA; border: 1px solid #E4E4E7;
                border-radius: 8px; color: #18181B; font-size: 12px; padding: 8px;
            }}

            /* Log Console */
            QPlainTextEdit#LogConsole {{
                background-color: #FFFFFF; border: 1px solid #E4E4E7;
                border-radius: 8px; color: #3F3F46;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 11px; padding: 12px;
            }}

            /* Inputs */
            QLineEdit, QComboBox {{
                padding: 9px 14px; background-color: #FFFFFF;
                border: 1px solid #E4E4E7; color: #18181B; border-radius: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid #09090B; }}
            QComboBox::drop-down {{ border: 0px; width: 24px; }}
            QComboBox QAbstractItemView {{
                background-color: #FFFFFF; border: 1px solid #E4E4E7;
                selection-background-color: #F4F4F5; selection-color: #09090B; color: #18181B;
            }}

            /* Buttons */
            QPushButton#ActionBtn, QPushButton#SaveBtn {{
                padding: 9px 20px; font-weight: 600; border-radius: 8px;
                border: none; font-size: 13px;
            }}
            QPushButton#ActionBtn {{
                background-color: #FFFFFF; color: #52525B; border: 1px solid #E4E4E7;
            }}
            QPushButton#ActionBtn:hover {{
                background-color: #F4F4F5; border-color: #D4D4D8; color: #09090B;
            }}
            QPushButton#SaveBtn {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {primary}, stop:1 {secondary});
                color: #FFFFFF;
            }}
            QPushButton#SaveBtn:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {hover_primary}, stop:1 {hover_secondary});
            }}
            QPushButton#SaveBtn:disabled {{
                background: #D4D4D8; color: #A1A1AA;
            }}

            /* Scrollbar */
            QScrollBar:vertical {{
                border: none; background: transparent; width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #D4D4D8; min-height: 20px; border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

            /* Preview area */
            QFrame#PreviewFrame {{
                background-color: #F4F4F5; border: 1px solid #E4E4E7; border-radius: 12px;
            }}

            /* ScrollArea */
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """
    else:
        return f"""
            QWidget#DashboardWindow {{
                background-color: #09090B;
            }}
            QFrame#Sidebar {{
                background-color: #030303;
                border-right: 1px solid #1A1A1E;
            }}
            QLabel {{
                color: #FAFAFA;
                font-family: "Segoe UI", "Segoe UI Variable", -apple-system, sans-serif;
            }}
            QLabel#LogoTitle {{
                font-size: 22px;
                font-weight: 800;
                color: #FFFFFF;
                letter-spacing: 4px;
            }}
            QLabel#LogoSubtitle {{
                font-size: 8px;
                font-weight: 700;
                color: #52525B;
                letter-spacing: 2px;
            }}
            QLabel#SectionTitle {{
                font-size: 17px;
                font-weight: 700;
                color: #FFFFFF;
            }}
            QLabel#StatusHeader {{
                color: #52525B;
                font-size: 9px;
                font-weight: 700;
                letter-spacing: 1px;
            }}
            QLabel#VersionLabel {{
                color: #3F3F46;
                font-size: 10px;
            }}
            QLabel#CardTitle {{
                font-size: 11px;
                font-weight: 700;
                color: #52525B;
                letter-spacing: 0.5px;
            }}
            QLabel#FieldLabel {{
                font-size: 13px;
                font-weight: 500;
                color: #A1A1AA;
            }}

            /* Nav Buttons */
            QPushButton#NavButton, QPushButton#NavButtonActive {{
                text-align: left;
                padding: 10px 16px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                border: none;
            }}
            QPushButton#NavButton {{
                background-color: transparent;
                color: #71717A;
            }}
            QPushButton#NavButton:hover {{
                background-color: #18181B;
                color: #FAFAFA;
            }}
            QPushButton#NavButtonActive {{
                background-color: #18181B;
                color: #FFFFFF;
                border-left: 3px solid qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 {primary}, stop:1 {secondary});
            }}

            /* Cards */
            QFrame#Card {{
                background-color: #111113;
                border: 1px solid #1E1E22;
                border-radius: 12px;
            }}
            QFrame#LogoAccentLine {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #FFFFFF, stop:0.5 {primary}, stop:1 {secondary});
                border: none; border-radius: 1px;
            }}
            QLabel#StatLabel {{
                color: #52525B; font-size: 10px; font-weight: 700; letter-spacing: 0.5px;
            }}
            QLabel#StatVal {{
                color: #FFFFFF; font-size: 22px; font-weight: 700;
            }}

            /* List Widget */
            QListWidget {{
                background-color: #09090B; border: 1px solid #1E1E22;
                border-radius: 8px; color: #E4E4E7; outline: 0;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 10px; border-bottom: 1px solid #18181B; border-radius: 4px;
            }}
            QListWidget::item:hover {{ background-color: #18181B; }}
            QListWidget::item:selected {{ background-color: #27272A; color: #FFFFFF; }}

            /* Detail */
            QFrame#DetailPanel {{
                background-color: #111113; border: 1px solid #1E1E22; border-radius: 12px;
            }}
            QLabel#DetailLabel {{ font-size: 12px; font-weight: 600; color: #A1A1AA; }}
            QPlainTextEdit#DetailText {{
                background-color: #09090B; border: 1px solid #1E1E22;
                border-radius: 8px; color: #E4E4E7; font-size: 12px; padding: 8px;
            }}

            /* Log Console */
            QPlainTextEdit#LogConsole {{
                background-color: #030303; border: 1px solid #1A1A1E;
                border-radius: 8px; color: #A1A1AA;
                font-family: 'Consolas', 'Fira Code', monospace;
                font-size: 11px; padding: 12px;
            }}

            /* Inputs */
            QLineEdit, QComboBox {{
                padding: 9px 14px; background-color: #18181B;
                border: 1px solid #27272A; color: #F4F4F5; border-radius: 8px;
                font-size: 13px;
            }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid #FAFAFA; }}
            QComboBox::drop-down {{ border: 0px; width: 24px; }}
            QComboBox QAbstractItemView {{
                background-color: #18181B; border: 1px solid #27272A;
                selection-background-color: #27272A; selection-color: #FFFFFF; color: #F4F4F5;
            }}

            /* Buttons */
            QPushButton#ActionBtn, QPushButton#SaveBtn {{
                padding: 9px 20px; font-weight: 600; border-radius: 8px;
                border: none; font-size: 13px;
            }}
            QPushButton#ActionBtn {{
                background-color: transparent; color: #71717A; border: 1px solid #27272A;
            }}
            QPushButton#ActionBtn:hover {{
                background-color: #18181B; border-color: #3F3F46; color: #FAFAFA;
            }}
            QPushButton#SaveBtn {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {primary}, stop:1 {secondary});
                color: #FFFFFF;
            }}
            QPushButton#SaveBtn:hover {{
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {hover_primary}, stop:1 {hover_secondary});
            }}
            QPushButton#SaveBtn:disabled {{
                background: #27272A; color: #52525B;
            }}

            /* Scrollbar */
            QScrollBar:vertical {{
                border: none; background: transparent; width: 6px;
            }}
            QScrollBar::handle:vertical {{
                background: #27272A; min-height: 20px; border-radius: 3px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; }}

            /* Preview area */
            QFrame#PreviewFrame {{
                background-color: #030303; border: 1px solid #1A1A1E; border-radius: 12px;
            }}

            /* ScrollArea */
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
        """


def get_stylesheet(theme, preset_key="emerald"):
    if preset_key not in ACCENT_PRESETS:
        preset_key = "emerald"
    acc = ACCENT_PRESETS[preset_key][theme]
    primary = acc["primary"]
    secondary = acc["secondary"]
    hover_primary = acc["hover_primary"]
    hover_secondary = acc["hover_secondary"]

    if theme == "light":
        bg = "#F4F6F8"
        sidebar = "#FFFFFF"
        surface = "#FFFFFF"
        surface_2 = "#F8FAFC"
        surface_3 = "#EEF2F6"
        text = "#111827"
        muted = "#64748B"
        faint = "#94A3B8"
        border = "#E2E8F0"
        border_soft = "#EDF2F7"
        input_bg = "#FFFFFF"
        nav_hover = "#F1F5F9"
        selected = "#EAF5FF"
        console = "#FFFFFF"
    else:
        bg = "#0E1116"
        sidebar = "#12161D"
        surface = "#171B22"
        surface_2 = "#1C222B"
        surface_3 = "#242B36"
        text = "#F3F7FB"
        muted = "#A7B0BE"
        faint = "#6B7482"
        border = "#252C36"
        border_soft = "#20262F"
        input_bg = "#11161D"
        nav_hover = "#1A2029"
        selected = "#18283A"
        console = "#10141A"

    return f"""
        QWidget#DashboardWindow {{
            background-color: {bg};
        }}
        QWidget {{
            font-family: "Arial", "Segoe UI", "Microsoft Sans Serif", sans-serif;
            font-size: 13px;
            color: {text};
        }}
        QFrame#Sidebar {{
            background-color: {sidebar};
            border-right: 1px solid {border_soft};
        }}
        QLabel {{
            color: {text};
            background: transparent;
        }}
        QLabel#LogoTitle {{
            font-size: 24px;
            font-weight: 800;
            color: {text};
            letter-spacing: 2px;
        }}
        QLabel#LogoSubtitle {{
            font-size: 10px;
            font-weight: 700;
            color: {faint};
            letter-spacing: 1px;
        }}
        QLabel#SectionTitle {{
            font-size: 24px;
            font-weight: 800;
            color: {text};
            letter-spacing: 0px;
        }}
        QLabel#StatusHeader, QLabel#CardTitle, QLabel#StatLabel {{
            color: {faint};
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0px;
        }}
        QLabel#FieldLabel {{
            font-size: 13px;
            font-weight: 600;
            color: {muted};
        }}
        QLabel#VersionLabel {{
            color: {faint};
            font-size: 11px;
        }}
        QLabel#StatVal {{
            color: {text};
            font-size: 26px;
            font-weight: 800;
            letter-spacing: 0px;
        }}
        QFrame#LogoAccentLine {{
            background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 {primary}, stop:1 {secondary});
            border: none;
            border-radius: 1px;
        }}

        QPushButton#NavButton, QPushButton#NavButtonActive {{
            text-align: left;
            padding: 11px 14px;
            border-radius: 8px;
            font-weight: 650;
            font-size: 13px;
            border: none;
            letter-spacing: 0px;
        }}
        QPushButton#NavButton {{
            background-color: transparent;
            color: {muted};
        }}
        QPushButton#NavButton:hover {{
            background-color: {nav_hover};
            color: {text};
        }}
        QPushButton#NavButtonActive {{
            background-color: {selected};
            color: {text};
            border-left: 3px solid {primary};
        }}

        QFrame#Card, QFrame#DetailPanel {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 8px;
        }}
        QFrame#PreviewFrame {{
            background-color: {surface_2};
            border: 1px solid {border_soft};
            border-radius: 8px;
        }}

        QLineEdit, QComboBox {{
            padding: 10px 13px;
            background-color: {input_bg};
            border: 1px solid {border};
            color: {text};
            border-radius: 8px;
            selection-background-color: {primary};
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {primary};
        }}
        QComboBox::drop-down {{
            border: none;
            width: 34px;
            background-color: transparent;
            border-top-right-radius: 8px;
            border-bottom-right-radius: 8px;
        }}
        QComboBox::down-arrow {{
            image: none;
            width: 0px;
            height: 0px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 8px;
            selection-background-color: {selected};
            selection-color: {text};
            color: {text};
            outline: 0;
            padding: 6px;
        }}

        QPushButton#ActionBtn, QPushButton#SaveBtn {{
            padding: 10px 18px;
            font-weight: 700;
            border-radius: 8px;
            font-size: 13px;
            border: 1px solid transparent;
            letter-spacing: 0px;
        }}
        QPushButton#ActionBtn {{
            background-color: {surface_2};
            color: {muted};
            border-color: {border};
        }}
        QPushButton#ActionBtn:hover {{
            background-color: {surface_3};
            color: {text};
            border-color: {primary};
        }}
        QPushButton#SaveBtn {{
            background-color: {primary};
            color: #FFFFFF;
        }}
        QPushButton#SaveBtn:hover {{
            background-color: {hover_primary};
        }}
        QPushButton#SaveBtn:disabled {{
            background-color: {surface_3};
            color: {faint};
        }}

        QListWidget {{
            background-color: {surface};
            border: 1px solid {border};
            border-radius: 8px;
            color: {text};
            outline: 0;
            padding: 6px;
        }}
        QListWidget::item {{
            padding: 11px 10px;
            border-radius: 7px;
            border: none;
            color: {muted};
        }}
        QListWidget::item:hover {{
            background-color: {nav_hover};
            color: {text};
        }}
        QListWidget::item:selected {{
            background-color: {selected};
            color: {text};
        }}

        QLabel#DetailLabel {{
            color: {muted};
            font-size: 12px;
            font-weight: 700;
        }}
        QPlainTextEdit#DetailText, QPlainTextEdit#LogConsole {{
            background-color: {console};
            border: 1px solid {border};
            border-radius: 8px;
            color: {text};
            padding: 10px;
            selection-background-color: {primary};
        }}
        QPlainTextEdit#LogConsole {{
            font-family: "Cascadia Mono", "Consolas", monospace;
            font-size: 11px;
            color: {muted};
        }}
        QPlainTextEdit#DetailText {{
            font-size: 12px;
        }}

        QScrollArea {{
            background-color: transparent;
            border: none;
        }}
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 8px;
            margin: 4px 0;
        }}
        QScrollBar::handle:vertical {{
            background: {surface_3};
            min-height: 24px;
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
    """


# ──────────────────────────────────────────────
#  Custom Widgets
# ──────────────────────────────────────────────

class ToggleSwitch(QWidget):
    """Animated iOS-style toggle switch."""
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setFixedSize(44, 24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = checked
        self._handle_pos = 1.0 if checked else 0.0
        self._theme = "dark"
        self._on_col1 = QColor(6, 182, 212)
        self._on_col2 = QColor(16, 185, 129)
        self._animation = QPropertyAnimation(self, b"handle_position", self)
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def set_colors(self, on_col1, on_col2):
        self._on_col1 = on_col1
        self._on_col2 = on_col2
        self.update()

    def get_handle_position(self):
        return self._handle_pos

    def set_handle_position(self, pos):
        self._handle_pos = pos
        self.update()

    handle_position = pyqtProperty(float, get_handle_position, set_handle_position)

    def isChecked(self):
        return self._checked

    def setChecked(self, val):
        self._checked = val
        self._handle_pos = 1.0 if val else 0.0
        self.update()

    def set_theme(self, theme):
        self._theme = theme
        self.update()

    def mousePressEvent(self, event):
        self._checked = not self._checked
        self._animation.setStartValue(self._handle_pos)
        self._animation.setEndValue(1.0 if self._checked else 0.0)
        self._animation.start()
        self.toggled.emit(self._checked)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = h / 2

        # Track
        if self._handle_pos > 0.01:
            grad = QLinearGradient(0, 0, w, 0)
            if self._theme == "dark":
                off_col = QColor(63, 63, 70)
            else:
                off_col = QColor(212, 212, 216)
            on_col1 = self._on_col1
            on_col2 = self._on_col2
            t = self._handle_pos
            grad.setColorAt(0, _lerp_color(off_col, on_col1, t))
            grad.setColorAt(1, _lerp_color(off_col, on_col2, t))
            p.setBrush(QBrush(grad))
        else:
            if self._theme == "dark":
                p.setBrush(QBrush(QColor(63, 63, 70)))
            else:
                p.setBrush(QBrush(QColor(212, 212, 216)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)

        # Handle
        margin = 3
        handle_d = h - margin * 2
        handle_x = margin + self._handle_pos * (w - handle_d - margin * 2)
        p.setBrush(QBrush(QColor(255, 255, 255)))
        p.drawEllipse(QRectF(handle_x, margin, handle_d, handle_d))
        p.end()


def _lerp_color(c1, c2, t):
    return QColor(
        int(c1.red() + (c2.red() - c1.red()) * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue() + (c2.blue() - c1.blue()) * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


class SegmentedControl(QWidget):
    """Compact chip-style segmented button group."""
    currentChanged = pyqtSignal(int)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._options = options
        self._current = 0
        self._theme = "dark"
        self._buttons = []
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(34)

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(6)

        for i, text in enumerate(options):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(32)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda checked, idx=i: self._on_click(idx))
            lay.addWidget(btn)
            self._buttons.append(btn)

        self._update_styles()

    def _on_click(self, idx):
        if idx != self._current:
            self._current = idx
            self._update_styles()
            self.currentChanged.emit(idx)

    def currentIndex(self):
        return self._current

    def setCurrentIndex(self, idx):
        self._current = idx
        self._update_styles()

    def set_theme(self, theme):
        self._theme = theme
        self._update_styles()

    def _update_styles(self):
        for i, btn in enumerate(self._buttons):
            if i == self._current:
                if self._theme == "dark":
                    btn.setStyleSheet("""
                        QPushButton { background-color: #E8F4FF; color: #0B1220;
                        border: 1px solid #E8F4FF; border-radius: 8px; font-weight: 700; font-size: 12px;
                        padding: 0 13px; }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton { background-color: #111827; color: #FFFFFF;
                        border: 1px solid #111827; border-radius: 8px; font-weight: 700; font-size: 12px;
                        padding: 0 13px; }
                    """)
            else:
                if self._theme == "dark":
                    btn.setStyleSheet("""
                        QPushButton { background-color: #171D26; color: #A7B0BE;
                        border: 1px solid #252C36; border-radius: 8px; font-weight: 600; font-size: 12px;
                        padding: 0 13px; }
                        QPushButton:hover { color: #F3F7FB; background-color: #1C2430; border-color: #334155; }
                    """)
                else:
                    btn.setStyleSheet("""
                        QPushButton { background-color: #FFFFFF; color: #64748B;
                        border: 1px solid #E2E8F0; border-radius: 8px; font-weight: 600; font-size: 12px;
                        padding: 0 13px; }
                        QPushButton:hover { color: #111827; background-color: #F8FAFC; border-color: #CBD5E1; }
                    """)

    def paintEvent(self, event):
        super().paintEvent(event)


class ColorPresetSelector(QWidget):
    """Row of clickable colored circles for choosing a visualizer color preset."""
    presetChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "emerald"
        self._theme = "dark"
        self.setFixedHeight(64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._preset_order = ["emerald", "arctic", "neon", "sunset", "mono"]

    def currentPreset(self):
        return self._current

    def setCurrentPreset(self, key):
        self._current = key
        self.update()

    def set_theme(self, theme):
        self._theme = theme
        self.update()

    def mousePressEvent(self, event):
        x = event.position().x()
        count = len(self._preset_order)
        total_w = count * 52
        start_x = (self.width() - total_w) / 2
        for i, key in enumerate(self._preset_order):
            cx = start_x + i * 52 + 16
            if abs(x - cx) < 20:
                self._current = key
                self.update()
                self.presetChanged.emit(key)
                break

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        count = len(self._preset_order)
        total_w = count * 52
        start_x = (self.width() - total_w) / 2

        for i, key in enumerate(self._preset_order):
            preset = VISUALIZER_PRESETS[key]
            cx = start_x + i * 52 + 16
            cy = 18
            r = 14

            # Draw gradient circle from preset colors
            colors = preset["waves"]
            c1 = colors[0][self._theme]
            c2 = colors[1][self._theme]
            c3 = colors[2][self._theme]
            grad = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
            grad.setColorAt(0.0, QColor(c1.red(), c1.green(), c1.blue(), 220))
            grad.setColorAt(0.5, QColor(c2.red(), c2.green(), c2.blue(), 200))
            grad.setColorAt(1.0, QColor(c3.red(), c3.green(), c3.blue(), 180))
            p.setBrush(QBrush(grad))

            if key == self._current:
                ring_pen = QPen(QColor(6, 182, 212), 2.5)
                p.setPen(ring_pen)
            else:
                if self._theme == "dark":
                    p.setPen(QPen(QColor(39, 39, 42), 1))
                else:
                    p.setPen(QPen(QColor(212, 212, 216), 1))

            p.drawEllipse(QPointF(cx, cy), r, r)

            # Name label
            p.setPen(QPen(QColor(161, 161, 170) if self._theme == "dark" else QColor(113, 113, 122)))
            font = QFont("Segoe UI", 8)
            font.setWeight(QFont.Weight.Medium)
            p.setFont(font)
            name = preset["name"]
            tw = p.fontMetrics().horizontalAdvance(name)
            p.drawText(int(cx - tw / 2), 50, name)

        p.end()


class PreviewWidget(QWidget):
    """Live preview of the overlay visualization in the settings tab."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(100)
        self._theme = "dark"
        self._style = "wave"
        self._preset_key = "emerald"
        self._size_key = "medium"
        self._phase = 0.0
        self._demo_volume = 0.0
        self._demo_target = 0.6
        self._time_counter = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def set_style(self, style):
        self._style = style
        self.update()

    def set_preset(self, key):
        self._preset_key = key
        self.update()

    def set_size(self, key):
        self._size_key = key
        self.update()

    def set_theme(self, theme):
        self._theme = theme
        self.update()

    def _tick(self):
        self._time_counter += 0.033
        # Natural-looking volume oscillation
        self._demo_target = 0.35 + 0.35 * math.sin(self._time_counter * 1.7) + 0.15 * math.sin(self._time_counter * 3.1)
        self._demo_target = max(0.1, min(1.0, self._demo_target))
        self._demo_volume += (self._demo_target - self._demo_volume) * 0.25
        self._phase += 0.08
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Get overlay dimensions
        ow, oh = VISUALIZER_SIZES.get(self._size_key, (80, 26))

        # Center the pill in the widget
        ox = (self.width() - ow) / 2
        oy = (self.height() - oh) / 2

        # Draw pill background
        if self._theme == "dark":
            bg = QColor(9, 9, 11, 245)
            border = QColor(39, 39, 42)
        else:
            bg = QColor(250, 250, 250, 240)
            border = QColor(228, 228, 231)

        p.setBrush(QBrush(bg))
        p.setPen(QPen(border, 1))
        p.drawRoundedRect(QRectF(ox, oy, ow, oh), 8, 8)

        # Draw visualization inside the pill
        preset = VISUALIZER_PRESETS.get(self._preset_key, VISUALIZER_PRESETS["emerald"])
        center_x = ox + ow / 2
        center_y = oy + oh / 2
        volume = self._demo_volume

        if self._style == "wave":
            self._draw_wave(p, ox, oy, ow, oh, preset, volume)
        elif self._style == "bars":
            self._draw_bars(p, ox, oy, ow, oh, preset, volume)
        elif self._style == "dots":
            self._draw_dots(p, ox, oy, ow, oh, preset, volume)
        elif self._style == "ribbon":
            self._draw_ribbon(p, ox, oy, ow, oh, preset, volume)

        p.end()

    def _draw_wave(self, p, ox, oy, ow, oh, preset, volume):
        center_y = oy + oh / 2
        max_amp = oh * 0.38
        pad = 6

        for wi, wave_cfg in enumerate(preset["waves"]):
            color = wave_cfg[self._theme]
            amp_mult = wave_cfg["amp"]
            freq = wave_cfg["freq"]
            phase_mult = wave_cfg["phase"]
            pen_w = wave_cfg["width"]

            path = QPainterPath()
            first = True
            curr_amp = max_amp * min(1.0, volume) * amp_mult
            if curr_amp < 0.5:
                curr_amp = 0.5 * amp_mult

            for x_i in range(pad, int(ow) - pad):
                t = (x_i - pad) / max(1, (ow - 2 * pad))
                envelope = math.pow(math.sin(math.pi * t), 2.0)
                angle = (x_i * freq) + (self._phase * phase_mult)
                y = center_y + curr_amp * envelope * math.sin(angle)
                if first:
                    path.moveTo(ox + x_i, y)
                    first = False
                else:
                    path.lineTo(ox + x_i, y)

            pen = QPen(color)
            pen.setWidthF(pen_w)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawPath(path)

    def _draw_bars(self, p, ox, oy, ow, oh, preset, volume):
        num_bars = max(5, int(ow / 8))
        bar_w = max(2.5, (ow - 12) / (num_bars * 1.6))
        gap = (ow - 12 - bar_w * num_bars) / max(1, num_bars - 1)
        max_h = oh * 0.7
        center_y = oy + oh / 2
        colors = [w[self._theme] for w in preset["waves"]]

        for i in range(num_bars):
            t = i / max(1, num_bars - 1)
            bar_volume = volume * (0.4 + 0.6 * math.sin(self._phase * 1.5 + i * 0.8) ** 2)
            bar_h = max(2, max_h * bar_volume)
            bx = ox + 6 + i * (bar_w + gap)
            by = center_y - bar_h / 2

            # Interpolate color
            if t < 0.5:
                color = _lerp_color(colors[0], colors[1], t * 2)
            else:
                color = _lerp_color(colors[1], colors[2], (t - 0.5) * 2)

            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(color))
            p.drawRoundedRect(QRectF(bx, by, bar_w, bar_h), bar_w / 2, bar_w / 2)

    def _draw_dots(self, p, ox, oy, ow, oh, preset, volume):
        colors = [w[self._theme] for w in preset["waves"]]
        count = max(7, int(ow / 11))
        gap = ow / max(1, count)
        center_y = oy + oh / 2

        for i in range(count):
            t = i / max(1, count - 1)
            pulse = 0.45 + 0.55 * math.sin(self._phase * 1.8 + i * 0.7) ** 2
            radius = 2.0 + volume * pulse * oh * 0.16
            x = ox + gap * (i + 0.5)
            color = _lerp_color(colors[0], colors[1 if t < 0.65 else 2], min(1.0, t * 1.4))
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(QPointF(x, center_y), radius, radius)

    def _draw_ribbon(self, p, ox, oy, ow, oh, preset, volume):
        center_y = oy + oh / 2
        colors = [w[self._theme] for w in preset["waves"]]
        amp = max(1.4, oh * (0.14 + 0.24 * volume))
        pad = 7

        path = QPainterPath()
        path.moveTo(ox + pad, center_y)
        for x_i in range(pad, int(ow) - pad):
            t = (x_i - pad) / max(1, (ow - 2 * pad))
            y = center_y + amp * math.sin(self._phase * 1.1 + t * math.pi * 2.2)
            y += amp * 0.45 * math.sin(self._phase * -0.7 + t * math.pi * 5.1)
            path.lineTo(ox + x_i, y)

        pen = QPen(colors[0])
        pen.setWidthF(4.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawPath(path)

        pen = QPen(colors[1])
        pen.setWidthF(1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawPath(path)


# ──────────────────────────────────────────────
#  Dashboard Window
# ──────────────────────────────────────────────

class DashboardWindow(QWidget):
    def __init__(self, config, save_callback):
        super().__init__()
        self.setObjectName("DashboardWindow")
        self.config = config
        self.save_callback = save_callback
        self.theme_name = self.config.get("theme", "dark")
        self.history_entries = []
        self.init_ui()
        self.apply_theme(self.theme_name)
        self.load_logs()
        self.load_history()
        self.update_statistics()

    def init_ui(self):
        self.setWindowTitle("Echo Dashboard")
        self.setMinimumSize(980, 640)
        self.resize(1040, 680)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ── Sidebar ──
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(230)
        sb = QVBoxLayout(sidebar)
        sb.setContentsMargins(20, 26, 20, 22)
        sb.setSpacing(7)

        # Logo
        logo_w = QWidget()
        logo_l = QVBoxLayout(logo_w)
        logo_l.setContentsMargins(0, 0, 0, 0)
        logo_l.setSpacing(4)
        title_lbl = QLabel("ECHO")
        title_lbl.setObjectName("LogoTitle")
        sub_lbl = QLabel("VOICE ASSISTANT")
        sub_lbl.setObjectName("LogoSubtitle")
        accent = QFrame()
        accent.setFixedHeight(2)
        accent.setObjectName("LogoAccentLine")
        logo_l.addWidget(title_lbl)
        logo_l.addWidget(sub_lbl)
        logo_l.addSpacing(6)
        logo_l.addWidget(accent)
        sb.addWidget(logo_w)
        sb.addSpacing(28)

        # Nav buttons
        self.nav_buttons = []
        nav_items = ["Обзор", "Визуализатор", "История", "Настройки", "Логи"]
        for i, name in enumerate(nav_items):
            btn = QPushButton(name)
            btn.setObjectName("NavButtonActive" if i == 0 else "NavButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            sb.addWidget(btn)
            self.nav_buttons.append(btn)

        sb.addStretch()

        # Status
        status_hdr = QLabel("STATUS")
        status_hdr.setObjectName("StatusHeader")
        self.status_value = QLabel("Готов к работе")
        self.status_value.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")
        ver_lbl = QLabel("v1.0")
        ver_lbl.setObjectName("VersionLabel")
        sb.addWidget(status_hdr)
        sb.addWidget(self.status_value)
        sb.addSpacing(4)
        sb.addWidget(ver_lbl)

        main_layout.addWidget(sidebar)

        # ── Content Stack ──
        self.stack = QStackedWidget()
        main_layout.addWidget(self.stack)

        self._build_dashboard_tab()
        self._build_visualizer_tab()
        self._build_history_tab()
        self._build_settings_tab()
        self._build_logs_tab()

        # Window icon
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    # ── Tab 0: Dashboard ──
    def _build_dashboard_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 30, 32, 30)
        lay.setSpacing(18)

        title = QLabel("Обзор")
        title.setObjectName("SectionTitle")
        lay.addWidget(title)

        # Status card
        state_card = QFrame()
        state_card.setObjectName("Card")
        sc_lay = QHBoxLayout(state_card)
        sc_lay.setContentsMargins(20, 16, 20, 16)

        self.dash_indicator = QFrame()
        self.dash_indicator.setFixedSize(10, 10)
        self.dash_indicator.setStyleSheet("background-color: #10B981; border-radius: 5px;")

        st_lbl = QLabel("Состояние")
        st_lbl.setStyleSheet("font-weight: 600; font-size: 13px;")
        self.dash_state_val = QLabel("Ожидание")
        self.dash_state_val.setStyleSheet("font-weight: 700; font-size: 13px; color: #10B981;")

        sc_lay.addWidget(self.dash_indicator)
        sc_lay.addSpacing(8)
        sc_lay.addWidget(st_lbl)
        sc_lay.addWidget(self.dash_state_val)
        sc_lay.addStretch()
        lay.addWidget(state_card)

        # Stats grid
        stats_w = QWidget()
        sg = QGridLayout(stats_w)
        sg.setContentsMargins(0, 0, 0, 0)
        sg.setSpacing(12)

        def make_stat(label_text):
            card = QFrame()
            card.setObjectName("Card")
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 16, 18, 16)
            cl.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setObjectName("StatLabel")
            val = QLabel("0")
            val.setObjectName("StatVal")
            cl.addWidget(lbl)
            cl.addWidget(val)
            return card, val

        c1, self.val_total = make_stat("ВСЕГО ДИКТОВОК")
        c2, self.val_lat = make_stat("СРЕДНЯЯ ЗАДЕРЖКА")
        c3, self.val_words = make_stat("РАСПОЗНАНО СЛОВ")
        self.val_lat.setText("0.0 сек")

        sg.addWidget(c1, 0, 0)
        sg.addWidget(c2, 0, 1)
        sg.addWidget(c3, 0, 2)
        lay.addWidget(stats_w)

        # Tips card
        tips = QFrame()
        tips.setObjectName("Card")
        tl = QVBoxLayout(tips)
        tl.setContentsMargins(18, 16, 18, 16)
        tl.setSpacing(6)
        tips_title = QLabel("Диктовка")
        tips_title.setStyleSheet("font-weight: 700; font-size: 13px;")
        tip1 = QLabel("Удерживайте Ctrl + Win, говорите, отпустите клавиши — текст появится в активном окне.")
        tip1.setStyleSheet("color: #71717A; font-size: 12px;")
        tip1.setWordWrap(True)
        tl.addWidget(tips_title)
        tl.addWidget(tip1)
        lay.addWidget(tips)
        lay.addStretch()

        self.stack.addWidget(page)

    # ── Tab 1: Visualizer ──
    def _build_visualizer_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 30, 32, 30)
        lay.setSpacing(16)

        title = QLabel("Визуализатор")
        title.setObjectName("SectionTitle")
        lay.addWidget(title)

        # Preview card
        preview_card = QFrame()
        preview_card.setObjectName("PreviewFrame")
        pc_lay = QVBoxLayout(preview_card)
        pc_lay.setContentsMargins(16, 16, 16, 16)
        self.preview_widget = PreviewWidget()
        self.preview_widget.set_style(self.config.get("visualizer_style", "wave"))
        self.preview_widget.set_preset(self.config.get("visualizer_color_preset", "emerald"))
        self.preview_widget.set_size(self.config.get("visualizer_size", "medium"))
        pc_lay.addWidget(self.preview_widget)
        lay.addWidget(preview_card)

        # Style card
        style_card = QFrame()
        style_card.setObjectName("Card")
        scl = QVBoxLayout(style_card)
        scl.setContentsMargins(18, 16, 18, 16)
        scl.setSpacing(12)
        style_title = QLabel("СТИЛЬ")
        style_title.setObjectName("CardTitle")
        scl.addWidget(style_title)

        # Shape segmented control
        shape_row = QHBoxLayout()
        shape_lbl = QLabel("Форма")
        shape_lbl.setObjectName("FieldLabel")
        shape_lbl.setFixedWidth(60)
        self.shape_seg = SegmentedControl(["Волна", "Бары", "Точки", "Лента"])
        style_map = {"wave": 0, "bars": 1, "dots": 2, "ribbon": 3, "pulse": 0}
        self.shape_seg.setCurrentIndex(style_map.get(self.config.get("visualizer_style", "wave"), 0))
        self.shape_seg.currentChanged.connect(self._on_shape_changed)
        shape_row.addWidget(shape_lbl)
        shape_row.addWidget(self.shape_seg)
        shape_row.addStretch()
        scl.addLayout(shape_row)

        # Size row
        size_row = QHBoxLayout()
        size_lbl = QLabel("Размер")
        size_lbl.setObjectName("FieldLabel")
        size_lbl.setFixedWidth(60)
        self.size_seg = SegmentedControl(["S", "M", "L"])
        size_map_idx = {"small": 0, "medium": 1, "large": 2}
        self.size_seg.setCurrentIndex(size_map_idx.get(self.config.get("visualizer_size", "medium"), 1))
        self.size_seg.currentChanged.connect(self._on_size_changed)
        size_row.addWidget(size_lbl)
        size_row.addWidget(self.size_seg)
        size_row.addStretch()
        scl.addLayout(size_row)

        theme_row = QHBoxLayout()
        theme_lbl = QLabel("Тема")
        theme_lbl.setObjectName("FieldLabel")
        theme_lbl.setFixedWidth(60)
        self.theme_seg = SegmentedControl(["Dark", "Light"])
        self.theme_seg.setCurrentIndex(0 if self.config.get("theme", "dark") == "dark" else 1)
        self.theme_seg.currentChanged.connect(lambda idx: self.apply_theme("dark" if idx == 0 else "light"))
        theme_row.addWidget(theme_lbl)
        theme_row.addWidget(self.theme_seg)
        theme_row.addStretch()
        scl.addLayout(theme_row)

        lay.addWidget(style_card)

        # Color preset card
        color_card = QFrame()
        color_card.setObjectName("Card")
        ccl = QVBoxLayout(color_card)
        ccl.setContentsMargins(18, 16, 18, 16)
        ccl.setSpacing(10)
        color_title = QLabel("ЦВЕТОВАЯ ТЕМА")
        color_title.setObjectName("CardTitle")
        ccl.addWidget(color_title)

        self.color_selector = ColorPresetSelector()
        self.color_selector.setCurrentPreset(self.config.get("visualizer_color_preset", "emerald"))
        self.color_selector.presetChanged.connect(self._on_preset_changed)
        ccl.addWidget(self.color_selector)
        lay.addWidget(color_card)

        # Save button
        self.vis_save_btn = QPushButton("Сохранить")
        self.vis_save_btn.setObjectName("SaveBtn")
        self.vis_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vis_save_btn.clicked.connect(self._save_visualizer)
        lay.addWidget(self.vis_save_btn, 0, Qt.AlignmentFlag.AlignLeft)

        lay.addStretch()
        self.stack.addWidget(page)

    def _on_shape_changed(self, idx):
        styles = ["wave", "bars", "dots", "ribbon"]
        self.preview_widget.set_style(styles[idx])

    def _on_size_changed(self, idx):
        sizes = ["small", "medium", "large"]
        self.preview_widget.set_size(sizes[idx])

    def _on_preset_changed(self, key):
        self.preview_widget.set_preset(key)
        self.config["visualizer_color_preset"] = key
        self.apply_theme(self.theme_name, key)

    def _save_visualizer(self):
        styles = ["wave", "bars", "dots", "ribbon"]
        sizes = ["small", "medium", "large"]
        self.config["visualizer_style"] = styles[self.shape_seg.currentIndex()]
        self.config["visualizer_size"] = sizes[self.size_seg.currentIndex()]
        self.config["visualizer_color_preset"] = self.color_selector.currentPreset()
        self.config["theme"] = "dark" if self.theme_seg.currentIndex() == 0 else "light"
        self.save_callback(self.config)
        self.vis_save_btn.setText("Сохранено!")
        self.vis_save_btn.setEnabled(False)
        QTimer.singleShot(1500, lambda: (self.vis_save_btn.setText("Сохранить"), self.vis_save_btn.setEnabled(True)))

    # ── Tab 2: History ──
    def _build_history_tab(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        # Left: search + list
        left = QWidget()
        ll = QVBoxLayout(left)
        ll.setContentsMargins(0, 0, 0, 0)
        ll.setSpacing(8)

        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Поиск по истории...")
        self.history_search.textChanged.connect(self.filter_history)
        ll.addWidget(self.history_search)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.show_history_detail)
        ll.addWidget(self.history_list)

        self.btn_clear_history = QPushButton("Очистить историю")
        self.btn_clear_history.setObjectName("ActionBtn")
        self.btn_clear_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_history.clicked.connect(self.clear_all_history)
        ll.addWidget(self.btn_clear_history)

        lay.addWidget(left, 2)

        # Right: detail panel
        self.detail_panel = QFrame()
        self.detail_panel.setObjectName("DetailPanel")
        dl = QVBoxLayout(self.detail_panel)
        dl.setContentsMargins(18, 18, 18, 18)
        dl.setSpacing(10)

        self.placeholder_detail_label = QLabel("Выберите запись из списка\nдля просмотра деталей.")
        self.placeholder_detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_detail_label.setWordWrap(True)
        self.placeholder_detail_label.setStyleSheet("color: #52525B; font-size: 13px;")
        dl.addWidget(self.placeholder_detail_label)

        self.detail_meta = QLabel()
        self.detail_meta.setStyleSheet("font-size: 11px; color: #71717A;")
        self.detail_meta.setVisible(False)

        self.lbl_raw = QLabel("Распознано Whisper:")
        self.lbl_raw.setObjectName("DetailLabel")
        self.lbl_raw.setVisible(False)
        self.txt_raw = QPlainTextEdit()
        self.txt_raw.setReadOnly(True)
        self.txt_raw.setObjectName("DetailText")
        self.txt_raw.setVisible(False)

        self.lbl_clean = QLabel("Обработано LLM:")
        self.lbl_clean.setObjectName("DetailLabel")
        self.lbl_clean.setVisible(False)
        self.txt_clean = QPlainTextEdit()
        self.txt_clean.setReadOnly(True)
        self.txt_clean.setObjectName("DetailText")
        self.txt_clean.setVisible(False)

        self.copy_btn_widget = QWidget()
        cbl = QHBoxLayout(self.copy_btn_widget)
        cbl.setContentsMargins(0, 0, 0, 0)
        self.btn_copy_raw = QPushButton("Копировать сырой")
        self.btn_copy_raw.setObjectName("ActionBtn")
        self.btn_copy_raw.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_raw.clicked.connect(self.copy_raw_text)
        self.btn_copy_clean = QPushButton("Копировать готовый")
        self.btn_copy_clean.setObjectName("SaveBtn")
        self.btn_copy_clean.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_clean.clicked.connect(self.copy_clean_text)
        cbl.addWidget(self.btn_copy_raw)
        cbl.addWidget(self.btn_copy_clean)
        self.copy_btn_widget.setVisible(False)

        dl.addWidget(self.detail_meta)
        dl.addWidget(self.lbl_raw)
        dl.addWidget(self.txt_raw)
        dl.addWidget(self.lbl_clean)
        dl.addWidget(self.txt_clean)
        dl.addWidget(self.copy_btn_widget)

        lay.addWidget(self.detail_panel, 3)
        self.stack.addWidget(page)

    # ── Tab 3: Settings ──
    def _build_settings_tab(self):
        page = QWidget()
        main_lay = QVBoxLayout(page)
        main_lay.setContentsMargins(32, 30, 32, 24)
        main_lay.setSpacing(12)

        title = QLabel("Конфигурация")
        title.setObjectName("SectionTitle")
        main_lay.addWidget(title)

        settings_card = QFrame()
        settings_card.setObjectName("Card")
        lay = QVBoxLayout(settings_card)
        lay.setContentsMargins(22, 20, 22, 20)
        lay.setSpacing(16)

        def section_label(text):
            lbl = QLabel(text)
            lbl.setObjectName("CardTitle")
            return lbl

        def setting_row(label_text, control, width=None):
            row = QHBoxLayout()
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(14)
            lbl = QLabel(label_text)
            lbl.setObjectName("FieldLabel")
            lbl.setFixedWidth(150)
            if width:
                control.setFixedWidth(width)
            row.addWidget(lbl)
            row.addWidget(control)
            row.addStretch()
            return row

        lay.addWidget(section_label("API"))
        api_row = QHBoxLayout()
        api_row.setSpacing(12)
        self.api_input = QLineEdit()
        self.api_input.setText(self.config.get("api_key", ""))
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setPlaceholderText("Введите API-ключ Groq")
        self.api_input.setMinimumWidth(360)
        self.api_input.setMaximumWidth(620)
        self.btn_toggle_api = QPushButton("Показать")
        self.btn_toggle_api.setObjectName("ActionBtn")
        self.btn_toggle_api.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_api.setFixedWidth(104)
        self.btn_toggle_api.clicked.connect(self.toggle_api_visibility)
        api_lbl = QLabel("Groq API Key")
        api_lbl.setObjectName("FieldLabel")
        api_lbl.setFixedWidth(150)
        api_row.addWidget(api_lbl)
        api_row.addWidget(self.api_input, 1)
        api_row.addWidget(self.btn_toggle_api)
        api_row.addStretch()
        lay.addLayout(api_row)

        lay.addSpacing(4)
        lay.addWidget(section_label("Ввод"))
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["ctrl+windows", "left alt+space", "f8"])
        self.hotkey_combo.setCurrentText(self.config.get("hotkey", "ctrl+windows"))
        lay.addLayout(setting_row("Горячая клавиша", self.hotkey_combo, 260))

        lay.addSpacing(4)
        lay.addWidget(section_label("Модель"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen/qwen3-32b"
        ])
        self.model_combo.setCurrentText(self.config.get("text_model", "llama-3.3-70b-versatile"))
        lay.addLayout(setting_row("Текстовая модель", self.model_combo, 340))

        lay.addSpacing(4)
        lay.addWidget(section_label("Система"))
        self.startup_toggle = ToggleSwitch(checked=self.config.get("run_on_startup", False))
        lay.addLayout(setting_row("Автозапуск", self.startup_toggle))

        main_lay.addWidget(settings_card)

        # Save button
        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setObjectName("SaveBtn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedWidth(132)
        self.save_btn.clicked.connect(self.save)
        main_lay.addWidget(self.save_btn, 0, Qt.AlignmentFlag.AlignLeft)
        main_lay.addStretch()

        self.stack.addWidget(page)

    # ── Tab 4: Logs ──
    def _build_logs_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(32, 30, 32, 30)
        lay.setSpacing(12)

        title = QLabel("Логи системы")
        title.setObjectName("SectionTitle")
        lay.addWidget(title)

        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setObjectName("LogConsole")
        lay.addWidget(self.log_area)

        btn_clear = QPushButton("Очистить логи")
        btn_clear.setObjectName("ActionBtn")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_logs)
        lay.addWidget(btn_clear, 0, Qt.AlignmentFlag.AlignRight)

        self.stack.addWidget(page)

    # ── Theme ──
    def apply_theme(self, theme, preset=None):
        self.theme_name = theme
        if preset is None:
            preset = self.config.get("visualizer_color_preset", "emerald")
        self.setStyleSheet(get_stylesheet(theme, preset))

        # Update toggle switch colors to match the preset
        if preset in ACCENT_PRESETS:
            acc = ACCENT_PRESETS[preset][theme]
            self.startup_toggle.set_colors(QColor(acc["primary"]), QColor(acc["secondary"]))

        # Update custom widgets
        for btn in self.nav_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self.startup_toggle.set_theme(theme)
        self.theme_seg.set_theme(theme)
        self.shape_seg.set_theme(theme)
        self.size_seg.set_theme(theme)
        self.color_selector.set_theme(theme)
        self.preview_widget.set_theme(theme)

    # ── State ──
    def set_system_state(self, state):
        if state == "idle":
            self.status_value.setText("Готов к работе")
            self.status_value.setStyleSheet("color: #10B981; font-weight: bold; font-size: 12px;")
            self.dash_state_val.setText("Ожидание")
            self.dash_state_val.setStyleSheet("font-weight: 700; font-size: 13px; color: #10B981;")
            self.dash_indicator.setStyleSheet("background-color: #10B981; border-radius: 5px;")
        elif state == "recording":
            self.status_value.setText("Запись...")
            self.status_value.setStyleSheet("color: #06B6D4; font-weight: bold; font-size: 12px;")
            self.dash_state_val.setText("Запись голоса")
            self.dash_state_val.setStyleSheet("font-weight: 700; font-size: 13px; color: #06B6D4;")
            self.dash_indicator.setStyleSheet("background-color: #06B6D4; border-radius: 5px;")
        elif state == "processing":
            self.status_value.setText("Обработка...")
            self.status_value.setStyleSheet("color: #8B5CF6; font-weight: bold; font-size: 12px;")
            self.dash_state_val.setText("AI обработка")
            self.dash_state_val.setStyleSheet("font-weight: 700; font-size: 13px; color: #8B5CF6;")
            self.dash_indicator.setStyleSheet("background-color: #8B5CF6; border-radius: 5px;")

    # ── Navigation ──
    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setObjectName("NavButtonActive" if i == index else "NavButton")
        self.apply_theme(self.theme_name)

        if index == 0:
            self.update_statistics()
        elif index == 2:
            self.load_history()
        elif index == 4:
            self.load_logs()

    # ── Logs ──
    def load_logs(self):
        log_path = "echo.log"
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    self.log_area.setPlainText("".join(lines[-150:]))
                    self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
            except Exception as e:
                self.log_area.setPlainText(f"Ошибка чтения логов: {e}")
        else:
            self.log_area.setPlainText("Лог-файл пуст. Начните диктовку.")

    def append_log(self, text):
        self.log_area.appendPlainText(text)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def clear_logs(self):
        log_path = "echo.log"
        if os.path.exists(log_path):
            try:
                open(log_path, "w", encoding="utf-8").close()
            except Exception:
                pass
        self.log_area.clear()

    # ── History ──
    def load_history(self):
        self.history_entries = history_manager.load_history()
        self.filter_history()

    def filter_history(self):
        query = self.history_search.text().lower()
        self.history_list.clear()
        for idx, entry in enumerate(self.history_entries):
            if query in entry.get("raw_text", "").lower() or query in entry.get("cleaned_text", "").lower():
                time_str = entry.get("timestamp", "").split()[-1][:5]
                snippet = entry.get("cleaned_text", "")[:45].replace("\n", " ")
                if len(entry.get("cleaned_text", "")) > 45:
                    snippet += "..."
                item_text = f"{time_str}\n{snippet}"
                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, idx)
                self.history_list.addItem(item)
        self.clear_detail_panel()

    def show_history_detail(self, item):
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None and idx < len(self.history_entries):
            entry = self.history_entries[idx]
            self.placeholder_detail_label.setVisible(False)
            self.txt_raw.setPlainText(entry.get("raw_text", ""))
            self.txt_clean.setPlainText(entry.get("cleaned_text", ""))
            time_str = entry.get("timestamp", "")
            lat = entry.get("total_latency", 0.0)
            model = entry.get("model", "")
            self.detail_meta.setText(f"Время: {time_str}\nЗадержка: {lat}s  •  Модель: {model}")
            self.detail_meta.setVisible(True)
            self.lbl_raw.setVisible(True)
            self.txt_raw.setVisible(True)
            self.lbl_clean.setVisible(True)
            self.txt_clean.setVisible(True)
            self.copy_btn_widget.setVisible(True)

    def clear_detail_panel(self):
        self.placeholder_detail_label.setVisible(True)
        self.detail_meta.setVisible(False)
        self.lbl_raw.setVisible(False)
        self.txt_raw.setVisible(False)
        self.lbl_clean.setVisible(False)
        self.txt_clean.setVisible(False)
        self.copy_btn_widget.setVisible(False)
        self.txt_raw.clear()
        self.txt_clean.clear()

    def copy_raw_text(self):
        QApplication.clipboard().setText(self.txt_raw.toPlainText())

    def copy_clean_text(self):
        QApplication.clipboard().setText(self.txt_clean.toPlainText())

    def clear_all_history(self):
        history_manager.clear_history()
        self.load_history()
        self.update_statistics()

    def update_statistics(self):
        stats = history_manager.get_statistics()
        self.val_total.setText(str(stats["total_dictations"]))
        self.val_lat.setText(f"{stats['avg_total_latency']:.1f} сек")
        self.val_words.setText(str(stats["total_words"]))

    # ── Settings ──
    def toggle_api_visibility(self):
        if self.api_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_api.setText("Скрыть")
        else:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_api.setText("Показать")

    def save(self):
        self.config["api_key"] = self.api_input.text().strip()
        self.config["hotkey"] = self.hotkey_combo.currentText()
        self.config["text_model"] = self.model_combo.currentText()
        self.config["theme"] = "dark" if self.theme_seg.currentIndex() == 0 else "light"
        self.config["run_on_startup"] = self.startup_toggle.isChecked()
        self.save_callback(self.config)
        self.save_btn.setText("Сохранено!")
        self.save_btn.setEnabled(False)
        QTimer.singleShot(1500, self.reset_save_btn)

    def reset_save_btn(self):
        self.save_btn.setText("Сохранить")
        self.save_btn.setEnabled(True)

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            self.hide()


# ──────────────────────────────────────────────
#  Overlay Window
# ──────────────────────────────────────────────

class OverlayWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.vis_style = "wave"
        self.color_preset = "emerald"
        self.size_key = "medium"

        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        w, h = VISUALIZER_SIZES[self.size_key]
        self.setFixedSize(w, h)
        self.state = "idle"
        self.volume = 0.0
        self.target_volume = 0.0
        self.phase = 0.0
        self.spinner_angle = 0

        self.reposition()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def apply_config(self, config):
        self.set_vis_style(config.get("visualizer_style", "wave"))
        self.set_color_preset(config.get("visualizer_color_preset", "emerald"))
        self.set_vis_size(config.get("visualizer_size", "medium"))

    def set_vis_style(self, style):
        self.vis_style = style

    def set_color_preset(self, key):
        if key in VISUALIZER_PRESETS:
            self.color_preset = key

    def set_vis_size(self, size_key):
        if size_key in VISUALIZER_SIZES:
            self.size_key = size_key
            w, h = VISUALIZER_SIZES[size_key]
            self.setFixedSize(w, h)
            self.reposition()

    def reposition(self):
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if not screen:
            screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            x = sg.x() + (sg.width() - self.width()) // 2
            y = sg.y() + sg.height() - self.height() - 15
            self.move(x, y)

    def set_theme(self, theme_name):
        self.theme = theme_name
        self.update()

    def update_animation(self):
        if self.state == "processing":
            self.spinner_angle = (self.spinner_angle + 45) % 360
            self.update()
        elif self.state == "recording":
            self.volume += (self.target_volume - self.volume) * 0.25
            self.target_volume = max(0.0, self.target_volume - 0.04)
            self.phase += 0.08
            self.update()

    def set_volume(self, volume):
        self.target_volume = volume

    def set_state(self, state):
        self.state = state
        if state == "idle":
            self.hide()
        else:
            if state == "recording":
                self.volume = 0.0
                self.target_volume = 0.0
                self.phase = 0.0
            elif state == "processing":
                self.spinner_angle = 0
            self.reposition()
            self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = self.width(), self.height()
        preset = VISUALIZER_PRESETS.get(self.color_preset, VISUALIZER_PRESETS["emerald"])

        # Soft translucent pill
        if self.theme == "light":
            bg_color = QColor(250, 250, 250, 185)
            glow_color = QColor(255, 255, 255, 70)
        else:
            bg_color = QColor(10, 14, 20, 172)
            glow_color = QColor(255, 255, 255, 24)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, w, h), 10, 10)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(glow_color, 1))
        painter.drawRoundedRect(QRectF(1.5, 1.5, w - 3, h - 3), 9, 9)

        if self.state == "recording":
            if self.vis_style == "wave":
                self._paint_wave(painter, w, h, preset)
            elif self.vis_style == "bars":
                self._paint_bars(painter, w, h, preset)
            elif self.vis_style == "dots":
                self._paint_dots(painter, w, h, preset)
            elif self.vis_style == "ribbon":
                self._paint_ribbon(painter, w, h, preset)
        elif self.state == "processing":
            self._paint_spinner(painter, w, h, preset)

        painter.end()

    def _paint_wave(self, painter, w, h, preset):
        center_y = h / 2
        max_amplitude = h * 0.38

        for wave_cfg in preset["waves"]:
            color = wave_cfg[self.theme]
            amp_mult = wave_cfg["amp"]
            freq = wave_cfg["freq"]
            phase_mult = wave_cfg["phase"]
            pen_w = wave_cfg["width"]

            path = QPainterPath()
            first = True
            curr_amp = max_amplitude * min(1.0, self.volume) * amp_mult
            if curr_amp < 0.5:
                curr_amp = 0.5 * amp_mult

            for x in range(6, w - 6):
                t = (x - 6) / max(1, (w - 12))
                envelope = math.pow(math.sin(math.pi * t), 2.0)
                angle = (x * freq) + (self.phase * phase_mult)
                y = center_y + (curr_amp * envelope * math.sin(angle))
                if first:
                    path.moveTo(x, y)
                    first = False
                else:
                    path.lineTo(x, y)

            pen = QPen(color)
            pen.setWidthF(pen_w)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawPath(path)

    def _paint_bars(self, painter, w, h, preset):
        num_bars = max(5, int(w / 8))
        bar_w = max(2.5, (w - 12) / (num_bars * 1.6))
        gap = (w - 12 - bar_w * num_bars) / max(1, num_bars - 1)
        max_h = h * 0.7
        center_y = h / 2
        colors = [wc[self.theme] for wc in preset["waves"]]

        for i in range(num_bars):
            t = i / max(1, num_bars - 1)
            bar_vol = self.volume * (0.4 + 0.6 * math.sin(self.phase * 1.5 + i * 0.8) ** 2)
            bar_h = max(2, max_h * bar_vol)
            bx = 6 + i * (bar_w + gap)
            by = center_y - bar_h / 2

            if t < 0.5:
                color = _lerp_color(colors[0], colors[1], t * 2)
            else:
                color = _lerp_color(colors[1], colors[2], (t - 0.5) * 2)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(QRectF(bx, by, bar_w, bar_h), bar_w / 2, bar_w / 2)

    def _paint_dots(self, painter, w, h, preset):
        colors = [wc[self.theme] for wc in preset["waves"]]
        count = max(7, int(w / 11))
        gap = w / max(1, count)
        center_y = h / 2

        for i in range(count):
            t = i / max(1, count - 1)
            pulse = 0.45 + 0.55 * math.sin(self.phase * 1.8 + i * 0.7) ** 2
            radius = 2.0 + self.volume * pulse * h * 0.16
            x = gap * (i + 0.5)
            color = _lerp_color(colors[0], colors[1 if t < 0.65 else 2], min(1.0, t * 1.4))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(x, center_y), radius, radius)

    def _paint_ribbon(self, painter, w, h, preset):
        center_y = h / 2
        colors = [wc[self.theme] for wc in preset["waves"]]
        amp = max(1.4, h * (0.14 + 0.24 * self.volume))
        pad = 7

        path = QPainterPath()
        path.moveTo(pad, center_y)
        for x in range(pad, w - pad):
            t = (x - pad) / max(1, (w - 2 * pad))
            y = center_y + amp * math.sin(self.phase * 1.1 + t * math.pi * 2.2)
            y += amp * 0.45 * math.sin(self.phase * -0.7 + t * math.pi * 5.1)
            path.lineTo(x, y)

        pen = QPen(colors[0])
        pen.setWidthF(4.0)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

        pen = QPen(colors[1])
        pen.setWidthF(1.6)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

    def _paint_spinner(self, painter, w, h, preset):
        center_x, center_y = w / 2, h / 2
        base_color = preset["waves"][0][self.theme]

        painter.translate(center_x, center_y)
        painter.rotate(self.spinner_angle)

        segments = 8
        for i in range(segments):
            opacity = int(255 - (255 / segments) * i)
            pen = QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), opacity))
            pen.setWidth(2)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            painter.drawLine(0, 3, 0, 6)
            painter.rotate(-360 / segments)

        painter.resetTransform()

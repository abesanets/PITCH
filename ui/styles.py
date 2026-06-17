import os
import sys
from PyQt6.QtGui import QColor
from .styles_data import ACCENT_PRESETS

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Fixed accent palette — indigo/violet for premium look
UI_PRIMARY  = "#7C3AED"
UI_HOVER    = "#6D28D9"
UI_SELECTED = "#1E1B4B"


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two QColors."""
    return QColor(
        int(c1.red()   + (c2.red()   - c1.red())   * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue()  + (c2.blue()  - c1.blue())  * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


def get_stylesheet(theme="dark", preset_key="mono"):
    """Generate stylesheet based on theme (always dark)."""
    bg          = "#080812"
    sidebar     = "#0E0E1A"
    surface     = "#111120"
    surface2    = "#161628"
    text        = "#E8E6FF"
    muted       = "#7B7AA0"
    faint       = "#4A4870"
    border      = "#1E1D35"
    nav_hover   = "#17162A"
    selected    = "#1E1B4B"
    console     = "#0E0E1A"
    input_bg    = "#111120"
    primary     = "#7C3AED"
    hover       = "#8B5CF6"
    accent_glow = "rgba(124,58,237,0.15)"
    seg_act_bg  = "rgba(124,58,237,0.18)"
    seg_act_bdr = "rgba(139,92,246,0.50)"
    seg_act_txt = "#C4B5FD"
    badge_bg    = "rgba(124,58,237,0.15)"
    badge_bdr   = "rgba(139,92,246,0.40)"

    return f"""
        /* ── Global ── */
        QWidget#DashboardWindow {{
            background-color: {bg};
        }}
        QWidget {{
            font-family: "Inter", "Segoe UI Variable", "Segoe UI", "SF Pro Display", sans-serif;
            font-size: 13px;
            color: {text};
        }}

        /* ── Title Bar ── */
        QFrame#TitleBar {{
            background-color: {sidebar};
            border-bottom: 1px solid {border};
        }}
        QLabel#TitleBarLabel {{
            font-size: 11px;
            font-weight: 600;
            color: {muted};
            letter-spacing: 1px;
            background: transparent;
        }}
        QPushButton#TitleBtn {{
            background: transparent;
            color: {muted};
            border: none;
            font-size: 13px;
            font-weight: 400;
            border-radius: 0px;
        }}
        QPushButton#TitleBtn:hover {{
            background: {nav_hover};
            color: {text};
        }}
        QPushButton#TitleBtnClose {{
            background: transparent;
            color: {muted};
            border: none;
            font-size: 13px;
            font-weight: 400;
            border-radius: 0px;
        }}
        QPushButton#TitleBtnClose:hover {{
            background: #DC2626;
            color: #FFFFFF;
        }}

        /* ── Sidebar ── */
        QFrame#Sidebar {{
            background-color: {sidebar};
            border-right: 1px solid {border};
        }}
        QLabel {{ color: {text}; background: transparent; }}

        /* Logo text */
        QLabel#AppName {{
            font-size: 16px;
            font-weight: 800;
            color: {text};
            letter-spacing: 2px;
        }}
        QLabel#AppSub {{
            font-size: 10px;
            color: {faint};
            letter-spacing: 0.5px;
        }}

        /* Nav buttons */
        QPushButton#NavBtn {{
            text-align: left;
            padding: 9px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            border: none;
            background: transparent;
            color: {muted};
        }}
        QPushButton#NavBtn:hover {{
            background: {nav_hover};
            color: {text};
        }}
        QPushButton#NavBtnActive {{
            text-align: left;
            padding: 9px 14px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: {selected};
            color: {text};
        }}

        /* Status/version */
        QLabel#StatusDot {{
            font-size: 11px;
            color: {muted};
        }}
        QLabel#VersionLbl {{
            font-size: 10px;
            color: {faint};
            letter-spacing: 0.5px;
        }}

        /* ── Content area ── */
        QLabel#PageTitle {{
            font-size: 20px;
            font-weight: 700;
            color: {text};
            letter-spacing: -0.3px;
        }}
        QLabel#SectionCap {{
            font-size: 10px;
            font-weight: 700;
            color: {faint};
            letter-spacing: 1.2px;
        }}
        QLabel#FieldLbl {{
            font-size: 13px;
            font-weight: 500;
            color: {muted};
        }}

        /* Cards */
        QFrame#Card {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 14px;
        }}
        QFrame#SubCard {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 10px;
        }}

        /* Stat cards */
        QLabel#StatNum {{
            font-size: 26px;
            font-weight: 800;
            color: {text};
            letter-spacing: -0.5px;
        }}
        QLabel#StatCap {{
            font-size: 10px;
            color: {faint};
            font-weight: 700;
            letter-spacing: 1px;
        }}

        /* Inputs */
        QLineEdit, QComboBox {{
            padding: 9px 13px;
            background: {input_bg};
            border: 1px solid {border};
            color: {text};
            border-radius: 9px;
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {primary};
            background: {surface};
        }}
        QComboBox::drop-down {{ border: none; width: 28px; background: transparent; }}
        QComboBox::down-arrow {{ image: none; width: 0; height: 0; }}
        QComboBox QAbstractItemView {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 9px;
            selection-background-color: {selected};
            selection-color: {text};
            color: {text};
            outline: 0;
            padding: 4px;
        }}

        /* Primary button */
        QPushButton#PrimaryBtn {{
            padding: 9px 20px;
            font-weight: 700;
            font-size: 13px;
            border-radius: 9px;
            border: none;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #7C3AED, stop:1 #3B82F6);
            color: #FFFFFF;
            letter-spacing: 0.3px;
        }}
        QPushButton#PrimaryBtn:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #6D28D9, stop:1 #2563EB);
        }}
        QPushButton#PrimaryBtn:disabled {{
            background: {border};
            color: {faint};
        }}

        /* Secondary button */
        QPushButton#SecondaryBtn {{
            padding: 9px 20px;
            font-weight: 500;
            font-size: 13px;
            border-radius: 9px;
            border: 1px solid {border};
            background: {surface2};
            color: {muted};
        }}
        QPushButton#SecondaryBtn:hover {{
            background: {nav_hover};
            color: {text};
            border-color: {primary};
        }}

        /* List widget */
        QListWidget {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 10px;
            color: {text};
            outline: 0;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 7px 10px;
            border-radius: 7px;
            color: {muted};
        }}
        QListWidget::item:hover {{ background: {nav_hover}; color: {text}; }}
        QListWidget::item:selected {{ background: {selected}; color: {text}; }}

        /* History cards container */
        QWidget#HistoryCardsWidget {{
            background: {bg};
        }}

        /* Hide horizontal scrollbar */
        QScrollBar:horizontal {{
            border: none;
            background: transparent;
            height: 0px;
        }}
        QScrollBar::handle:horizontal {{ background: transparent; }}
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{ background: transparent; }}

        /* Text areas */
        QPlainTextEdit {{
            background: {console};
            border: 1px solid {border};
            border-radius: 10px;
            color: {text};
            padding: 12px;
            selection-background-color: {primary};
        }}
        QPlainTextEdit#LogConsole {{
            font-family: "Cascadia Mono", "JetBrains Mono", "Consolas", monospace;
            font-size: 11px;
            color: {muted};
        }}

        /* Detail labels */
        QLabel#DetailLbl {{
            font-size: 10px;
            font-weight: 700;
            color: {faint};
            letter-spacing: 1px;
        }}
        QLabel#DetailMeta {{
            font-size: 11px;
            color: {faint};
        }}
        QLabel#HintTitle {{
            font-weight: 600;
            font-size: 13px;
            color: {text};
        }}
        QLabel#HintBody {{
            font-size: 12px;
            color: {muted};
        }}

        /* Hotkey badge */
        QLabel#HotkeyBadge {{
            font-size: 11px;
            font-weight: 700;
            color: {primary};
            background: {badge_bg};
            border: 1px solid {badge_bdr};
            border-radius: 6px;
            padding: 4px 10px;
            letter-spacing: 0.5px;
        }}

        /* Recent dictation items */
        QFrame#RecentItem {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 10px;
        }}
        QLabel#RecentSnippet {{
            font-size: 12px;
            color: {text};
        }}
        QWidget#RecentSnippet {{
            font-size: 12px;
            color: {text};
        }}
        QLabel#RecentMeta {{
            font-size: 10px;
            color: {faint};
        }}
        QLabel#HistoryLatency {{
            font-size: 12px;
            font-weight: 700;
            color: {primary};
        }}

        /* Scrollbar */
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 6px;
            margin: 0px;
            border-radius: 3px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        QScrollBar::handle:vertical {{
            background: {border};
            min-height: 30px;
            border-radius: 3px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {faint}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        /* Preview frame */
        QFrame#PreviewFrame {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 12px;
        }}

        /* Slider */
        QSlider::groove:horizontal {{
            height: 4px;
            background: {border};
            border-radius: 2px;
        }}
        QSlider::handle:horizontal {{
            background: {primary};
            width: 14px;
            height: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {hover};
        }}
        QSlider::sub-page:horizontal {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #7C3AED, stop:1 #3B82F6);
            border-radius: 2px;
        }}

        /* SegmentedControl active state */
        QWidget#SegActive {{
            background: {seg_act_bg};
            border: 1px solid {seg_act_bdr};
            color: {seg_act_txt};
        }}
    """

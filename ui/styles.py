import os
import sys
from PyQt6.QtGui import QColor

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two QColors."""
    return QColor(
        int(c1.red()   + (c2.red()   - c1.red())   * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue()  + (c2.blue()  - c1.blue())  * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


def get_stylesheet(theme="dark"):
    """Generate stylesheet based on theme (Dark Pixel aesthetic)."""
    bg          = "#111115"
    sidebar     = "#16161e"
    content_bg  = "#1a1a24"
    surface     = "#20202c"
    surface2    = "#28283b"
    text        = "#f0f0f5"
    muted       = "#9090a2"
    faint       = "#5a5a72"
    border      = "#38384d"
    nav_hover   = "#262638"
    selected    = "#2e2e40"
    console     = "#14141c"
    input_bg    = "#181822"
    primary     = "#e0e0e8"
    hover       = "#ffffff"
    badge_bg    = "#252536"
    badge_bdr   = "#38384d"

    return f"""
        /* ── Global ── */
        QWidget#DashboardWindow {{
            background-color: {bg};
            border-radius: 0px;
            border: 2px solid {border};
        }}
        QWidget {{
            font-family: "Courier New", "Consolas", "Segoe UI", monospace;
            font-size: 13px;
            color: {text};
        }}

        /* ── Title Bar ── */
        QFrame#TitleBar {{
            background-color: {sidebar};
            border-bottom: 2px solid {border};
            border-radius: 0px;
        }}
        QFrame#TitleBar QWidget {{
            color: {text};
        }}
        QLabel#TitleBarLabel {{
            font-size: 11px;
            font-weight: 700;
            color: {muted};
            letter-spacing: 1px;
            background: transparent;
        }}
        QPushButton#TitleBtn {{
            background: transparent;
            color: {muted};
            border: none;
            font-size: 13px;
            font-weight: 700;
            border-radius: 0px;
        }}
        QPushButton#TitleBtn:hover {{
            background: {nav_hover};
            color: {hover};
        }}
        QPushButton#TitleBtnClose {{
            background: transparent;
            color: {muted};
            border: none;
            font-size: 13px;
            font-weight: 700;
            border-radius: 0px;
        }}
        QPushButton#TitleBtnClose:hover {{
            background: #dc2626;
            color: #ffffff;
            border-radius: 0px;
        }}

        /* ── Sidebar ── */
        QFrame#Sidebar {{
            background-color: {sidebar};
            border-right: 2px solid {border};
            border-radius: 0px;
        }}
        QFrame#Sidebar QWidget {{
            color: {text};
        }}
        QLabel {{ color: {text}; background: transparent; }}

        #AppName {{
            font-family: "Courier New", "Consolas", monospace;
            font-size: 32px;
            font-weight: 900;
            color: {text};
            margin-bottom: 4px;
        }}
        QLabel#AppSub {{
            font-size: 10px;
            color: {muted};
            letter-spacing: 0.5px;
        }}

        QPushButton#NavBtn {{
            text-align: left;
            padding: 9px 12px;
            border-radius: 0px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid transparent;
            background: transparent;
            color: {muted};
        }}
        QPushButton#NavBtn:hover {{
            background: {nav_hover};
            color: {text};
            border: 1px solid {border};
        }}
        QPushButton#NavBtnActive {{
            text-align: left;
            padding: 9px 12px;
            border-radius: 0px;
            font-size: 13px;
            font-weight: 700;
            border: 1px solid {border};
            background: {surface};
            color: {hover};
        }}

        /* Status/version */
        QLabel#VersionLbl {{
            font-size: 10px;
            color: {faint};
            letter-spacing: 0.5px;
        }}

        /* ── Main Content Container ── */
        QFrame#MainContentContainer {{
            background-color: {content_bg};
            border-radius: 0px;
            border: 2px solid {border};
        }}
        QStackedWidget {{
            background: transparent;
        }}
        QStackedWidget > QWidget {{
            background: transparent;
        }}

        #PageTitle {{
            font-size: 24px;
            font-weight: 900;
            color: {text};
            letter-spacing: 0px;
        }}
        QLabel#SectionCap {{
            font-size: 10px;
            font-weight: 700;
            color: {faint};
            letter-spacing: 1.2px;
        }}
        QLabel#FieldLbl {{
            font-size: 13px;
            font-weight: 700;
            color: {muted};
        }}

        /* Cards */
        QFrame#Card {{
            background: {surface};
            border: 2px solid {border};
            border-radius: 0px;
        }}
        QFrame#SubCard {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 0px;
        }}

        /* Stat cards */
        QLabel#StatNum {{
            font-size: 22px;
            font-weight: 900;
            color: {text};
            letter-spacing: 0px;
        }}
        QLabel#StatCap {{
            font-size: 10px;
            color: {muted};
            font-weight: 700;
            letter-spacing: 0.5px;
        }}

        /* Inputs */
        QLineEdit, QComboBox {{
            padding: 8px 12px;
            background: {input_bg};
            border: 2px solid {border};
            color: {text};
            border-radius: 0px;
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {text};
            background: {surface};
        }}
        QComboBox::drop-down {{ border: none; width: 28px; background: transparent; }}
        QComboBox::down-arrow {{ image: none; width: 0; height: 0; }}
        QComboBox QAbstractItemView {{
            background: {surface2};
            border: 2px solid {border};
            border-radius: 0px;
            selection-background-color: {selected};
            selection-color: {hover};
            color: {text};
            outline: 0;
            padding: 4px;
        }}

        /* Primary button */
        QPushButton#PrimaryBtn {{
            padding: 9px 20px;
            font-weight: 700;
            font-size: 13px;
            border-radius: 0px;
            border: 2px solid {text};
            background: {text};
            color: {bg};
            letter-spacing: 0.3px;
        }}
        QPushButton#PrimaryBtn:hover {{
            background: {hover};
            color: {bg};
            border: 2px solid {hover};
        }}
        QPushButton#PrimaryBtn:disabled {{
            background: {surface2};
            border: 2px solid {border};
            color: {faint};
        }}

        /* Secondary button */
        QPushButton#SecondaryBtn {{
            padding: 9px 20px;
            font-weight: 700;
            font-size: 13px;
            border-radius: 0px;
            border: 2px solid {border};
            background: {surface2};
            color: {muted};
        }}
        QPushButton#SecondaryBtn:hover {{
            background: {surface};
            border: 2px solid {text};
            color: {text};
        }}

        /* List widget */
        QListWidget {{
            background: {surface};
            border: 2px solid {border};
            border-radius: 0px;
            color: {text};
            outline: 0;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 7px 10px;
            border-radius: 0px;
            color: {muted};
        }}
        QListWidget::item:hover {{ background: {nav_hover}; color: {text}; }}
        QListWidget::item:selected {{ background: {selected}; color: {hover}; border: 1px solid {border}; }}

        /* History cards container */
        QWidget#HistoryCardsWidget {{
            background: transparent;
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
            border: 2px solid {border};
            border-radius: 0px;
            color: {text};
            padding: 10px;
            selection-background-color: {selected};
        }}
        QPlainTextEdit#LogConsole {{
            font-family: "Courier New", "Consolas", monospace;
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
            font-weight: 700;
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
            color: {text};
            background: {badge_bg};
            border: 1px solid {badge_bdr};
            border-radius: 0px;
            padding: 4px 10px;
            letter-spacing: 0.5px;
        }}

        /* Recent dictation items (Flat list style) & History items */
        QFrame#RecentItemFlat, QFrame#RecentItem {{
            background: transparent;
            border: 1px solid transparent;
            border-radius: 0px;
        }}
        QFrame#RecentItemFlat:hover, QFrame#RecentItem:hover {{
            background: {surface};
            border: 1px solid {border};
        }}
        QLabel#RecentSnippetFlat, QLabel#RecentSnippet {{
            font-size: 13px;
            font-weight: 700;
            color: {text};
        }}
        QLabel#RecentMetaFlat, QLabel#RecentMeta {{
            font-size: 10px;
            font-weight: 600;
            color: {muted};
        }}
        QLabel#HistoryLatency {{
            font-size: 12px;
            font-weight: 700;
            color: {text};
        }}

        /* Style description / example labels in Recognition tab */
        QLabel#StyleDescLbl {{
            font-size: 11px;
            color: {faint};
        }}
        QLabel#StyleExampleLbl {{
            font-size: 12px;
            font-weight: 500;
            color: {muted};
        }}

        /* Scrollbar */
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{
            border: none;
            background: {console};
            width: 8px;
            margin: 0px;
            border-radius: 0px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
        }}
        QScrollBar::handle:vertical {{
            background: {border};
            min-height: 30px;
            border-radius: 0px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {muted}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        /* Preview frame */
        QFrame#PreviewFrame {{
            background: {surface2};
            border: 2px solid {border};
            border-radius: 0px;
        }}

        /* Slider */
        QSlider::groove:horizontal {{
            height: 6px;
            background: {surface2};
            border: 1px solid {border};
            border-radius: 0px;
        }}
        QSlider::handle:horizontal {{
            background: {text};
            width: 14px;
            height: 14px;
            margin: -4px 0;
            border-radius: 0px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {hover};
        }}
        QSlider::sub-page:horizontal {{
            background: {muted};
            border-radius: 0px;
        }}

        /* SegmentedControl active state */
        QWidget#SegActive {{
            background: {surface};
            border: 2px solid {text};
            color: {hover};
        }}
    """


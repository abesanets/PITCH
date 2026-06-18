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


def get_stylesheet(theme="dark", preset_key="mono"):
    """Generate stylesheet based on theme (always dark)."""
    bg          = "#DFCEBA"
    sidebar     = "#DFCEBA"
    content_bg  = "#6D5141"
    surface     = "#5A4234"
    surface2    = "#4E382B"
    text        = "#F5ECE3"
    muted       = "#D4C5B9"
    faint       = "#968375"
    border      = "#7D6454"
    nav_hover   = "#E5D7C6"
    selected    = "#F5ECE3"
    console     = "#4E382B"
    input_bg    = "#4E382B"
    primary     = "#DFCEBA"
    hover       = "#F5ECE3"
    accent_glow = "rgba(223,206,186,0.15)"
    seg_act_bg  = "rgba(223,206,186,0.18)"
    seg_act_bdr = "rgba(245,236,227,0.50)"
    seg_act_txt = "#F5ECE3"
    badge_bg    = "rgba(223,206,186,0.15)"
    badge_bdr   = "rgba(245,236,227,0.40)"

    return f"""
        /* ── Global ── */
        QWidget#DashboardWindow {{
            background-color: {bg};
            border-radius: 20px;
            border: 1px solid #7D6454;
        }}
        QWidget {{
            font-family: "Comic Sans MS", "Segoe UI Variable", "Segoe UI", sans-serif;
            font-size: 13px;
            color: {text};
        }}

        /* ── Title Bar ── */
        QFrame#TitleBar {{
            background-color: {sidebar};
            border-bottom: none;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
        }}
        QFrame#TitleBar QWidget {{
            color: #281B15;
        }}
        QLabel#TitleBarLabel {{
            font-size: 11px;
            font-weight: 600;
            color: #4E382B;
            letter-spacing: 1px;
            background: transparent;
        }}
        QPushButton#TitleBtn {{
            background: transparent;
            color: #4E382B;
            border: none;
            font-size: 13px;
            font-weight: 400;
            border-radius: 0px;
        }}
        QPushButton#TitleBtn:hover {{
            background: {nav_hover};
            color: #281B15;
        }}
        QPushButton#TitleBtnClose {{
            background: transparent;
            color: #4E382B;
            border: none;
            font-size: 13px;
            font-weight: 400;
            border-radius: 0px;
        }}
        QPushButton#TitleBtnClose:hover {{
            background: #DC2626;
            color: #FFFFFF;
            border-top-right-radius: 20px;
        }}

        /* ── Sidebar ── */
        QFrame#Sidebar {{
            background-color: {sidebar};
            border-right: none;
            border-bottom-left-radius: 20px;
        }}
        QFrame#Sidebar QWidget {{
            color: #281B15;
        }}
        QLabel {{ color: {text}; background: transparent; }}

        #AppName {{
            font-family: "Pacifico", "Brush Script MT", "Great Vibes", "Lucida Handwriting", "Segoe Script", cursive;
            font-size: 50px;
            font-weight: bold;
            color: #281B15;
            margin-bottom: 4px;
        }}
        QLabel#AppSub {{
            font-size: 10px;
            color: #7D6454;
            letter-spacing: 0.5px;
        }}

        QPushButton#NavBtn {{
            text-align: left;
            padding: 9px 10px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: transparent;
            color: #281B15;
        }}
        QPushButton#NavBtnActive {{
            text-align: left;
            padding: 9px 10px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: rgba(78, 56, 43, 0.15);
            color: #281B15;
        }}

        /* Status/version */
        QLabel#VersionLbl {{
            font-size: 10px;
            color: #7D6454;
            letter-spacing: 0.5px;
        }}

        /* ── Main Content Container ── */
        QFrame#MainContentContainer {{
            background-color: {content_bg};
            border-top-left-radius: 24px;
            border-bottom-left-radius: 24px;
            border-top-right-radius: 24px;
            border-bottom-right-radius: 24px;
            border: none;
        }}
        QStackedWidget {{
            background: transparent;
        }}
        QStackedWidget > QWidget {{
            background: transparent;
        }}


        #PageTitle {{
            font-size: 26px;
            font-weight: 800;
            color: #FFFFFF;
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
            border: none;
            border-radius: 16px;
        }}
        QFrame#SubCard {{
            background: {surface2};
            border: none;
            border-radius: 12px;
        }}

        /* Stat cards */
        QLabel#StatNum {{
            font-size: 24px;
            font-weight: 900;
            color: {text};
            letter-spacing: -0.8px;
        }}
        QLabel#StatCap {{
            font-size: 10px;
            color: {muted};
            font-weight: 800;
            letter-spacing: 0.5px;
        }}

        /* Inputs */
        QLineEdit, QComboBox {{
            padding: 9px 16px;
            background: {input_bg};
            border: none;
            color: {text};
            border-radius: 18px;
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: none;
            background: {surface};
        }}
        QComboBox::drop-down {{ border: none; width: 28px; background: transparent; }}
        QComboBox::down-arrow {{ image: none; width: 0; height: 0; }}
        QComboBox QAbstractItemView {{
            background: {surface2};
            border: none;
            border-radius: 12px;
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
            border-radius: 18px;
            border: none;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #DFCEBA, stop:1 #F5ECE3);
            color: #281B15;
            letter-spacing: 0.3px;
        }}
        QPushButton#PrimaryBtn:hover {{
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #E5D7C6, stop:1 #FFFFFF);
            color: #281B15;
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
            border-radius: 18px;
            border: none;
            background: {surface2};
            color: {muted};
        }}
        QPushButton#SecondaryBtn:hover {{
            background: {surface};
            color: {text};
        }}

        /* List widget */
        QListWidget {{
            background: {surface};
            border: none;
            border-radius: 12px;
            color: {text};
            outline: 0;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 7px 10px;
            border-radius: 8px;
            color: {muted};
        }}
        QListWidget::item:hover {{ background: {nav_hover}; color: {text}; }}
        QListWidget::item:selected {{ background: {selected}; color: {text}; }}

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
            border: none;
            border-radius: 12px;
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
            border: none;
            border-radius: 8px;
            padding: 4px 10px;
            letter-spacing: 0.5px;
        }}

        /* Recent dictation items (Flat list style) & History items */
        QFrame#RecentItemFlat, QFrame#RecentItem {{
            background: transparent;
            border: none;
            border-radius: 12px;
        }}
        QFrame#RecentItemFlat:hover, QFrame#RecentItem:hover {{
            background: rgba(255, 255, 255, 0.04);
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
            color: {primary};
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
            border: none;
            border-radius: 16px;
        }}

        /* Slider */
        QSlider::groove:horizontal {{
            height: 6px;
            background: {surface2};
            border-radius: 3px;
        }}
        QSlider::handle:horizontal {{
            background: {primary};
            width: 14px;
            height: 14px;
            margin: -4px 0;
            border-radius: 7px;
        }}
        QSlider::handle:horizontal:hover {{
            background: {hover};
        }}
        QSlider::sub-page:horizontal {{
            background: {primary};
            border-radius: 3px;
        }}

        /* SegmentedControl active state */
        QWidget#SegActive {{
            background: {seg_act_bg};
            border: 1px solid {seg_act_bdr};
            color: {seg_act_txt};
        }}
    """

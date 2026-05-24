"""Styles and themes for VoiceAssistant UI"""
from PyQt6.QtGui import QColor
from .styles_data import ACCENT_PRESETS

# Fixed UI accent — independent of the visualizer colour preset
UI_PRIMARY  = "#A0A0A0"   # muted gray
UI_HOVER    = "#8A8A8A"   # slightly lighter gray
UI_SELECTED = "#353535"   # dark muted tone for selected/active backgrounds


def _lerp_color(c1, c2, t):
    """Linearly interpolate between two colors"""
    return QColor(
        int(c1.red()   + (c2.red()   - c1.red())   * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue()  + (c2.blue()  - c1.blue())  * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


def get_stylesheet(theme, preset_key="mono"):
    """Generate stylesheet based on theme. preset_key is used only for
    visualizer-related colours; all UI chrome uses fixed muted palette."""

    if theme == "light":
        bg        = "#F5F5F5"
        sidebar   = "#FFFFFF"
        surface   = "#FFFFFF"
        surface2  = "#FAFAFA"
        text      = "#1A1A1A"
        muted     = "#6B6B6B"
        faint     = "#9A9A9A"
        border    = "#E0E0E0"
        nav_hover = "#F0F0F0"
        selected  = "#E8E8E8"
        console   = "#FAFAFA"
        input_bg  = "#FFFFFF"
        primary   = "#2A2A2A"
        hover     = "#404040"
        seg_act_bg  = "rgba(42,42,42,0.12)"
        seg_act_bdr = "rgba(42,42,42,0.30)"
        seg_act_txt = "#1A1A1A"
    else:
        bg        = "#1E1E1E"
        sidebar   = "#252525"
        surface   = "#2A2A2A"
        surface2  = "#2F2F2F"
        text      = "#E5E5E5"
        muted     = "#8A8A8A"
        faint     = "#5A5A5A"
        border    = "#3A3A3A"
        nav_hover = "#2D2D2D"
        selected  = "#353535"
        console   = "#252525"
        input_bg  = "#252525"
        primary   = "#A0A0A0"
        hover     = "#8A8A8A"
        seg_act_bg  = "rgba(160,160,160,0.15)"
        seg_act_bdr = "rgba(160,160,160,0.40)"
        seg_act_txt = "#C0C0C0"

    return f"""
        QWidget#DashboardWindow {{
            background-color: {bg};
        }}
        QWidget {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Helvetica Neue", sans-serif;
            font-size: 13px;
            color: {text};
        }}

        /* ── Title Bar ── */
        QFrame#TitleBar {{
            background-color: {sidebar};
            border-bottom: 1px solid {border};
        }}
        QLabel#TitleBarLabel {{
            font-size: 12px;
            font-weight: 600;
            color: {muted};
            letter-spacing: 0.5px;
            background: transparent;
        }}
        QPushButton#TitleBtn {{
            background: transparent;
            color: {muted};
            border: none;
            font-size: 13px;
            font-weight: 400;
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
        }}
        QPushButton#TitleBtnClose:hover {{
            background: #E81123;
            color: #FFFFFF;
        }}

        /* ── Sidebar ── */
        QFrame#Sidebar {{
            background-color: {sidebar};
            border-right: 1px solid {border};
        }}
        QLabel {{ color: {text}; background: transparent; }}

        /* Logo */
        QLabel#AppName {{
            font-size: 15px;
            font-weight: 700;
            color: {text};
            letter-spacing: 1px;
        }}
        QLabel#AppSub {{
            font-size: 10px;
            color: {faint};
            letter-spacing: 0.5px;
        }}

        /* Nav */
        QPushButton#NavBtn {{
            text-align: left;
            padding: 8px 12px;
            border-radius: 6px;
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
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 13px;
            font-weight: 600;
            border: none;
            background: {selected};
            color: {text};
        }}

        /* Status dot label */
        QLabel#StatusDot {{
            font-size: 11px;
            color: {muted};
        }}
        QLabel#VersionLbl {{
            font-size: 10px;
            color: {faint};
        }}

        /* ── Content area ── */
        QLabel#PageTitle {{
            font-size: 16px;
            font-weight: 700;
            color: {text};
        }}
        QLabel#SectionCap {{
            font-size: 10px;
            font-weight: 600;
            color: {faint};
            letter-spacing: 0.8px;
        }}
        QLabel#FieldLbl {{
            font-size: 13px;
            color: {muted};
        }}

        /* Cards */
        QFrame#Card {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 10px;
        }}
        QFrame#SubCard {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 8px;
        }}

        /* Stat */
        QLabel#StatNum {{
            font-size: 20px;
            font-weight: 700;
            color: {text};
        }}
        QLabel#StatCap {{
            font-size: 10px;
            color: {faint};
            font-weight: 600;
            letter-spacing: 0.5px;
        }}

        /* Inputs */
        QLineEdit, QComboBox {{
            padding: 8px 12px;
            background: {input_bg};
            border: 1px solid {border};
            color: {text};
            border-radius: 7px;
            font-size: 13px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 1px solid {primary};
        }}
        QComboBox::drop-down {{ border: none; width: 28px; background: transparent; }}
        QComboBox::down-arrow {{ image: none; width: 0; height: 0; }}
        QComboBox QAbstractItemView {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 7px;
            selection-background-color: {selected};
            selection-color: {text};
            color: {text};
            outline: 0;
            padding: 4px;
        }}

        /* Buttons */
        QPushButton#PrimaryBtn {{
            padding: 8px 18px;
            font-weight: 600;
            font-size: 13px;
            border-radius: 7px;
            border: none;
            background: {primary};
            color: #FFFFFF;
        }}
        QPushButton#PrimaryBtn:hover {{
            background: {hover};
            color: #FFFFFF;
        }}
        QPushButton#PrimaryBtn:disabled {{ background: {border}; color: {faint}; }}

        QPushButton#SecondaryBtn {{
            padding: 8px 18px;
            font-weight: 500;
            font-size: 13px;
            border-radius: 7px;
            border: 1px solid {border};
            background: {surface2};
            color: {muted};
        }}
        QPushButton#SecondaryBtn:hover {{
            background: {nav_hover};
            color: {text};
            border-color: {primary};
        }}

        /* List */
        QListWidget {{
            background: {surface};
            border: 1px solid {border};
            border-radius: 8px;
            color: {text};
            outline: 0;
            padding: 4px;
        }}
        QListWidget::item {{
            padding: 6px 8px;
            border-radius: 6px;
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

        /* Detail labels */
        QLabel#DetailLbl {{
            font-size: 11px;
            font-weight: 600;
            color: {faint};
            letter-spacing: 0.5px;
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
            background: rgba(59,130,246,0.12);
            border: 1px solid rgba(59,130,246,0.35);
            border-radius: 5px;
            padding: 3px 8px;
            letter-spacing: 0.5px;
        }}

        /* Recent dictation items */
        QFrame#RecentItem {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 8px;
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
            font-size: 13px;
            font-weight: 700;
            color: {primary};
        }}

        /* Scrollbar */
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{
            border: none;
            background: transparent;
            width: 16px;
            margin: 0px;
            border-radius: 8px;
        }}
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background: transparent;
            border-radius: 8px;
        }}
        QScrollBar::handle:vertical {{
            background: {border};
            min-height: 30px;
            border-radius: 8px;
        }}
        QScrollBar::handle:vertical:hover {{ background: {muted}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}

        /* Preview frame */
        QFrame#PreviewFrame {{
            background: {surface2};
            border: 1px solid {border};
            border-radius: 10px;
        }}

        /* Sensitivity slider */
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
        QSlider::sub-page:horizontal {{
            background: {primary};
            border-radius: 2px;
        }}

        /* SegmentedControl active state — exposed as CSS vars via objectName trick.
           Actual painting is done in SegmentedControl._update_styles() using
           the seg_act_* values passed through set_theme(). */
        QWidget#SegActive {{
            background: {seg_act_bg};
            border: 1px solid {seg_act_bdr};
            color: {seg_act_txt};
        }}
    """

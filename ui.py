import os
import sys
import math
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox,
                             QStackedWidget, QPlainTextEdit, QFrame, QApplication,
                             QListWidget, QListWidgetItem, QGridLayout,
                             QSizePolicy, QScrollArea, QSlider)
from PyQt6.QtCore import (Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve,
                           pyqtProperty, pyqtSignal, QPointF)
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QIcon, QPixmap,
                          QCursor, QPainterPath, QLinearGradient)

import history_manager

# ──────────────────────────────────────────────
#  Visualizer Presets & Sizes  (unchanged)
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
    "xs":     (48,  16),
    "small":  (60,  20),
    "medium": (80,  26),
    "large":  (110, 32),
    "xl":     (140, 40),
}

# ──────────────────────────────────────────────
#  Accent Color Presets
# ──────────────────────────────────────────────

ACCENT_PRESETS = {
    "emerald": {
        "dark":  {"primary": "#06B6D4", "secondary": "#10B981", "hover": "#0891B2"},
        "light": {"primary": "#0891B2", "secondary": "#059669", "hover": "#06B6D4"},
    },
    "arctic": {
        "dark":  {"primary": "#38BDF8", "secondary": "#0EA5E9", "hover": "#0284C7"},
        "light": {"primary": "#0284C7", "secondary": "#0369A1", "hover": "#38BDF8"},
    },
    "neon": {
        "dark":  {"primary": "#EC4899", "secondary": "#A855F7", "hover": "#DB2777"},
        "light": {"primary": "#BE185D", "secondary": "#7E22CE", "hover": "#EC4899"},
    },
    "sunset": {
        "dark":  {"primary": "#F59E0B", "secondary": "#EF4444", "hover": "#D97706"},
        "light": {"primary": "#D97706", "secondary": "#B91C1C", "hover": "#F59E0B"},
    },
    "mono": {
        "dark":  {"primary": "#A1A1AA", "secondary": "#52525B", "hover": "#F4F4F5"},
        "light": {"primary": "#18181B", "secondary": "#52525B", "hover": "#3F3F46"},
    },
}

# ──────────────────────────────────────────────
#  Stylesheet  — clean, Telegram-inspired
# ──────────────────────────────────────────────

def get_stylesheet(theme, preset_key="emerald"):
    if preset_key not in ACCENT_PRESETS:
        preset_key = "emerald"
    acc = ACCENT_PRESETS[preset_key][theme]
    primary   = acc["primary"]
    secondary = acc["secondary"]
    hover     = acc["hover"]

    if theme == "light":
        bg        = "#F0F2F5"
        sidebar   = "#FFFFFF"
        surface   = "#FFFFFF"
        surface2  = "#F7F8FA"
        text      = "#0D0D0D"
        muted     = "#6B7280"
        faint     = "#9CA3AF"
        border    = "#E5E7EB"
        nav_hover = "#F3F4F6"
        selected  = "#EFF6FF"
        console   = "#FAFAFA"
        input_bg  = "#FFFFFF"
    else:
        bg        = "#0F1117"
        sidebar   = "#16181F"
        surface   = "#1C1F28"
        surface2  = "#22252F"
        text      = "#F1F3F7"
        muted     = "#8B92A5"
        faint     = "#555D6E"
        border    = "#2A2D38"
        nav_hover = "#1F2330"
        selected  = "#1A2540"
        console   = "#13151C"
        input_bg  = "#13151C"

    return f"""
        QWidget#DashboardWindow {{
            background-color: {bg};
        }}
        QWidget {{
            font-family: "Segoe UI", "Arial", sans-serif;
            font-size: 13px;
            color: {text};
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
        QPushButton#PrimaryBtn:hover {{ background: {hover}; }}
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
            padding: 9px 10px;
            border-radius: 6px;
            color: {muted};
        }}
        QListWidget::item:hover {{ background: {nav_hover}; color: {text}; }}
        QListWidget::item:selected {{ background: {selected}; color: {text}; }}

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

        /* Scrollbar */
        QScrollArea {{ background: transparent; border: none; }}
        QScrollBar:vertical {{
            border: none; background: transparent; width: 6px; margin: 2px 0;
        }}
        QScrollBar::handle:vertical {{
            background: {border}; min-height: 20px; border-radius: 3px;
        }}
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
    """

# ──────────────────────────────────────────────
#  Helper
# ──────────────────────────────────────────────

def _lerp_color(c1, c2, t):
    return QColor(
        int(c1.red()   + (c2.red()   - c1.red())   * t),
        int(c1.green() + (c2.green() - c1.green()) * t),
        int(c1.blue()  + (c2.blue()  - c1.blue())  * t),
        int(c1.alpha() + (c2.alpha() - c1.alpha()) * t),
    )


# ──────────────────────────────────────────────
#  ToggleSwitch  (unchanged logic)
# ──────────────────────────────────────────────

class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = checked
        self._handle_pos = 1.0 if checked else 0.0
        self._theme = "dark"
        self._on_col1 = QColor(6, 182, 212)
        self._on_col2 = QColor(16, 185, 129)
        self._anim = QPropertyAnimation(self, b"handle_position", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def set_colors(self, c1, c2):
        self._on_col1 = c1; self._on_col2 = c2; self.update()

    def get_handle_position(self): return self._handle_pos
    def set_handle_position(self, v): self._handle_pos = v; self.update()
    handle_position = pyqtProperty(float, get_handle_position, set_handle_position)

    def isChecked(self): return self._checked
    def setChecked(self, v):
        self._checked = v; self._handle_pos = 1.0 if v else 0.0; self.update()
    def set_theme(self, t): self._theme = t; self.update()

    def mousePressEvent(self, e):
        self._checked = not self._checked
        self._anim.setStartValue(self._handle_pos)
        self._anim.setEndValue(1.0 if self._checked else 0.0)
        self._anim.start()
        self.toggled.emit(self._checked)

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        r = h / 2
        if self._handle_pos > 0.01:
            grad = QLinearGradient(0, 0, w, 0)
            off = QColor(63, 63, 70) if self._theme == "dark" else QColor(212, 212, 216)
            t = self._handle_pos
            grad.setColorAt(0, _lerp_color(off, self._on_col1, t))
            grad.setColorAt(1, _lerp_color(off, self._on_col2, t))
            p.setBrush(QBrush(grad))
        else:
            p.setBrush(QBrush(QColor(63, 63, 70) if self._theme == "dark" else QColor(212, 212, 216)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)
        m = 3
        d = h - m * 2
        x = m + self._handle_pos * (w - d - m * 2)
        p.setBrush(QBrush(QColor(255, 255, 255)))
        p.drawEllipse(QRectF(x, m, d, d))
        p.end()

# ──────────────────────────────────────────────
#  SegmentedControl  (chip-style)
# ──────────────────────────────────────────────

class SegmentedControl(QWidget):
    currentChanged = pyqtSignal(int)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._options = options
        self._current = 0
        self._theme = "dark"
        self._buttons = []
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(30)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(4)
        for i, text in enumerate(options):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            btn.clicked.connect(lambda _, idx=i: self._on_click(idx))
            lay.addWidget(btn)
            self._buttons.append(btn)
        self._update_styles()

    def _on_click(self, idx):
        if idx != self._current:
            self._current = idx
            self._update_styles()
            self.currentChanged.emit(idx)

    def currentIndex(self): return self._current
    def setCurrentIndex(self, idx): self._current = idx; self._update_styles()
    def set_theme(self, t): self._theme = t; self._update_styles()

    def _update_styles(self):
        for i, btn in enumerate(self._buttons):
            if i == self._current:
                if self._theme == "dark":
                    btn.setStyleSheet("QPushButton { background:#E8F4FF; color:#0B1220; border:1px solid #E8F4FF; border-radius:6px; font-weight:700; font-size:12px; padding:0 11px; }")
                else:
                    btn.setStyleSheet("QPushButton { background:#111827; color:#FFFFFF; border:1px solid #111827; border-radius:6px; font-weight:700; font-size:12px; padding:0 11px; }")
            else:
                if self._theme == "dark":
                    btn.setStyleSheet("QPushButton { background:#1C1F28; color:#8B92A5; border:1px solid #2A2D38; border-radius:6px; font-weight:500; font-size:12px; padding:0 11px; } QPushButton:hover { color:#F1F3F7; background:#22252F; }")
                else:
                    btn.setStyleSheet("QPushButton { background:#FFFFFF; color:#6B7280; border:1px solid #E5E7EB; border-radius:6px; font-weight:500; font-size:12px; padding:0 11px; } QPushButton:hover { color:#0D0D0D; background:#F9FAFB; }")

    def paintEvent(self, e): super().paintEvent(e)


# ──────────────────────────────────────────────
#  ColorPresetSelector  (unchanged logic)
# ──────────────────────────────────────────────

class ColorPresetSelector(QWidget):
    presetChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "emerald"
        self._theme = "dark"
        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._order = ["emerald", "arctic", "neon", "sunset", "mono"]

    def currentPreset(self): return self._current
    def setCurrentPreset(self, k): self._current = k; self.update()
    def set_theme(self, t): self._theme = t; self.update()

    def mousePressEvent(self, e):
        x = e.position().x()
        n = len(self._order)
        total = n * 48
        sx = (self.width() - total) / 2
        for i, key in enumerate(self._order):
            cx = sx + i * 48 + 14
            if abs(x - cx) < 18:
                self._current = key
                self.update()
                self.presetChanged.emit(key)
                break

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        n = len(self._order)
        total = n * 48
        sx = (self.width() - total) / 2
        for i, key in enumerate(self._order):
            preset = VISUALIZER_PRESETS[key]
            cx = sx + i * 48 + 14
            cy = 16
            r = 12
            colors = preset["waves"]
            c1, c2, c3 = colors[0][self._theme], colors[1][self._theme], colors[2][self._theme]
            grad = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
            grad.setColorAt(0.0, QColor(c1.red(), c1.green(), c1.blue(), 220))
            grad.setColorAt(0.5, QColor(c2.red(), c2.green(), c2.blue(), 200))
            grad.setColorAt(1.0, QColor(c3.red(), c3.green(), c3.blue(), 180))
            p.setBrush(QBrush(grad))
            if key == self._current:
                p.setPen(QPen(QColor(6, 182, 212), 2.5))
            else:
                p.setPen(QPen(QColor(39, 39, 42) if self._theme == "dark" else QColor(212, 212, 216), 1))
            p.drawEllipse(QPointF(cx, cy), r, r)
            p.setPen(QPen(QColor(161, 161, 170) if self._theme == "dark" else QColor(113, 113, 122)))
            font = QFont("Segoe UI", 8)
            p.setFont(font)
            name = preset["name"]
            tw = p.fontMetrics().horizontalAdvance(name)
            p.drawText(int(cx - tw / 2), 46, name)
        p.end()

# ──────────────────────────────────────────────
#  PreviewWidget  (unchanged logic, same drawing)
# ──────────────────────────────────────────────

class PreviewWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self._theme = "dark"
        self._style = "wave"
        self._preset_key = "emerald"
        self._size_key = "medium"
        self._sensitivity = 1.0
        self._phase = 0.0
        self._demo_volume = 0.0
        self._demo_target = 0.6
        self._time_counter = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def set_style(self, s): self._style = s; self.update()
    def set_preset(self, k): self._preset_key = k; self.update()
    def set_size(self, k): self._size_key = k; self.update()
    def set_theme(self, t): self._theme = t; self.update()
    def set_sensitivity(self, v): self._sensitivity = v; self.update()

    def _tick(self):
        self._time_counter += 0.033
        self._demo_target = 0.35 + 0.35 * math.sin(self._time_counter * 1.7) + 0.15 * math.sin(self._time_counter * 3.1)
        self._demo_target = max(0.1, min(1.0, self._demo_target))
        self._demo_volume += (self._demo_target - self._demo_volume) * 0.25
        self._phase += 0.08
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        ow, oh = VISUALIZER_SIZES.get(self._size_key, (80, 26))
        ox = (self.width() - ow) / 2
        oy = (self.height() - oh) / 2
        bg = QColor(9, 9, 11, 245) if self._theme == "dark" else QColor(250, 250, 250, 240)
        brd = QColor(39, 39, 42) if self._theme == "dark" else QColor(228, 228, 231)
        p.setBrush(QBrush(bg))
        p.setPen(QPen(brd, 1))
        p.drawRoundedRect(QRectF(ox, oy, ow, oh), 8, 8)
        preset = VISUALIZER_PRESETS.get(self._preset_key, VISUALIZER_PRESETS["emerald"])
        vol = self._demo_volume * self._sensitivity
        if self._style == "wave":    self._draw_wave(p, ox, oy, ow, oh, preset, vol)
        elif self._style == "bars":  self._draw_bars(p, ox, oy, ow, oh, preset, vol)
        p.end()

    def _draw_wave(self, p, ox, oy, ow, oh, preset, volume):
        cy = oy + oh / 2; max_amp = oh * 0.38; pad = 6
        for wc in preset["waves"]:
            color = wc[self._theme]; amp_m = wc["amp"]; freq = wc["freq"]
            phase_m = wc["phase"]; pen_w = wc["width"]
            path = QPainterPath(); first = True
            curr_amp = max(0.5 * amp_m, max_amp * min(1.0, volume) * amp_m)
            for xi in range(pad, int(ow) - pad):
                t = (xi - pad) / max(1, ow - 2 * pad)
                env = math.pow(math.sin(math.pi * t), 2.0)
                y = cy + curr_amp * env * math.sin(xi * freq + self._phase * phase_m)
                if first: path.moveTo(ox + xi, y); first = False
                else: path.lineTo(ox + xi, y)
            pen = QPen(color); pen.setWidthF(pen_w); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen); p.drawPath(path)

    def _draw_bars(self, p, ox, oy, ow, oh, preset, volume):
        nb = max(5, int(ow / 8)); bw = max(2.5, (ow - 12) / (nb * 1.6))
        gap = (ow - 12 - bw * nb) / max(1, nb - 1); max_h = oh * 0.7; cy = oy + oh / 2
        colors = [w[self._theme] for w in preset["waves"]]
        for i in range(nb):
            t = i / max(1, nb - 1)
            bvol = volume * (0.4 + 0.6 * math.sin(self._phase * 1.5 + i * 0.8) ** 2)
            bh = max(2, max_h * bvol); bx = ox + 6 + i * (bw + gap); by = cy - bh / 2
            color = _lerp_color(colors[0], colors[1], t * 2) if t < 0.5 else _lerp_color(colors[1], colors[2], (t - 0.5) * 2)
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(color))
            p.drawRoundedRect(QRectF(bx, by, bw, bh), bw / 2, bw / 2)

    def _draw_dots(self, p, ox, oy, ow, oh, preset, volume):
        colors = [w[self._theme] for w in preset["waves"]]
        count = max(7, int(ow / 11)); gap = ow / max(1, count); cy = oy + oh / 2
        for i in range(count):
            t = i / max(1, count - 1)
            pulse = 0.45 + 0.55 * math.sin(self._phase * 1.8 + i * 0.7) ** 2
            radius = 2.0 + volume * pulse * oh * 0.16
            x = ox + gap * (i + 0.5)
            color = _lerp_color(colors[0], colors[1 if t < 0.65 else 2], min(1.0, t * 1.4))
            p.setPen(Qt.PenStyle.NoPen); p.setBrush(QBrush(color))
            p.drawEllipse(QPointF(x, cy), radius, radius)

    def _draw_ribbon(self, p, ox, oy, ow, oh, preset, volume):
        cy = oy + oh / 2; colors = [w[self._theme] for w in preset["waves"]]
        amp = max(1.4, oh * (0.14 + 0.24 * volume)); pad = 7
        path = QPainterPath(); path.moveTo(ox + pad, cy)
        for xi in range(pad, int(ow) - pad):
            t = (xi - pad) / max(1, ow - 2 * pad)
            y = cy + amp * math.sin(self._phase * 1.1 + t * math.pi * 2.2)
            y += amp * 0.45 * math.sin(self._phase * -0.7 + t * math.pi * 5.1)
            path.lineTo(ox + xi, y)
        pen = QPen(colors[0]); pen.setWidthF(4.0); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen); p.drawPath(path)
        pen = QPen(colors[1]); pen.setWidthF(1.6); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen); p.drawPath(path)

# ──────────────────────────────────────────────
#  DashboardWindow  — redesigned
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

    # ── Init ──────────────────────────────────

    def init_ui(self):
        self.setWindowTitle("Echo")
        self.setMinimumSize(620, 460)
        self.resize(700, 500)

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        self.stack = QStackedWidget()
        root.addWidget(self.stack)
        # stack stretches but content inside is width-constrained via _content_page()

        self._build_overview_tab()
        self._build_visualizer_tab()
        self._build_history_tab()
        self._build_settings_tab()
        self._build_logs_tab()

        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    # ── Sidebar ───────────────────────────────

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(14, 20, 14, 16)
        lay.setSpacing(2)

        # App name
        name_lbl = QLabel("Echo")
        name_lbl.setObjectName("AppName")
        sub_lbl = QLabel("Voice Assistant")
        sub_lbl.setObjectName("AppSub")
        lay.addWidget(name_lbl)
        lay.addWidget(sub_lbl)
        lay.addSpacing(16)

        # Nav
        self.nav_buttons = []
        nav_items = [
            ("Обзор",        0),
            ("Визуализатор", 1),
            ("История",      2),
            ("Настройки",    3),
            ("Логи",         4),
        ]
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("NavBtnActive" if idx == 0 else "NavBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.switch_tab(i))
            lay.addWidget(btn)
            self.nav_buttons.append(btn)

        lay.addStretch()

        # Status indicator
        self.status_dot_lbl = QLabel("● Готов")
        self.status_dot_lbl.setObjectName("StatusDot")
        self.status_dot_lbl.setStyleSheet("color: #10B981; font-size: 11px;")
        ver_lbl = QLabel("v1.0")
        ver_lbl.setObjectName("VersionLbl")
        lay.addWidget(self.status_dot_lbl)
        lay.addWidget(ver_lbl)

        return sidebar

    # ── Tab 0: Overview ───────────────────────

    def _build_overview_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(400)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)

        # Header row
        hdr = QHBoxLayout()
        title = QLabel("Обзор")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        self.dash_state_badge = QLabel("● Ожидание")
        self.dash_state_badge.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 600;")
        hdr.addWidget(self.dash_state_badge)
        lay.addLayout(hdr)

        # Stats row — equal-width cards
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)
        c1, self.val_total = self._stat_card("ДИКТОВОК")
        c2, self.val_lat   = self._stat_card("ЗАДЕРЖКА")
        c3, self.val_words = self._stat_card("СЛОВ")
        self.val_lat.setText("0.0 с")
        stats_row.addWidget(c1)
        stats_row.addWidget(c2)
        stats_row.addWidget(c3)
        lay.addLayout(stats_row)

        # Hint card
        hint = QFrame()
        hint.setObjectName("Card")
        hl = QVBoxLayout(hint)
        hl.setContentsMargins(14, 12, 14, 12)
        hl.setSpacing(3)
        ht = QLabel("Как использовать")
        ht.setStyleSheet("font-weight: 600; font-size: 13px;")
        hd = QLabel("Удерживайте Ctrl + Win, говорите, отпустите — текст вставится в активное поле.")
        hd.setWordWrap(True)
        hd.setStyleSheet("font-size: 12px;")
        hl.addWidget(ht)
        hl.addWidget(hd)
        lay.addWidget(hint)
        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _stat_card(self, caption):
        card = QFrame()
        card.setObjectName("Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 10, 12, 10)
        cl.setSpacing(3)
        cap = QLabel(caption)
        cap.setObjectName("StatCap")
        val = QLabel("0")
        val.setObjectName("StatNum")
        cl.addWidget(cap)
        cl.addWidget(val)
        return card, val

    # ── Tab 1: Visualizer ─────────────────────

    def _build_visualizer_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(400)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)

        title = QLabel("Визуализатор")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        # Preview
        preview_frame = QFrame()
        preview_frame.setObjectName("PreviewFrame")
        pfl = QVBoxLayout(preview_frame)
        pfl.setContentsMargins(0, 0, 0, 0)
        self.preview_widget = PreviewWidget()
        self.preview_widget.set_style(self.config.get("visualizer_style", "wave"))
        self.preview_widget.set_preset(self.config.get("visualizer_color_preset", "emerald"))
        self.preview_widget.set_size(self.config.get("visualizer_size", "medium"))
        pfl.addWidget(self.preview_widget)
        lay.addWidget(preview_frame)

        # Controls card
        ctrl = QFrame()
        ctrl.setObjectName("Card")
        cl = QVBoxLayout(ctrl)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.setSpacing(10)

        def row(label, widget):
            r = QHBoxLayout()
            r.setSpacing(12)
            lbl = QLabel(label)
            lbl.setObjectName("FieldLbl")
            lbl.setFixedWidth(56)
            r.addWidget(lbl)
            r.addWidget(widget)
            r.addStretch()
            return r

        self.shape_seg = SegmentedControl(["Волна", "Бары"])
        style_map = {"wave": 0, "bars": 1, "dots": 0, "ribbon": 0}
        self.shape_seg.setCurrentIndex(style_map.get(self.config.get("visualizer_style", "wave"), 0))
        self.shape_seg.currentChanged.connect(self._on_shape_changed)
        cl.addLayout(row("Форма", self.shape_seg))

        self.size_seg = SegmentedControl(["XS", "S", "M", "L", "XL"])
        size_map = {"xs": 0, "small": 1, "medium": 2, "large": 3, "xl": 4}
        self.size_seg.setCurrentIndex(size_map.get(self.config.get("visualizer_size", "medium"), 2))
        self.size_seg.currentChanged.connect(self._on_size_changed)
        cl.addLayout(row("Размер", self.size_seg))

        self.theme_seg = SegmentedControl(["Dark", "Light"])
        self.theme_seg.setCurrentIndex(0 if self.config.get("theme", "dark") == "dark" else 1)
        self.theme_seg.currentChanged.connect(lambda i: self.apply_theme("dark" if i == 0 else "light"))
        cl.addLayout(row("Тема", self.theme_seg))

        # Sensitivity slider
        sens_row = QHBoxLayout()
        sens_row.setSpacing(10)
        sens_lbl = QLabel("Чувств.")
        sens_lbl.setObjectName("FieldLbl")
        sens_lbl.setFixedWidth(56)
        self.sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.sens_slider.setRange(1, 10)
        saved_sens = self.config.get("visualizer_sensitivity", 1.0)
        self.sens_slider.setValue(max(1, min(10, round(saved_sens * 5))))
        self.sens_slider.setFixedWidth(130)
        self.sens_val_lbl = QLabel(f"{self.sens_slider.value() / 5:.1f}×")
        self.sens_val_lbl.setObjectName("FieldLbl")
        self.sens_val_lbl.setFixedWidth(34)
        self.sens_slider.valueChanged.connect(self._on_sensitivity_changed)
        sens_row.addWidget(sens_lbl)
        sens_row.addWidget(self.sens_slider)
        sens_row.addWidget(self.sens_val_lbl)
        sens_row.addStretch()
        cl.addLayout(sens_row)

        lay.addWidget(ctrl)

        # Color preset card
        color_card = QFrame()
        color_card.setObjectName("Card")
        ccl = QVBoxLayout(color_card)
        ccl.setContentsMargins(14, 10, 14, 10)
        ccl.setSpacing(6)
        cap = QLabel("ЦВЕТ")
        cap.setObjectName("SectionCap")
        ccl.addWidget(cap)
        self.color_selector = ColorPresetSelector()
        self.color_selector.setCurrentPreset(self.config.get("visualizer_color_preset", "emerald"))
        self.color_selector.presetChanged.connect(self._on_preset_changed)
        ccl.addWidget(self.color_selector)
        lay.addWidget(color_card)

        self.vis_save_btn = QPushButton("Сохранить")
        self.vis_save_btn.setObjectName("PrimaryBtn")
        self.vis_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vis_save_btn.setFixedWidth(120)
        self.vis_save_btn.clicked.connect(self._save_visualizer)
        lay.addWidget(self.vis_save_btn)
        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _on_shape_changed(self, idx):
        self.preview_widget.set_style(["wave", "bars"][idx])

    def _on_size_changed(self, idx):
        self.preview_widget.set_size(["xs", "small", "medium", "large", "xl"][idx])

    def _on_sensitivity_changed(self, val):
        sens = val / 5.0
        self.sens_val_lbl.setText(f"{sens:.1f}×")
        self.preview_widget.set_sensitivity(sens)

    def _on_preset_changed(self, key):
        self.preview_widget.set_preset(key)
        self.config["visualizer_color_preset"] = key
        self.apply_theme(self.theme_name, key)

    def _save_visualizer(self):
        self.config["visualizer_style"] = ["wave", "bars"][self.shape_seg.currentIndex()]
        self.config["visualizer_size"]  = ["xs", "small", "medium", "large", "xl"][self.size_seg.currentIndex()]
        self.config["visualizer_color_preset"] = self.color_selector.currentPreset()
        self.config["theme"] = "dark" if self.theme_seg.currentIndex() == 0 else "light"
        self.config["visualizer_sensitivity"] = self.sens_slider.value() / 5.0
        self.save_callback(self.config)
        self.vis_save_btn.setText("Сохранено!")
        self.vis_save_btn.setEnabled(False)
        QTimer.singleShot(1500, lambda: (self.vis_save_btn.setText("Сохранить"), self.vis_save_btn.setEnabled(True)))

    # ── Tab 2: History ────────────────────────

    def _build_history_tab(self):
        page = QWidget()
        lay = QHBoxLayout(page)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # Left panel
        left = QFrame()
        left.setObjectName("Sidebar")
        left.setFixedWidth(240)
        ll = QVBoxLayout(left)
        ll.setContentsMargins(12, 16, 12, 12)
        ll.setSpacing(8)

        title = QLabel("История")
        title.setObjectName("PageTitle")
        ll.addWidget(title)

        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Поиск...")
        self.history_search.textChanged.connect(self.filter_history)
        ll.addWidget(self.history_search)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.show_history_detail)
        ll.addWidget(self.history_list)

        self.btn_clear_history = QPushButton("Очистить")
        self.btn_clear_history.setObjectName("SecondaryBtn")
        self.btn_clear_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_history.clicked.connect(self.clear_all_history)
        ll.addWidget(self.btn_clear_history)

        lay.addWidget(left)

        # Right detail
        right = QWidget()
        rl = QVBoxLayout(right)
        rl.setContentsMargins(16, 16, 16, 16)
        rl.setSpacing(8)

        self.placeholder_detail_label = QLabel("Выберите запись")
        self.placeholder_detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_detail_label.setStyleSheet("color: #555D6E; font-size: 13px;")
        rl.addWidget(self.placeholder_detail_label, 1, Qt.AlignmentFlag.AlignCenter)

        self.detail_meta = QLabel()
        self.detail_meta.setStyleSheet("font-size: 11px; color: #555D6E;")
        self.detail_meta.setVisible(False)
        rl.addWidget(self.detail_meta)

        self.lbl_raw = QLabel("WHISPER")
        self.lbl_raw.setObjectName("DetailLbl")
        self.lbl_raw.setVisible(False)
        self.txt_raw = QPlainTextEdit()
        self.txt_raw.setReadOnly(True)
        self.txt_raw.setVisible(False)
        rl.addWidget(self.lbl_raw)
        rl.addWidget(self.txt_raw)

        self.lbl_clean = QLabel("LLM")
        self.lbl_clean.setObjectName("DetailLbl")
        self.lbl_clean.setVisible(False)
        self.txt_clean = QPlainTextEdit()
        self.txt_clean.setReadOnly(True)
        self.txt_clean.setVisible(False)
        rl.addWidget(self.lbl_clean)
        rl.addWidget(self.txt_clean)

        self.copy_btn_widget = QWidget()
        self.copy_btn_widget.setVisible(False)
        cbl = QHBoxLayout(self.copy_btn_widget)
        cbl.setContentsMargins(0, 0, 0, 0)
        cbl.setSpacing(8)
        self.btn_copy_raw = QPushButton("Копировать сырой")
        self.btn_copy_raw.setObjectName("SecondaryBtn")
        self.btn_copy_raw.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_raw.clicked.connect(self.copy_raw_text)
        self.btn_copy_clean = QPushButton("Копировать готовый")
        self.btn_copy_clean.setObjectName("PrimaryBtn")
        self.btn_copy_clean.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_clean.clicked.connect(self.copy_clean_text)
        cbl.addWidget(self.btn_copy_raw)
        cbl.addWidget(self.btn_copy_clean)
        cbl.addStretch()
        rl.addWidget(self.copy_btn_widget)

        lay.addWidget(right)
        self.stack.addWidget(page)

    # ── Tab 3: Settings ───────────────────────

    def _build_settings_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(400)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)

        title = QLabel("Настройки")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        card = QFrame()
        card.setObjectName("Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(12)

        def cap(text):
            lbl = QLabel(text)
            lbl.setObjectName("SectionCap")
            return lbl

        def field_row(label, widget, w=None):
            r = QHBoxLayout()
            r.setSpacing(12)
            lbl = QLabel(label)
            lbl.setObjectName("FieldLbl")
            lbl.setFixedWidth(120)
            if w: widget.setFixedWidth(w)
            r.addWidget(lbl)
            r.addWidget(widget)
            r.addStretch()
            return r

        # API key
        cl.addWidget(cap("API"))
        api_row = QHBoxLayout()
        api_row.setSpacing(8)
        self.api_input = QLineEdit()
        self.api_input.setText(self.config.get("api_key", ""))
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setPlaceholderText("Groq API Key")
        api_lbl = QLabel("Groq API Key")
        api_lbl.setObjectName("FieldLbl")
        api_lbl.setFixedWidth(100)
        self.btn_toggle_api = QPushButton("Показать")
        self.btn_toggle_api.setObjectName("SecondaryBtn")
        self.btn_toggle_api.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_api.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_toggle_api.setMinimumWidth(80)
        self.btn_toggle_api.clicked.connect(self.toggle_api_visibility)
        api_row.addWidget(api_lbl)
        api_row.addWidget(self.api_input, 1)
        api_row.addWidget(self.btn_toggle_api)
        cl.addLayout(api_row)

        # Hotkey
        cl.addWidget(cap("ВВОД"))
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["ctrl+windows", "left alt+space", "f8"])
        self.hotkey_combo.setCurrentText(self.config.get("hotkey", "ctrl+windows"))
        cl.addLayout(field_row("Горячая клавиша", self.hotkey_combo, 180))

        # Model
        cl.addWidget(cap("МОДЕЛЬ"))
        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen/qwen3-32b",
        ])
        self.model_combo.setCurrentText(self.config.get("text_model", "llama-3.3-70b-versatile"))
        cl.addLayout(field_row("Текстовая модель", self.model_combo, 220))

        # Startup
        cl.addWidget(cap("СИСТЕМА"))
        self.startup_toggle = ToggleSwitch(checked=self.config.get("run_on_startup", False))
        cl.addLayout(field_row("Автозапуск", self.startup_toggle))

        lay.addWidget(card)

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setObjectName("PrimaryBtn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedWidth(120)
        self.save_btn.clicked.connect(self.save)
        lay.addWidget(self.save_btn)
        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    # ── Tab 4: Logs ───────────────────────────

    def _build_logs_tab(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(20, 16, 20, 16)
        lay.setSpacing(10)

        hdr = QHBoxLayout()
        title = QLabel("Логи")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        btn_clear = QPushButton("Очистить")
        btn_clear.setObjectName("SecondaryBtn")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_logs)
        hdr.addWidget(btn_clear)
        lay.addLayout(hdr)

        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setObjectName("LogConsole")
        lay.addWidget(self.log_area)
        self.stack.addWidget(page)

    # ── Theme ─────────────────────────────────

    def apply_theme(self, theme, preset=None):
        self.theme_name = theme
        if preset is None:
            preset = self.config.get("visualizer_color_preset", "emerald")
        self.setStyleSheet(get_stylesheet(theme, preset))

        if preset in ACCENT_PRESETS:
            acc = ACCENT_PRESETS[preset][theme]
            self.startup_toggle.set_colors(QColor(acc["primary"]), QColor(acc["secondary"]))

        self.startup_toggle.set_theme(theme)
        self.theme_seg.set_theme(theme)
        self.shape_seg.set_theme(theme)
        self.size_seg.set_theme(theme)
        self.color_selector.set_theme(theme)
        self.preview_widget.set_theme(theme)

        for btn in self.nav_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    # ── State ─────────────────────────────────

    def set_system_state(self, state):
        colors = {
            "idle":       ("#10B981", "● Готов"),
            "recording":  ("#06B6D4", "● Запись"),
            "processing": ("#8B5CF6", "● Обработка"),
        }
        color, text = colors.get(state, ("#10B981", "● Готов"))
        style = f"color: {color}; font-size: 11px;"
        self.status_dot_lbl.setText(text)
        self.status_dot_lbl.setStyleSheet(style)
        self.dash_state_badge.setText(text)
        self.dash_state_badge.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")

    # ── Navigation ────────────────────────────

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setObjectName("NavBtnActive" if i == index else "NavBtn")
        self.apply_theme(self.theme_name)
        if index == 0: self.update_statistics()
        elif index == 2: self.load_history()
        elif index == 4: self.load_logs()

    # ── Logs ──────────────────────────────────

    def load_logs(self):
        log_path = "echo.log"
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    self.log_area.setPlainText("".join(f.readlines()[-150:]))
                    self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
            except Exception as e:
                self.log_area.setPlainText(f"Ошибка: {e}")
        else:
            self.log_area.setPlainText("Лог пуст.")

    def append_log(self, text):
        self.log_area.appendPlainText(text)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def clear_logs(self):
        log_path = "echo.log"
        if os.path.exists(log_path):
            try: open(log_path, "w", encoding="utf-8").close()
            except Exception: pass
        self.log_area.clear()

    # ── History ───────────────────────────────

    def load_history(self):
        self.history_entries = history_manager.load_history()
        self.filter_history()

    def filter_history(self):
        query = self.history_search.text().lower()
        self.history_list.clear()
        for idx, entry in enumerate(self.history_entries):
            if query in entry.get("raw_text", "").lower() or query in entry.get("cleaned_text", "").lower():
                time_str = entry.get("timestamp", "").split()[-1][:5]
                snippet = entry.get("cleaned_text", "")[:42].replace("\n", " ")
                if len(entry.get("cleaned_text", "")) > 42: snippet += "…"
                item = QListWidgetItem(f"{time_str}  {snippet}")
                item.setData(Qt.ItemDataRole.UserRole, idx)
                self.history_list.addItem(item)
        self.clear_detail_panel()

    def show_history_detail(self, item):
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None and idx < len(self.history_entries):
            e = self.history_entries[idx]
            self.placeholder_detail_label.setVisible(False)
            self.txt_raw.setPlainText(e.get("raw_text", ""))
            self.txt_clean.setPlainText(e.get("cleaned_text", ""))
            self.detail_meta.setText(f"{e.get('timestamp','')}  ·  {e.get('total_latency',0):.1f}s  ·  {e.get('model','')}")
            self.detail_meta.setVisible(True)
            self.lbl_raw.setVisible(True); self.txt_raw.setVisible(True)
            self.lbl_clean.setVisible(True); self.txt_clean.setVisible(True)
            self.copy_btn_widget.setVisible(True)

    def clear_detail_panel(self):
        self.placeholder_detail_label.setVisible(True)
        self.detail_meta.setVisible(False)
        self.lbl_raw.setVisible(False); self.txt_raw.setVisible(False)
        self.lbl_clean.setVisible(False); self.txt_clean.setVisible(False)
        self.copy_btn_widget.setVisible(False)
        self.txt_raw.clear(); self.txt_clean.clear()

    def copy_raw_text(self):   QApplication.clipboard().setText(self.txt_raw.toPlainText())
    def copy_clean_text(self): QApplication.clipboard().setText(self.txt_clean.toPlainText())

    def clear_all_history(self):
        history_manager.clear_history()
        self.load_history()
        self.update_statistics()

    def update_statistics(self):
        stats = history_manager.get_statistics()
        self.val_total.setText(str(stats["total_dictations"]))
        self.val_lat.setText(f"{stats['avg_total_latency']:.1f} с")
        self.val_words.setText(str(stats["total_words"]))

    # ── Settings ──────────────────────────────

    def toggle_api_visibility(self):
        if self.api_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_api.setText("Скрыть")
        else:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_api.setText("Показать")

    def save(self):
        self.config["api_key"]    = self.api_input.text().strip()
        self.config["hotkey"]     = self.hotkey_combo.currentText()
        self.config["text_model"] = self.model_combo.currentText()
        self.config["theme"]      = "dark" if self.theme_seg.currentIndex() == 0 else "light"
        self.config["run_on_startup"] = self.startup_toggle.isChecked()
        self.save_callback(self.config)
        self.save_btn.setText("Сохранено!")
        self.save_btn.setEnabled(False)
        QTimer.singleShot(1500, lambda: (self.save_btn.setText("Сохранить"), self.save_btn.setEnabled(True)))

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            self.hide()


# ──────────────────────────────────────────────
#  OverlayWindow  (unchanged — visualizer pill)
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
        self.sensitivity = 1.0

        self.reposition()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def apply_config(self, config):
        self.set_vis_style(config.get("visualizer_style", "wave"))
        self.set_color_preset(config.get("visualizer_color_preset", "emerald"))
        self.set_vis_size(config.get("visualizer_size", "medium"))
        self.sensitivity = config.get("visualizer_sensitivity", 1.0)

    def set_vis_style(self, style):   self.vis_style = style
    def set_color_preset(self, key):
        if key in VISUALIZER_PRESETS: self.color_preset = key

    def set_vis_size(self, size_key):
        if size_key in VISUALIZER_SIZES:
            self.size_key = size_key
            w, h = VISUALIZER_SIZES[size_key]
            self.setFixedSize(w, h)
            self.reposition()

    def reposition(self):
        cursor_pos = QCursor.pos()
        screen = QApplication.screenAt(cursor_pos)
        if not screen: screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            x = sg.x() + (sg.width() - self.width()) // 2
            y = sg.y() + sg.height() - self.height() - 15
            self.move(x, y)

    def set_theme(self, theme_name): self.theme = theme_name; self.update()

    def update_animation(self):
        if self.state == "processing":
            self.spinner_angle = (self.spinner_angle + 45) % 360
            self.update()
        elif self.state == "recording":
            self.volume += (self.target_volume - self.volume) * 0.25
            self.target_volume = max(0.0, self.target_volume - 0.04)
            self.phase += 0.08
            self.update()

    def set_volume(self, volume): self.target_volume = volume

    def set_state(self, state):
        self.state = state
        if state == "idle":
            self.hide()
        else:
            if state == "recording":
                self.volume = 0.0; self.target_volume = 0.0; self.phase = 0.0
            elif state == "processing":
                self.spinner_angle = 0
            self.reposition()
            self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        preset = VISUALIZER_PRESETS.get(self.color_preset, VISUALIZER_PRESETS["emerald"])

        if self.theme == "light":
            bg_color   = QColor(250, 250, 250, 185)
            glow_color = QColor(255, 255, 255, 70)
        else:
            bg_color   = QColor(10, 14, 20, 172)
            glow_color = QColor(255, 255, 255, 24)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(0, 0, w, h), 10, 10)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(glow_color, 1))
        painter.drawRoundedRect(QRectF(1.5, 1.5, w - 3, h - 3), 9, 9)

        if self.state == "recording":
            vol = min(1.0, self.volume * self.sensitivity)
            if self.vis_style == "wave":    self._paint_wave(painter, w, h, preset, vol)
            elif self.vis_style == "bars":  self._paint_bars(painter, w, h, preset, vol)
        elif self.state == "processing":
            self._paint_spinner(painter, w, h, preset)
        painter.end()

    def _paint_wave(self, painter, w, h, preset, vol):
        cy = h / 2; max_amp = h * 0.38
        for wc in preset["waves"]:
            color = wc[self.theme]; amp_m = wc["amp"]; freq = wc["freq"]
            phase_m = wc["phase"]; pen_w = wc["width"]
            path = QPainterPath(); first = True
            curr_amp = max(0.5 * amp_m, max_amp * min(1.0, vol) * amp_m)
            for x in range(6, w - 6):
                t = (x - 6) / max(1, w - 12)
                env = math.pow(math.sin(math.pi * t), 2.0)
                y = cy + curr_amp * env * math.sin(x * freq + self.phase * phase_m)
                if first: path.moveTo(x, y); first = False
                else: path.lineTo(x, y)
            pen = QPen(color); pen.setWidthF(pen_w); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen); painter.drawPath(path)

    def _paint_bars(self, painter, w, h, preset, vol):
        nb = max(5, int(w / 8)); bw = max(2.5, (w - 12) / (nb * 1.6))
        gap = (w - 12 - bw * nb) / max(1, nb - 1); max_h = h * 0.7; cy = h / 2
        colors = [wc[self.theme] for wc in preset["waves"]]
        for i in range(nb):
            t = i / max(1, nb - 1)
            bvol = vol * (0.4 + 0.6 * math.sin(self.phase * 1.5 + i * 0.8) ** 2)
            bh = max(2, max_h * bvol); bx = 6 + i * (bw + gap); by = cy - bh / 2
            color = _lerp_color(colors[0], colors[1], t * 2) if t < 0.5 else _lerp_color(colors[1], colors[2], (t - 0.5) * 2)
            painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(QBrush(color))
            painter.drawRoundedRect(QRectF(bx, by, bw, bh), bw / 2, bw / 2)

    def _paint_dots(self, painter, w, h, preset):
        colors = [wc[self.theme] for wc in preset["waves"]]
        count = max(7, int(w / 11)); gap = w / max(1, count); cy = h / 2
        for i in range(count):
            t = i / max(1, count - 1)
            pulse = 0.45 + 0.55 * math.sin(self.phase * 1.8 + i * 0.7) ** 2
            radius = 2.0 + self.volume * pulse * h * 0.16
            x = gap * (i + 0.5)
            color = _lerp_color(colors[0], colors[1 if t < 0.65 else 2], min(1.0, t * 1.4))
            painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(QBrush(color))
            painter.drawEllipse(QPointF(x, cy), radius, radius)

    def _paint_ribbon(self, painter, w, h, preset):
        cy = h / 2; colors = [wc[self.theme] for wc in preset["waves"]]
        amp = max(1.4, h * (0.14 + 0.24 * self.volume)); pad = 7
        path = QPainterPath(); path.moveTo(pad, cy)
        for x in range(pad, w - pad):
            t = (x - pad) / max(1, w - 2 * pad)
            y = cy + amp * math.sin(self.phase * 1.1 + t * math.pi * 2.2)
            y += amp * 0.45 * math.sin(self.phase * -0.7 + t * math.pi * 5.1)
            path.lineTo(x, y)
        pen = QPen(colors[0]); pen.setWidthF(4.0); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen); painter.drawPath(path)
        pen = QPen(colors[1]); pen.setWidthF(1.6); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen); painter.drawPath(path)

    def _paint_spinner(self, painter, w, h, preset):
        cx, cy = w / 2, h / 2
        base_color = preset["waves"][0][self.theme]
        painter.translate(cx, cy)
        painter.rotate(self.spinner_angle)
        segments = 8
        for i in range(segments):
            opacity = int(255 - (255 / segments) * i)
            pen = QPen(QColor(base_color.red(), base_color.green(), base_color.blue(), opacity))
            pen.setWidth(2); pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen); painter.drawLine(0, 3, 0, 6)
            painter.rotate(-360 / segments)
        painter.resetTransform()

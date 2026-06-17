"""Custom UI widgets for VoiceAssistant"""
import math
from PyQt6.QtWidgets import (QWidget, QPushButton, QHBoxLayout, QColorDialog, QSizePolicy, 
                             QVBoxLayout, QLabel, QFrame, QGridLayout, QDialog)
from PyQt6.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient

from .styles import _lerp_color
from .styles_data import VISUALIZER_PRESETS


class ToggleSwitch(QWidget):
    """Custom toggle switch widget"""
    toggled = pyqtSignal(bool)

    # Indigo/violet accent palette matching the redesigned theme
    _COL_ON   = QColor(124, 58, 237)   # indigo-600
    _COL_OFF  = QColor(30, 28, 50)     # dark surface

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = checked
        self._handle_pos = 1.0 if checked else 0.0
        self._theme = "dark"
        self._anim = QPropertyAnimation(self, b"handle_position", self)
        self._anim.setDuration(160)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def get_handle_position(self): return self._handle_pos
    def set_handle_position(self, v): self._handle_pos = v; self.update()
    handle_position = pyqtProperty(float, get_handle_position, set_handle_position)

    def isChecked(self): return self._checked
    def setChecked(self, v):
        self._checked = v; self._handle_pos = 1.0 if v else 0.0; self.update()
    def set_theme(self, t): self._theme = t; self.update()

    # Keep signature compatible with old call sites — ignored now
    def set_colors(self, c1, c2): pass

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

        track = _lerp_color(self._COL_OFF, self._COL_ON, self._handle_pos)
        p.setBrush(QBrush(track))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(QRectF(0, 0, w, h), r, r)

        m = 3
        d = h - m * 2
        x = m + self._handle_pos * (w - d - m * 2)
        p.setBrush(QBrush(QColor(255, 255, 255)))
        p.drawEllipse(QRectF(x, m, d, d))
        p.end()


class SegmentedControl(QWidget):
    """Segmented control widget (chip-style) — fixed dark-blue palette"""
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
    # Keep signature compatible — accent is now fixed, arg ignored
    def set_accent(self, primary_hex): pass

    def _update_styles(self):
        active_bg   = "rgba(124,58,237,0.18)"
        active_bdr  = "rgba(139,92,246,0.55)"
        active_txt  = "#C4B5FD"          # violet-300
        idle_bg     = "#111120"
        idle_bdr    = "#1E1D35"
        idle_txt    = "#7B7AA0"
        hover_bg    = "#17162A"
        hover_txt   = "#E8E6FF"

        for i, btn in enumerate(self._buttons):
            if i == self._current:
                btn.setStyleSheet(
                    f"QPushButton {{ background:{active_bg}; color:{active_txt}; "
                    f"border:1px solid {active_bdr}; border-radius:6px; "
                    f"font-weight:700; font-size:12px; padding:0 11px; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background:{idle_bg}; color:{idle_txt}; "
                    f"border:1px solid {idle_bdr}; border-radius:6px; "
                    f"font-weight:500; font-size:12px; padding:0 11px; }} "
                    f"QPushButton:hover {{ color:{hover_txt}; background:{hover_bg}; }}"
                )

    def paintEvent(self, e): super().paintEvent(e)


class ColorPresetSelector(QWidget):
    """Color preset selector"""
    presetChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "mono"
        self._theme = "dark"
        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._order = ["mono", "ocean", "neon", "sunset", "lavender"]

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
            cx = sx + i * 48 + 14
            cy = 16
            r = 12
            
            preset = VISUALIZER_PRESETS[key]
            colors = preset["waves"]
            c1, c2, c3 = colors[0][self._theme], colors[1][self._theme], colors[2][self._theme]
            
            grad = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
            grad.setColorAt(0.0, QColor(c1.red(), c1.green(), c1.blue(), 220))
            grad.setColorAt(0.5, QColor(c2.red(), c2.green(), c2.blue(), 200))
            grad.setColorAt(1.0, QColor(c3.red(), c3.green(), c3.blue(), 180))
            p.setBrush(QBrush(grad))
            if key == self._current:
                p.setPen(QPen(QColor(139, 92, 246), 2.5))  # violet-500 selection ring
            else:
                p.setPen(QPen(QColor(30, 29, 53), 1))
            p.drawEllipse(QPointF(cx, cy), r, r)
            p.setPen(QPen(QColor(138, 138, 138)))
            font = QFont("Arial", 8)
            p.setFont(font)
            name = preset["name"]
            tw = p.fontMetrics().horizontalAdvance(name)
            p.drawText(int(cx - tw / 2), 46, name)
        p.end()



class ElidedLabel(QWidget):
    """Label that elides text with '…' when it doesn't fit, without causing horizontal scroll."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)
        # Allow stylesheet color/font to propagate
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, False)

    def setText(self, text):
        self._text = text
        self.update()

    def sizeHint(self):
        from PyQt6.QtCore import QSize
        fm = self.fontMetrics()
        return QSize(fm.horizontalAdvance(self._text), fm.height())

    def minimumSizeHint(self):
        from PyQt6.QtCore import QSize
        fm = self.fontMetrics()
        return QSize(0, fm.height())

    def paintEvent(self, e):
        from PyQt6.QtGui import QPalette
        p = QPainter(self)
        # Use the foreground color set via stylesheet
        color = self.palette().color(QPalette.ColorRole.WindowText)
        p.setPen(color)
        fm = p.fontMetrics()
        elided = fm.elidedText(self._text, Qt.TextElideMode.ElideRight, self.width())
        p.drawText(0, fm.ascent(), elided)
        p.end()


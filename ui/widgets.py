"""Custom UI widgets for VoiceAssistant"""
import math
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QColorDialog, QSizePolicy
from PyQt6.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient

from .styles import _lerp_color
from .styles_data import VISUALIZER_PRESETS


class ToggleSwitch(QWidget):
    """Custom toggle switch widget"""
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


class SegmentedControl(QWidget):
    """Segmented control widget (chip-style)"""
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


class ColorPresetSelector(QWidget):
    """Color preset selector with custom color support"""
    presetChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "mono"
        self._theme = "dark"
        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._order = ["mono", "ocean", "neon", "sunset", "lavender", "custom"]
        self._custom_colors = {
            "dark": [QColor(244, 244, 245, 255), QColor(161, 161, 170, 160), QColor(113, 113, 122, 100)],
            "light": [QColor(24, 24, 27, 255), QColor(113, 113, 122, 140), QColor(161, 161, 170, 100)]
        }

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
                if key == "custom" and e.buttons() == Qt.MouseButton.LeftButton:
                    # Open color picker for custom preset
                    self._open_custom_color_picker()
                else:
                    self._current = key
                    self.update()
                    self.presetChanged.emit(key)
                break

    def _open_custom_color_picker(self):
        """Open color dialog to set custom colors"""
        for idx in range(3):
            current_color = self._custom_colors[self._theme][idx]
            color = QColorDialog.getColor(current_color, self, f"Wave {idx + 1} Color")
            if color.isValid():
                self._custom_colors[self._theme][idx] = color
        
        self._current = "custom"
        self.update()
        self.presetChanged.emit("custom")

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
            
            if key == "custom":
                # Draw custom preset with user-defined colors
                c1, c2, c3 = self._custom_colors[self._theme]
            else:
                preset = VISUALIZER_PRESETS[key]
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
            name = "Custom" if key == "custom" else preset["name"]
            tw = p.fontMetrics().horizontalAdvance(name)
            p.drawText(int(cx - tw / 2), 46, name)
        p.end()

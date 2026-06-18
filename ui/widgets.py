"""Custom UI widgets for VoiceAssistant"""
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QLabel
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath, QFontMetrics

from .styles import _lerp_color
from .styles_data import VISUALIZER_PRESETS


class ToggleSwitch(QWidget):
    """Custom toggle switch widget"""
    toggled = pyqtSignal(bool)

    # Indigo/violet accent palette matching the redesigned theme
    _COL_ON   = QColor(223, 206, 186)   # sand
    _COL_OFF  = QColor(78, 56, 43)      # dark chocolate

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
    """Segmented control widget (pill-track style)"""
    currentChanged = pyqtSignal(int)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._options = options
        self._current = 0
        self._theme = "dark"
        self._buttons = []
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(32)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("SegmentedControl { background: #4E382B; border-radius: 16px; }")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(2)
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
        active_bg   = "#DFCEBA"
        active_txt  = "#281B15"
        idle_bg     = "transparent"
        idle_txt    = "#D4C5B9"
        hover_bg    = "rgba(255,255,255,0.06)"
        hover_txt   = "#F5ECE3"

        for i, btn in enumerate(self._buttons):
            if i == self._current:
                btn.setStyleSheet(
                    f"QPushButton {{ background:{active_bg}; color:{active_txt}; "
                    f"border:none; border-radius:14px; "
                    f"font-weight:700; font-size:11px; padding:0 14px; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background:{idle_bg}; color:{idle_txt}; "
                    f"border:none; border-radius:14px; "
                    f"font-weight:600; font-size:11px; padding:0 14px; }} "
                    f"QPushButton:hover {{ color:{hover_txt}; background:{hover_bg}; }}"
                )

    def paintEvent(self, e): super().paintEvent(e)


class ColorPresetSelector(QWidget):
    """Color preset selector (dots-only style)"""
    presetChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "mono"
        self._theme = "dark"
        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._order = ["mono", "chocolate", "ocean", "aurora", "neon", "sunset", "lavender", "rose", "forest"]

    def currentPreset(self): return self._current
    def setCurrentPreset(self, k): self._current = k; self.update()
    def set_theme(self, t): self._theme = t; self.update()

    def mousePressEvent(self, e):
        x = e.position().x()
        n = len(self._order)
        total = n * 44
        sx = (self.width() - total) / 2
        for i, key in enumerate(self._order):
            cx = sx + i * 44 + 22
            if abs(x - cx) < 20:
                self._current = key
                self.update()
                self.presetChanged.emit(key)
                break

    def paintEvent(self, e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        n = len(self._order)
        total = n * 44
        sx = (self.width() - total) / 2

        # Draw unified track container
        track_rect = QRectF(sx - 12, 0, total + 24, 42)
        p.setBrush(QBrush(QColor(78, 56, 43)))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(track_rect, 21, 21)

        for i, key in enumerate(self._order):
            cx = sx + i * 44 + 22
            cy = 21
            r = 13
            
            preset = VISUALIZER_PRESETS[key]
            colors = preset["waves"]
            c1, c2, c3 = colors[0][self._theme], colors[1][self._theme], colors[2][self._theme]
            
            # Active selection outline ring
            if key == self._current:
                p.setPen(QPen(QColor(245, 236, 227), 2.0))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QPointF(cx, cy), r + 3, r + 3)

            # Color dot
            grad = QLinearGradient(cx - r, cy - r, cx + r, cy + r)
            grad.setColorAt(0.0, QColor(c1.red(), c1.green(), c1.blue(), 230))
            grad.setColorAt(0.5, QColor(c2.red(), c2.green(), c2.blue(), 210))
            grad.setColorAt(1.0, QColor(c3.red(), c3.green(), c3.blue(), 190))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(cx, cy), r, r)
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


class OutlinedLabel(QLabel):
    """A QLabel that renders text with a custom fill color and outline stroke color."""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._fill_color = QColor(255, 255, 255) # Default white
        self._stroke_color = QColor(40, 27, 21)   # Default dark brown (#281B15)
        self._stroke_width = 4.0

    def setColors(self, fill, stroke, stroke_width=4.0):
        self._fill_color = QColor(fill)
        self._stroke_color = QColor(stroke)
        self._stroke_width = stroke_width
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        path = QPainterPath()
        font = self.font()
        fm = QFontMetrics(font)
        
        text = self.text()
        text_w = fm.horizontalAdvance(text)
        text_h = fm.height()
        
        # Calculate horizontal and vertical positioning based on alignment
        x = float(rect.left())
        align = self.alignment()
        if align & Qt.AlignmentFlag.AlignHCenter:
            x = rect.left() + (rect.width() - text_w) / 2.0
        elif align & Qt.AlignmentFlag.AlignRight:
            x = rect.right() - text_w
            
        y = rect.top() + (rect.height() - text_h) / 2.0 + fm.ascent()
        
        path.addText(x, y, font, text)
        
        # Draw stroke
        pen = QPen(self._stroke_color, self._stroke_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        
        # Draw fill
        painter.fillPath(path, QBrush(self._fill_color))
        painter.end()



"""Custom UI widgets for VoiceAssistant"""
from PyQt6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QSizePolicy, QLabel
from PyQt6.QtCore import Qt, QRectF, QPropertyAnimation, QEasingCurve, pyqtProperty, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QLinearGradient, QPainterPath, QFontMetrics

from .styles import _lerp_color
from .styles_data import VISUALIZER_PRESETS


class ToggleSwitch(QWidget):
    """Custom pixel toggle switch widget"""
    toggled = pyqtSignal(bool)

    _COL_ON   = QColor(240, 240, 245)
    _COL_OFF  = QColor(24, 24, 34)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setFixedSize(42, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = checked
        self._handle_pos = 1.0 if checked else 0.0
        self._theme = "dark"
        self._anim = QPropertyAnimation(self, b"handle_position", self)
        self._anim.setDuration(120)
        self._anim.setEasingCurve(QEasingCurve.Type.Linear)

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
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w, h = self.width(), self.height()

        # Dark pixel track background
        track_col = _lerp_color(QColor(24, 24, 34), QColor(40, 40, 59), self._handle_pos)
        p.setBrush(QBrush(track_col))
        p.setPen(QPen(QColor(56, 56, 77), 2))
        p.drawRect(QRectF(1, 1, w - 2, h - 2))

        m = 2
        d = h - m * 2
        max_x = w - d - m
        x = m + self._handle_pos * (max_x - m)
        handle_col = _lerp_color(QColor(90, 90, 114), QColor(240, 240, 245), self._handle_pos)
        p.setBrush(QBrush(handle_col))
        p.setPen(QPen(QColor(17, 17, 21), 1))
        p.drawRect(QRectF(x, m, d, d))
        p.end()



class SegmentedControl(QWidget):
    """Segmented control widget (Pixel rect style)"""
    currentChanged = pyqtSignal(int)

    def __init__(self, options, parent=None):
        super().__init__(parent)
        self._options = options
        self._current = 0
        self._theme = "dark"
        self._buttons = []
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(34)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setStyleSheet("SegmentedControl { background: #181822; border: 2px solid #38384d; border-radius: 0px; }")

        lay = QHBoxLayout(self)
        lay.setContentsMargins(2, 2, 2, 2)
        lay.setSpacing(2)
        for i, text in enumerate(options):
            btn = QPushButton(text)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(26)
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
        active_bg   = "#f0f0f5"
        active_txt  = "#111115"
        idle_bg     = "transparent"
        idle_txt    = "#9090a2"
        hover_bg    = "rgba(255,255,255,0.08)"
        hover_txt   = "#ffffff"

        for i, btn in enumerate(self._buttons):
            if i == self._current:
                btn.setStyleSheet(
                    f"QPushButton {{ background:{active_bg}; color:{active_txt}; "
                    f"border: 1px solid #ffffff; border-radius:0px; "
                    f"font-weight:700; font-size:11px; padding:0 12px; }}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background:{idle_bg}; color:{idle_txt}; "
                    f"border: none; border-radius:0px; "
                    f"font-weight:700; font-size:11px; padding:0 12px; }} "
                    f"QPushButton:hover {{ color:{hover_txt}; background:{hover_bg}; }}"
                )

    def paintEvent(self, e): super().paintEvent(e)


class ColorPresetSelector(QWidget):
    """Color preset selector (Pixel squares style)"""
    presetChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current = "mono"
        self._theme = "dark"
        self.setFixedHeight(42)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._order = ["mono", "matrix", "cyber", "amber", "synth", "plasma", "acid", "ice", "void"]

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
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        n = len(self._order)
        total = n * 44
        sx = (self.width() - total) / 2

        # Draw unified pixel track container
        track_rect = QRectF(sx - 12, 2, total + 24, 38)
        p.setBrush(QBrush(QColor(24, 24, 34)))
        p.setPen(QPen(QColor(56, 56, 77), 2))
        p.drawRect(track_rect)

        for i, key in enumerate(self._order):
            cx = sx + i * 44 + 22
            cy = 21
            size = 22
            rx = cx - size / 2
            ry = cy - size / 2
            
            preset = VISUALIZER_PRESETS[key]
            colors = preset["waves"]
            c1, c2, c3 = colors[0][self._theme], colors[1][self._theme], colors[2][self._theme]
            
            # Active selection pixel outline frame
            if key == self._current:
                p.setPen(QPen(QColor(240, 240, 245), 2.0))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRect(QRectF(rx - 4, ry - 4, size + 8, size + 8))

            # Color square chip
            grad = QLinearGradient(rx, ry, rx + size, ry + size)
            grad.setColorAt(0.0, QColor(c1.red(), c1.green(), c1.blue(), 230))
            grad.setColorAt(0.5, QColor(c2.red(), c2.green(), c2.blue(), 210))
            grad.setColorAt(1.0, QColor(c3.red(), c3.green(), c3.blue(), 190))
            p.setBrush(QBrush(grad))
            p.setPen(QPen(QColor(17, 17, 21), 1))
            p.drawRect(QRectF(rx, ry, size, size))
        p.end()


class ElidedLabel(QWidget):
    """Label that elides text with '…' when it doesn't fit, without causing horizontal scroll."""

    def __init__(self, text="", parent=None):
        super().__init__(parent)
        self._text = text
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        self.setMinimumWidth(0)
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
        self._fill_color = QColor(240, 240, 245)
        self._stroke_color = QColor(17, 17, 21)
        self._stroke_width = 3.0

    def setColors(self, fill, stroke, stroke_width=3.0):
        self._fill_color = QColor(fill)
        self._stroke_color = QColor(stroke)
        self._stroke_width = stroke_width
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        rect = self.rect()
        path = QPainterPath()
        font = self.font()
        fm = QFontMetrics(font)
        
        text = self.text()
        text_w = fm.horizontalAdvance(text)
        text_h = fm.height()
        
        x = float(rect.left())
        align = self.alignment()
        if align & Qt.AlignmentFlag.AlignHCenter:
            x = rect.left() + (rect.width() - text_w) / 2.0
        elif align & Qt.AlignmentFlag.AlignRight:
            x = rect.right() - text_w
            
        y = rect.top() + (rect.height() - text_h) / 2.0 + fm.ascent()
        
        path.addText(x, y, font, text)
        
        pen = QPen(self._stroke_color, self._stroke_width)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.drawPath(path)
        
        painter.fillPath(path, QBrush(self._fill_color))
        painter.end()


class PixelLogoWidget(QWidget):
    """Pixel art logo displaying the word PITCH rendered entirely in pixel matrix art."""

    FONT_MATRICES = {
        'P': [
            [1, 1, 1, 1, 0],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
        ],
        'I': [
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [1, 1, 1, 1, 1],
        ],
        'T': [
            [1, 1, 1, 1, 1],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
        ],
        'C': [
            [0, 1, 1, 1, 1],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [1, 0, 0, 0, 0],
            [0, 1, 1, 1, 1],
        ],
        'H': [
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
        ],
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(50)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        word = "PITCH"
        pixel_size = 3.5
        pixel_gap = 1.0
        char_gap = 6.0

        rows = 7
        cols_per_char = 5
        char_w = cols_per_char * (pixel_size + pixel_gap)
        total_w = len(word) * char_w + (len(word) - 1) * char_gap
        total_h = rows * (pixel_size + pixel_gap)

        start_x = (self.width() - total_w) / 2
        start_y = (self.height() - total_h) / 2

        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(QColor(240, 240, 245)))

        curr_x = start_x
        for char in word:
            matrix = self.FONT_MATRICES.get(char)
            if matrix:
                for r, row in enumerate(matrix):
                    for c, val in enumerate(row):
                        if val == 1:
                            px = curr_x + c * (pixel_size + pixel_gap)
                            py = start_y + r * (pixel_size + pixel_gap)
                            p.drawRect(QRectF(px, py, pixel_size, pixel_size))
            curr_x += char_w + char_gap

        p.end()



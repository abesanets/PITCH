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

    # Fixed blue palette — independent of visualizer preset
    _COL_ON_DARK   = QColor(160, 160, 160)  # muted gray
    _COL_OFF_DARK  = QColor(42, 42, 42)     # dark surface
    _COL_ON_LIGHT  = QColor(42, 42, 42)     # dark gray
    _COL_OFF_LIGHT = QColor(200, 200, 200)  # light gray

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

        col_on  = self._COL_ON_DARK  if self._theme == "dark" else self._COL_ON_LIGHT
        col_off = self._COL_OFF_DARK if self._theme == "dark" else self._COL_OFF_LIGHT

        track = _lerp_color(col_off, col_on, self._handle_pos)
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
        if self._theme == "dark":
            active_bg   = "rgba(160,160,160,0.15)"
            active_bdr  = "rgba(160,160,160,0.40)"
            active_txt  = "#C0C0C0"          # muted gray — readable on dark
            idle_bg     = "#2A2A2A"
            idle_bdr    = "#3A3A3A"
            idle_txt    = "#8A8A8A"
            hover_bg    = "#2F2F2F"
            hover_txt   = "#E5E5E5"
        else:
            active_bg   = "rgba(42,42,42,0.12)"
            active_bdr  = "rgba(42,42,42,0.30)"
            active_txt  = "#1A1A1A"          # dark gray
            idle_bg     = "#FFFFFF"
            idle_bdr    = "#E0E0E0"
            idle_txt    = "#6B6B6B"
            hover_bg    = "#F0F0F0"
            hover_txt   = "#1A1A1A"

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
            "dark": [QColor(229, 229, 229, 255), QColor(138, 138, 138, 160), QColor(90, 90, 90, 100)],
            "light": [QColor(26, 26, 26, 255), QColor(107, 107, 107, 140), QColor(154, 154, 154, 100)]
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
        """Open custom color picker dialog"""
        dialog = CustomColorDialog(self._custom_colors, self._theme, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._custom_colors = dialog.get_colors()
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
                p.setPen(QPen(QColor(160, 160, 160), 2.5))  # Muted gray selection
            else:
                p.setPen(QPen(QColor(58, 58, 58) if self._theme == "dark" else QColor(224, 224, 224), 1))
            p.drawEllipse(QPointF(cx, cy), r, r)
            p.setPen(QPen(QColor(138, 138, 138) if self._theme == "dark" else QColor(107, 107, 107)))
            font = QFont("Arial", 8)
            p.setFont(font)
            name = "Custom" if key == "custom" else preset["name"]
            tw = p.fontMetrics().horizontalAdvance(name)
            p.drawText(int(cx - tw / 2), 46, name)
        p.end()


class CustomColorDialog(QDialog):
    """Custom color picker dialog matching app aesthetic"""
    
    def __init__(self, colors, theme, parent=None):
        super().__init__(parent)
        self._colors = {
            "dark": [QColor(c) for c in colors["dark"]],
            "light": [QColor(c) for c in colors["light"]]
        }
        self._theme = theme
        self._init_ui()
        
    def _init_ui(self):
        self.setWindowTitle("Custom Color Preset")
        self.setModal(True)
        self.setFixedSize(320, 380)
        
        # Remove default window decorations for cleaner look
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowSystemMenuHint
        )
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header = QFrame()
        header.setObjectName("DialogHeader")
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("Custom Colors")
        title.setObjectName("DialogTitle")
        title.setStyleSheet(f"""
            QLabel {{
                color: {'#F1F3F7' if self._theme == 'dark' else '#0D0D0D'};
                font-size: 16px;
                font-weight: 600;
            }}
        """)
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setObjectName("DialogCloseBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {'#8B92A5' if self._theme == 'dark' else '#6B7280'};
                border: none;
                border-radius: 14px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {'rgba(255,255,255,0.1)' if self._theme == 'dark' else 'rgba(0,0,0,0.05)'};
                color: {'#F1F3F7' if self._theme == 'dark' else '#0D0D0D'};
            }}
        """)
        close_btn.clicked.connect(self.reject)
        header_layout.addWidget(close_btn)
        
        main_layout.addWidget(header)
        
        # Content area
        content = QFrame()
        content.setObjectName("DialogContent")
        bg_color = '#16181F' if self._theme == 'dark' else '#FFFFFF'
        content.setStyleSheet(f"""
            QFrame#DialogContent {{
                background: {bg_color};
                border-radius: 12px;
            }}
        """)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 20, 24, 20)
        content_layout.setSpacing(16)
        
        # Color selectors
        self._color_buttons = []
        wave_names = ["Primary Wave", "Secondary Wave", "Accent Wave"]
        
        for i in range(3):
            color_row = self._create_color_row(i, wave_names[i])
            content_layout.addWidget(color_row)
        
        # Preview area
        preview_frame = QFrame()
        preview_frame.setObjectName("PreviewFrame")
        preview_frame.setFixedHeight(60)
        preview_bg = '#1C1F28' if self._theme == 'dark' else '#F9FAFB'
        preview_frame.setStyleSheet(f"""
            QFrame#PreviewFrame {{
                background: {preview_bg};
                border-radius: 8px;
                border: 1px solid {'#2A2D38' if self._theme == 'dark' else '#E5E7EB'};
            }}
        """)
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(12, 8, 12, 8)
        
        self._preview_label = QLabel("Preview")
        self._preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._preview_label.setStyleSheet(f"""
            QLabel {{
                color: {'#8B92A5' if self._theme == 'dark' else '#6B7280'};
                font-size: 11px;
            }}
        """)
        preview_layout.addWidget(self._preview_label)
        
        content_layout.addWidget(preview_frame)
        
        main_layout.addWidget(content)
        
        # Footer with buttons
        footer = QFrame()
        footer.setObjectName("DialogFooter")
        footer.setFixedHeight(60)
        footer.setStyleSheet(f"""
            QFrame#DialogFooter {{
                background: {bg_color};
                border-top: 1px solid {'#2A2D38' if self._theme == 'dark' else '#E5E7EB'};
            }}
        """)
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(20, 10, 20, 10)
        footer_layout.setSpacing(12)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("DialogCancelBtn")
        cancel_btn.setFixedHeight(36)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {'#1C1F28' if self._theme == 'dark' else '#F3F4F6'};
                color: {'#8B92A5' if self._theme == 'dark' else '#6B7280'};
                border: 1px solid {'#2A2D38' if self._theme == 'dark' else '#E5E7EB'};
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: {'#22252F' if self._theme == 'dark' else '#E5E7EB'};
                color: {'#F1F3F7' if self._theme == 'dark' else '#0D0D0D'};
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # Apply button
        apply_btn = QPushButton("Apply")
        apply_btn.setObjectName("DialogApplyBtn")
        apply_btn.setFixedHeight(36)
        apply_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        apply_btn.setStyleSheet(f"""
            QPushButton {{
                background: #3B82F6;
                color: #FFFFFF;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 16px;
            }}
            QPushButton:hover {{
                background: #2563EB;
            }}
        """)
        apply_btn.clicked.connect(self.accept)
        
        footer_layout.addStretch()
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(apply_btn)
        
        main_layout.addWidget(footer)
        
    def _create_color_row(self, index, name):
        """Create a row for selecting a color"""
        row = QFrame()
        row.setObjectName(f"ColorRow_{index}")
        row.setFixedHeight(48)
        
        is_dark = self._theme == 'dark'
        row.setStyleSheet(f"""
            QFrame#{row.objectName()} {{
                background: {'#1C1F28' if is_dark else '#F9FAFB'};
                border-radius: 8px;
                border: 1px solid {'#2A2D38' if is_dark else '#E5E7EB'};
            }}
        """)
        
        layout = QHBoxLayout(row)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)
        
        # Color name label
        name_label = QLabel(name)
        name_label.setStyleSheet(f"""
            QLabel {{
                color: {'#F1F3F7' if is_dark else '#0D0D0D'};
                font-size: 13px;
                font-weight: 500;
            }}
        """)
        layout.addWidget(name_label)
        
        layout.addStretch()
        
        # Color preview button
        color_btn = QPushButton()
        color_btn.setObjectName(f"ColorBtn_{index}")
        color_btn.setFixedSize(32, 32)
        color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        color_btn.setProperty("color_index", index)
        
        current_color = self._colors[self._theme][index]
        self._update_color_button(color_btn, current_color)
        
        color_btn.clicked.connect(lambda: self._on_color_clicked(index))
        layout.addWidget(color_btn)
        
        self._color_buttons.append(color_btn)
        
        return row
    
    def _update_color_button(self, btn, color):
        """Update color button appearance"""
        hex_color = color.name()
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {hex_color};
                border: 2px solid {'#2A2D38' if self._theme == 'dark' else '#E5E7EB'};
                border-radius: 16px;
            }}
            QPushButton:hover {{
                border: 2px solid #3B82F6;
            }}
        """)
        btn.setToolTip(f"Current: {hex_color.upper()}")
    
    def _on_color_clicked(self, index):
        """Handle color button click"""
        current_color = self._colors[self._theme][index]
        color = QColorDialog.getColor(current_color, self, f"Select {['Primary', 'Secondary', 'Accent'][index]} Color")
        if color.isValid():
            self._colors[self._theme][index] = color
            self._update_color_button(self._color_buttons[index], color)
            self._update_preview()
    
    def _update_preview(self):
        """Update preview with current colors"""
        c1, c2, c3 = self._colors[self._theme]
        self._preview_label.setText(
            f"<span style='color: #{c1.red():02x}{c1.green():02x}{c1.blue():02x}'>●</span>  "
            f"<span style='color: #{c2.red():02x}{c2.green():02x}{c2.blue():02x}'>●</span>  "
            f"<span style='color: #{c3.red():02x}{c3.green():02x}{c3.blue():02x}'>●</span>"
        )
    
    def get_colors(self):
        """Get the selected colors"""
        return self._colors
    
    def paintEvent(self, event):
        """Draw rounded corners for the dialog"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw dialog background with rounded corners
        bg_color = QColor('#16181F' if self._theme == 'dark' else '#FFFFFF')
        painter.setBrush(QBrush(bg_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 12, 12)
        
        super().paintEvent(event)



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
        p.setFont(self.font())
        # Use the foreground color set via stylesheet
        color = self.palette().color(QPalette.ColorRole.WindowText)
        p.setPen(color)
        fm = p.fontMetrics()
        elided = fm.elidedText(self._text, Qt.TextElideMode.ElideRight, self.width())
        p.drawText(0, fm.ascent(), elided)
        p.end()

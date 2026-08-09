"""Visualizer widgets for VoiceAssistant"""
import math
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QCursor, QPainterPath

from ..styles import _lerp_color
from ..styles_data import VISUALIZER_PRESETS, VISUALIZER_SIZES
from .renderers import draw_wave_visualizer, draw_matrix_visualizer, draw_wave_processing, draw_matrix_processing


def _draw_pixel_pill(painter, ox, oy, ow, oh, fill_color, stroke_color):
    """Draw a pixelated stepped oval/pill container with a 2px pixel stroke."""
    r = oh / 2.0
    path = QPainterPath()
    
    h1 = 3.0
    h2 = 6.0
    x_in1 = r * 0.45
    x_in2 = r * 0.18
    
    path.moveTo(ox + x_in1, oy)
    path.lineTo(ox + ow - x_in1, oy)
    path.lineTo(ox + ow - x_in1, oy + h1)
    path.lineTo(ox + ow - x_in2, oy + h1)
    path.lineTo(ox + ow - x_in2, oy + h2)
    path.lineTo(ox + ow, oy + h2)
    path.lineTo(ox + ow, oy + oh - h2)
    path.lineTo(ox + ow - x_in2, oy + oh - h2)
    path.lineTo(ox + ow - x_in2, oy + oh - h1)
    path.lineTo(ox + ow - x_in1, oy + oh - h1)
    path.lineTo(ox + ow - x_in1, oy + oh)
    path.lineTo(ox + x_in1, oy + oh)
    path.lineTo(ox + x_in1, oy + oh - h1)
    path.lineTo(ox + x_in2, oy + oh - h1)
    path.lineTo(ox + x_in2, oy + oh - h2)
    path.lineTo(ox, oy + oh - h2)
    path.lineTo(ox, oy + h2)
    path.lineTo(ox + x_in2, oy + h2)
    path.lineTo(ox + x_in2, oy + h1)
    path.lineTo(ox + x_in1, oy + h1)
    path.lineTo(ox + x_in1, oy)
    path.closeSubpath()
    
    painter.fillPath(path, QBrush(fill_color))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawPath(path)


class PreviewWidget(QWidget):
    """Preview widget for visualizer settings"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(90)
        self._theme = "dark"
        self._style = "wave"
        self._preset_key = "mono"
        self._size_key = "medium"
        self._sensitivity = 1.0
        self._phase = 0.0
        self._demo_volume = 0.0
        self._demo_target = 0.6
        self._time_counter = 0.0
        self._scroll_offset = 0.0
        self._bg_mode = "solid"
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(33)

    def set_style(self, s): self._style = s; self.update()
    def set_preset(self, k): 
        self._preset_key = k
        self.update()
            
    def set_size(self, k): self._size_key = k; self.update()
    def set_theme(self, t): self._theme = t; self.update()
    def set_sensitivity(self, v): self._sensitivity = v; self.update()
    def set_bg_mode(self, mode): 
        self._bg_mode = mode
        self.update()

    def _tick(self):
        self._time_counter += 0.033
        self._demo_target = 0.35 + 0.35 * math.sin(self._time_counter * 1.7) + 0.15 * math.sin(self._time_counter * 3.1)
        self._demo_target = max(0.1, min(1.0, self._demo_target))
        self._demo_volume += (self._demo_target - self._demo_volume) * 0.25
        self._phase += 0.08
        self._scroll_offset += 2.5
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        ow, oh = VISUALIZER_SIZES.get(self._size_key, (80, 26))
        ox = (self.width() - ow) / 2
        oy = (self.height() - oh) / 2
        
        # Draw background based on mode (pixelated stepped oval container)
        if self._bg_mode == "solid":
            preset = VISUALIZER_PRESETS.get(self._preset_key, VISUALIZER_PRESETS["mono"])
            bg = preset.get("bg_color", {}).get(self._theme, QColor(17, 17, 21, 245))
            brd = QColor(56, 56, 77)
            _draw_pixel_pill(p, ox, oy, ow, oh, bg, brd)
        
        preset = VISUALIZER_PRESETS.get(self._preset_key, VISUALIZER_PRESETS["mono"])
        vol = self._demo_volume * self._sensitivity
        if self._style == "matrix":
            draw_matrix_visualizer(p, ox, oy, ow, oh, preset, self._theme, vol, self._phase)
        else:
            draw_wave_visualizer(p, ox, oy, ow, oh, preset, self._theme, vol, self._phase)
        p.end()

    def _draw_wave(self, p, ox, oy, ow, oh, preset, volume):
        draw_wave_visualizer(p, ox, oy, ow, oh, preset, self._theme, volume, self._phase)

    def _draw_matrix(self, p, ox, oy, ow, oh, preset, volume):
        draw_matrix_visualizer(p, ox, oy, ow, oh, preset, self._theme, volume, self._phase)



class OverlayWindow(QWidget):
    """Overlay window for visualizer (recording/processing indicator)"""
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.vis_style = "wave"
        self.color_preset = "mono"
        self.size_key = "medium"
        self.bg_mode = "solid"

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
        self.scroll_offset = 0.0
        self.sensitivity = 1.0

        # Processing timing & progress tracking
        self.progress = 0.0
        self.estimated_processing_time = 0.5
        self.processing_elapsed = 0.0

        self.reposition()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(30)

    def apply_config(self, config):
        self.set_vis_style(config.get("visualizer_style", "wave"))
        self.set_color_preset(config.get("visualizer_color_preset", "mono"))
        self.set_vis_size(config.get("visualizer_size", "medium"))
        self.set_bg_mode(config.get("visualizer_bg_mode", "solid"))
        self.sensitivity = config.get("visualizer_sensitivity", 1.0)

    def set_vis_style(self, style):   self.vis_style = style
    def set_color_preset(self, key):
        if key in VISUALIZER_PRESETS: self.color_preset = key
    def set_bg_mode(self, mode):
        self.bg_mode = mode

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

    def start_processing(self, audio_duration: float, avg_rtf: float = 0.15):
        """Called when recognition starts with total audio duration and estimated RTF."""
        self.progress = 0.0
        self.processing_elapsed = 0.0
        
        # Apply a subtle scale factor for longer audio (> 30s) to account for extended context latency
        if audio_duration > 30.0:
            scale_factor = 1.0 + 0.08 * math.log2(audio_duration / 30.0)
        else:
            scale_factor = 1.0

        self.estimated_processing_time = max(0.25, audio_duration * avg_rtf * scale_factor)

    def finish_processing(self, callback=None):
        """Smoothly complete progress to 100% during paste operation before hiding."""
        self.state = "completing"
        self._completion_callback = callback

    def update_animation(self):
        if self.state == "processing":
            self.spinner_angle = (self.spinner_angle + 12) % 360
            self.processing_elapsed += 0.03
            
            ratio = self.processing_elapsed / max(0.01, self.estimated_processing_time)
            if ratio < 0.92:
                self.progress = ratio * 0.92
            else:
                # Easing curve asymptotically approaching 97%
                over = ratio - 0.92
                self.progress = 0.92 + (1.0 - math.exp(-over * 3.0)) * 0.06
                
            self.progress = min(0.97, max(0.0, self.progress))
            self.update()
        elif self.state == "completing":
            self.spinner_angle = (self.spinner_angle + 16) % 360
            self.progress += (1.0 - self.progress) * 0.45
            if self.progress >= 0.99:
                self.progress = 1.0
                self.state = "idle"
                self.hide()
                if hasattr(self, "_completion_callback") and self._completion_callback:
                    cb = self._completion_callback
                    self._completion_callback = None
                    cb()
            self.update()
        elif self.state == "recording":
            self.volume += (self.target_volume - self.volume) * 0.25
            self.target_volume = max(0.0, self.target_volume - 0.04)
            self.phase += 0.08
            self.scroll_offset += 2.5
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
                self.processing_elapsed = 0.0
            self.reposition()
            self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        w, h = self.width(), self.height()
        
        preset = VISUALIZER_PRESETS.get(self.color_preset, VISUALIZER_PRESETS["mono"])

        bg_color = preset.get("bg_color", {}).get(self.theme, QColor(17, 17, 21, 230))
        glow_color = QColor(56, 56, 77)

        # Draw background based on mode (pixelated stepped oval container)
        if self.bg_mode == "solid":
            _draw_pixel_pill(painter, 0, 0, w, h, bg_color, glow_color)

        if self.state == "recording":
            vol = min(1.0, self.volume * self.sensitivity)
            if self.vis_style == "matrix":    self._paint_matrix(painter, w, h, preset, vol)
            else:                             self._paint_wave(painter, w, h, preset, vol)
        elif self.state == "processing":
            if self.vis_style == "matrix":    self._paint_matrix_processing(painter, w, h, preset)
            else:                             self._paint_wave_processing(painter, w, h, preset)
        painter.end()

    def _paint_wave(self, painter, w, h, preset, vol):
        draw_wave_visualizer(painter, 0, 0, w, h, preset, self.theme, vol, self.phase)

    def _paint_wave_processing(self, painter, w, h, preset):
        draw_wave_processing(painter, 0, 0, w, h, preset, self.theme, self.spinner_angle, self.progress)

    def _paint_matrix(self, painter, w, h, preset, vol):
        draw_matrix_visualizer(painter, 0, 0, w, h, preset, self.theme, vol, self.phase)

    def _paint_matrix_processing(self, painter, w, h, preset):
        draw_matrix_processing(painter, 0, 0, w, h, preset, self.theme, self.spinner_angle, self.progress)



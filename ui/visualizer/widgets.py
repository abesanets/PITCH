"""Visualizer widgets for VoiceAssistant"""
import math
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QCursor, QPainterPath

from ..styles import _lerp_color
from ..styles_data import VISUALIZER_PRESETS, VISUALIZER_SIZES
from .renderers import draw_wave_visualizer, draw_matrix_visualizer


def _draw_pixel_pill(painter, ox, oy, ow, oh, fill_color, stroke_color):
    """Draw a pixelated stepped oval/pill container with a 2px pixel stroke."""
    r = oh / 2.0
    path = QPainterPath()
    
    h1 = 3.0
    h2 = 6.0
    
    x_in1 = r * 0.45
    x_in2 = r * 0.18
    
    # Top edge
    path.moveTo(ox + x_in1, oy)
    path.lineTo(ox + ow - x_in1, oy)
    
    # Right cap steps
    path.lineTo(ox + ow - x_in1, oy + h1)
    path.lineTo(ox + ow - x_in2, oy + h1)
    path.lineTo(ox + ow - x_in2, oy + h2)
    path.lineTo(ox + ow, oy + h2)
    path.lineTo(ox + ow, oy + oh - h2)
    path.lineTo(ox + ow - x_in2, oy + oh - h2)
    path.lineTo(ox + ow - x_in2, oy + oh - h1)
    path.lineTo(ox + ow - x_in1, oy + oh - h1)
    path.lineTo(ox + ow - x_in1, oy + oh)
    
    # Bottom edge
    path.lineTo(ox + x_in1, oy + oh)
    
    # Left cap steps
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

    def update_animation(self):
        if self.state == "processing":
            self.spinner_angle = (self.spinner_angle + 12) % 360
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
        """Calm, smooth flowing wave processing animation for Wave visualizer style"""
        cy = h / 2.0
        colors = [wc[self.theme] for wc in preset["waves"]]
        primary = colors[0]
        
        path = QPainterPath()
        first = True
        head_phase = (self.spinner_angle / 360.0) * math.pi * 2.0
        
        for x in range(6, w - 6):
            t = (x - 6) / max(1, w - 12)
            env = math.pow(math.sin(math.pi * t), 2.0)
            y = cy + (h * 0.22) * env * math.sin(x * 0.12 + head_phase)
            if first: path.moveTo(x, y); first = False
            else: path.lineTo(x, y)

        pen = QPen(QColor(primary.red(), primary.green(), primary.blue(), 200))
        pen.setWidthF(1.8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)

    def _paint_matrix(self, painter, w, h, preset, vol):
        draw_matrix_visualizer(painter, 0, 0, w, h, preset, self.theme, vol, self.phase)

    def _paint_matrix_processing(self, painter, w, h, preset):
        """Matrix Processing Animation: Rotating Pixel Snake travelling cleanly on exact Matrix cells (no background grid)"""
        cols, rows = 19, 7
        cell_size = max(2.0, (h - 6.0) / rows * 0.75)
        gap = max(1.0, cell_size * 0.4)

        grid_w = cols * cell_size + (cols - 1) * gap
        grid_h = rows * cell_size + (rows - 1) * gap

        start_x = (w - grid_w) / 2.0
        start_y = (h - grid_h) / 2.0

        mid_c = (cols - 1) / 2.0
        mid_r = (rows - 1) / 2.0

        colors = [wc[self.theme] for wc in preset["waves"]]
        primary_color = colors[0]

        head_angle = (self.spinner_angle / 360.0) * math.pi * 2.0

        painter.setPen(Qt.PenStyle.NoPen)

        for r in range(rows):
            if r == 0 or r == 6:
                continue

            for c in range(cols):
                norm_x = abs(c - mid_c) / max(1, mid_c)
                norm_y = abs(r - mid_r) / max(1, mid_r)
                diamond_val = norm_x + norm_y

                if diamond_val > 1.15:
                    continue

                cell_angle = math.atan2((r - mid_r), (c - mid_c) * 0.45)
                angle_diff = (head_angle - cell_angle) % (math.pi * 2.0)
                
                # Snake tail intensity (only active snake pixels light up)
                snake_glow = math.exp(-angle_diff * 2.2)
                if snake_glow < 0.15:
                    continue

                bx = start_x + c * (cell_size + gap)
                by = start_y + r * (cell_size + gap)

                opacity = int(255 * min(1.0, snake_glow))
                c_col = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), opacity)
                painter.setBrush(QBrush(c_col))
                painter.drawRect(QRectF(bx, by, cell_size, cell_size))



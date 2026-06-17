"""Visualizer widgets for VoiceAssistant"""
import os
import math
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRectF, pyqtSignal, QPointF
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QCursor, 
                         QPainterPath, QLinearGradient)

from .styles import _lerp_color
from .styles_data import VISUALIZER_PRESETS, VISUALIZER_SIZES


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
        self._bg_mode = "solid"  # "solid", "none"
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
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        ow, oh = VISUALIZER_SIZES.get(self._size_key, (80, 26))
        ox = (self.width() - ow) / 2
        oy = (self.height() - oh) / 2
        
        # Draw background based on mode
        if self._bg_mode == "solid":
            bg = QColor(9, 9, 11, 245)
            brd = QColor(39, 39, 42)
            p.setBrush(QBrush(bg))
            p.setPen(QPen(brd, 1))
            p.drawRoundedRect(QRectF(ox, oy, ow, oh), 8, 8)
        # For "none" mode, skip background drawing entirely
        
        preset = VISUALIZER_PRESETS.get(self._preset_key, VISUALIZER_PRESETS["mono"])
        vol = self._demo_volume * self._sensitivity
        if self._style == "wave":    self._draw_wave(p, ox, oy, ow, oh, preset, vol)
        elif self._style == "bars":  self._draw_bars(p, ox, oy, ow, oh, preset, vol)
        elif self._style == "scroll": self._draw_scroll(p, ox, oy, ow, oh, preset, vol)
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

    def _draw_scroll(self, p, ox, oy, ow, oh, preset, volume):
        """Scrolling bars that move continuously to the left - equalizer style"""
        bar_width = 2.5
        bar_spacing = 4.0
        total_spacing = bar_width + bar_spacing
        max_h = oh * 0.85
        cy = oy + oh / 2
        
        colors = [w[self._theme] for w in preset["waves"]]
        
        # Calculate how many bars fit in the visible area
        visible_width = ow - 12
        num_bars = int(visible_width / total_spacing) + 2
        
        # Draw bars scrolling from right to left
        for i in range(num_bars):
            # Position with scroll offset
            x_pos = ox + 6 + (i * total_spacing) - (self._scroll_offset % total_spacing)
            
            # Skip if outside visible area
            if x_pos < ox or x_pos > ox + ow - 6:
                continue
            
            # Height based on volume and position
            t = i / max(1, num_bars - 1)
            # Create wave pattern that moves
            wave_factor = 0.5 + 0.5 * math.sin(self._phase * 2.0 + i * 0.6)
            bvol = volume * (0.3 + 0.7 * wave_factor)
            bh = max(3, max_h * bvol)
            
            # Center-aligned (equalizer style) - grows both up and down
            by = cy - bh / 2
            
            # Color gradient
            color = _lerp_color(colors[0], colors[1], t * 2) if t < 0.5 else _lerp_color(colors[1], colors[2], (t - 0.5) * 2)
            
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QBrush(color))
            p.drawRoundedRect(QRectF(x_pos, by, bar_width, bh), bar_width / 2, bar_width / 2)


class OverlayWindow(QWidget):
    """Overlay window for visualizer (recording/processing indicator)"""
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.vis_style = "wave"
        self.color_preset = "mono"
        self.size_key = "medium"
        self.bg_mode = "solid"  # "solid", "none"

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
            self.spinner_angle = (self.spinner_angle + 45) % 360
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        
        preset = VISUALIZER_PRESETS.get(self.color_preset, VISUALIZER_PRESETS["mono"])

        bg_color   = QColor(34, 34, 34, 172)     # Soft dark background
        glow_color = QColor(255, 255, 255, 24)

        # Draw background based on mode
        if self.bg_mode == "solid":
            painter.setBrush(QBrush(bg_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(0, 0, w, h), 10, 10)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(glow_color, 1))
            painter.drawRoundedRect(QRectF(1.5, 1.5, w - 3, h - 3), 9, 9)
        # For "none" mode, skip background drawing entirely

        if self.state == "recording":
            vol = min(1.0, self.volume * self.sensitivity)
            if self.vis_style == "wave":    self._paint_wave(painter, w, h, preset, vol)
            elif self.vis_style == "bars":  self._paint_bars(painter, w, h, preset, vol)
            elif self.vis_style == "scroll": self._paint_scroll(painter, w, h, preset, vol)
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

    def _paint_scroll(self, painter, w, h, preset, vol):
        """Scrolling bars that move continuously to the left - equalizer style"""
        bar_width = 2.5
        bar_spacing = 4.0
        total_spacing = bar_width + bar_spacing
        max_h = h * 0.85
        cy = h / 2
        
        colors = [wc[self.theme] for wc in preset["waves"]]
        
        # Calculate how many bars fit in the visible area
        visible_width = w - 12
        num_bars = int(visible_width / total_spacing) + 2
        
        # Draw bars scrolling from right to left
        for i in range(num_bars):
            # Position with scroll offset
            x_pos = 6 + (i * total_spacing) - (self.scroll_offset % total_spacing)
            
            # Skip if outside visible area
            if x_pos < 0 or x_pos > w - 6:
                continue
            
            # Height based on volume and position
            t = i / max(1, num_bars - 1)
            # Create wave pattern that moves
            wave_factor = 0.5 + 0.5 * math.sin(self.phase * 2.0 + i * 0.6)
            bvol = vol * (0.3 + 0.7 * wave_factor)
            bh = max(3, max_h * bvol)
            
            # Center-aligned (equalizer style) - grows both up and down
            by = cy - bh / 2
            
            # Color gradient
            color = _lerp_color(colors[0], colors[1], t * 2) if t < 0.5 else _lerp_color(colors[1], colors[2], (t - 0.5) * 2)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawRoundedRect(QRectF(x_pos, by, bar_width, bh), bar_width / 2, bar_width / 2)

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

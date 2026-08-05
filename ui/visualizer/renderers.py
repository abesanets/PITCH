"""Shared rendering logic for visualizer wave and matrix styles."""
import math
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath
from ..styles import _lerp_color


def draw_wave_visualizer(painter, ox: float, oy: float, ow: float, oh: float, preset: dict, theme: str, volume: float, phase: float):
    """Draw wave visualizer animation."""
    cy = oy + oh / 2.0
    max_amp = oh * 0.38
    pad = 6
    for wc in preset["waves"]:
        color = wc[theme]
        amp_m = wc["amp"]
        freq = wc["freq"]
        phase_m = wc["phase"]
        pen_w = wc["width"]
        path = QPainterPath()
        first = True
        curr_amp = max(0.5 * amp_m, max_amp * min(1.0, volume) * amp_m)
        for xi in range(pad, int(ow) - pad):
            t = (xi - pad) / max(1, ow - 2 * pad)
            env = math.pow(math.sin(math.pi * t), 2.0)
            y = cy + curr_amp * env * math.sin(xi * freq + phase * phase_m)
            if first:
                path.moveTo(ox + xi, y)
                first = False
            else:
                path.lineTo(ox + xi, y)
        pen = QPen(color)
        pen.setWidthF(pen_w)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawPath(path)


def draw_matrix_visualizer(painter, ox: float, oy: float, ow: float, oh: float, preset: dict, theme: str, volume: float, phase: float):
    """Draw discrete diamond pixel field matrix visualizer animation."""
    cols, rows = 19, 7
    # Dynamically scale cell size and gap with container height and width
    cell_size = max(2.0, (oh - 6.0) / rows * 0.75)
    gap = max(1.0, cell_size * 0.4)

    grid_w = cols * cell_size + (cols - 1) * gap
    grid_h = rows * cell_size + (rows - 1) * gap

    start_x = ox + (ow - grid_w) / 2.0
    start_y = oy + (oh - grid_h) / 2.0

    mid_c = (cols - 1) / 2.0
    mid_r = (rows - 1) / 2.0

    colors = [w[theme] for w in preset["waves"]]
    primary_color = colors[0]
    bg_dim = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), 20)

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

            px_hash = ((c * 13 + r * 29) % 11) / 35.0
            center_dist = diamond_val * 0.5 + min(norm_x, norm_y) * 0.5 + px_hash

            pulse = 0.05 * math.sin(phase * 1.4 - center_dist * 2.0)
            threshold = center_dist * 0.60
            side_damp = 1.0 - 0.3 * norm_x

            bx = start_x + c * (cell_size + gap)
            by = start_y + r * (cell_size + gap)

            if volume > threshold:
                intensity = (volume - threshold) / (1.0 - threshold + 0.01) + pulse
                intensity = min(1.0, max(0.2, intensity * side_damp))
                c_col = _lerp_color(bg_dim, primary_color, intensity)
                painter.setBrush(QBrush(c_col))
            else:
                faint_col = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), int(25 * side_damp))
                painter.setBrush(QBrush(faint_col))

            painter.drawRect(QRectF(bx, by, cell_size, cell_size))

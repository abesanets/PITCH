"""Shared rendering logic for visualizer wave and matrix styles."""
import math
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath, QPainter
from ..styles import _lerp_color


def draw_wave_visualizer(painter, ox: float, oy: float, ow: float, oh: float, preset: dict, theme: str, volume: float, phase: float):
    """Draw wave visualizer animation."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
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
    """Draw discrete diamond pixel field matrix visualizer animation with scale-adaptive density."""
    base_dot_size = 2.0
    base_gap = 1.0
    pitch = base_dot_size + base_gap

    # Calculate count of columns and rows that fit inside container dimensions
    cols = max(11, int((ow - 10.0) / pitch))
    rows = max(5, int((oh - 4.0) / pitch))
    # Ensure odd dimensions for clear center alignment
    if cols % 2 == 0: cols -= 1
    if rows % 2 == 0: rows -= 1

    cell_size = base_dot_size
    gap = base_gap

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
        if r == 0 or r == rows - 1:
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


def draw_wave_processing(painter, ox: float, oy: float, ow: float, oh: float, preset: dict, theme: str, spinner_angle: float, progress: float = 0.0):
    """Smooth antialiased wave processing where wave transitions from dim resting color to bright active theme color as progress advances."""
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    cy = oy + oh / 2.0
    pad = 6
    ow_int = int(ow)
    
    colors = [wc[theme] for wc in preset["waves"]]
    primary = colors[0]
    dim_color = QColor(140, 140, 160, 90) if theme == "dark" else QColor(100, 100, 120, 80)
    
    head_phase = (spinner_angle / 360.0) * math.pi * 2.0
    fill_x = pad + (ow - 2 * pad) * max(0.0, min(1.0, progress))

    for wc in preset["waves"]:
        color_active = wc[theme]
        amp_m = wc["amp"]
        freq = wc["freq"]
        phase_m = wc["phase"]
        pen_w = wc["width"]
        max_amp = oh * 0.28 * amp_m

        # Draw unprocessed (dim/grayish) wave segment
        path_dim = QPainterPath()
        first_dim = True
        for xi in range(pad, ow_int - pad):
            t = (xi - pad) / max(1, ow - 2 * pad)
            env = math.pow(math.sin(math.pi * t), 2.0)
            y = cy + max_amp * env * math.sin(xi * freq + head_phase * phase_m)
            if first_dim:
                path_dim.moveTo(ox + xi, y)
                first_dim = False
            else:
                path_dim.lineTo(ox + xi, y)

        pen_dim = QPen(dim_color)
        pen_dim.setWidthF(pen_w)
        pen_dim.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen_dim)
        painter.drawPath(path_dim)

        # Draw processed (bright/active) wave segment overlay up to fill_x
        if fill_x > pad:
            path_active = QPainterPath()
            first_act = True
            for xi in range(pad, min(ow_int - pad, int(fill_x) + 1)):
                t = (xi - pad) / max(1, ow - 2 * pad)
                env = math.pow(math.sin(math.pi * t), 2.0)
                y = cy + max_amp * env * math.sin(xi * freq + head_phase * phase_m)
                if first_act:
                    path_active.moveTo(ox + xi, y)
                    first_act = False
                else:
                    path_active.lineTo(ox + xi, y)

            pen_active = QPen(color_active)
            pen_active.setWidthF(pen_w + 0.3)
            pen_active.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen_active)
            painter.drawPath(path_active)


def draw_matrix_processing(painter, ox: float, oy: float, ow: float, oh: float, preset: dict, theme: str, spinner_angle: float, progress: float = 0.0):
    """Matrix Processing Animation: Organic pixel-jitter fill with dynamic edge scan pulse."""
    base_dot_size = 2.0
    base_gap = 1.0
    pitch = base_dot_size + base_gap

    cols = max(11, int((ow - 10.0) / pitch))
    rows = max(5, int((oh - 4.0) / pitch))
    if cols % 2 == 0: cols -= 1
    if rows % 2 == 0: rows -= 1

    cell_size = base_dot_size
    gap = base_gap

    grid_w = cols * cell_size + (cols - 1) * gap
    grid_h = rows * cell_size + (rows - 1) * gap

    start_x = ox + (ow - grid_w) / 2.0
    start_y = oy + (oh - grid_h) / 2.0

    mid_c = (cols - 1) / 2.0
    mid_r = (rows - 1) / 2.0

    colors = [wc[theme] for wc in preset["waves"]]
    primary_color = colors[0]

    # Front column position based on progress (from 0 to cols)
    front_col_float = progress * cols
    scanner_phase = (spinner_angle / 360.0) * math.pi * 2.0

    painter.setPen(Qt.PenStyle.NoPen)

    for r in range(rows):
        if r == 0 or r == rows - 1:
            continue

        for c in range(cols):
            norm_x = abs(c - mid_c) / max(1, mid_c)
            norm_y = abs(r - mid_r) / max(1, mid_r)
            diamond_val = norm_x + norm_y

            if diamond_val > 1.15:
                continue

            # Deterministic pseudo-random pixel offset per row for organic pixel-jitter front
            row_jitter = math.sin(r * 3.7 + c * 0.4) * 0.75 + math.cos(r * 1.3) * 0.45
            effective_front = front_col_float + row_jitter

            dist_to_front = c - effective_front

            bx = start_x + c * (cell_size + gap)
            by = start_y + r * (cell_size + gap)

            if dist_to_front <= -1.2:
                # Fully filled zone (behind the front wave)
                # Soft subtle inner pulse so it feels alive
                inner_pulse = 0.85 + 0.15 * math.sin(scanner_phase + (c + r) * 0.3)
                opacity = int(240 * inner_pulse)
                c_col = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), opacity)

            elif -1.2 < dist_to_front <= 0.8:
                # Front scan edge (bright pixel pulse line)
                pulse_spark = 0.5 + 0.5 * math.sin(scanner_phase * 2.0 + r * 0.8)
                opacity = min(255, int(255 * (0.85 + 0.15 * pulse_spark)))
                c_col = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), opacity)

            else:
                # Unprocessed zone (ahead of front wave): dim resting pixels
                faint_pulse = 0.08 + 0.05 * math.sin(scanner_phase + norm_x * 2.0)
                opacity = int(255 * faint_pulse)
                c_col = QColor(primary_color.red(), primary_color.green(), primary_color.blue(), opacity)

            painter.setBrush(QBrush(c_col))
            painter.drawRect(QRectF(bx, by, cell_size, cell_size))



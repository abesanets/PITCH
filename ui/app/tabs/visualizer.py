"""Visualizer tab: preview widget, shape/size/bg/sensitivity/color controls."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)

from ...widgets import SegmentedControl, ColorPresetSelector
from ...visualizer.widgets import PreviewWidget


def build_visualizer_tab(d) -> QWidget:
    """Build the Visualizer tab and attach relevant attributes to d."""
    page = QWidget()
    outer = QHBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    inner = QWidget()
    inner.setFixedWidth(460)
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    hdr = QHBoxLayout()
    title = QLabel("Визуализатор")
    title.setObjectName("PageTitle")
    hdr.addWidget(title)
    hdr.addStretch()
    lay.addLayout(hdr)

    preview_card = QFrame()
    preview_card.setObjectName("Card")
    pcl = QVBoxLayout(preview_card)
    pcl.setContentsMargins(16, 10, 16, 10)
    pcl.setSpacing(6)
    preview_cap = QLabel("ПРЕДПРОСМОТР")
    preview_cap.setObjectName("SectionCap")
    pcl.addWidget(preview_cap)
    d.preview_widget = PreviewWidget()
    d.preview_widget.set_style(d.config.get("visualizer_style", "wave"))
    d.preview_widget.set_preset(d.config.get("visualizer_color_preset", "mono"))
    d.preview_widget.set_size(d.config.get("visualizer_size", "medium"))
    d.preview_widget.set_bg_mode(d.config.get("visualizer_bg_mode", "solid"))
    pcl.addWidget(d.preview_widget)
    lay.addWidget(preview_card)

    ctrl = QFrame()
    ctrl.setObjectName("Card")
    cl = QVBoxLayout(ctrl)
    cl.setContentsMargins(16, 12, 16, 12)
    cl.setSpacing(10)

    d.shape_seg = SegmentedControl(["Волна", "Бары", "Скролл"])
    style_map = {"wave": 0, "bars": 1, "scroll": 2, "dots": 0, "ribbon": 0}
    d.shape_seg.setCurrentIndex(style_map.get(d.config.get("visualizer_style", "wave"), 0))
    d.shape_seg.currentChanged.connect(d._on_shape_changed)

    d.bg_seg = SegmentedControl(["Сплошной", "Без фона"])
    bg_map = {"solid": 0, "none": 1}
    d.bg_seg.setCurrentIndex(bg_map.get(d.config.get("visualizer_bg_mode", "solid"), 0))
    d.bg_seg.currentChanged.connect(d._on_bg_mode_changed)

    d.size_seg = SegmentedControl(["XS", "S", "M", "L", "XL"])
    size_map = {"xs": 0, "small": 1, "medium": 2, "large": 3, "xl": 4}
    d.size_seg.setCurrentIndex(size_map.get(d.config.get("visualizer_size", "medium"), 2))
    d.size_seg.currentChanged.connect(d._on_size_changed)

    row1 = QHBoxLayout()
    row1.setSpacing(14)
    row1.addWidget(_ctrl_cell("ФОРМА", d.shape_seg))
    row1.addWidget(_ctrl_cell("РАЗМЕР", d.size_seg))
    cl.addLayout(row1)

    d.sens_values = [0.7, 1.0, 1.2, 1.5, 2.0]
    d.sens_seg = SegmentedControl(["0.7", "1.0", "1.2", "1.5", "2.0"])
    saved_sens = d.config.get("visualizer_sensitivity", 1.0)
    try:
        closest_idx = min(range(len(d.sens_values)), key=lambda i: abs(d.sens_values[i] - saved_sens))
    except Exception:
        closest_idx = 1
    d.sens_seg.setCurrentIndex(closest_idx)
    d.sens_seg.currentChanged.connect(d._on_sensitivity_changed)

    row2 = QHBoxLayout()
    row2.setSpacing(14)
    row2.addWidget(_ctrl_cell("ФОН", d.bg_seg))
    row2.addWidget(_ctrl_cell("ЧУВСТВИТЕЛЬНОСТЬ", d.sens_seg))
    cl.addLayout(row2)
    lay.addWidget(ctrl)

    color_card = QFrame()
    color_card.setObjectName("Card")
    ccl = QVBoxLayout(color_card)
    ccl.setContentsMargins(16, 10, 16, 10)
    ccl.setSpacing(6)
    color_cap = QLabel("ЦВЕТ")
    color_cap.setObjectName("SectionCap")
    ccl.addWidget(color_cap)
    d.color_selector = ColorPresetSelector()
    d.color_selector.setCurrentPreset(d.config.get("visualizer_color_preset", "mono"))
    d.color_selector.presetChanged.connect(d._on_preset_changed)
    ccl.addWidget(d.color_selector)
    lay.addWidget(color_card)

    lay.addStretch()
    outer.addStretch()
    outer.addWidget(inner)
    outer.addStretch()
    return page


def _ctrl_cell(label_text: str, widget) -> QWidget:
    """Vertical layout cell: CAPS label on top, control widget below."""
    cell = QWidget()
    vl = QVBoxLayout(cell)
    vl.setContentsMargins(0, 0, 0, 0)
    vl.setSpacing(4)
    lbl = QLabel(label_text)
    lbl.setObjectName("SectionCap")
    vl.addWidget(lbl)
    vl.addWidget(widget)
    return cell

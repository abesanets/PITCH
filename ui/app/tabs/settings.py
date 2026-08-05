"""Settings tab: STT engine status, hotkey, recording duration, and system configuration."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt

from ...widgets import ToggleSwitch, SegmentedControl


_HOTKEY_OPTIONS = [
    "ctrl+windows", "shift+windows", "ctrl+shift+windows",
    "ctrl+alt", "ctrl+shift", "ctrl+alt+space",
    "ctrl+shift+space", "left alt+space", "f8"
]
_DUR_VALUES = [0.3, 0.5, 1.0, 0.0]


def build_settings_tab(d) -> QWidget:
    """Build the merged Settings tab and attach relevant attributes to d."""
    page = QWidget()
    outer = QHBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    d.settings_scroll = QScrollArea()
    d.settings_scroll.setWidgetResizable(True)
    d.settings_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    d.settings_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    d.settings_scroll.setFrameShape(QFrame.Shape.NoFrame)
    d.settings_scroll.setFixedWidth(460)
    d.settings_scroll.setStyleSheet(
        "QScrollArea { background: transparent; border: none; padding: 0px; margin: 0px; }"
    )

    inner = QWidget()
    inner.setObjectName("SettingsInnerWidget")
    inner.setStyleSheet("QWidget#SettingsInnerWidget { background: transparent; }")
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    title = QLabel("Настройки")
    title.setObjectName("PageTitle")
    lay.addWidget(title)

    lay.addWidget(_build_engine_card(d))
    lay.addWidget(_build_input_card(d))
    lay.addWidget(_build_system_card(d))
    lay.addStretch()

    d.settings_scroll.setWidget(inner)
    outer.addStretch()
    outer.addWidget(d.settings_scroll)
    outer.addStretch()
    return page


def _build_engine_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    acl = QVBoxLayout(card)
    acl.setContentsMargins(16, 14, 16, 14)
    acl.setSpacing(8)

    api_cap = QLabel("ДВИЖОК РАСПОЗНАВАНИЯ")
    api_cap.setObjectName("SectionCap")
    acl.addWidget(api_cap)

    status_lbl = QLabel("GigaAM v3 (Сбер) • Silero VAD")
    status_lbl.setObjectName("FieldLbl")
    acl.addWidget(status_lbl)

    info_lbl = QLabel(
        "Локальная автономная модель распознавания речи (CPU ONNX Execution Provider). "
        "Оптимизирована под русский язык."
    )
    info_lbl.setWordWrap(True)
    info_lbl.setObjectName("DetailMeta")
    acl.addWidget(info_lbl)

    return card


def _build_input_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    icl = QVBoxLayout(card)
    icl.setContentsMargins(16, 14, 16, 14)
    icl.setSpacing(14)

    # Hotkey selection
    d.hotkey_1_combo = QComboBox()
    d.hotkey_1_combo.addItems(_HOTKEY_OPTIONS)
    d.hotkey_1_combo.setCurrentText(d.config.get("hotkey_1", "ctrl+windows"))
    d.hotkey_1_combo.currentTextChanged.connect(d._auto_save_settings)
    icl.addWidget(_setting_cell("СОЧЕТАНИЕ КЛАВИШ", d.hotkey_1_combo))

    # Recording minimum duration selection
    d.min_duration_seg = SegmentedControl(["0.3с", "0.5с", "1с", "Выкл"])
    dur_map = {0.3: 0, 0.5: 1, 1.0: 2, 0.0: 3}
    saved_dur = d.config.get("min_recording_duration", 0.5)
    d.min_duration_seg.setCurrentIndex(dur_map.get(saved_dur, 1))
    d.min_duration_seg.currentChanged.connect(d._auto_save_settings)

    dur_cell = QWidget()
    dur_vl = QVBoxLayout(dur_cell)
    dur_vl.setContentsMargins(0, 0, 0, 0)
    dur_vl.setSpacing(6)
    dur_lbl = QLabel("МИНИМАЛЬНАЯ ДЛИТЕЛЬНОСТЬ ЗАПИСИ")
    dur_lbl.setObjectName("SectionCap")
    dur_sub = QLabel("Короче — игнорировать как случайное нажатие")
    dur_sub.setObjectName("DetailMeta")
    dur_vl.addWidget(dur_lbl)
    dur_vl.addWidget(dur_sub)
    dur_vl.addWidget(d.min_duration_seg)
    icl.addWidget(dur_cell)

    return card


def _build_system_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    scl = QVBoxLayout(card)
    scl.setContentsMargins(16, 14, 16, 14)
    scl.setSpacing(0)

    d.startup_toggle = ToggleSwitch(checked=d.config.get("run_on_startup", False))
    d.startup_toggle.toggled.connect(d._auto_save_settings)

    row = QHBoxLayout()
    row.setSpacing(12)
    lbl_block = QVBoxLayout()
    lbl_block.setSpacing(2)
    toggle_title = QLabel("Автозапуск")
    toggle_title.setObjectName("FieldLbl")
    toggle_sub = QLabel("Запускать PITCH при входе в систему")
    toggle_sub.setObjectName("DetailMeta")
    lbl_block.addWidget(toggle_title)
    lbl_block.addWidget(toggle_sub)
    row.addLayout(lbl_block, 1)
    row.addWidget(d.startup_toggle)
    scl.addLayout(row)

    return card


def _setting_cell(label_text: str, widget) -> QWidget:
    """Vertical layout cell: CAPS label on top, control widget below."""
    cell = QWidget()
    vl = QVBoxLayout(cell)
    vl.setContentsMargins(0, 0, 0, 0)
    vl.setSpacing(6)
    lbl = QLabel(label_text)
    lbl.setObjectName("SectionCap")
    vl.addWidget(lbl)
    vl.addWidget(widget)
    return cell


def auto_save_settings(d) -> None:
    d.config["hotkey_1"] = d.hotkey_1_combo.currentText()
    d.config["min_recording_duration"] = _DUR_VALUES[d.min_duration_seg.currentIndex()]
    d.config["theme"] = "dark"
    d.config["run_on_startup"] = d.startup_toggle.isChecked()
    d.save_callback(d.config)
    _update_hotkey_badge(d)


def _update_hotkey_badge(d) -> None:
    h1 = d.config.get("hotkey_1", "ctrl+windows").upper()
    if hasattr(d, "hotkey_badge") and d.hotkey_badge:
        d.hotkey_badge.setText(h1)

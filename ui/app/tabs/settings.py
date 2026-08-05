"""Settings tab: Hotkeys and startup configuration."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt

from ...widgets import ToggleSwitch


_HOTKEY_OPTIONS_1 = ["ctrl+windows", "shift+windows", "ctrl+shift+windows", "ctrl+alt", "ctrl+shift", "ctrl+alt+space", "ctrl+shift+space", "left alt+space", "f8"]
_HOTKEY_OPTIONS_2 = ["shift+windows", "ctrl+windows", "ctrl+shift+windows", "ctrl+alt", "ctrl+shift", "ctrl+alt+space", "ctrl+shift+space", "left alt+space", "f8"]
_MODE_OPTIONS     = ["Стандартный (Словарная автозамена)", "Сырой STT"]
_MODE_TO_KEY      = {"Стандартный (Словарная автозамена)": "default", "Сырой STT": "raw"}
_KEY_TO_MODE      = {v: k for k, v in _MODE_TO_KEY.items()}


def build_settings_tab(d) -> QWidget:
    """Build the Settings tab and attach relevant attributes to d."""
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

    lay.addWidget(_build_api_card(d))
    lay.addWidget(_build_input_model_card(d))
    lay.addWidget(_build_system_card(d))
    lay.addStretch()

    d.settings_scroll.setWidget(inner)
    outer.addStretch()
    outer.addWidget(d.settings_scroll)
    outer.addStretch()
    return page


def _build_api_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    acl = QVBoxLayout(card)
    acl.setContentsMargins(16, 14, 16, 14)
    acl.setSpacing(8)

    api_cap = QLabel("ДВИЖОК РАСПОЗНАВАНИЯ")
    api_cap.setObjectName("SectionCap")
    acl.addWidget(api_cap)

    status_lbl = QLabel("GigaAM v3 (Сбер) • Локальный (CPU, 0.05x RTF)")
    status_lbl.setObjectName("FieldLbl")
    acl.addWidget(status_lbl)

    info_lbl = QLabel("Полностью автономная модель. Облачные API и ключи не требуются.")
    info_lbl.setObjectName("DetailMeta")
    acl.addWidget(info_lbl)

    return card


def _build_input_model_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    icl = QVBoxLayout(card)
    icl.setContentsMargins(16, 14, 16, 14)
    icl.setSpacing(14)

    d.hotkey_1_combo = QComboBox()
    d.hotkey_1_combo.addItems(_HOTKEY_OPTIONS_1)
    d.hotkey_1_combo.setCurrentText(d.config.get("hotkey_1", "ctrl+windows"))
    d.hotkey_1_combo.currentTextChanged.connect(d._auto_save_settings)

    d.mode_1_combo = QComboBox()
    d.mode_1_combo.addItems(_MODE_OPTIONS)
    d.mode_1_combo.setCurrentText(_KEY_TO_MODE.get(d.config.get("mode_1", "default"), "Стандартный (Словарная автозамена)"))
    d.mode_1_combo.currentTextChanged.connect(d._auto_save_settings)

    icl.addWidget(_setting_cell("СОЧЕТАНИЕ КЛАВИШ 1", d.hotkey_1_combo))
    icl.addWidget(_setting_cell("РЕЖИМ 1", d.mode_1_combo))

    d.hotkey_2_enabled_cb = ToggleSwitch(checked=d.config.get("hotkey_2_enabled", False))
    d.hotkey_2_enabled_cb.toggled.connect(d._auto_save_settings)
    d.hotkey_2_enabled_cb.toggled.connect(d._toggle_hotkey_2_widgets)

    h2_toggle_row = QHBoxLayout()
    h2_toggle_row.setSpacing(12)
    h2_lbl_block = QVBoxLayout()
    h2_lbl_block.setSpacing(2)
    h2_title = QLabel("Второе сочетание клавиш")
    h2_title.setObjectName("FieldLbl")
    h2_sub = QLabel("Назначить отдельное сочетание клавиш")
    h2_sub.setObjectName("DetailMeta")
    h2_lbl_block.addWidget(h2_title)
    h2_lbl_block.addWidget(h2_sub)
    h2_toggle_row.addLayout(h2_lbl_block, 1)
    h2_toggle_row.addWidget(d.hotkey_2_enabled_cb)
    icl.addLayout(h2_toggle_row)

    d.h2_widget = QWidget()
    h2_layout = QVBoxLayout(d.h2_widget)
    h2_layout.setContentsMargins(0, 0, 0, 0)
    h2_layout.setSpacing(14)

    d.hotkey_2_combo = QComboBox()
    d.hotkey_2_combo.addItems(_HOTKEY_OPTIONS_2)
    d.hotkey_2_combo.setCurrentText(d.config.get("hotkey_2", "shift+windows"))
    d.hotkey_2_combo.currentTextChanged.connect(d._auto_save_settings)

    d.mode_2_combo = QComboBox()
    d.mode_2_combo.addItems(_MODE_OPTIONS)
    d.mode_2_combo.setCurrentText(_KEY_TO_MODE.get(d.config.get("mode_2", "raw"), "Сырой STT"))
    d.mode_2_combo.currentTextChanged.connect(d._auto_save_settings)

    h2_layout.addWidget(_setting_cell("СОЧЕТАНИЕ КЛАВИШ 2", d.hotkey_2_combo))
    h2_layout.addWidget(_setting_cell("РЕЖИМ 2", d.mode_2_combo))
    icl.addWidget(d.h2_widget)
    d.h2_widget.setVisible(d.hotkey_2_enabled_cb.isChecked())

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
    d.config["mode_1"] = _MODE_TO_KEY.get(d.mode_1_combo.currentText(), "default")
    d.config["hotkey_2_enabled"] = d.hotkey_2_enabled_cb.isChecked()
    d.config["hotkey_2"] = d.hotkey_2_combo.currentText()
    d.config["mode_2"] = _MODE_TO_KEY.get(d.mode_2_combo.currentText(), "raw")
    d.config["theme"] = "dark"
    d.config["run_on_startup"] = d.startup_toggle.isChecked()
    d.save_callback(d.config)
    _update_hotkey_badge(d)


def on_base_url_changed(d) -> None:
    pass


def toggle_api_visibility(d) -> None:
    pass


def _update_hotkey_badge(d) -> None:
    h1 = d.config.get("hotkey_1", "ctrl+windows").upper()
    if d.config.get("hotkey_2_enabled", False):
        h2 = d.config.get("hotkey_2", "shift+windows").upper()
        d.hotkey_badge.setText(f"{h1} / {h2}")
    else:
        d.hotkey_badge.setText(h1)

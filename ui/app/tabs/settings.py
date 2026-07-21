"""Settings tab: API key, hotkeys, model selection, startup toggle."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt

from ...widgets import ToggleSwitch


_HOTKEY_OPTIONS_1 = ["ctrl+windows", "shift+windows", "ctrl+shift+windows", "ctrl+alt", "ctrl+shift", "ctrl+alt+space", "ctrl+shift+space", "left alt+space", "f8"]
_HOTKEY_OPTIONS_2 = ["shift+windows", "ctrl+windows", "ctrl+shift+windows", "ctrl+alt", "ctrl+shift", "ctrl+alt+space", "ctrl+shift+space", "left alt+space", "f8"]
_MODE_OPTIONS     = ["Редактор", "Чат", "Английский", "Кастом"]
_MODE_TO_KEY      = {"Редактор": "default", "Чат": "chat", "Английский": "translate_en", "Кастом": "custom"}
_KEY_TO_MODE      = {v: k for k, v in _MODE_TO_KEY.items()}
_TEXT_MODELS      = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-120b",
]


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
    acl.setSpacing(10)

    api_cap = QLabel("API")
    api_cap.setObjectName("SectionCap")
    acl.addWidget(api_cap)

    d.api_input = QLineEdit()
    d.api_input.setText(d.config.get("api_key", ""))
    d.api_input.setEchoMode(QLineEdit.EchoMode.Password)
    d.api_input.setPlaceholderText("gsk_...")
    d.api_input.editingFinished.connect(d._auto_save_settings)

    d.btn_toggle_api = QPushButton("Показать")
    d.btn_toggle_api.setObjectName("SecondaryBtn")
    d.btn_toggle_api.setCursor(Qt.CursorShape.PointingHandCursor)
    d.btn_toggle_api.clicked.connect(d.toggle_api_visibility)

    api_row = QHBoxLayout()
    api_row.setSpacing(8)
    api_row.addWidget(d.api_input, 1)
    api_row.addWidget(d.btn_toggle_api)
    acl.addLayout(api_row)

    d.base_url_input = QLineEdit()
    d.base_url_input.setText(d.config.get("groq_base_url", ""))
    d.base_url_input.setPlaceholderText(
        "https://your-worker.your-subdomain.workers.dev (without /openai/v1)"
    )
    d.base_url_input.editingFinished.connect(d._on_base_url_changed)
    acl.addWidget(d.base_url_input)

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
    d.mode_1_combo.setCurrentText(_KEY_TO_MODE.get(d.config.get("mode_1", "default"), "Редактор"))
    d.mode_1_combo.currentTextChanged.connect(d._auto_save_settings)

    h1_layout = QHBoxLayout()
    h1_layout.setSpacing(10)
    h1_layout.addWidget(_setting_cell("СОЧЕТАНИЕ КЛАВИШ 1", d.hotkey_1_combo), 2)
    h1_layout.addWidget(_setting_cell("РЕЖИМ 1", d.mode_1_combo), 1)
    icl.addLayout(h1_layout)

    d.hotkey_2_enabled_cb = ToggleSwitch(checked=d.config.get("hotkey_2_enabled", False))
    d.hotkey_2_enabled_cb.toggled.connect(d._auto_save_settings)
    d.hotkey_2_enabled_cb.toggled.connect(d._toggle_hotkey_2_widgets)

    h2_toggle_row = QHBoxLayout()
    h2_toggle_row.setSpacing(12)
    h2_lbl_block = QVBoxLayout()
    h2_lbl_block.setSpacing(2)
    h2_title = QLabel("Второе сочетание клавиш")
    h2_title.setObjectName("FieldLbl")
    h2_sub = QLabel("Назначить отдельный режим для второго хоткея")
    h2_sub.setObjectName("DetailMeta")
    h2_lbl_block.addWidget(h2_title)
    h2_lbl_block.addWidget(h2_sub)
    h2_toggle_row.addLayout(h2_lbl_block, 1)
    h2_toggle_row.addWidget(d.hotkey_2_enabled_cb)
    icl.addLayout(h2_toggle_row)

    d.h2_widget = QWidget()
    h2_layout = QHBoxLayout(d.h2_widget)
    h2_layout.setContentsMargins(0, 0, 0, 0)
    h2_layout.setSpacing(10)

    d.hotkey_2_combo = QComboBox()
    d.hotkey_2_combo.addItems(_HOTKEY_OPTIONS_2)
    d.hotkey_2_combo.setCurrentText(d.config.get("hotkey_2", "shift+windows"))
    d.hotkey_2_combo.currentTextChanged.connect(d._auto_save_settings)

    d.mode_2_combo = QComboBox()
    d.mode_2_combo.addItems(_MODE_OPTIONS)
    d.mode_2_combo.setCurrentText(_KEY_TO_MODE.get(d.config.get("mode_2", "translate_en"), "Английский"))
    d.mode_2_combo.currentTextChanged.connect(d._auto_save_settings)

    h2_layout.addWidget(_setting_cell("СОЧЕТАНИЕ КЛАВИШ 2", d.hotkey_2_combo), 2)
    h2_layout.addWidget(_setting_cell("РЕЖИМ 2", d.mode_2_combo), 1)
    icl.addWidget(d.h2_widget)
    d.h2_widget.setVisible(d.hotkey_2_enabled_cb.isChecked())

    d.model_combo = QComboBox()
    d.model_combo.addItems(_TEXT_MODELS)
    d.model_combo.setCurrentText(d.config.get("text_model", "llama-3.3-70b-versatile"))
    d.model_combo.currentTextChanged.connect(d._auto_save_settings)
    icl.addWidget(_setting_cell("ТЕКСТОВАЯ МОДЕЛЬ", d.model_combo))

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
    """Persist settings from the Settings tab to config and notify core."""
    d.config["api_key"]   = d.api_input.text().strip()
    d.config["hotkey_1"]  = d.hotkey_1_combo.currentText()
    d.config["hotkey"]    = d.hotkey_1_combo.currentText()
    d.config["mode_1"]    = _MODE_TO_KEY.get(d.mode_1_combo.currentText(), "default")
    d.config["hotkey_2_enabled"] = d.hotkey_2_enabled_cb.isChecked()
    d.config["hotkey_2"]  = d.hotkey_2_combo.currentText()
    d.config["mode_2"]    = _MODE_TO_KEY.get(d.mode_2_combo.currentText(), "translate_en")
    d.config["text_model"] = d.model_combo.currentText()
    d.config["theme"]      = "dark"
    d.config["run_on_startup"] = d.startup_toggle.isChecked()
    d.save_callback(d.config)
    _update_hotkey_badge(d)


def on_base_url_changed(d) -> None:
    """Handle Base URL change and prompt for restart if needed."""
    new_url = d.base_url_input.text().strip()
    old_url = d.config.get("groq_base_url", "")
    d.config["groq_base_url"] = new_url
    d.save_callback(d.config)
    if new_url != old_url:
        reply = QMessageBox.question(
            d,
            "Требуется перезапуск",
            "Изменение URL сервера требует перезагрузки приложения.\n\nПерезапустить сейчас?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if reply == QMessageBox.StandardButton.Yes:
            d.restart_requested.emit()


def toggle_api_visibility(d) -> None:
    if d.api_input.echoMode() == QLineEdit.EchoMode.Password:
        d.api_input.setEchoMode(QLineEdit.EchoMode.Normal)
        d.btn_toggle_api.setText("Скрыть")
    else:
        d.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        d.btn_toggle_api.setText("Показать")


def _update_hotkey_badge(d) -> None:
    h1 = d.config.get("hotkey_1", "ctrl+windows").upper()
    if d.config.get("hotkey_2_enabled", False):
        h2 = d.config.get("hotkey_2", "shift+windows").upper()
        d.hotkey_badge.setText(f"{h1} / {h2}")
    else:
        d.hotkey_badge.setText(h1)

"""Recognition tab: Whisper options, hallucination filter, formatting style selector."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QPlainTextEdit
)
from PyQt6.QtCore import Qt

from ...widgets import ToggleSwitch, SegmentedControl


STYLE_DETAILS = {
    "default": {
        "desc": "Исправляет опечатки, пунктуацию и расставляет абзацы. Превращает технический сленг в английские термины.",
        "example": "Пример: «привет запиши это в джэсон» → <b>«Привет, запиши это в JSON.»</b>",
    },
    "chat": {
        "desc": "Пишет весь текст строчными буквами без разделения на предложения (все мысли через запятую) и без точек. Удаляет слова-паразиты.",
        "example": "Пример: «ну привет короче как дела завтра пойдём гулять» → <b>«привет, как дела, завтра пойдем гулять»</b>",
    },
    "translate_en": {
        "desc": "Переводит русскую речь на английский с исправлением пунктуации и удалением слов-паразитов. Сохраняет русские имена и названия.",
        "example": "Пример: «запусти скрипт антигравити» → <b>«Run the \"Антигравити\" script.»</b>",
    },
    "custom": {
        "desc": "Применяет вашу собственную текстовую инструкцию для форматирования распознанного текста.",
        "example": "Пример: [Действует указанная ниже пользовательская инструкция]",
    },
}

_DUR_VALUES = [0.3, 0.5, 1.0, 0.0]
_STYLE_KEYS  = ["default", "chat", "translate_en", "custom"]


def build_recognition_tab(d) -> QWidget:
    """Build the Recognition tab and attach relevant attributes to d."""
    page = QWidget()
    outer = QHBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    d.recognition_scroll = QScrollArea()
    d.recognition_scroll.setWidgetResizable(True)
    d.recognition_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    d.recognition_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    d.recognition_scroll.setFrameShape(QFrame.Shape.NoFrame)
    d.recognition_scroll.setFixedWidth(460)
    d.recognition_scroll.setStyleSheet(
        "QScrollArea { background: transparent; border: none; padding: 0px; margin: 0px; }"
    )

    d.recognition_inner = QWidget()
    d.recognition_inner.setObjectName("RecognitionInnerWidget")
    d.recognition_inner.setStyleSheet("QWidget#RecognitionInnerWidget { background: transparent; }")
    lay = QVBoxLayout(d.recognition_inner)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    title = QLabel("Распознавание")
    title.setObjectName("PageTitle")
    lay.addWidget(title)

    lay.addWidget(_build_whisper_card(d))
    lay.addWidget(_build_filter_card(d))
    lay.addWidget(_build_style_card(d))
    lay.addStretch()

    d.recognition_scroll.setWidget(d.recognition_inner)
    outer.addStretch()
    outer.addWidget(d.recognition_scroll)
    outer.addStretch()
    return page


def _build_whisper_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    wcl = QVBoxLayout(card)
    wcl.setContentsMargins(16, 14, 16, 14)
    wcl.setSpacing(14)

    cap = QLabel("WHISPER")
    cap.setObjectName("SectionCap")
    wcl.addWidget(cap)

    d.raw_whisper_toggle = ToggleSwitch(checked=d.config.get("use_raw_whisper", False))
    d.raw_whisper_toggle.toggled.connect(d._auto_save_recognition)
    _add_toggle_row(wcl, "Сырой Whisper", "Быстрее, но без улучшения качества LLM", d.raw_whisper_toggle)

    d.whisper_model_seg = SegmentedControl(["Авто", "Turbo", "Large v3"])
    model_map = {"auto": 0, "whisper-large-v3-turbo": 1, "whisper-large-v3": 2}
    saved_model = d.config.get("whisper_model", "auto")
    d.whisper_model_seg.setCurrentIndex(model_map.get(saved_model, 0))
    d.whisper_model_seg.currentChanged.connect(d._auto_save_recognition)

    wm_cell = QWidget()
    wm_vl = QVBoxLayout(wm_cell)
    wm_vl.setContentsMargins(0, 0, 0, 0)
    wm_vl.setSpacing(6)
    wm_lbl = QLabel("МОДЕЛЬ WHISPER ПО УМОЛЧАНИЮ")
    wm_lbl.setObjectName("SectionCap")
    wm_sub = QLabel("Turbo — быстрее, Large v3 — точнее")
    wm_sub.setObjectName("DetailMeta")
    wm_vl.addWidget(wm_lbl)
    wm_vl.addWidget(wm_sub)
    wm_vl.addWidget(d.whisper_model_seg)
    wcl.addWidget(wm_cell)

    return card


def _build_filter_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    fcl = QVBoxLayout(card)
    fcl.setContentsMargins(16, 14, 16, 14)
    fcl.setSpacing(14)

    cap = QLabel("ФИЛЬТРАЦИЯ")
    cap.setObjectName("SectionCap")
    fcl.addWidget(cap)

    d.hallucination_filter_toggle = ToggleSwitch(
        checked=d.config.get("filter_hallucinations", True)
    )
    d.hallucination_filter_toggle.toggled.connect(d._auto_save_recognition)
    _add_toggle_row(
        fcl,
        "Фильтр галлюцинаций",
        "Блокировать «Продолжение следует…» и похожие",
        d.hallucination_filter_toggle,
    )

    d.min_duration_seg = SegmentedControl(["0.3с", "0.5с", "1с", "Выкл"])
    dur_map = {0.3: 0, 0.5: 1, 1.0: 2, 0.0: 3}
    saved_dur = d.config.get("min_recording_duration", 0.5)
    d.min_duration_seg.setCurrentIndex(dur_map.get(saved_dur, 1))
    d.min_duration_seg.currentChanged.connect(d._auto_save_recognition)

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
    fcl.addWidget(dur_cell)

    return card


def _build_style_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    scl = QVBoxLayout(card)
    scl.setContentsMargins(16, 14, 16, 14)
    scl.setSpacing(10)

    cap = QLabel("СТИЛЬ ФОРМАТИРОВАНИЯ")
    cap.setObjectName("SectionCap")
    scl.addWidget(cap)

    d.style_seg = SegmentedControl(["Редактор", "Чат", "Английский", "Кастом"])
    d.style_keys = _STYLE_KEYS
    d.style_seg.currentChanged.connect(d._on_style_seg_changed)
    scl.addWidget(d.style_seg)

    d.style_info_card = QFrame()
    d.style_info_card.setObjectName("SubCard")
    sil = QVBoxLayout(d.style_info_card)
    sil.setContentsMargins(12, 10, 12, 10)
    sil.setSpacing(6)

    d.style_desc_lbl = QLabel()
    d.style_desc_lbl.setWordWrap(True)
    d.style_desc_lbl.setObjectName("StyleDescLbl")

    d.style_example_lbl = QLabel()
    d.style_example_lbl.setWordWrap(True)
    d.style_example_lbl.setObjectName("StyleExampleLbl")

    sil.addWidget(d.style_desc_lbl)
    sil.addWidget(d.style_example_lbl)
    scl.addWidget(d.style_info_card)

    d.custom_style_label = QLabel("ИНСТРУКЦИЯ ДЛЯ КАСТОМНОГО СТИЛЯ:")
    d.custom_style_label.setObjectName("SectionCap")
    scl.addWidget(d.custom_style_label)

    d.custom_style_edit = QPlainTextEdit()
    d.custom_style_edit.setPlaceholderText(
        "Например: Переведи текст на английский язык или Перепиши текст в деловом стиле."
    )
    d.custom_style_edit.setFixedHeight(120)
    d.custom_style_edit.setPlainText(d.config.get("custom_formatting_style", ""))
    d.custom_style_edit.textChanged.connect(d._auto_save_recognition)
    scl.addWidget(d.custom_style_edit)

    return card


def _add_toggle_row(parent_layout, title_text: str, sub_text: str, toggle_widget) -> None:
    row = QHBoxLayout()
    row.setSpacing(12)
    lbl_block = QVBoxLayout()
    lbl_block.setSpacing(2)
    t = QLabel(title_text)
    t.setObjectName("FieldLbl")
    s = QLabel(sub_text)
    s.setObjectName("DetailMeta")
    lbl_block.addWidget(t)
    lbl_block.addWidget(s)
    row.addLayout(lbl_block, 1)
    row.addWidget(toggle_widget)
    parent_layout.addLayout(row)


def update_style_ui(d, key: str) -> None:
    """Sync the style segmented control and description labels to the given key."""
    if hasattr(d, "style_seg") and hasattr(d, "style_keys"):
        try:
            idx = d.style_keys.index(key)
            if d.style_seg.currentIndex() != idx:
                d.style_seg.setCurrentIndex(idx)
        except ValueError:
            pass

    info = STYLE_DETAILS.get(key, STYLE_DETAILS["default"])
    d.style_desc_lbl.setText(info["desc"])
    d.style_example_lbl.setText(info["example"])

    is_custom = key == "custom"
    d.custom_style_label.setVisible(is_custom)
    d.custom_style_edit.setVisible(is_custom)


def auto_save_recognition(d) -> None:
    """Persist recognition settings from the Recognition tab to config."""
    d.config["use_raw_whisper"] = d.raw_whisper_toggle.isChecked()
    d.config["filter_hallucinations"] = d.hallucination_filter_toggle.isChecked()
    d.config["min_recording_duration"] = _DUR_VALUES[d.min_duration_seg.currentIndex()]
    if hasattr(d, "whisper_model_seg"):
        _MODEL_VALUES = ["auto", "whisper-large-v3-turbo", "whisper-large-v3"]
        d.config["whisper_model"] = _MODEL_VALUES[d.whisper_model_seg.currentIndex()]
    d.config["custom_formatting_style"] = d.custom_style_edit.toPlainText().strip()
    d.save_callback(d.config)

"""Recognition tab: Local engine status, hallucination filter, dictionary management."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt

from ...widgets import ToggleSwitch, SegmentedControl


_DUR_VALUES = [0.3, 0.5, 1.0, 0.0]


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

    lay.addWidget(_build_engine_card(d))
    lay.addWidget(_build_filter_card(d))
    lay.addWidget(_build_corrections_card(d))
    lay.addStretch()

    d.recognition_scroll.setWidget(d.recognition_inner)
    outer.addStretch()
    outer.addWidget(d.recognition_scroll)
    outer.addStretch()
    return page


def _build_engine_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    ecl = QVBoxLayout(card)
    ecl.setContentsMargins(16, 14, 16, 14)
    ecl.setSpacing(10)

    cap = QLabel("ЛОКАЛЬНЫЙ ДВИЖОК STT")
    cap.setObjectName("SectionCap")
    ecl.addWidget(cap)

    status_lbl = QLabel("GigaAM v3 (Сбер) + Silero VAD")
    status_lbl.setObjectName("FieldLbl")
    ecl.addWidget(status_lbl)

    info_lbl = QLabel(
        "Локальная эндогенная модель распознавания речи (CPU ONNX Execution Provider). "
        "Включает автоматическую нечеткую автозамену терминов по файлу corrections.json."
    )
    info_lbl.setWordWrap(True)
    info_lbl.setObjectName("DetailMeta")
    ecl.addWidget(info_lbl)

    return card


def _build_filter_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    fcl = QVBoxLayout(card)
    fcl.setContentsMargins(16, 14, 16, 14)
    fcl.setSpacing(14)

    cap = QLabel("ФИЛЬТРАЦИЯ И ЗАПИСЬ")
    cap.setObjectName("SectionCap")
    fcl.addWidget(cap)

    d.hallucination_filter_toggle = ToggleSwitch(
        checked=d.config.get("filter_hallucinations", True)
    )
    d.hallucination_filter_toggle.toggled.connect(d._auto_save_recognition)
    _add_toggle_row(
        fcl,
        "Фильтр галлюцинаций",
        "Удалять повторяющиеся фразы и артефакты тишины",
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


def _build_corrections_card(d) -> QFrame:
    card = QFrame()
    card.setObjectName("Card")
    ccl = QVBoxLayout(card)
    ccl.setContentsMargins(16, 14, 16, 14)
    ccl.setSpacing(12)

    cap = QLabel("СЛОВАРЬ АВТОЗАМЕНЫ (CORRECTIONS.JSON)")
    cap.setObjectName("SectionCap")
    ccl.addWidget(cap)

    # Form to add a new term correction rule
    form_layout = QHBoxLayout()
    form_layout.setSpacing(8)

    d.corr_key_input = QLineEdit()
    d.corr_key_input.setPlaceholderText("Слово/Ошибка")
    
    d.corr_val_input = QLineEdit()
    d.corr_val_input.setPlaceholderText("Правильная замена")

    btn_add = QPushButton("Добавить")
    btn_add.setObjectName("PrimaryBtn")
    btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
    btn_add.clicked.connect(lambda: _add_correction_rule(d))

    form_layout.addWidget(d.corr_key_input, 1)
    form_layout.addWidget(d.corr_val_input, 1)
    form_layout.addWidget(btn_add, 0)
    ccl.addLayout(form_layout)

    # Container for existing correction items
    d.corrections_list_widget = QWidget()
    d.corrections_list_layout = QVBoxLayout(d.corrections_list_widget)
    d.corrections_list_layout.setContentsMargins(0, 0, 0, 0)
    d.corrections_list_layout.setSpacing(6)
    ccl.addWidget(d.corrections_list_widget)

    _refresh_corrections_list(d)

    return card


def _add_correction_rule(d) -> None:
    key = d.corr_key_input.text().strip()
    val = d.corr_val_input.text().strip()
    if not key or not val:
        return

    postprocessor = getattr(d, "postprocessor", None)
    if not postprocessor and hasattr(d, "core") and hasattr(d.core, "_stt_engine"):
        postprocessor = d.core._stt_engine.postprocessor

    if postprocessor:
        postprocessor.add_correction(key, val)
    else:
        # Fallback to direct json update if postprocessor instance isn't attached
        import os, json
        path = d.config.get("corrections_path", "corrections.json")
        data = {}
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                pass
        data[key.lower()] = val
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    d.corr_key_input.clear()
    d.corr_val_input.clear()
    _refresh_corrections_list(d)


def _remove_correction_rule(d, key: str) -> None:
    postprocessor = getattr(d, "postprocessor", None)
    if not postprocessor and hasattr(d, "core") and hasattr(d.core, "_stt_engine"):
        postprocessor = d.core._stt_engine.postprocessor

    if postprocessor:
        postprocessor.remove_correction(key)
    else:
        import os, json
        path = d.config.get("corrections_path", "corrections.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if key.lower() in data:
                    del data[key.lower()]
                    with open(path, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass

    _refresh_corrections_list(d)


def _refresh_corrections_list(d) -> None:
    if not hasattr(d, "corrections_list_layout"):
        return

    # Clear current UI items
    while d.corrections_list_layout.count() > 0:
        item = d.corrections_list_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()

    # Get dictionary items
    corrections = {}
    postprocessor = getattr(d, "postprocessor", None)
    if not postprocessor and hasattr(d, "core") and hasattr(d.core, "_stt_engine"):
        postprocessor = d.core._stt_engine.postprocessor

    if postprocessor:
        corrections = postprocessor.corrections
    else:
        import os, json
        path = d.config.get("corrections_path", "corrections.json")
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    corrections = json.load(f)
            except Exception:
                pass

    if not corrections:
        empty_lbl = QLabel("Словарь пуст.")
        empty_lbl.setObjectName("DetailMeta")
        d.corrections_list_layout.addWidget(empty_lbl)
        return

    for k, v in corrections.items():
        row_frame = QFrame()
        row_frame.setObjectName("SubCard")
        rl = QHBoxLayout(row_frame)
        rl.setContentsMargins(12, 8, 12, 8)
        rl.setSpacing(8)

        lbl = QLabel(f"«{k}»  ➔  <b>{v}</b>")
        lbl.setObjectName("FieldLbl")
        rl.addWidget(lbl, 1)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(24, 24)
        btn_del.setObjectName("SecondaryBtn")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda _, key=k: _remove_correction_rule(d, key))
        rl.addWidget(btn_del, 0)

        d.corrections_list_layout.addWidget(row_frame)


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
    pass


def auto_save_recognition(d) -> None:
    """Persist recognition settings from the Recognition tab to config."""
    d.config["filter_hallucinations"] = d.hallucination_filter_toggle.isChecked()
    d.config["min_recording_duration"] = _DUR_VALUES[d.min_duration_seg.currentIndex()]
    d.save_callback(d.config)

"""History tab: list view with search, detail view with raw/cleaned text."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QScrollArea, QStackedWidget, QLineEdit, QPushButton,
    QPlainTextEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize

from core import history_manager
from ...widgets import ElidedLabel


def build_history_tab(d) -> QWidget:
    """Build the History tab and attach relevant attributes to d."""
    page = QWidget()
    outer = QHBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    inner = QWidget()
    inner.setFixedWidth(460)
    inner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    d.history_stack = QStackedWidget()

    list_page = QWidget()
    list_lay = QVBoxLayout(list_page)
    list_lay.setContentsMargins(0, 0, 0, 0)
    list_lay.setSpacing(10)

    hdr = QHBoxLayout()
    title = QLabel("История")
    title.setObjectName("PageTitle")
    hdr.addWidget(title)
    hdr.addStretch()
    d.btn_clear_history = QPushButton("Очистить")
    d.btn_clear_history.setObjectName("SecondaryBtn")
    d.btn_clear_history.setCursor(Qt.CursorShape.PointingHandCursor)
    d.btn_clear_history.clicked.connect(d.clear_all_history)
    hdr.addWidget(d.btn_clear_history)
    list_lay.addLayout(hdr)

    d.history_search = QLineEdit()
    d.history_search.setPlaceholderText("Поиск...")
    d.history_search.textChanged.connect(d.filter_history)
    list_lay.addWidget(d.history_search)

    d.history_scroll = QScrollArea()
    d.history_scroll.setWidgetResizable(True)
    d.history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    d.history_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    d.history_scroll.setFrameShape(QFrame.Shape.NoFrame)

    d.history_cards_widget = QWidget()
    d.history_cards_widget.setObjectName("HistoryCardsWidget")
    d.history_cards_layout = QVBoxLayout(d.history_cards_widget)
    d.history_cards_layout.setContentsMargins(0, 0, 0, 0)
    d.history_cards_layout.setSpacing(6)
    d.history_cards_layout.addStretch()

    d.history_scroll.setWidget(d.history_cards_widget)
    list_lay.addWidget(d.history_scroll, 1)
    d.history_stack.addWidget(list_page)

    detail_page = QWidget()
    detail_lay = QVBoxLayout(detail_page)
    detail_lay.setContentsMargins(0, 0, 0, 0)
    detail_lay.setSpacing(10)

    back_hdr = QHBoxLayout()
    d.btn_back_to_list = QPushButton("Назад")
    d.btn_back_to_list.setObjectName("SecondaryBtn")
    d.btn_back_to_list.setCursor(Qt.CursorShape.PointingHandCursor)
    d.btn_back_to_list.setFixedWidth(100)
    d.btn_back_to_list.clicked.connect(d.hide_history_detail)
    back_hdr.addWidget(d.btn_back_to_list)
    back_hdr.addStretch()
    detail_lay.addLayout(back_hdr)

    d.detail_meta = QLabel()
    d.detail_meta.setObjectName("DetailMeta")
    detail_lay.addWidget(d.detail_meta)

    d.lbl_clean = QLabel("ТЕКСТ ДИКТОВКИ")
    d.lbl_clean.setObjectName("DetailLbl")
    d.txt_clean = QPlainTextEdit()
    d.txt_clean.setReadOnly(True)
    detail_lay.addWidget(d.lbl_clean)
    detail_lay.addWidget(d.txt_clean)

    d.lbl_raw = QLabel("ИСХОДНЫЙ СЫРОЙ ТЕКСТ (ДО АВТОЗАМЕНЫ)")
    d.lbl_raw.setObjectName("DetailLbl")
    d.txt_raw = QPlainTextEdit()
    d.txt_raw.setReadOnly(True)
    detail_lay.addWidget(d.lbl_raw)
    detail_lay.addWidget(d.txt_raw)

    d.history_stack.addWidget(detail_page)
    lay.addWidget(d.history_stack)

    outer.addStretch()
    outer.addWidget(inner)
    outer.addStretch()
    return page


def load_history(d) -> None:
    """Load history entries from disk and refresh the list."""
    d.history_entries = history_manager.load_history()
    filter_history(d)


def filter_history(d) -> None:
    """Render history cards matching the search query."""
    query = d.history_search.text().lower()
    while d.history_cards_layout.count() > 1:
        item = d.history_cards_layout.takeAt(0)
        if item.widget():
            item.widget().deleteLater()

    for idx, entry in enumerate(d.history_entries):
        raw, clean = entry.get("raw_text", ""), entry.get("cleaned_text", "")
        if query and query not in raw.lower() and query not in clean.lower():
            continue

        text = clean or raw
        snippet = (text[:80].replace("\n", " ") + "…") if len(text) > 80 else text[:80].replace("\n", " ")
        parts = entry.get("timestamp", "").split()
        time_str = parts[-1][:5] if parts else ""
        date_str = parts[0] if parts else ""
        lat_str = f"{entry.get('total_latency', 0):.1f}с"
        words = entry.get("word_count", 0)

        card = QFrame()
        card.setObjectName("RecentItem")
        card.setCursor(Qt.CursorShape.PointingHandCursor)
        cl = QHBoxLayout(card)
        cl.setContentsMargins(12, 10, 12, 10)
        cl.setSpacing(10)

        left = QVBoxLayout()
        left.setSpacing(3)
        snip_lbl = ElidedLabel(snippet if snippet else "—")
        snip_lbl.setObjectName("RecentSnippet")
        snip_lbl.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        meta_lbl = QLabel(f"{date_str}  {time_str}  ·  {words} сл.")
        meta_lbl.setObjectName("RecentMeta")
        left.addWidget(snip_lbl)
        left.addWidget(meta_lbl)

        right_lbl = QLabel(lat_str)
        right_lbl.setObjectName("HistoryLatency")
        right_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        right_lbl.setFixedWidth(44)

        cl.addLayout(left, 1)
        cl.addWidget(right_lbl, 0)
        card.mousePressEvent = lambda e, i=idx: d._open_history_entry(i)
        d.history_cards_layout.insertWidget(d.history_cards_layout.count() - 1, card)


def open_history_entry(d, idx: int) -> None:
    """Show the detail view for the given history entry index."""
    if idx is not None and idx < len(d.history_entries):
        e = d.history_entries[idx]
        raw_text = e.get("raw_text", "").strip()
        cleaned_text = e.get("cleaned_text", "").strip()

        d.txt_clean.setPlainText(cleaned_text or raw_text)
        
        has_diff = bool(raw_text and cleaned_text and raw_text != cleaned_text)
        d.lbl_raw.setVisible(has_diff)
        d.txt_raw.setVisible(has_diff)
        if has_diff:
            d.txt_raw.setPlainText(raw_text)

        d.detail_meta.setText(
            f"{e.get('timestamp', '')}  ·  {e.get('total_latency', 0):.1f}с  ·  {e.get('model', '')}"
        )
        d.history_stack.setCurrentIndex(1)



def clear_all_history(d) -> None:
    """Clear all history and refresh."""
    history_manager.clear_history()
    load_history(d)

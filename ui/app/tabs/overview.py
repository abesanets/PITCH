"""Overview tab: statistics cards, hotkey badge, recent dictations list."""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt

from core import history_manager
from ._helpers import update_hotkey_badge


def build_overview_tab(d) -> QWidget:
    """Build the Overview tab and attach relevant attributes to the dashboard instance d."""
    page = QWidget()
    outer = QHBoxLayout(page)
    outer.setContentsMargins(0, 0, 0, 0)

    inner = QWidget()
    inner.setFixedWidth(460)
    lay = QVBoxLayout(inner)
    lay.setContentsMargins(0, 0, 0, 0)
    lay.setSpacing(10)

    hdr = QHBoxLayout()
    title = QLabel("Обзор")
    title.setObjectName("PageTitle")
    hdr.addWidget(title)
    hdr.addStretch()
    lay.addLayout(hdr)

    row1_lay = QHBoxLayout()
    row1_lay.setSpacing(8)
    c1, d.val_total = _stat_card("ДИКТОВОК")
    c2, d.val_words = _stat_card("СЛОВ")
    c3, d.val_chars = _stat_card("СИМВОЛОВ")
    row1_lay.addWidget(c1, 1)
    row1_lay.addWidget(c2, 1)
    row1_lay.addWidget(c3, 1)
    lay.addLayout(row1_lay)

    row2_lay = QHBoxLayout()
    row2_lay.setSpacing(8)
    c4, d.val_lat = _stat_card("СРЕДНЯЯ ЗАДЕРЖКА")
    c5, d.val_rtf = _stat_card("СКОРОСТЬ STT")
    d.val_lat.setText("0.0 с")
    d.val_rtf.setText("0.05x RTF")
    row2_lay.addWidget(c4, 1)
    row2_lay.addWidget(c5, 1)
    lay.addLayout(row2_lay)

    hotkey_card = QFrame()
    hotkey_card.setObjectName("Card")
    hkl = QHBoxLayout(hotkey_card)
    hkl.setContentsMargins(14, 10, 14, 10)
    hkl.setSpacing(10)
    hk_text = QLabel("Горячая клавиша")
    hk_text.setObjectName("FieldLbl")
    hkl.addWidget(hk_text)
    hkl.addStretch()
    d.hotkey_badge = QLabel(d.config.get("hotkey_1", "ctrl+windows").upper())
    d.hotkey_badge.setObjectName("HotkeyBadge")
    hkl.addWidget(d.hotkey_badge)
    lay.addWidget(hotkey_card)

    recent_title = QLabel("ПОСЛЕДНИЕ ДИКТОВКИ")
    recent_title.setObjectName("SectionCap")
    lay.addWidget(recent_title)

    d.recent_items = []
    for _ in range(5):
        item_frame = QFrame()
        item_frame.setObjectName("RecentItemFlat")
        ifl = QHBoxLayout(item_frame)
        ifl.setContentsMargins(8, 4, 8, 4)
        ifl.setSpacing(10)

        left = QVBoxLayout()
        left.setSpacing(1)
        snippet = QLabel("—")
        snippet.setObjectName("RecentSnippetFlat")
        snippet.setWordWrap(False)
        ts = QLabel("")
        ts.setObjectName("RecentMetaFlat")
        left.addWidget(snippet)
        left.addWidget(ts)

        right = QLabel("")
        right.setObjectName("RecentMetaFlat")
        right.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        item_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        ifl.addLayout(left, 1)
        ifl.addWidget(right)
        lay.addWidget(item_frame)
        d.recent_items.append((item_frame, snippet, ts, right))

    lay.addStretch()

    outer.addStretch()
    outer.addWidget(inner)
    outer.addStretch()
    return page


def _stat_card(caption: str):
    """Create a stat card widget. Returns (card, value_label)."""
    card = QFrame()
    card.setObjectName("Card")
    cl = QVBoxLayout(card)
    cl.setContentsMargins(10, 8, 10, 8)
    cl.setSpacing(2)
    cap = QLabel(caption)
    cap.setObjectName("StatCap")
    val = QLabel("0")
    val.setObjectName("StatNum")
    cl.addWidget(cap)
    cl.addWidget(val)
    return card, val


def update_statistics(d) -> None:
    """Refresh statistics cards and recent items from history."""
    stats = history_manager.get_statistics()
    d.val_total.setText(str(stats["total_dictations"]))
    d.val_words.setText(str(stats["total_words"]))
    d.val_chars.setText(str(stats["total_chars"]))
    d.val_lat.setText(f"{stats['avg_total_latency']:.1f} с")
    avg_rtf = stats.get("avg_rtf", 0.05)
    d.val_rtf.setText(f"{avg_rtf:.2f}x RTF")
    update_hotkey_badge(d)

    entries = history_manager.load_history()[:5]
    for i, (item_frame, snippet_lbl, ts_lbl, right_lbl) in enumerate(d.recent_items):
        if i < len(entries):
            e = entries[i]
            text = e.get("cleaned_text") or e.get("raw_text", "")
            short = (text[:55].replace("\n", " ") + "…") if len(text) > 55 else text[:55].replace("\n", " ")
            snippet_lbl.setText(short if short else "—")
            ts_lbl.setText(e.get("timestamp", "").split()[-1][:5])
            right_lbl.setText(f"{e.get('total_latency', 0):.1f}с")
            item_frame.mousePressEvent = lambda e, idx=i: d._open_history_from_overview(idx)
        else:
            snippet_lbl.setText("—")
            ts_lbl.setText("")
            right_lbl.setText("")
            item_frame.mousePressEvent = None



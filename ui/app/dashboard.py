"""Dashboard window for VoiceAssistant"""
import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox,
                             QStackedWidget, QPlainTextEdit, QFrame, QApplication,
                             QGridLayout,
                             QSizePolicy, QScrollArea, QSlider, QColorDialog,
                             QDialog, QMessageBox)
from PyQt6.QtCore import (Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve,
                           pyqtProperty, pyqtSignal, QPointF, QPoint, QSize)
from PyQt6.QtGui import (QPainter, QPen, QBrush, QFont, QIcon, QPixmap,
                          QCursor, QPainterPath, QLinearGradient, QPalette, QColor)

from core import history_manager
from ..styles import get_stylesheet, get_resource_path
from ..widgets import ToggleSwitch, SegmentedControl, ColorPresetSelector, ElidedLabel
from ..visualizer.widgets import PreviewWidget, OverlayWindow

STYLE_DETAILS = {
    "default": {
        "desc": "Исправляет опечатки, пунктуацию и расставляет абзацы. Превращает технический сленг в английские термины.",
        "example": "Пример: «привет запиши это в джэсон» → <b>«Привет, запиши это в JSON.»</b>"
    },
    "chat": {
        "desc": "Пишет весь текст строчными буквами без разделения на предложения (все мысли через запятую) и без точек. Удаляет слова-паразиты.",
        "example": "Пример: «ну привет короче как дела завтра пойдём гулять» → <b>«привет, как дела, завтра пойдем гулять»</b>"
    },
    "translate_en": {
        "desc": "Переводит русскую речь на английский с исправлением пунктуации и удалением слов-паразитов. Сохраняет русские имена и названия.",
        "example": "Пример: «запусти скрипт антигравити» → <b>«Run the \"Антигравити\" script.»</b>"
    },
    "custom": {
        "desc": "Применяет вашу собственную текстовую инструкцию для форматирования распознанного текста.",
        "example": "Пример: [Действует указанная ниже пользовательская инструкция]"
    }
}



def _apply_dwm_rounded_corners(win_id):
    """Apply native rounded corners via Windows DWM API (Windows 11+)."""
    if sys.platform != "win32":
        return False
    try:
        import ctypes
        DWMWCP_ROUND = 2
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            int(win_id),
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(DWMWCP_ROUND)),
            ctypes.sizeof(ctypes.c_int),
        )
        return True
    except Exception:
        return False


class TitleBar(QFrame):
    """Custom title bar with window controls"""
    def __init__(self, parent_window):
        super().__init__()
        self.setObjectName("TitleBar")
        self.setFixedHeight(28)
        self._win = parent_window

        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 0, 0, 0)
        lay.setSpacing(0)

        # No title label - logo is in sidebar
        lay.addStretch()

        # Minimize button
        self._btn_min = QPushButton("─")
        self._btn_min.setObjectName("TitleBtn")
        self._btn_min.setFixedSize(36, 28)
        self._btn_min.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_min.clicked.connect(parent_window.showMinimized)
        lay.addWidget(self._btn_min)

        # Close button
        self._btn_close = QPushButton("✕")
        self._btn_close.setObjectName("TitleBtnClose")
        self._btn_close.setFixedSize(36, 28)
        self._btn_close.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_close.clicked.connect(parent_window.close)
        lay.addWidget(self._btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._win._dragging = True
            self._win._drag_pos = event.globalPosition().toPoint() - self._win.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._win._dragging:
            self._win.move(event.globalPosition().toPoint() - self._win._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._win._dragging = False


class DashboardWindow(QWidget):
    """Main dashboard window with tabs"""
    restart_requested = pyqtSignal()  # Signal to request application restart
    
    def __init__(self, config, save_callback):
        super().__init__()
        self.setObjectName("DashboardWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.config = config
        self.save_callback = save_callback
        self.theme_name = self.config.get("theme", "dark")
        self.history_entries = []
        self.init_ui()
        self.apply_theme(self.theme_name)
        self.load_logs()
        self.load_history()
        self.update_statistics()

    def init_ui(self):
        self.setWindowTitle("PITCH")
        self.setFixedSize(760, 620)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        # Main vertical layout: title bar + content
        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(2, 2, 2, 2)
        main_vbox.setSpacing(0)

        # Custom title bar
        self.title_bar = TitleBar(self)
        main_vbox.addWidget(self.title_bar)

        # Content area (sidebar + pages)
        content = QWidget()
        content.setObjectName("DashboardContent")
        root = QHBoxLayout(content)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())

        # Main content container for rounded chocolate panel
        self.main_container = QFrame()
        self.main_container.setObjectName("MainContentContainer")
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(12, 12, 12, 12)

        self.stack = QStackedWidget()
        container_layout.addWidget(self.stack)

        # Wrap main_container in a layout with 12px margin on all sides to make it float symmetrically
        # and ensure the 1px border is fully visible on all 4 sides without touching adjacent widgets.
        main_container_wrapper = QWidget()
        wrapper_layout = QVBoxLayout(main_container_wrapper)
        wrapper_layout.setContentsMargins(12, 12, 12, 12)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(self.main_container)

        root.addWidget(main_container_wrapper)

        main_vbox.addWidget(content)

        self._build_overview_tab()
        self._build_visualizer_tab()
        self._build_history_tab()
        self._build_settings_tab()
        self._build_recognition_tab()
        self._build_logs_tab()

        icon_path = get_resource_path(os.path.join("assets", "p.jpeg"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Drag state
        self._dragging = False
        self._drag_pos = QPoint()

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(210)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(14, 20, 14, 16)
        lay.setSpacing(2)
        self.sidebar_layout = lay  # Store reference for icon updates

        # Script Logo Label
        logo_lbl = QLabel("Pitch")
        logo_lbl.setObjectName("AppName")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        logo_lbl.setContentsMargins(10, 10, 0, 10)
        lay.addWidget(logo_lbl)
        lay.addSpacing(8)

        self.nav_buttons = []
        nav_items = [
            ("Обзор",          0, "overview"),
            ("Визуализатор",   1, "visualizer"),
            ("История",        2, "history"),
            ("Настройки",      3, "settings"),
            ("Прогнозирование", 4, "predict"),
            ("Логи",           5, "logs"),
        ]
        for label, idx, icon_key in nav_items:
            btn = QPushButton("  " + label)
            btn.setProperty("icon_key", icon_key)
            is_active = (idx == 0)
            btn.setObjectName("NavBtnActive" if is_active else "NavBtn")
            state = "active" if is_active else "inactive"
            icon_path = get_resource_path(os.path.join("assets", f"nav_{icon_key}_{state}.svg"))
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.switch_tab(i))
            lay.addWidget(btn)
            self.nav_buttons.append(btn)

        lay.addStretch()

        self.status_dot_lbl = QLabel("● Готов")
        self.status_dot_lbl.setObjectName("StatusDot")
        self.status_dot_lbl.setStyleSheet("color: #10B981; font-size: 11px;")
        ver_lbl = QLabel("v1.2")
        ver_lbl.setObjectName("VersionLbl")
        lay.addWidget(ver_lbl)

        return sidebar

    def _stat_card(self, caption):
        card = QFrame()
        card.setObjectName("Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(4)
        cap = QLabel(caption)
        cap.setObjectName("StatCap")
        val = QLabel("0")
        val.setObjectName("StatNum")
        cl.addWidget(cap)
        cl.addWidget(val)
        return card, val

    def _build_overview_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(460)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 16, 0, 16)
        lay.setSpacing(10)

        # ── Header ──
        hdr = QHBoxLayout()
        title = QLabel("Обзор")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        self.dash_state_badge = QLabel("Готов")
        self.dash_state_badge.setStyleSheet(
            "color: #10B981; font-size: 11px; font-weight: 800; "
            "background: rgba(16,185,129,0.15); "
            "border-radius: 4px; padding: 2px 8px;"
        )
        lay.addLayout(hdr)

        # ── Stats grid 2×2 ──
        stats_grid = QGridLayout()
        stats_grid.setSpacing(8)
        c1, self.val_total = self._stat_card("ДИКТОВОК")
        c2, self.val_lat   = self._stat_card("ЗАДЕРЖКА")
        c3, self.val_words = self._stat_card("СЛОВ")
        c4, self.val_chars = self._stat_card("СИМВОЛОВ")
        self.val_lat.setText("0.0 с")
        stats_grid.addWidget(c1, 0, 0)
        stats_grid.addWidget(c2, 0, 1)
        stats_grid.addWidget(c3, 1, 0)
        stats_grid.addWidget(c4, 1, 1)
        lay.addLayout(stats_grid)

        # ── Hotkey card ──
        hotkey_card = QFrame()
        hotkey_card.setObjectName("Card")
        hkl = QHBoxLayout(hotkey_card)
        hkl.setContentsMargins(14, 10, 14, 10)
        hkl.setSpacing(10)
        hk_text = QLabel("Горячая клавиша")
        hk_text.setObjectName("FieldLbl")
        hkl.addWidget(hk_text)
        hkl.addStretch()
        self.hotkey_badge = QLabel(self.config.get("hotkey", "ctrl+windows").upper())
        self.hotkey_badge.setObjectName("HotkeyBadge")
        hkl.addWidget(self.hotkey_badge)
        lay.addWidget(hotkey_card)

        # ── Recent dictations (Flat list) ──
        recent_title = QLabel("ПОСЛЕДНИЕ ДИКТОВКИ")
        recent_title.setObjectName("SectionCap")
        lay.addWidget(recent_title)

        self.recent_items = []
        for _ in range(3):
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

            ifl.addLayout(left, 1)
            ifl.addWidget(right)
            lay.addWidget(item_frame)
            self.recent_items.append((snippet, ts, right))

        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _build_visualizer_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(460)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 16, 0, 16)
        lay.setSpacing(10)

        # ── Header ──
        hdr = QHBoxLayout()
        title = QLabel("Визуализатор")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        lay.addLayout(hdr)

        # ── Preview card ──
        preview_card = QFrame()
        preview_card.setObjectName("Card")
        pcl = QVBoxLayout(preview_card)
        pcl.setContentsMargins(16, 10, 16, 10)
        pcl.setSpacing(6)

        preview_cap = QLabel("ПРЕДПРОСМОТР")
        preview_cap.setObjectName("SectionCap")
        pcl.addWidget(preview_cap)

        self.preview_widget = PreviewWidget()
        self.preview_widget.set_style(self.config.get("visualizer_style", "wave"))
        self.preview_widget.set_preset(self.config.get("visualizer_color_preset", "mono"))
        self.preview_widget.set_size(self.config.get("visualizer_size", "medium"))
        self.preview_widget.set_bg_mode(self.config.get("visualizer_bg_mode", "solid"))
        pcl.addWidget(self.preview_widget)
        lay.addWidget(preview_card)

        # ── Controls card ──
        ctrl = QFrame()
        ctrl.setObjectName("Card")
        cl = QVBoxLayout(ctrl)
        cl.setContentsMargins(16, 12, 16, 12)
        cl.setSpacing(10)

        def ctrl_cell(label_text, widget):
            """Vertical cell: small cap label on top, control below."""
            cell = QWidget()
            vl = QVBoxLayout(cell)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setSpacing(4)
            lbl = QLabel(label_text)
            lbl.setObjectName("SectionCap")
            vl.addWidget(lbl)
            vl.addWidget(widget)
            return cell

        self.shape_seg = SegmentedControl(["Волна", "Бары", "Скролл"])
        style_map = {"wave": 0, "bars": 1, "scroll": 2, "dots": 0, "ribbon": 0}
        self.shape_seg.setCurrentIndex(style_map.get(self.config.get("visualizer_style", "wave"), 0))
        self.shape_seg.currentChanged.connect(self._on_shape_changed)

        self.bg_seg = SegmentedControl(["Сплошной", "Без фона"])
        bg_map = {"solid": 0, "none": 1}
        self.bg_seg.setCurrentIndex(bg_map.get(self.config.get("visualizer_bg_mode", "solid"), 0))
        self.bg_seg.currentChanged.connect(self._on_bg_mode_changed)

        self.size_seg = SegmentedControl(["XS", "S", "M", "L", "XL"])
        size_map = {"xs": 0, "small": 1, "medium": 2, "large": 3, "xl": 4}
        self.size_seg.setCurrentIndex(size_map.get(self.config.get("visualizer_size", "medium"), 2))
        self.size_seg.currentChanged.connect(self._on_size_changed)

        # Row 1: Форма | Размер
        row1 = QHBoxLayout()
        row1.setSpacing(14)
        row1.addWidget(ctrl_cell("ФОРМА", self.shape_seg))
        row1.addWidget(ctrl_cell("РАЗМЕР", self.size_seg))
        cl.addLayout(row1)

        # Row 2: Фон | Чувствительность
        row2 = QHBoxLayout()
        row2.setSpacing(14)
        row2.addWidget(ctrl_cell("ФОН", self.bg_seg))

        self.sens_values = [0.7, 1.0, 1.2, 1.5, 2.0]
        self.sens_seg = SegmentedControl(["0.7", "1.0", "1.2", "1.5", "2.0"])
        saved_sens = self.config.get("visualizer_sensitivity", 1.0)
        try:
            closest_idx = min(range(len(self.sens_values)), key=lambda i: abs(self.sens_values[i] - saved_sens))
        except Exception:
            closest_idx = 1
        self.sens_seg.setCurrentIndex(closest_idx)
        self.sens_seg.currentChanged.connect(self._on_sensitivity_changed)

        row2.addWidget(ctrl_cell("ЧУВСТВИТЕЛЬНОСТЬ", self.sens_seg))
        cl.addLayout(row2)
        lay.addWidget(ctrl)

        # ── Color card ──
        color_card = QFrame()
        color_card.setObjectName("Card")
        ccl = QVBoxLayout(color_card)
        ccl.setContentsMargins(16, 10, 16, 10)
        ccl.setSpacing(6)
        
        color_cap = QLabel("ЦВЕТ")
        color_cap.setObjectName("SectionCap")
        ccl.addWidget(color_cap)
        
        self.color_selector = ColorPresetSelector()
        self.color_selector.setCurrentPreset(self.config.get("visualizer_color_preset", "mono"))
        self.color_selector.presetChanged.connect(self._on_preset_changed)
        ccl.addWidget(self.color_selector)
        lay.addWidget(color_card)

        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _on_shape_changed(self, idx):
        self.preview_widget.set_style(["wave", "bars", "scroll"][idx])
        self._auto_save_visualizer()

    def _on_bg_mode_changed(self, idx):
        self.preview_widget.set_bg_mode(["solid", "none"][idx])
        self._auto_save_visualizer()

    def _on_size_changed(self, idx):
        self.preview_widget.set_size(["xs", "small", "medium", "large", "xl"][idx])
        self._auto_save_visualizer()

    def _on_sensitivity_changed(self, idx):
        sens = self.sens_values[idx]
        self.preview_widget.set_sensitivity(sens)
        self._auto_save_visualizer()

    def _on_preset_changed(self, key):
        self.preview_widget.set_preset(key)
        self.config["visualizer_color_preset"] = key
        self.apply_theme(self.theme_name, key)
        self._auto_save_visualizer()

    def _auto_save_visualizer(self):
        """Auto-save visualizer settings without button click"""
        self.config["visualizer_style"] = ["wave", "bars", "scroll"][self.shape_seg.currentIndex()]
        self.config["visualizer_size"]  = ["xs", "small", "medium", "large", "xl"][self.size_seg.currentIndex()]
        self.config["visualizer_color_preset"] = self.color_selector.currentPreset()
        self.config["visualizer_bg_mode"] = ["solid", "none"][self.bg_seg.currentIndex()]
        self.config["theme"] = "dark"
        self.config["visualizer_sensitivity"] = self.sens_values[self.sens_seg.currentIndex()]
        self.save_callback(self.config)

    def _update_hotkey_badge(self):
        h1 = self.config.get("hotkey_1", "ctrl+windows").upper()
        if self.config.get("hotkey_2_enabled", False):
            h2 = self.config.get("hotkey_2", "shift+windows").upper()
            self.hotkey_badge.setText(f"{h1} / {h2}")
        else:
            self.hotkey_badge.setText(h1)

    def _toggle_hotkey_2_widgets(self):
        if hasattr(self, "h2_widget") and self.h2_widget:
            self.h2_widget.setVisible(self.hotkey_2_enabled_cb.isChecked())

    def _auto_save_settings(self):
        """Auto-save settings without button click"""
        self.config["api_key"]    = self.api_input.text().strip()
        
        # Save new hotkeys configuration
        self.config["hotkey_1"]   = self.hotkey_1_combo.currentText()
        # Maintain backward compatibility key for other modules
        self.config["hotkey"]     = self.hotkey_1_combo.currentText()
        
        mode_map = {"Редактор": "default", "Чат": "chat", "Английский": "translate_en", "Кастом": "custom"}
        self.config["mode_1"]     = mode_map.get(self.mode_1_combo.currentText(), "default")
        
        self.config["hotkey_2_enabled"] = self.hotkey_2_enabled_cb.isChecked()
        self.config["hotkey_2"]   = self.hotkey_2_combo.currentText()
        self.config["mode_2"]     = mode_map.get(self.mode_2_combo.currentText(), "translate_en")
        
        self.config["text_model"] = self.model_combo.currentText()
        self.config["theme"]      = "dark"
        self.config["run_on_startup"] = self.startup_toggle.isChecked()
        # Don't save base_url here - it's handled by _on_base_url_changed
        self.save_callback(self.config)
        self._update_hotkey_badge()

    def _on_base_url_changed(self):
        """Handle Base URL change with restart notification"""
        new_url = self.base_url_input.text().strip()
        old_url = self.config.get("groq_base_url", "")
        
        # Save the new URL
        self.config["groq_base_url"] = new_url
        self.save_callback(self.config)
        
        # Show restart notification if URL actually changed
        if new_url != old_url:
            reply = QMessageBox.question(
                self,
                "Требуется перезапуск",
                "Изменение URL сервера требует перезагрузки приложения для вступления в силу.\n\nПерезапустить сейчас?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Signal the main app to restart
                if hasattr(self, 'restart_requested'):
                    self.restart_requested.emit()

    def _build_history_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(460)
        inner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 24, 0, 24)
        lay.setSpacing(12)

        self.history_stack = QStackedWidget()

        # ── Page 1: History List ──
        list_page = QWidget()
        list_lay = QVBoxLayout(list_page)
        list_lay.setContentsMargins(0, 0, 0, 0)
        list_lay.setSpacing(10)

        hdr = QHBoxLayout()
        title = QLabel("История")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        self.btn_clear_history = QPushButton("Очистить")
        self.btn_clear_history.setObjectName("SecondaryBtn")
        self.btn_clear_history.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_clear_history.clicked.connect(self.clear_all_history)
        hdr.addWidget(self.btn_clear_history)
        list_lay.addLayout(hdr)

        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Поиск...")
        self.history_search.textChanged.connect(self.filter_history)
        list_lay.addWidget(self.history_search)

        # Scroll area with card list — no visible scrollbar
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.history_scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.history_cards_widget = QWidget()
        self.history_cards_widget.setObjectName("HistoryCardsWidget")
        self.history_cards_layout = QVBoxLayout(self.history_cards_widget)
        self.history_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.history_cards_layout.setSpacing(6)
        self.history_cards_layout.addStretch()

        self.history_scroll.setWidget(self.history_cards_widget)
        list_lay.addWidget(self.history_scroll, 1)

        self.history_stack.addWidget(list_page)

        # ── Page 2: Detail View ──
        detail_page = QWidget()
        detail_lay = QVBoxLayout(detail_page)
        detail_lay.setContentsMargins(0, 0, 0, 0)
        detail_lay.setSpacing(10)

        back_hdr = QHBoxLayout()
        self.btn_back_to_list = QPushButton("← Назад")
        self.btn_back_to_list.setObjectName("SecondaryBtn")
        self.btn_back_to_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back_to_list.setFixedWidth(100)
        self.btn_back_to_list.clicked.connect(self.hide_history_detail)
        back_hdr.addWidget(self.btn_back_to_list)
        back_hdr.addStretch()
        detail_lay.addLayout(back_hdr)

        self.detail_meta = QLabel()
        self.detail_meta.setObjectName("DetailMeta")
        detail_lay.addWidget(self.detail_meta)

        self.lbl_raw = QLabel("WHISPER")
        self.lbl_raw.setObjectName("DetailLbl")
        self.txt_raw = QPlainTextEdit()
        self.txt_raw.setReadOnly(True)
        detail_lay.addWidget(self.lbl_raw)
        detail_lay.addWidget(self.txt_raw)

        self.lbl_clean = QLabel("LLM")
        self.lbl_clean.setObjectName("DetailLbl")
        self.txt_clean = QPlainTextEdit()
        self.txt_clean.setReadOnly(True)
        detail_lay.addWidget(self.lbl_clean)
        detail_lay.addWidget(self.txt_clean)

        copy_lay = QHBoxLayout()
        copy_lay.setSpacing(8)
        self.btn_copy_raw = QPushButton("Копировать сырой")
        self.btn_copy_raw.setObjectName("SecondaryBtn")
        self.btn_copy_raw.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_raw.clicked.connect(self.copy_raw_text)
        self.btn_copy_clean = QPushButton("Копировать готовый")
        self.btn_copy_clean.setObjectName("PrimaryBtn")
        self.btn_copy_clean.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_clean.clicked.connect(self.copy_clean_text)
        copy_lay.addWidget(self.btn_copy_raw, 1)
        copy_lay.addWidget(self.btn_copy_clean, 1)
        detail_lay.addLayout(copy_lay)

        self.history_stack.addWidget(detail_page)

        lay.addWidget(self.history_stack)

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _build_settings_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(440)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 24, 0, 24)
        lay.setSpacing(12)

        title = QLabel("Настройки")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        def setting_cell(label_text, widget):
            """Vertical cell: small cap label on top, control below — matches visualizer style."""
            cell = QWidget()
            vl = QVBoxLayout(cell)
            vl.setContentsMargins(0, 0, 0, 0)
            vl.setSpacing(6)
            lbl = QLabel(label_text)
            lbl.setObjectName("SectionCap")
            vl.addWidget(lbl)
            vl.addWidget(widget)
            return cell

        # ── API card ──
        api_card = QFrame()
        api_card.setObjectName("Card")
        acl = QVBoxLayout(api_card)
        acl.setContentsMargins(16, 14, 16, 14)
        acl.setSpacing(10)

        api_cap = QLabel("API")
        api_cap.setObjectName("SectionCap")
        acl.addWidget(api_cap)

        self.api_input = QLineEdit()
        self.api_input.setText(self.config.get("api_key", ""))
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setPlaceholderText("gsk_...")
        self.api_input.editingFinished.connect(self._auto_save_settings)

        self.btn_toggle_api = QPushButton("Показать")
        self.btn_toggle_api.setObjectName("SecondaryBtn")
        self.btn_toggle_api.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_api.clicked.connect(self.toggle_api_visibility)

        api_input_row = QHBoxLayout()
        api_input_row.setSpacing(8)
        api_input_row.addWidget(self.api_input, 1)
        api_input_row.addWidget(self.btn_toggle_api)

        acl.addLayout(api_input_row)

        # Groq Base URL input (for Cloudflare Workers proxy)
        self.base_url_input = QLineEdit()
        self.base_url_input.setText(self.config.get("groq_base_url", ""))
        self.base_url_input.setPlaceholderText("https://your-worker.your-subdomain.workers.dev (without /openai/v1)")
        self.base_url_input.editingFinished.connect(self._on_base_url_changed)

        acl.addWidget(self.base_url_input)
        lay.addWidget(api_card)

        # ── Input + Model card ──
        input_card = QFrame()
        input_card.setObjectName("Card")
        icl = QVBoxLayout(input_card)
        icl.setContentsMargins(16, 14, 16, 14)
        icl.setSpacing(14)

        # Hotkey 1
        h1_layout = QHBoxLayout()
        h1_layout.setSpacing(10)
        
        self.hotkey_1_combo = QComboBox()
        self.hotkey_1_combo.addItems(["ctrl+windows", "shift+windows", "ctrl+shift+windows", "left alt+space", "f8"])
        self.hotkey_1_combo.setCurrentText(self.config.get("hotkey_1", "ctrl+windows"))
        self.hotkey_1_combo.currentTextChanged.connect(self._auto_save_settings)
        
        self.mode_1_combo = QComboBox()
        self.mode_1_combo.addItems(["Редактор", "Чат", "Английский", "Кастом"])
        mode_map = {"default": "Редактор", "chat": "Чат", "translate_en": "Английский", "custom": "Кастом"}
        current_mode_1 = self.config.get("mode_1", "default")
        self.mode_1_combo.setCurrentText(mode_map.get(current_mode_1, "Редактор"))
        self.mode_1_combo.currentTextChanged.connect(self._auto_save_settings)
        
        h1_layout.addWidget(setting_cell("СОЧЕТАНИЕ КЛАВИШ 1", self.hotkey_1_combo), 2)
        h1_layout.addWidget(setting_cell("РЕЖИМ 1", self.mode_1_combo), 1)
        icl.addLayout(h1_layout)
        
        # Hotkey 2 toggle row — same style as other setting toggles
        self.hotkey_2_enabled_cb = ToggleSwitch(checked=self.config.get("hotkey_2_enabled", False))
        self.hotkey_2_enabled_cb.toggled.connect(self._auto_save_settings)
        self.hotkey_2_enabled_cb.toggled.connect(self._toggle_hotkey_2_widgets)

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
        h2_toggle_row.addWidget(self.hotkey_2_enabled_cb)
        icl.addLayout(h2_toggle_row)
        
        # Hotkey 2 Panel
        self.h2_widget = QWidget()
        h2_layout = QHBoxLayout(self.h2_widget)
        h2_layout.setContentsMargins(0, 0, 0, 0)
        h2_layout.setSpacing(10)
        
        self.hotkey_2_combo = QComboBox()
        self.hotkey_2_combo.addItems(["shift+windows", "ctrl+windows", "ctrl+shift+windows", "left alt+space", "f8"])
        self.hotkey_2_combo.setCurrentText(self.config.get("hotkey_2", "shift+windows"))
        self.hotkey_2_combo.currentTextChanged.connect(self._auto_save_settings)
        
        self.mode_2_combo = QComboBox()
        self.mode_2_combo.addItems(["Редактор", "Чат", "Английский", "Кастом"])
        current_mode_2 = self.config.get("mode_2", "translate_en")
        self.mode_2_combo.setCurrentText(mode_map.get(current_mode_2, "Английский"))
        self.mode_2_combo.currentTextChanged.connect(self._auto_save_settings)
        
        h2_layout.addWidget(setting_cell("СОЧЕТАНИЕ КЛАВИШ 2", self.hotkey_2_combo), 2)
        h2_layout.addWidget(setting_cell("РЕЖИМ 2", self.mode_2_combo), 1)
        icl.addWidget(self.h2_widget)
        
        # Initial visibility toggle
        self.h2_widget.setVisible(self.hotkey_2_enabled_cb.isChecked())

        self.model_combo = QComboBox()
        self.model_combo.addItems([
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen/qwen3-32b",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
        ])
        self.model_combo.setCurrentText(self.config.get("text_model", "llama-3.3-70b-versatile"))
        self.model_combo.currentTextChanged.connect(self._auto_save_settings)

        icl.addWidget(setting_cell("ТЕКСТОВАЯ МОДЕЛЬ", self.model_combo))
        lay.addWidget(input_card)

        # ── System card ──
        sys_card = QFrame()
        sys_card.setObjectName("Card")
        scl = QVBoxLayout(sys_card)
        scl.setContentsMargins(16, 14, 16, 14)
        scl.setSpacing(0)

        self.startup_toggle = ToggleSwitch(checked=self.config.get("run_on_startup", False))
        self.startup_toggle.toggled.connect(self._auto_save_settings)

        toggle_row_layout = QHBoxLayout()
        toggle_row_layout.setSpacing(12)
        toggle_lbl_block = QVBoxLayout()
        toggle_lbl_block.setSpacing(2)
        toggle_title = QLabel("Автозапуск")
        toggle_title.setObjectName("FieldLbl")
        toggle_sub = QLabel("Запускать PITCH при входе в систему")
        toggle_sub.setObjectName("DetailMeta")
        toggle_lbl_block.addWidget(toggle_title)
        toggle_lbl_block.addWidget(toggle_sub)
        toggle_row_layout.addLayout(toggle_lbl_block, 1)
        toggle_row_layout.addWidget(self.startup_toggle)
        scl.addLayout(toggle_row_layout)
        lay.addWidget(sys_card)

        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _build_recognition_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        # Create QScrollArea with hidden scrollbars
        self.recognition_scroll = QScrollArea()
        self.recognition_scroll.setWidgetResizable(True)
        self.recognition_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recognition_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recognition_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.recognition_scroll.setFixedWidth(460)
        self.recognition_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.recognition_inner = QWidget()
        self.recognition_inner.setObjectName("RecognitionInnerWidget")
        self.recognition_inner.setStyleSheet("QWidget#RecognitionInnerWidget { background: transparent; }")
        lay = QVBoxLayout(self.recognition_inner)
        lay.setContentsMargins(10, 20, 10, 20)
        lay.setSpacing(10)

        title = QLabel("Распознавание")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        def toggle_row(parent_layout, title_text, sub_text, toggle_widget):
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

        # ── Whisper card ──
        whisper_card = QFrame()
        whisper_card.setObjectName("Card")
        wcl = QVBoxLayout(whisper_card)
        wcl.setContentsMargins(16, 14, 16, 14)
        wcl.setSpacing(14)

        whisper_cap = QLabel("WHISPER")
        whisper_cap.setObjectName("SectionCap")
        wcl.addWidget(whisper_cap)

        self.raw_whisper_toggle = ToggleSwitch(checked=self.config.get("use_raw_whisper", False))
        self.raw_whisper_toggle.toggled.connect(self._auto_save_recognition)
        toggle_row(wcl, "Сырой Whisper",
                   "Быстрее, но без улучшения качества LLM",
                   self.raw_whisper_toggle)

        lay.addWidget(whisper_card)

        # ── Фильтрация card ──
        filter_card = QFrame()
        filter_card.setObjectName("Card")
        fcl = QVBoxLayout(filter_card)
        fcl.setContentsMargins(16, 14, 16, 14)
        fcl.setSpacing(14)

        filter_cap = QLabel("ФИЛЬТРАЦИЯ")
        filter_cap.setObjectName("SectionCap")
        fcl.addWidget(filter_cap)

        self.hallucination_filter_toggle = ToggleSwitch(
            checked=self.config.get("filter_hallucinations", True)
        )
        self.hallucination_filter_toggle.toggled.connect(self._auto_save_recognition)
        toggle_row(fcl, "Фильтр галлюцинаций",
                   "Блокировать «Продолжение следует…» и похожие",
                   self.hallucination_filter_toggle)

        self.min_duration_seg = SegmentedControl(["0.3с", "0.5с", "1с", "Выкл"])
        dur_map = {0.3: 0, 0.5: 1, 1.0: 2, 0.0: 3}
        saved_dur = self.config.get("min_recording_duration", 0.5)
        self.min_duration_seg.setCurrentIndex(dur_map.get(saved_dur, 1))
        self.min_duration_seg.currentChanged.connect(self._auto_save_recognition)

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
        dur_vl.addWidget(self.min_duration_seg)
        fcl.addWidget(dur_cell)

        lay.addWidget(filter_card)

        # ── Стиль форматирования card ──
        style_card = QFrame()
        style_card.setObjectName("Card")
        scl = QVBoxLayout(style_card)
        scl.setContentsMargins(16, 14, 16, 14)
        scl.setSpacing(10)
        
        style_cap = QLabel("СТИЛЬ ФОРМАТИРОВАНИЯ")
        style_cap.setObjectName("SectionCap")
        scl.addWidget(style_cap)
        
        # Grid of buttons for selecting style
        buttons_widget = QWidget()
        buttons_lay = QGridLayout(buttons_widget)
        buttons_lay.setContentsMargins(0, 0, 0, 0)
        buttons_lay.setSpacing(6)
        
        self.style_buttons = {}
        styles_info = [
            ("Редактор", "default", 0, 0),
            ("Чат", "chat", 0, 1),
            ("Английский", "translate_en", 1, 0),
            ("Кастом", "custom", 1, 1),
        ]
        
        for name, key, r, c in styles_info:
            btn = QPushButton(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.clicked.connect(lambda _, k=key: self._select_style(k))
            buttons_lay.addWidget(btn, r, c)
            self.style_buttons[key] = btn
            
        scl.addWidget(buttons_widget)
        
        # Style details info card (SubCard)
        self.style_info_card = QFrame()
        self.style_info_card.setObjectName("SubCard")
        sil = QVBoxLayout(self.style_info_card)
        sil.setContentsMargins(12, 10, 12, 10)
        sil.setSpacing(6)
        
        self.style_desc_lbl = QLabel()
        self.style_desc_lbl.setWordWrap(True)
        self.style_desc_lbl.setStyleSheet("font-size: 11px; color: #8A8A8A;")
        
        self.style_example_lbl = QLabel()
        self.style_example_lbl.setWordWrap(True)
        self.style_example_lbl.setStyleSheet("font-size: 12px; font-weight: 500;")
        
        sil.addWidget(self.style_desc_lbl)
        sil.addWidget(self.style_example_lbl)
        scl.addWidget(self.style_info_card)
        
        # Custom instructions field
        self.custom_style_label = QLabel("ИНСТРУКЦИЯ ДЛЯ КАСТОМНОГО СТИЛЯ:")
        self.custom_style_label.setObjectName("SectionCap")
        scl.addWidget(self.custom_style_label)
        
        self.custom_style_edit = QPlainTextEdit()
        self.custom_style_edit.setPlaceholderText("Например: Переведи текст на английский язык или Перепиши текст в деловом стиле.")
        self.custom_style_edit.setFixedHeight(120)
        self.custom_style_edit.setPlainText(self.config.get("custom_formatting_style", ""))
        self.custom_style_edit.textChanged.connect(self._auto_save_recognition)
        scl.addWidget(self.custom_style_edit)
        
        saved_style = self.config.get("formatting_style", "default")
        self._update_style_ui(saved_style)
        
        lay.addWidget(style_card)
        lay.addStretch()

        self.recognition_scroll.setWidget(self.recognition_inner)

        outer.addStretch()
        outer.addWidget(self.recognition_scroll)
        outer.addStretch()
        self.stack.addWidget(page)

    def _select_style(self, key):
        self.config["formatting_style"] = key
        self._update_style_ui(key)
        self._auto_save_recognition()

    def _update_style_ui(self, key):
        active_style = (
            "background: rgba(223,206,186,0.18); border: 1px solid rgba(245,236,227,0.50); "
            "color: #F5ECE3; font-weight: 700; border-radius: 8px;"
        )
        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _build_recognition_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        # Create QScrollArea with hidden scrollbars
        self.recognition_scroll = QScrollArea()
        self.recognition_scroll.setWidgetResizable(True)
        self.recognition_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recognition_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.recognition_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.recognition_scroll.setFixedWidth(460)
        self.recognition_scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self.recognition_inner = QWidget()
        self.recognition_inner.setObjectName("RecognitionInnerWidget")
        self.recognition_inner.setStyleSheet("QWidget#RecognitionInnerWidget { background: transparent; }")
        lay = QVBoxLayout(self.recognition_inner)
        lay.setContentsMargins(10, 20, 10, 20)
        lay.setSpacing(10)

        title = QLabel("Распознавание")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        def toggle_row(parent_layout, title_text, sub_text, toggle_widget):
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

        # ── Whisper card ──
        whisper_card = QFrame()
        whisper_card.setObjectName("Card")
        wcl = QVBoxLayout(whisper_card)
        wcl.setContentsMargins(16, 14, 16, 14)
        wcl.setSpacing(14)

        whisper_cap = QLabel("WHISPER")
        whisper_cap.setObjectName("SectionCap")
        wcl.addWidget(whisper_cap)

        self.raw_whisper_toggle = ToggleSwitch(checked=self.config.get("use_raw_whisper", False))
        self.raw_whisper_toggle.toggled.connect(self._auto_save_recognition)
        toggle_row(wcl, "Сырой Whisper",
                   "Быстрее, но без улучшения качества LLM",
                   self.raw_whisper_toggle)

        lay.addWidget(whisper_card)

        # ── Фильтрация card ──
        filter_card = QFrame()
        filter_card.setObjectName("Card")
        fcl = QVBoxLayout(filter_card)
        fcl.setContentsMargins(16, 14, 16, 14)
        fcl.setSpacing(14)

        filter_cap = QLabel("ФИЛЬТРАЦИЯ")
        filter_cap.setObjectName("SectionCap")
        fcl.addWidget(filter_cap)

        self.hallucination_filter_toggle = ToggleSwitch(
            checked=self.config.get("filter_hallucinations", True)
        )
        self.hallucination_filter_toggle.toggled.connect(self._auto_save_recognition)
        toggle_row(fcl, "Фильтр галлюцинаций",
                   "Блокировать «Продолжение следует…» и похожие",
                   self.hallucination_filter_toggle)

        self.min_duration_seg = SegmentedControl(["0.3с", "0.5с", "1с", "Выкл"])
        dur_map = {0.3: 0, 0.5: 1, 1.0: 2, 0.0: 3}
        saved_dur = self.config.get("min_recording_duration", 0.5)
        self.min_duration_seg.setCurrentIndex(dur_map.get(saved_dur, 1))
        self.min_duration_seg.currentChanged.connect(self._auto_save_recognition)

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
        dur_vl.addWidget(self.min_duration_seg)
        fcl.addWidget(dur_cell)

        lay.addWidget(filter_card)

        # ── Стиль форматирования card ──
        style_card = QFrame()
        style_card.setObjectName("Card")
        scl = QVBoxLayout(style_card)
        scl.setContentsMargins(16, 14, 16, 14)
        scl.setSpacing(10)
        
        style_cap = QLabel("СТИЛЬ ФОРМАТИРОВАНИЯ")
        style_cap.setObjectName("SectionCap")
        scl.addWidget(style_cap)
        
        # Grid of buttons for selecting style
        buttons_widget = QWidget()
        buttons_lay = QGridLayout(buttons_widget)
        buttons_lay.setContentsMargins(0, 0, 0, 0)
        buttons_lay.setSpacing(6)
        
        self.style_buttons = {}
        styles_info = [
            ("Редактор", "default", 0, 0),
            ("Чат", "chat", 0, 1),
            ("Английский", "translate_en", 1, 0),
            ("Кастом", "custom", 1, 1),
        ]
        
        for name, key, r, c in styles_info:
            btn = QPushButton(name)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(30)
            btn.clicked.connect(lambda _, k=key: self._select_style(k))
            buttons_lay.addWidget(btn, r, c)
            self.style_buttons[key] = btn
            
        scl.addWidget(buttons_widget)
        
        # Style details info card (SubCard)
        self.style_info_card = QFrame()
        self.style_info_card.setObjectName("SubCard")
        sil = QVBoxLayout(self.style_info_card)
        sil.setContentsMargins(12, 10, 12, 10)
        sil.setSpacing(6)
        
        self.style_desc_lbl = QLabel()
        self.style_desc_lbl.setWordWrap(True)
        self.style_desc_lbl.setStyleSheet("font-size: 11px; color: #8A8A8A;")
        
        self.style_example_lbl = QLabel()
        self.style_example_lbl.setWordWrap(True)
        self.style_example_lbl.setStyleSheet("font-size: 12px; font-weight: 500;")
        
        sil.addWidget(self.style_desc_lbl)
        sil.addWidget(self.style_example_lbl)
        scl.addWidget(self.style_info_card)
        
        # Custom instructions field
        self.custom_style_label = QLabel("ИНСТРУКЦИЯ ДЛЯ КАСТОМНОГО СТИЛЯ:")
        self.custom_style_label.setObjectName("SectionCap")
        scl.addWidget(self.custom_style_label)
        
        self.custom_style_edit = QPlainTextEdit()
        self.custom_style_edit.setPlaceholderText("Например: Переведи текст на английский язык или Перепиши текст в деловом стиле.")
        self.custom_style_edit.setFixedHeight(120)
        self.custom_style_edit.setPlainText(self.config.get("custom_formatting_style", ""))
        self.custom_style_edit.textChanged.connect(self._auto_save_recognition)
        scl.addWidget(self.custom_style_edit)
        
        saved_style = self.config.get("formatting_style", "default")
        self._update_style_ui(saved_style)
        
        lay.addWidget(style_card)
        lay.addStretch()

        self.recognition_scroll.setWidget(self.recognition_inner)

        outer.addStretch()
        outer.addWidget(self.recognition_scroll)
        outer.addStretch()
        self.stack.addWidget(page)

    def _select_style(self, key):
        self.config["formatting_style"] = key
        self._update_style_ui(key)
        self._auto_save_recognition()

    def _update_style_ui(self, key):
        active_style = (
            "background: rgba(223,206,186,0.18); border: 1px solid rgba(245,236,227,0.50); "
            "color: #F5ECE3; font-weight: 700; border-radius: 8px;"
        )
        idle_style = (
            "background: #4E382B; border: 1px solid #7D6454; "
            "color: #D4C5B9; font-weight: 500; border-radius: 8px;"
        )
            
        for k, btn in self.style_buttons.items():
            if k == key:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(idle_style)

        info = STYLE_DETAILS.get(key, STYLE_DETAILS["default"])
        self.style_desc_lbl.setText(info["desc"])
        self.style_example_lbl.setText(info["example"])

        is_custom = key == "custom"
        self.custom_style_label.setVisible(is_custom)
        self.custom_style_edit.setVisible(is_custom)

    def _auto_save_recognition(self):
        """Auto-save recognition settings."""
        self.config["use_raw_whisper"] = self.raw_whisper_toggle.isChecked()
        self.config["filter_hallucinations"] = self.hallucination_filter_toggle.isChecked()
        dur_values = [0.3, 0.5, 1.0, 0.0]
        self.config["min_recording_duration"] = dur_values[self.min_duration_seg.currentIndex()]
        self.config["custom_formatting_style"] = self.custom_style_edit.toPlainText().strip()
        self.save_callback(self.config)

    def _build_logs_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(440)
        inner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 24, 0, 24)
        lay.setSpacing(12)

        hdr = QHBoxLayout()
        title = QLabel("Логи")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        btn_clear = QPushButton("Очистить")
        btn_clear.setObjectName("SecondaryBtn")
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.clicked.connect(self.clear_logs)
        hdr.addWidget(btn_clear)
        lay.addLayout(hdr)

        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setObjectName("LogConsole")
        lay.addWidget(self.log_area, 1)

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def apply_theme(self, theme, preset=None):
        self.theme_name = theme
        if preset is None:
            preset = self.config.get("visualizer_color_preset", "mono")
        self.setStyleSheet(get_stylesheet(theme, preset))

        icon_name = "p.jpeg"
        icon_path = os.path.join(os.path.dirname(__file__), "..", "assets", icon_name)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.startup_toggle.set_theme(theme)
        self.hotkey_2_enabled_cb.set_theme(theme)
        self.raw_whisper_toggle.set_theme(theme)
        self.hallucination_filter_toggle.set_theme(theme)
        self.min_duration_seg.set_theme(theme)
        self.shape_seg.set_theme(theme)
        self.size_seg.set_theme(theme)
        self.bg_seg.set_theme(theme)
        self.color_selector.set_theme(theme)
        self.preview_widget.set_theme(theme)

        for btn in self.nav_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if hasattr(self, 'style_buttons'):
            self._update_style_ui(self.config.get("formatting_style", "default"))

    def set_system_state(self, state):
        states = {
            "idle":       ("#10B981", "rgba(16,185,129,0.12)",  "rgba(16,185,129,0.30)",  "● Готов"),
            "recording":  ("#38BDF8", "rgba(56,189,248,0.12)",  "rgba(56,189,248,0.30)",  "● Запись"),
            "processing": ("#A78BFA", "rgba(167,139,250,0.12)", "rgba(167,139,250,0.30)", "● Обработка"),
        }
        color, bg, bdr, text = states.get(state, states["idle"])
        badge_style = (
            f"color: {color}; font-size: 12px; font-weight: 700; "
            f"background: {bg}; border: 1px solid {bdr}; "
            f"border-radius: 6px; padding: 3px 10px;"
        )
        self.status_dot_lbl.setText(text)
        self.status_dot_lbl.setStyleSheet(f"color: {color}; font-size: 11px;")
        self.dash_state_badge.setText(text)
        self.dash_state_badge.setStyleSheet(badge_style)

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            is_active = (i == index)
            btn.setObjectName("NavBtnActive" if is_active else "NavBtn")
            icon_key = btn.property("icon_key")
            if icon_key:
                state = "active" if is_active else "inactive"
                icon_path = get_resource_path(os.path.join("assets", f"nav_{icon_key}_{state}.svg"))
                if os.path.exists(icon_path):
                    btn.setIcon(QIcon(icon_path))
                    btn.setIconSize(QSize(18, 18))
        self.apply_theme(self.theme_name)
        if index == 0: self.update_statistics()
        elif index == 2: self.load_history()
        elif index == 5: self.load_logs()

    def load_logs(self):
        log_path = "echo.log"
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8") as f:
                    self.log_area.setPlainText("".join(f.readlines()[-150:]))
                    self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())
            except Exception as e:
                self.log_area.setPlainText(f"Ошибка: {e}")
        else:
            self.log_area.setPlainText("Лог пуст.")

    def append_log(self, text):
        self.log_area.appendPlainText(text)
        self.log_area.verticalScrollBar().setValue(self.log_area.verticalScrollBar().maximum())

    def clear_logs(self):
        log_path = "echo.log"
        if os.path.exists(log_path):
            try: open(log_path, "w", encoding="utf-8").close()
            except Exception: pass
        self.log_area.clear()

    def load_history(self):
        self.history_entries = history_manager.load_history()
        self.filter_history()

    def filter_history(self):
        query = self.history_search.text().lower()
        while self.history_cards_layout.count() > 1:
            item = self.history_cards_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for idx, entry in enumerate(self.history_entries):
            raw, clean = entry.get("raw_text", ""), entry.get("cleaned_text", "")
            if query and query not in raw.lower() and query not in clean.lower(): continue
            text = clean or raw
            snippet = (text[:80].replace("\n", " ") + "…") if len(text) > 80 else text[:80].replace("\n", " ")
            time_str, date_str = entry.get("timestamp", "").split()[-1][:5], entry.get("timestamp", "").split()[0]
            lat_str, words = f"{entry.get('total_latency', 0):.1f}с", entry.get("word_count", 0)
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
            pal = snip_lbl.palette()
            pal.setColor(QPalette.ColorRole.WindowText, QColor("#F1F3F7" if self.theme_name == "dark" else "#0D0D0D"))
            snip_lbl.setPalette(pal)
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
            card.mousePressEvent = lambda e, i=idx: self._open_history_entry(i)
            self.history_cards_layout.insertWidget(self.history_cards_layout.count() - 1, card)

    def _open_history_entry(self, idx):
        if idx is not None and idx < len(self.history_entries):
            e = self.history_entries[idx]
            self.txt_raw.setPlainText(e.get("raw_text", ""))
            self.txt_clean.setPlainText(e.get("cleaned_text", ""))
            self.detail_meta.setText(f"{e.get('timestamp','')}  ·  {e.get('total_latency',0):.1f}с  ·  {e.get('model','')}")
            self.history_stack.setCurrentIndex(1)

    def hide_history_detail(self): self.history_stack.setCurrentIndex(0)
    def copy_raw_text(self): QApplication.clipboard().setText(self.txt_raw.toPlainText())
    def copy_clean_text(self): QApplication.clipboard().setText(self.txt_clean.toPlainText())
    def clear_all_history(self):
        history_manager.clear_history()
        self.load_history()
        self.update_statistics()

    def update_statistics(self):
        stats = history_manager.get_statistics()
        self.val_total.setText(str(stats["total_dictations"]))
        self.val_lat.setText(f"{stats['avg_total_latency']:.1f} с")
        self.val_words.setText(str(stats["total_words"]))
        self.val_chars.setText(str(stats["total_chars"]))
        self._update_hotkey_badge()
        entries = history_manager.load_history()[:3]
        for i, (snippet_lbl, ts_lbl, right_lbl) in enumerate(self.recent_items):
            if i < len(entries):
                e = entries[i]
                text = e.get("cleaned_text") or e.get("raw_text", "")
                short = (text[:55].replace("\n", " ") + "…") if len(text) > 55 else text[:55].replace("\n", " ")
                snippet_lbl.setText(short if short else "—")
                ts_lbl.setText(e.get("timestamp", "").split()[-1][:5])
                right_lbl.setText(f"{e.get('total_latency', 0):.1f}с")
            else:
                snippet_lbl.setText("—")
                ts_lbl.setText("")
                right_lbl.setText("")

    def toggle_api_visibility(self):
        if self.api_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_api.setText("Скрыть")
        else:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_api.setText("Показать")

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            self.hide()

    def showEvent(self, event):
        super().showEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        rect.adjust(0.5, 0.5, -0.5, -0.5)
        painter.setBrush(QBrush(QColor("#DFCEBA")))
        painter.setPen(QPen(QColor("#7D6454"), 1.0))
        painter.drawRoundedRect(rect, 20.0, 20.0)
        painter.end()

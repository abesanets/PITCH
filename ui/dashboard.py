"""Dashboard window for VoiceAssistant"""
import os
import sys
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QComboBox,
                             QStackedWidget, QPlainTextEdit, QFrame, QApplication,
                             QListWidget, QListWidgetItem, QGridLayout,
                             QSizePolicy, QScrollArea, QSlider, QColorDialog,
                             QDialog)
from PyQt6.QtCore import (Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve,
                           pyqtProperty, pyqtSignal, QPointF, QPoint)
from PyQt6.QtGui import (QPainter, QColor, QPen, QBrush, QFont, QIcon, QPixmap,
                          QCursor, QPainterPath, QLinearGradient)

import history_manager
from .styles import get_stylesheet
from .styles_data import ACCENT_PRESETS
from .widgets import ToggleSwitch, SegmentedControl, ColorPresetSelector
from .visualizer import PreviewWidget, OverlayWindow


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
        self.setFixedHeight(36)
        self._win = parent_window

        lay = QHBoxLayout(self)
        lay.setContentsMargins(12, 0, 0, 0)
        lay.setSpacing(0)

        # Title label
        self._title = QLabel("Echo")
        self._title.setObjectName("TitleBarLabel")
        lay.addWidget(self._title)
        lay.addStretch()

        # Minimize button
        self._btn_min = QPushButton("─")
        self._btn_min.setObjectName("TitleBtn")
        self._btn_min.setFixedSize(46, 36)
        self._btn_min.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_min.clicked.connect(parent_window.showMinimized)
        lay.addWidget(self._btn_min)

        # Close button
        self._btn_close = QPushButton("✕")
        self._btn_close.setObjectName("TitleBtnClose")
        self._btn_close.setFixedSize(46, 36)
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
    def __init__(self, config, save_callback):
        super().__init__()
        self.setObjectName("DashboardWindow")
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
        self.setWindowTitle("Echo")
        self.setFixedSize(700, 500)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Main vertical layout: title bar + content
        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(0, 0, 0, 0)
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

        self.stack = QStackedWidget()
        root.addWidget(self.stack)

        main_vbox.addWidget(content)

        self._build_overview_tab()
        self._build_visualizer_tab()
        self._build_history_tab()
        self._build_settings_tab()
        self._build_logs_tab()

        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Drag state
        self._dragging = False
        self._drag_pos = QPoint()

    def _build_sidebar(self):
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(200)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(14, 20, 14, 16)
        lay.setSpacing(2)

        name_lbl = QLabel("Echo")
        name_lbl.setObjectName("AppName")

        # Icon next to the title
        icon_path = os.path.join(os.path.dirname(__file__), "..", "icon_small.png")
        if os.path.exists(icon_path):
            title_row = QHBoxLayout()
            title_row.setSpacing(8)
            icon_lbl = QLabel()
            icon_lbl.setObjectName("SidebarIcon")
            icon_pix = QPixmap(icon_path).scaled(24, 24,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation)
            icon_lbl.setPixmap(icon_pix)
            title_row.addWidget(icon_lbl)
            title_row.addWidget(name_lbl)
            title_row.addStretch()
            lay.addLayout(title_row)
        else:
            lay.addWidget(name_lbl)
        lay.addSpacing(16)

        self.nav_buttons = []
        nav_items = [
            ("Обзор",        0),
            ("Визуализатор", 1),
            ("История",      2),
            ("Настройки",    3),
            ("Логи",         4),
        ]
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setObjectName("NavBtnActive" if idx == 0 else "NavBtn")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.switch_tab(i))
            lay.addWidget(btn)
            self.nav_buttons.append(btn)

        lay.addStretch()

        self.status_dot_lbl = QLabel("● Готов")
        self.status_dot_lbl.setObjectName("StatusDot")
        self.status_dot_lbl.setStyleSheet("color: #10B981; font-size: 11px;")
        ver_lbl = QLabel("v1.0")
        ver_lbl.setObjectName("VersionLbl")
        lay.addWidget(self.status_dot_lbl)
        lay.addWidget(ver_lbl)

        return sidebar

    def _stat_card(self, caption):
        card = QFrame()
        card.setObjectName("Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 10, 12, 10)
        cl.setSpacing(3)
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
        inner.setFixedWidth(400)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)

        hdr = QHBoxLayout()
        title = QLabel("Обзор")
        title.setObjectName("PageTitle")
        hdr.addWidget(title)
        hdr.addStretch()
        self.dash_state_badge = QLabel("● Ожидание")
        self.dash_state_badge.setStyleSheet("color: #10B981; font-size: 12px; font-weight: 600;")
        hdr.addWidget(self.dash_state_badge)
        lay.addLayout(hdr)

        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)
        c1, self.val_total = self._stat_card("ДИКТОВОК")
        c2, self.val_lat   = self._stat_card("ЗАДЕРЖКА")
        c3, self.val_words = self._stat_card("СЛОВ")
        self.val_lat.setText("0.0 с")
        stats_row.addWidget(c1)
        stats_row.addWidget(c2)
        stats_row.addWidget(c3)
        lay.addLayout(stats_row)

        hint = QFrame()
        hint.setObjectName("Card")
        hl = QVBoxLayout(hint)
        hl.setContentsMargins(14, 12, 14, 12)
        hl.setSpacing(3)
        ht = QLabel("Как использовать")
        ht.setStyleSheet("font-weight: 600; font-size: 13px;")
        hd = QLabel("Удерживайте Ctrl + Win, говорите, отпустите — текст вставится в активное поле.")
        hd.setWordWrap(True)
        hd.setStyleSheet("font-size: 12px;")
        hl.addWidget(ht)
        hl.addWidget(hd)
        lay.addWidget(hint)
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
        inner.setFixedWidth(400)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)

        title = QLabel("Визуализатор")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        preview_frame = QFrame()
        preview_frame.setObjectName("PreviewFrame")
        pfl = QVBoxLayout(preview_frame)
        pfl.setContentsMargins(0, 0, 0, 0)
        self.preview_widget = PreviewWidget()
        self.preview_widget.set_style(self.config.get("visualizer_style", "wave"))
        self.preview_widget.set_preset(self.config.get("visualizer_color_preset", "mono"))
        self.preview_widget.set_size(self.config.get("visualizer_size", "medium"))
        pfl.addWidget(self.preview_widget)
        lay.addWidget(preview_frame)

        ctrl = QFrame()
        ctrl.setObjectName("Card")
        cl = QVBoxLayout(ctrl)
        cl.setContentsMargins(14, 12, 14, 12)
        cl.setSpacing(10)

        def row(label, widget):
            r = QHBoxLayout()
            r.setSpacing(12)
            lbl = QLabel(label)
            lbl.setObjectName("FieldLbl")
            lbl.setFixedWidth(56)
            r.addWidget(lbl)
            r.addWidget(widget)
            r.addStretch()
            return r

        self.shape_seg = SegmentedControl(["Волна", "Бары", "Скролл"])
        style_map = {"wave": 0, "bars": 1, "scroll": 2, "dots": 0, "ribbon": 0}
        self.shape_seg.setCurrentIndex(style_map.get(self.config.get("visualizer_style", "wave"), 0))
        self.shape_seg.currentChanged.connect(self._on_shape_changed)
        cl.addLayout(row("Форма", self.shape_seg))

        self.size_seg = SegmentedControl(["XS", "S", "M", "L", "XL"])
        size_map = {"xs": 0, "small": 1, "medium": 2, "large": 3, "xl": 4}
        self.size_seg.setCurrentIndex(size_map.get(self.config.get("visualizer_size", "medium"), 2))
        self.size_seg.currentChanged.connect(self._on_size_changed)
        cl.addLayout(row("Размер", self.size_seg))

        self.theme_seg = SegmentedControl(["Dark", "Light"])
        self.theme_seg.setCurrentIndex(0 if self.config.get("theme", "dark") == "dark" else 1)
        self.theme_seg.currentChanged.connect(lambda i: self.apply_theme("dark" if i == 0 else "light"))
        cl.addLayout(row("Тема", self.theme_seg))

        sens_row = QHBoxLayout()
        sens_row.setSpacing(10)
        sens_lbl = QLabel("Чувств.")
        sens_lbl.setObjectName("FieldLbl")
        sens_lbl.setFixedWidth(56)
        self.sens_slider = QSlider(Qt.Orientation.Horizontal)
        self.sens_slider.setRange(1, 10)
        saved_sens = self.config.get("visualizer_sensitivity", 1.0)
        self.sens_slider.setValue(max(1, min(10, round(saved_sens * 5))))
        self.sens_slider.setFixedWidth(130)
        self.sens_val_lbl = QLabel(f"{self.sens_slider.value() / 5:.1f}×")
        self.sens_val_lbl.setObjectName("FieldLbl")
        self.sens_val_lbl.setFixedWidth(34)
        self.sens_slider.valueChanged.connect(self._on_sensitivity_changed)
        sens_row.addWidget(sens_lbl)
        sens_row.addWidget(self.sens_slider)
        sens_row.addWidget(self.sens_val_lbl)
        sens_row.addStretch()
        cl.addLayout(sens_row)

        lay.addWidget(ctrl)

        color_card = QFrame()
        color_card.setObjectName("Card")
        ccl = QVBoxLayout(color_card)
        ccl.setContentsMargins(14, 10, 14, 10)
        ccl.setSpacing(6)
        cap = QLabel("ЦВЕТ")
        cap.setObjectName("SectionCap")
        ccl.addWidget(cap)
        self.color_selector = ColorPresetSelector()
        self.color_selector.setCurrentPreset(self.config.get("visualizer_color_preset", "mono"))
        self.color_selector.presetChanged.connect(self._on_preset_changed)
        ccl.addWidget(self.color_selector)
        lay.addWidget(color_card)

        self.vis_save_btn = QPushButton("Сохранить")
        self.vis_save_btn.setObjectName("PrimaryBtn")
        self.vis_save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vis_save_btn.setFixedWidth(120)
        self.vis_save_btn.clicked.connect(self._save_visualizer)
        lay.addWidget(self.vis_save_btn)
        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _on_shape_changed(self, idx):
        self.preview_widget.set_style(["wave", "bars", "scroll"][idx])

    def _on_size_changed(self, idx):
        self.preview_widget.set_size(["xs", "small", "medium", "large", "xl"][idx])

    def _on_sensitivity_changed(self, val):
        sens = val / 5.0
        self.sens_val_lbl.setText(f"{sens:.1f}×")
        self.preview_widget.set_sensitivity(sens)

    def _on_preset_changed(self, key):
        self.preview_widget.set_preset(key)
        if key == "custom":
            self.preview_widget.set_custom_colors(self.color_selector._custom_colors)
        self.config["visualizer_color_preset"] = key
        self.apply_theme(self.theme_name, key)

    def _save_visualizer(self):
        self.config["visualizer_style"] = ["wave", "bars", "scroll"][self.shape_seg.currentIndex()]
        self.config["visualizer_size"]  = ["xs", "small", "medium", "large", "xl"][self.size_seg.currentIndex()]
        self.config["visualizer_color_preset"] = self.color_selector.currentPreset()
        self.config["theme"] = "dark" if self.theme_seg.currentIndex() == 0 else "light"
        self.config["visualizer_sensitivity"] = self.sens_slider.value() / 5.0
        self.save_callback(self.config)
        self.vis_save_btn.setText("Сохранено!")
        self.vis_save_btn.setEnabled(False)
        QTimer.singleShot(1500, lambda: (self.vis_save_btn.setText("Сохранить"), self.vis_save_btn.setEnabled(True)))

    def _build_history_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(400)
        inner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)
        
        # Create a stacked widget for history list and detail view
        self.history_stack = QStackedWidget()
        
        # ── Page 1: History List ──
        list_page = QWidget()
        list_lay = QVBoxLayout(list_page)
        list_lay.setContentsMargins(0, 0, 0, 0)
        list_lay.setSpacing(10)
        
        # Header
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
        
        # Search
        self.history_search = QLineEdit()
        self.history_search.setPlaceholderText("Поиск...")
        self.history_search.textChanged.connect(self.filter_history)
        list_lay.addWidget(self.history_search)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.show_history_detail)
        self.history_list.setWordWrap(True)
        self.history_list.setTextElideMode(Qt.TextElideMode.ElideNone)
        list_lay.addWidget(self.history_list)
        
        self.history_stack.addWidget(list_page)
        
        # ── Page 2: Detail View ──
        detail_page = QWidget()
        detail_lay = QVBoxLayout(detail_page)
        detail_lay.setContentsMargins(0, 0, 0, 0)
        detail_lay.setSpacing(10)
        
        # Back button and title
        back_hdr = QHBoxLayout()
        self.btn_back_to_list = QPushButton("← Назад")
        self.btn_back_to_list.setObjectName("SecondaryBtn")
        self.btn_back_to_list.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back_to_list.setFixedWidth(100)
        self.btn_back_to_list.clicked.connect(self.hide_history_detail)
        back_hdr.addWidget(self.btn_back_to_list)
        back_hdr.addStretch()
        detail_lay.addLayout(back_hdr)
        
        # Meta info
        self.detail_meta = QLabel()
        self.detail_meta.setStyleSheet("font-size: 11px; color: #555D6E;")
        detail_lay.addWidget(self.detail_meta)
        
        # Raw text
        self.lbl_raw = QLabel("WHISPER")
        self.lbl_raw.setObjectName("DetailLbl")
        self.txt_raw = QPlainTextEdit()
        self.txt_raw.setReadOnly(True)
        detail_lay.addWidget(self.lbl_raw)
        detail_lay.addWidget(self.txt_raw)
        
        # Clean text
        self.lbl_clean = QLabel("LLM")
        self.lbl_clean.setObjectName("DetailLbl")
        self.txt_clean = QPlainTextEdit()
        self.txt_clean.setReadOnly(True)
        detail_lay.addWidget(self.lbl_clean)
        detail_lay.addWidget(self.txt_clean)
        
        # Copy buttons
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
        copy_lay.addWidget(self.btn_copy_raw)
        copy_lay.addWidget(self.btn_copy_clean)
        copy_lay.addStretch()
        detail_lay.addLayout(copy_lay)
        
        self.history_stack.addWidget(detail_page)
        
        lay.addWidget(self.history_stack)
        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        
        self.stack.addWidget(page)

    def _build_settings_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(400)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)

        title = QLabel("Настройки")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        card = QFrame()
        card.setObjectName("Card")
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(12)

        def cap(text):
            lbl = QLabel(text)
            lbl.setObjectName("SectionCap")
            return lbl

        def field_row(label, widget, w=None):
            r = QHBoxLayout()
            r.setSpacing(12)
            lbl = QLabel(label)
            lbl.setObjectName("FieldLbl")
            lbl.setFixedWidth(120)
            if w: widget.setFixedWidth(w)
            r.addWidget(lbl)
            r.addWidget(widget)
            r.addStretch()
            return r

        cl.addWidget(cap("API"))
        api_row = QHBoxLayout()
        api_row.setSpacing(8)
        self.api_input = QLineEdit()
        self.api_input.setText(self.config.get("api_key", ""))
        self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_input.setPlaceholderText("Groq API Key")
        api_lbl = QLabel("Groq API Key")
        api_lbl.setObjectName("FieldLbl")
        api_lbl.setFixedWidth(100)
        self.btn_toggle_api = QPushButton("Показать")
        self.btn_toggle_api.setObjectName("SecondaryBtn")
        self.btn_toggle_api.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_api.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.btn_toggle_api.setMinimumWidth(80)
        self.btn_toggle_api.clicked.connect(self.toggle_api_visibility)
        api_row.addWidget(api_lbl)
        api_row.addWidget(self.api_input, 1)
        api_row.addWidget(self.btn_toggle_api)
        cl.addLayout(api_row)

        cl.addWidget(cap("ВВОД"))
        self.hotkey_combo = QComboBox()
        self.hotkey_combo.addItems(["ctrl+windows", "left alt+space", "f8"])
        self.hotkey_combo.setCurrentText(self.config.get("hotkey", "ctrl+windows"))
        cl.addLayout(field_row("Горячая клавиша", self.hotkey_combo, 180))

        cl.addWidget(cap("МОДЕЛЬ"))
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
        cl.addLayout(field_row("Текстовая модель", self.model_combo, 220))

        cl.addWidget(cap("СИСТЕМА"))
        self.startup_toggle = ToggleSwitch(checked=self.config.get("run_on_startup", False))
        cl.addLayout(field_row("Автозапуск", self.startup_toggle))

        lay.addWidget(card)

        self.save_btn = QPushButton("Сохранить")
        self.save_btn.setObjectName("PrimaryBtn")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedWidth(120)
        self.save_btn.clicked.connect(self.save)
        lay.addWidget(self.save_btn)
        lay.addStretch()

        outer.addStretch()
        outer.addWidget(inner)
        outer.addStretch()
        self.stack.addWidget(page)

    def _build_logs_tab(self):
        page = QWidget()
        outer = QHBoxLayout(page)
        outer.setContentsMargins(0, 0, 0, 0)

        inner = QWidget()
        inner.setFixedWidth(400)
        inner.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        lay = QVBoxLayout(inner)
        lay.setContentsMargins(0, 20, 0, 20)
        lay.setSpacing(10)

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

        if preset in ACCENT_PRESETS:
            acc = ACCENT_PRESETS[preset][theme]
            self.startup_toggle.set_colors(QColor(acc["primary"]), QColor(acc["secondary"]))

        self.startup_toggle.set_theme(theme)
        self.theme_seg.set_theme(theme)
        self.shape_seg.set_theme(theme)
        self.size_seg.set_theme(theme)
        self.color_selector.set_theme(theme)
        self.preview_widget.set_theme(theme)

        for btn in self.nav_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def set_system_state(self, state):
        colors = {
            "idle":       ("#10B981", "● Готов"),
            "recording":  ("#06B6D4", "● Запись"),
            "processing": ("#8B5CF6", "● Обработка"),
        }
        color, text = colors.get(state, ("#10B981", "● Готов"))
        style = f"color: {color}; font-size: 11px;"
        self.status_dot_lbl.setText(text)
        self.status_dot_lbl.setStyleSheet(style)
        self.dash_state_badge.setText(text)
        self.dash_state_badge.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: 600;")

    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            btn.setObjectName("NavBtnActive" if i == index else "NavBtn")
        self.apply_theme(self.theme_name)
        if index == 0: self.update_statistics()
        elif index == 2: self.load_history()
        elif index == 4: self.load_logs()

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
        self.history_list.clear()
        for idx, entry in enumerate(self.history_entries):
            if query in entry.get("raw_text", "").lower() or query in entry.get("cleaned_text", "").lower():
                time_str = entry.get("timestamp", "").split()[-1][:5]
                snippet = entry.get("cleaned_text", "")[:150].replace("\n", " ")
                if len(entry.get("cleaned_text", "")) > 150: snippet += "…"
                item = QListWidgetItem(f"{time_str}  {snippet}")
                item.setData(Qt.ItemDataRole.UserRole, idx)
                self.history_list.addItem(item)

    def show_history_detail(self, item):
        """Show detail view for selected history item"""
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is not None and idx < len(self.history_entries):
            e = self.history_entries[idx]
            self.txt_raw.setPlainText(e.get("raw_text", ""))
            self.txt_clean.setPlainText(e.get("cleaned_text", ""))
            self.detail_meta.setText(f"{e.get('timestamp','')}  ·  {e.get('total_latency',0):.1f}s  ·  {e.get('model','')}")
            
            # Switch to detail page
            self.history_stack.setCurrentIndex(1)

    def hide_history_detail(self):
        """Return to history list view"""
        self.history_stack.setCurrentIndex(0)

    def copy_raw_text(self):   QApplication.clipboard().setText(self.txt_raw.toPlainText())
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

    def toggle_api_visibility(self):
        if self.api_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.btn_toggle_api.setText("Скрыть")
        else:
            self.api_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_api.setText("Показать")

    def save(self):
        self.config["api_key"]    = self.api_input.text().strip()
        self.config["hotkey"]     = self.hotkey_combo.currentText()
        self.config["text_model"] = self.model_combo.currentText()
        self.config["theme"]      = "dark" if self.theme_seg.currentIndex() == 0 else "light"
        self.config["run_on_startup"] = self.startup_toggle.isChecked()
        self.save_callback(self.config)
        self.save_btn.setText("Сохранено!")
        self.save_btn.setEnabled(False)
        QTimer.singleShot(1500, lambda: (self.save_btn.setText("Сохранить"), self.save_btn.setEnabled(True)))

    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            self.hide()

    def showEvent(self, event):
        """Apply native rounded corners via DWM on first show."""
        super().showEvent(event)
        if not getattr(self, '_dwm_applied', False):
            self._dwm_applied = True
            _apply_dwm_rounded_corners(self.winId())

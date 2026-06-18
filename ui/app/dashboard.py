"""Dashboard window — orchestrates tab builders and wires signals."""
import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QStackedWidget, QFrame, QApplication,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QRectF, QPoint, QSize, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QBrush, QIcon, QColor

from ..styles import get_stylesheet, get_resource_path
from .tabs.overview    import build_overview_tab, update_statistics
from .tabs.visualizer  import build_visualizer_tab
from .tabs.history     import (
    build_history_tab, load_history, filter_history,
    open_history_entry, clear_all_history,
)
from .tabs.settings    import (
    build_settings_tab, auto_save_settings,
    on_base_url_changed, toggle_api_visibility,
)
from .tabs.recognition import (
    build_recognition_tab, update_style_ui, auto_save_recognition,
)
from ..widgets import ToggleSwitch


class TitleBar(QFrame):
    """Custom frameless title bar with minimize and close buttons."""
    def __init__(self, parent_window):
        super().__init__()
        self.setObjectName("TitleBar")
        self.setFixedHeight(24)
        self._win = parent_window

        from PyQt6.QtWidgets import QPushButton
        lay = QHBoxLayout(self)
        lay.setContentsMargins(8, 0, 0, 0)
        lay.setSpacing(0)
        lay.addStretch()

        self._btn_min = QPushButton("─")
        self._btn_min.setObjectName("TitleBtn")
        self._btn_min.setFixedSize(36, 24)
        self._btn_min.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_min.clicked.connect(parent_window.showMinimized)
        lay.addWidget(self._btn_min)

        self._btn_close = QPushButton("✕")
        self._btn_close.setObjectName("TitleBtnClose")
        self._btn_close.setFixedSize(36, 24)
        self._btn_close.setCursor(Qt.CursorShape.ArrowCursor)
        self._btn_close.clicked.connect(parent_window.close)
        lay.addWidget(self._btn_close)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._win._dragging = True
            self._win._drag_pos = (
                event.globalPosition().toPoint() - self._win.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if self._win._dragging:
            self._win.move(event.globalPosition().toPoint() - self._win._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._win._dragging = False


class DashboardWindow(QWidget):
    """Main dashboard window — tab container, theme manager, signal hub."""

    restart_requested = pyqtSignal()

    def __init__(self, config, save_callback):
        super().__init__()
        self.setObjectName("DashboardWindow")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.config = config
        self.save_callback = save_callback
        self.theme_name = self.config.get("theme", "dark")
        self.history_entries = []
        self._init_ui()
        self.apply_theme(self.theme_name)
        self.load_history()
        self.update_statistics()

    def _init_ui(self):
        self.setWindowTitle("PITCH")
        self.setFixedSize(730, 600)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        main_vbox = QVBoxLayout(self)
        main_vbox.setContentsMargins(2, 2, 2, 2)
        main_vbox.setSpacing(0)

        self.title_bar = TitleBar(self)
        main_vbox.addWidget(self.title_bar)

        content = QWidget()
        content.setObjectName("DashboardContent")
        root = QHBoxLayout(content)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_sidebar())

        self.main_container = QFrame()
        self.main_container.setObjectName("MainContentContainer")
        container_layout = QVBoxLayout(self.main_container)
        container_layout.setContentsMargins(12, 8, 12, 12)

        self.stack = QStackedWidget()
        container_layout.addWidget(self.stack)

        wrapper = QWidget()
        wrapper_layout = QVBoxLayout(wrapper)
        wrapper_layout.setContentsMargins(12, 6, 12, 12)
        wrapper_layout.setSpacing(0)
        wrapper_layout.addWidget(self.main_container)
        root.addWidget(wrapper)

        main_vbox.addWidget(content)

        self.stack.addWidget(build_overview_tab(self))
        self.stack.addWidget(build_visualizer_tab(self))
        self.stack.addWidget(build_history_tab(self))
        self.stack.addWidget(build_settings_tab(self))
        self.stack.addWidget(build_recognition_tab(self))

        self._update_style_ui(self.config.get("formatting_style", "default"))

        icon_path = get_resource_path(os.path.join("assets", "p.jpeg"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self._dragging = False
        self._drag_pos = QPoint()

    def _build_sidebar(self):
        from PyQt6.QtWidgets import QPushButton
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(180)

        lay = QVBoxLayout(sidebar)
        lay.setContentsMargins(10, 12, 10, 16)
        lay.setSpacing(2)
        self.sidebar_layout = lay

        logo_lbl = QLabel("Pitch")
        logo_lbl.setObjectName("AppName")
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        logo_lbl.setContentsMargins(6, 10, 0, 10)
        lay.addWidget(logo_lbl)
        lay.addSpacing(8)

        self.nav_buttons = []
        nav_items = [
            ("Обзор",         0, "overview"),
            ("Визуализатор",  1, "visualizer"),
            ("История",       2, "history"),
            ("Настройки",     3, "settings"),
            ("Распознавание", 4, "predict"),
        ]
        for label, idx, icon_key in nav_items:
            btn = QPushButton(" " + label)
            btn.setProperty("icon_key", icon_key)
            is_active = (idx == 0)
            btn.setObjectName("NavBtnActive" if is_active else "NavBtn")
            icon_path = get_resource_path(os.path.join("assets", f"nav_{icon_key}_active.svg"))
            if os.path.exists(icon_path):
                btn.setIcon(QIcon(icon_path))
                btn.setIconSize(QSize(18, 18))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, i=idx: self.switch_tab(i))
            lay.addWidget(btn)
            self.nav_buttons.append(btn)

        lay.addStretch()


        ver_lbl = QLabel("v1.2")
        ver_lbl.setObjectName("VersionLbl")
        lay.addWidget(ver_lbl)

        return sidebar

    # --- Tab-delegated handlers ---

    def update_statistics(self):
        update_statistics(self)

    def load_history(self):
        load_history(self)

    def filter_history(self):
        filter_history(self)

    def _open_history_entry(self, idx):
        open_history_entry(self, idx)

    def clear_all_history(self):
        clear_all_history(self)
        self.update_statistics()

    def _open_history_from_overview(self, idx):
        self.switch_tab(2)
        self._open_history_entry(idx)

    def hide_history_detail(self):
        self.history_stack.setCurrentIndex(0)

    def _auto_save_settings(self):
        auto_save_settings(self)

    def _on_base_url_changed(self):
        on_base_url_changed(self)

    def toggle_api_visibility(self):
        toggle_api_visibility(self)

    def _toggle_hotkey_2_widgets(self):
        if hasattr(self, "h2_widget") and self.h2_widget:
            self.h2_widget.setVisible(self.hotkey_2_enabled_cb.isChecked())

    def _auto_save_recognition(self):
        auto_save_recognition(self)

    def _select_style(self, key):
        self.config["formatting_style"] = key
        self._update_style_ui(key)
        self._auto_save_recognition()

    def _on_style_seg_changed(self, idx):
        self._select_style(self.style_keys[idx])

    def _update_style_ui(self, key):
        update_style_ui(self, key)

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
        self.preview_widget.set_sensitivity(self.sens_values[idx])
        self._auto_save_visualizer()

    def _on_preset_changed(self, key):
        self.preview_widget.set_preset(key)
        self.config["visualizer_color_preset"] = key
        self.apply_theme(self.theme_name, key)
        self._auto_save_visualizer()

    def _auto_save_visualizer(self):
        self.config["visualizer_style"] = ["wave", "bars", "scroll"][self.shape_seg.currentIndex()]
        self.config["visualizer_size"]  = ["xs", "small", "medium", "large", "xl"][self.size_seg.currentIndex()]
        self.config["visualizer_color_preset"] = self.color_selector.currentPreset()
        self.config["visualizer_bg_mode"] = ["solid", "none"][self.bg_seg.currentIndex()]
        self.config["theme"] = "dark"
        self.config["visualizer_sensitivity"] = self.sens_values[self.sens_seg.currentIndex()]
        self.save_callback(self.config)

    # --- Theme and state ---

    def apply_theme(self, theme, preset=None):
        self.theme_name = theme
        if preset is None:
            preset = self.config.get("visualizer_color_preset", "mono")
        self.setStyleSheet(get_stylesheet(theme, preset))

        icon_path = get_resource_path(os.path.join("assets", "p.jpeg"))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        for widget_name in (
            "startup_toggle", "hotkey_2_enabled_cb",
            "raw_whisper_toggle", "hallucination_filter_toggle",
        ):
            w = getattr(self, widget_name, None)
            if w:
                w.set_theme(theme)

        for seg_name in ("min_duration_seg", "shape_seg", "size_seg", "bg_seg", "sens_seg"):
            w = getattr(self, seg_name, None)
            if w:
                w.set_theme(theme)

        if hasattr(self, "color_selector"):
            self.color_selector.set_theme(theme)
        if hasattr(self, "preview_widget"):
            self.preview_widget.set_theme(theme)

        for btn in self.nav_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        self._update_style_ui(self.config.get("formatting_style", "default"))


    def switch_tab(self, index):
        self.stack.setCurrentIndex(index)
        for i, btn in enumerate(self.nav_buttons):
            is_active = (i == index)
            btn.setObjectName("NavBtnActive" if is_active else "NavBtn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        if index == 0:
            self.update_statistics()
        elif index == 2:
            self.load_history()

    # --- Qt events ---

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

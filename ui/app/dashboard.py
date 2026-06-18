"""Dashboard window — orchestrates tab builders and wires signals."""
import os
import sys
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QStackedWidget, QFrame, QApplication,
    QSizePolicy,
)
from PyQt6.QtCore import (
    Qt, QRectF, QRect, QPoint, QSize, pyqtSignal,
    QPropertyAnimation, QParallelAnimationGroup, QEasingCurve, QEvent
)
from PyQt6.QtGui import QPainter, QPen, QBrush, QIcon, QColor, QFont

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
from ..widgets import ToggleSwitch, OutlinedLabel


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
        self._btn_min.clicked.connect(parent_window.animate_minimize)
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
        self._win._normal_pos = self._win.pos()


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
        
        self._normal_pos = None
        self._is_animating_show = False
        self._is_animating_minimize = False
        self._is_animating_restore = False
        self._is_animating_close = False
        
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

        icon_path = get_resource_path(os.path.join("assets", "p.png"))
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
        lay.setContentsMargins(10, 2, 10, 16)
        lay.setSpacing(2)
        self.sidebar_layout = lay

        logo_lbl = OutlinedLabel("Pitch")
        logo_lbl.setObjectName("AppName")
        logo_lbl.setColors("#FFFFFF", "#281B15", 4.5)
        
        # Explicitly set font to Segoe Script Bold to match the tray icon and branding
        logo_font = QFont("Segoe Script")
        logo_font.setBold(True)
        logo_font.setPointSize(34)
        logo_lbl.setFont(logo_font)
        
        logo_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        logo_lbl.setContentsMargins(0, 0, 0, 10)
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


        ver_lbl = QLabel("v1.5")
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

        icon_path = get_resource_path(os.path.join("assets", "p.png"))
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

    # --- Custom Animations ---

    def animate_show(self):
        if self._is_animating_show:
            return
        self._is_animating_show = True

        pos = self._normal_pos if self._normal_pos is not None else self.pos()
        geom = self.geometry()
        normal_geom = QRect(pos.x(), pos.y(), geom.width(), geom.height())
        start_geom = self.geometry()

        self._show_anim_group = QParallelAnimationGroup()

        self._show_opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self._show_opacity_anim.setDuration(200)
        self._show_opacity_anim.setStartValue(0.0)
        self._show_opacity_anim.setEndValue(1.0)
        self._show_opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._show_anim_group.addAnimation(self._show_opacity_anim)

        self._show_geom_anim = QPropertyAnimation(self, b"geometry")
        self._show_geom_anim.setDuration(200)
        self._show_geom_anim.setStartValue(start_geom)
        self._show_geom_anim.setEndValue(normal_geom)
        self._show_geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._show_anim_group.addAnimation(self._show_geom_anim)

        def on_finished():
            self._is_animating_show = False
            self.setWindowOpacity(1.0)
            self.setGeometry(normal_geom)

        self._show_anim_group.finished.connect(on_finished)
        self._show_anim_group.start()

    def animate_minimize(self):
        if self._is_animating_minimize:
            return
        self._is_animating_minimize = True

        self._normal_pos = self.pos()

        self._min_anim_group = QParallelAnimationGroup()

        self._min_opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self._min_opacity_anim.setDuration(200)
        self._min_opacity_anim.setStartValue(1.0)
        self._min_opacity_anim.setEndValue(0.0)
        self._min_opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._min_anim_group.addAnimation(self._min_opacity_anim)

        self._min_geom_anim = QPropertyAnimation(self, b"geometry")
        self._min_geom_anim.setDuration(200)
        geom = self.geometry()
        target_geom = QRect(geom.x(), geom.y() + 40, geom.width(), geom.height())
        self._min_geom_anim.setStartValue(geom)
        self._min_geom_anim.setEndValue(target_geom)
        self._min_geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._min_anim_group.addAnimation(self._min_geom_anim)

        def on_finished():
            self.showMinimized()
            self._is_animating_minimize = False

        self._min_anim_group.finished.connect(on_finished)
        self._min_anim_group.start()

    def animate_restore(self):
        if self._is_animating_restore:
            return
        self._is_animating_restore = True

        pos = self._normal_pos if self._normal_pos is not None else self.pos()
        geom = self.geometry()
        normal_geom = QRect(pos.x(), pos.y(), geom.width(), geom.height())
        start_geom = QRect(pos.x(), pos.y() + 40, geom.width(), geom.height())

        self.setGeometry(start_geom)
        self.setWindowOpacity(0.0)

        self._restore_anim_group = QParallelAnimationGroup()

        self._restore_opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self._restore_opacity_anim.setDuration(250)
        self._restore_opacity_anim.setStartValue(0.0)
        self._restore_opacity_anim.setEndValue(1.0)
        self._restore_opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._restore_anim_group.addAnimation(self._restore_opacity_anim)

        self._restore_geom_anim = QPropertyAnimation(self, b"geometry")
        self._restore_geom_anim.setDuration(250)
        self._restore_geom_anim.setStartValue(start_geom)
        self._restore_geom_anim.setEndValue(normal_geom)
        self._restore_geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._restore_anim_group.addAnimation(self._restore_geom_anim)

        def on_finished():
            self._is_animating_restore = False
            self.setWindowOpacity(1.0)
            self.setGeometry(normal_geom)

        self._restore_anim_group.finished.connect(on_finished)
        self._restore_anim_group.start()

    def animate_close(self):
        if self._is_animating_close:
            return
        self._is_animating_close = True

        self._close_anim_group = QParallelAnimationGroup()

        self._close_opacity_anim = QPropertyAnimation(self, b"windowOpacity")
        self._close_opacity_anim.setDuration(200)
        self._close_opacity_anim.setStartValue(1.0)
        self._close_opacity_anim.setEndValue(0.0)
        self._close_opacity_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._close_anim_group.addAnimation(self._close_opacity_anim)

        self._close_geom_anim = QPropertyAnimation(self, b"geometry")
        self._close_geom_anim.setDuration(200)
        geom = self.geometry()
        target_geom = QRect(geom.x(), geom.y() + 20, geom.width(), geom.height())
        self._close_geom_anim.setStartValue(geom)
        self._close_geom_anim.setEndValue(target_geom)
        self._close_geom_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._close_anim_group.addAnimation(self._close_geom_anim)

        def on_finished():
            self.hide()
            self.setWindowOpacity(1.0)
            if self._normal_pos is not None:
                self.setGeometry(QRect(self._normal_pos.x(), self._normal_pos.y(), geom.width(), geom.height()))
            else:
                self.setGeometry(geom)
            self._is_animating_close = False

        self._close_anim_group.finished.connect(on_finished)
        self._close_anim_group.start()

    # --- Qt events ---

    def changeEvent(self, event):
        if event.type() == QEvent.Type.WindowStateChange:
            if not self.isMinimized() and self._normal_pos is not None:
                self.animate_restore()
        super().changeEvent(event)

    def closeEvent(self, event):
        if self._is_animating_close:
            event.accept()
            return
        event.ignore()
        self.animate_close()

    def showEvent(self, event):
        if not self._is_animating_show and not self._is_animating_restore and not self._is_animating_close:
            if self._normal_pos is None:
                self._normal_pos = self.pos()
            
            pos = self._normal_pos
            geom = self.geometry()
            start_geom = QRect(pos.x(), pos.y() + 20, geom.width(), geom.height())
            self.setGeometry(start_geom)
            self.setWindowOpacity(0.0)

        super().showEvent(event)
        
        if not self._is_animating_show and not self._is_animating_restore and not self._is_animating_close:
            self.animate_show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = QRectF(self.rect())
        rect.adjust(0.5, 0.5, -0.5, -0.5)
        painter.setBrush(QBrush(QColor("#DFCEBA")))
        painter.setPen(QPen(QColor("#7D6454"), 1.0))
        painter.drawRoundedRect(rect, 20.0, 20.0)
        painter.end()

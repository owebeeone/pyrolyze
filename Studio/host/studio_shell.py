from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QCursor, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class HandlePosition(Enum):
    TOP_LEFT = "TOP_LEFT"
    TOP = "TOP"
    TOP_RIGHT = "TOP_RIGHT"
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    BOTTOM_LEFT = "BOTTOM_LEFT"
    BOTTOM = "BOTTOM"
    BOTTOM_RIGHT = "BOTTOM_RIGHT"


_CURSOR_BY_HANDLE = {
    HandlePosition.TOP_LEFT: Qt.SizeFDiagCursor,
    HandlePosition.TOP: Qt.SizeVerCursor,
    HandlePosition.TOP_RIGHT: Qt.SizeBDiagCursor,
    HandlePosition.LEFT: Qt.SizeHorCursor,
    HandlePosition.RIGHT: Qt.SizeHorCursor,
    HandlePosition.BOTTOM_LEFT: Qt.SizeBDiagCursor,
    HandlePosition.BOTTOM: Qt.SizeVerCursor,
    HandlePosition.BOTTOM_RIGHT: Qt.SizeFDiagCursor,
}


class EdgeResizeHandle(QWidget):
    def __init__(self, parent: QWidget, position: HandlePosition, thickness: int = 5) -> None:
        super().__init__(parent)
        self.position = position
        self.thickness = max(3, int(thickness))
        self.setMouseTracking(True)
        self.setCursor(_CURSOR_BY_HANDLE[position])
        self.setStyleSheet("background: transparent;")
        self._resizing = False
        self._start_global = QPoint()
        self._start_geometry = parent.geometry()

    def update_geometry(self) -> None:
        parent = self.parentWidget()
        if parent is None:
            return
        w = parent.width()
        h = parent.height()
        t = self.thickness

        if self.position == HandlePosition.TOP_LEFT:
            self.setGeometry(0, 0, t, t)
        elif self.position == HandlePosition.TOP:
            self.setGeometry(t, 0, max(0, w - 2 * t), t)
        elif self.position == HandlePosition.TOP_RIGHT:
            self.setGeometry(max(0, w - t), 0, t, t)
        elif self.position == HandlePosition.LEFT:
            self.setGeometry(0, t, t, max(0, h - 2 * t))
        elif self.position == HandlePosition.RIGHT:
            self.setGeometry(max(0, w - t), t, t, max(0, h - 2 * t))
        elif self.position == HandlePosition.BOTTOM_LEFT:
            self.setGeometry(0, max(0, h - t), t, t)
        elif self.position == HandlePosition.BOTTOM:
            self.setGeometry(t, max(0, h - t), max(0, w - 2 * t), t)
        else:
            self.setGeometry(max(0, w - t), max(0, h - t), t, t)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        parent = self.parentWidget()
        if (
            event.button() == Qt.LeftButton
            and parent is not None
            and not parent.isMaximized()
            and not parent.isFullScreen()
        ):
            self._resizing = True
            self._start_global = event.globalPosition().toPoint()
            self._start_geometry = parent.geometry()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if not self._resizing:
            return super().mouseMoveEvent(event)
        parent = self.parentWidget()
        if parent is None:
            return
        delta = event.globalPosition().toPoint() - self._start_global
        rect = self._start_geometry
        min_w = max(320, parent.minimumWidth())
        min_h = max(240, parent.minimumHeight())

        x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()

        if self.position in {HandlePosition.LEFT, HandlePosition.TOP_LEFT, HandlePosition.BOTTOM_LEFT}:
            x = x + delta.x()
            w = w - delta.x()
            if w < min_w:
                x = rect.right() - min_w + 1
                w = min_w

        if self.position in {HandlePosition.RIGHT, HandlePosition.TOP_RIGHT, HandlePosition.BOTTOM_RIGHT}:
            w = max(min_w, w + delta.x())

        if self.position in {HandlePosition.TOP, HandlePosition.TOP_LEFT, HandlePosition.TOP_RIGHT}:
            y = y + delta.y()
            h = h - delta.y()
            if h < min_h:
                y = rect.bottom() - min_h + 1
                h = min_h

        if self.position in {HandlePosition.BOTTOM, HandlePosition.BOTTOM_LEFT, HandlePosition.BOTTOM_RIGHT}:
            h = max(min_h, h + delta.y())

        parent.setGeometry(x, y, w, h)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._resizing = False
        super().mouseReleaseEvent(event)


class TitleBarWidget(QWidget):
    def __init__(self, owner: "StudioMainWindow") -> None:
        super().__init__(owner)
        self._owner = owner
        self.setObjectName("custom_title_bar_widget")
        self.setFixedHeight(35)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(owner.show_title_bar_context_menu)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._owner.handle_title_bar_press(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._owner.handle_title_bar_move(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._owner.handle_title_bar_release(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        self._owner.handle_title_bar_double_click(event)


class StudioMainWindow(QMainWindow):
    inspector_requested = Signal()

    def __init__(self, title: str, *, width: int, height: int) -> None:
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setWindowTitle(title)
        self.resize(width, height)
        self.setMinimumSize(640, 420)
        self._drag_active = False
        self._drag_offset = QPoint()
        self.resize_handles: list[EdgeResizeHandle] = []
        self.setStyleSheet(
            """
            QMainWindow { border: 1px solid #3A3A3A; background: #1E1E1E; }
            #custom_title_bar_widget { background: #252526; border: 0px; }
            #title_bar_menu_bar_widget { background: transparent; color: #D4D4D4; }
            QPushButton#close_button { color: #F48771; }
            """
        )

        container = QWidget(self)
        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(1, 1, 1, 1)
        root_layout.setSpacing(0)

        self.title_bar = TitleBarWidget(self)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        self.window_icon_label = QLabel("🪟", self.title_bar)
        self.window_icon_label.setFixedWidth(21)
        self.window_icon_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(self.window_icon_label)

        self.menu_bar = QMenuBar(self.title_bar)
        self.menu_bar.setObjectName("title_bar_menu_bar_widget")
        self.menu_bar.setNativeMenuBar(False)
        self.menu_bar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.menu_bar.addMenu("&File")
        self.menu_bar.addMenu("&Edit")
        self.menu_bar.addMenu("&View")
        self.menu_bar.addMenu("&Help")
        title_layout.addWidget(self.menu_bar, 1)

        self.min_button = QPushButton("─", self.title_bar)
        self.min_button.setFixedSize(40, 20)
        self.min_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.min_button)

        self.max_button = QPushButton("□", self.title_bar)
        self.max_button.setFixedSize(40, 20)
        self.max_button.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.max_button)

        self.close_button = QPushButton("✕", self.title_bar)
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(40, 20)
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)

        root_layout.addWidget(self.title_bar)

        self.scroll_area = QScrollArea(container)
        self.scroll_area.setWidgetResizable(True)
        self.content_widget = QWidget(self.scroll_area)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)
        self.scroll_area.setWidget(self.content_widget)
        root_layout.addWidget(self.scroll_area, 1)

        self.setCentralWidget(container)
        self._create_resize_handles()

    def _create_resize_handles(self) -> None:
        for position in HandlePosition:
            handle = EdgeResizeHandle(self, position=position, thickness=5)
            handle.show()
            self.resize_handles.append(handle)
        self._update_resize_handles()

    def _update_resize_handles(self) -> None:
        visible = not self.isMaximized() and not self.isFullScreen()
        for handle in self.resize_handles:
            handle.setVisible(visible)
            handle.update_geometry()

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_resize_handles()

    def toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
            self.max_button.setText("□")
        else:
            self.showMaximized()
            self.max_button.setText("❐")
        self._update_resize_handles()

    def _should_ignore_drag(self, local_pos: QPoint) -> bool:
        target = self.title_bar.childAt(local_pos)
        return isinstance(target, (QPushButton, QMenuBar))

    def handle_title_bar_press(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return
        local_pos = event.position().toPoint()
        if self._should_ignore_drag(local_pos) or self.isMaximized() or self.isFullScreen():
            return
        self._drag_active = True
        self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()

    def handle_title_bar_move(self, event: QMouseEvent) -> None:
        if not self._drag_active:
            return
        self.move(event.globalPosition().toPoint() - self._drag_offset)
        event.accept()

    def handle_title_bar_release(self, event: QMouseEvent) -> None:
        self._drag_active = False
        event.accept()

    def handle_title_bar_double_click(self, event: QMouseEvent) -> None:
        if event.button() != Qt.LeftButton:
            return
        local_pos = event.position().toPoint()
        if self._should_ignore_drag(local_pos):
            return
        self.toggle_maximize()
        event.accept()

    def build_title_bar_context_menu(self) -> QMenu:
        menu = QMenu(self)
        if self.isMaximized():
            restore_action = menu.addAction("Restore")
            restore_action.triggered.connect(lambda: (self.showNormal(), self.max_button.setText("□")))
        else:
            maximize_action = menu.addAction("Maximize")
            maximize_action.triggered.connect(lambda: (self.showMaximized(), self.max_button.setText("❐")))
        move_action = menu.addAction("Move")
        move_action.triggered.connect(lambda: self.setCursor(QCursor(Qt.SizeAllCursor)))
        size_action = menu.addAction("Size")
        size_action.triggered.connect(lambda: None)
        menu.addSeparator()
        inspector_action = menu.addAction("Open Inspector")
        inspector_action.triggered.connect(self.inspector_requested.emit)
        menu.addSeparator()
        minimize_action = menu.addAction("Minimize")
        minimize_action.triggered.connect(self.showMinimized)
        close_action = menu.addAction("Close")
        close_action.triggered.connect(self.close)
        return menu

    def show_title_bar_context_menu(self, pos: QPoint) -> None:
        menu = self.build_title_bar_context_menu()
        menu.exec(self.title_bar.mapToGlobal(pos))


@dataclass(slots=True)
class StudioWindowHost:
    app: QApplication
    window: StudioMainWindow
    scroll_area: QScrollArea
    content_widget: QWidget
    content_layout: QVBoxLayout
    owner_state: Any = None

    def show(self) -> None:
        self.window.show()

    def exec(self) -> int:
        self.show()
        return self.app.exec()

    def close(self) -> None:
        self.window.close()


def create_studio_window(
    title: str,
    *,
    width: int = 1200,
    height: int = 820,
) -> StudioWindowHost:
    app = QApplication.instance() or QApplication([])
    window = StudioMainWindow(title, width=width, height=height)
    return StudioWindowHost(
        app=app,
        window=window,
        scroll_area=window.scroll_area,
        content_widget=window.content_widget,
        content_layout=window.content_layout,
    )


__all__ = [
    "EdgeResizeHandle",
    "HandlePosition",
    "StudioMainWindow",
    "StudioWindowHost",
    "create_studio_window",
]

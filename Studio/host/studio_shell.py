from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from PySide6.QtCore import QDir, QPoint, Qt, Signal
from PySide6.QtGui import QAction, QCursor, QMouseEvent, QResizeEvent
from PySide6.QtWidgets import (
    QApplication,
    QFileSystemModel,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QTabWidget,
    QTextEdit,
    QToolBar,
    QTreeView,
    QVBoxLayout,
    QWidget,
)


WINDOW_ICON_TEXT = "\U0001FA9F"
MINIMIZE_BUTTON_TEXT = "\u2500"
MAXIMIZE_BUTTON_TEXT = "\u25A1"
RESTORE_BUTTON_TEXT = "\u2750"
CLOSE_BUTTON_TEXT = "\u2715"


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
        width = parent.width()
        height = parent.height()
        thickness = self.thickness

        if self.position == HandlePosition.TOP_LEFT:
            self.setGeometry(0, 0, thickness, thickness)
        elif self.position == HandlePosition.TOP:
            self.setGeometry(thickness, 0, max(0, width - (2 * thickness)), thickness)
        elif self.position == HandlePosition.TOP_RIGHT:
            self.setGeometry(max(0, width - thickness), 0, thickness, thickness)
        elif self.position == HandlePosition.LEFT:
            self.setGeometry(0, thickness, thickness, max(0, height - (2 * thickness)))
        elif self.position == HandlePosition.RIGHT:
            self.setGeometry(
                max(0, width - thickness),
                thickness,
                thickness,
                max(0, height - (2 * thickness)),
            )
        elif self.position == HandlePosition.BOTTOM_LEFT:
            self.setGeometry(0, max(0, height - thickness), thickness, thickness)
        elif self.position == HandlePosition.BOTTOM:
            self.setGeometry(
                thickness,
                max(0, height - thickness),
                max(0, width - (2 * thickness)),
                thickness,
            )
        else:
            self.setGeometry(
                max(0, width - thickness),
                max(0, height - thickness),
                thickness,
                thickness,
            )

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
        min_width = max(640, parent.minimumWidth())
        min_height = max(420, parent.minimumHeight())

        x, y, width, height = rect.x(), rect.y(), rect.width(), rect.height()

        if self.position in {HandlePosition.LEFT, HandlePosition.TOP_LEFT, HandlePosition.BOTTOM_LEFT}:
            x = x + delta.x()
            width = width - delta.x()
            if width < min_width:
                x = rect.right() - min_width + 1
                width = min_width

        if self.position in {HandlePosition.RIGHT, HandlePosition.TOP_RIGHT, HandlePosition.BOTTOM_RIGHT}:
            width = max(min_width, width + delta.x())

        if self.position in {HandlePosition.TOP, HandlePosition.TOP_LEFT, HandlePosition.TOP_RIGHT}:
            y = y + delta.y()
            height = height - delta.y()
            if height < min_height:
                y = rect.bottom() - min_height + 1
                height = min_height

        if self.position in {HandlePosition.BOTTOM, HandlePosition.BOTTOM_LEFT, HandlePosition.BOTTOM_RIGHT}:
            height = max(min_height, height + delta.y())

        parent.setGeometry(x, y, width, height)

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


class ExplorerTitleBar(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setFixedHeight(24)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(4)
        icon = QLabel("\U0001F4C1", self)
        icon.setFixedWidth(20)
        title = QLabel("EXPLORER", self)
        title.setObjectName("explorer_title_label")
        layout.addWidget(icon)
        layout.addWidget(title)
        layout.addStretch(1)
        self.setStyleSheet(
            """
            QWidget { background: #252526; color: #d4d4d4; }
            QLabel#explorer_title_label { font-weight: 600; letter-spacing: 0.4px; }
            """
        )


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
        self._configure_window_style()
        self._build_shell_ui()
        self._create_resize_handles()

    def _configure_window_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                border: 1px solid #252526;
                background: #1e1e1e;
            }
            #custom_title_bar_widget {
                background: #252526;
                border: 0px;
            }
            #title_bar_menu_bar_widget {
                background: transparent;
                color: #d4d4d4;
            }
            QToolBar#explorer_toolbar {
                background: #252526;
                border: none;
                padding: 2px;
                spacing: 2px;
            }
            QToolBar#explorer_toolbar QToolButton {
                background: transparent;
                border: none;
                border-radius: 3px;
                padding: 6px;
                margin: 0px;
                color: #cccccc;
            }
            QToolBar#explorer_toolbar QToolButton:hover {
                background: #37373d;
                color: #ffffff;
            }
            QTreeView {
                border: none;
                background: #252526;
                color: #cccccc;
            }
            QTreeView::item:selected {
                background: #094771;
                color: #ffffff;
            }
            QTreeView::item:hover:!selected {
                background: #2a2d2e;
            }
            QSplitter::handle {
                background: #353535;
                border: 1px solid #474747;
            }
            QSplitter::handle:hover {
                background: #404040;
            }
            QSplitter::handle:pressed {
                background: #505050;
            }
            QTabWidget::pane {
                border: none;
                background: #1e1e1e;
            }
            QTabBar::tab {
                background: #2d2d2d;
                color: #cccccc;
                border: none;
                padding: 6px 12px;
                margin: 0px 1px 0px 0px;
            }
            QTabBar::tab:selected {
                background: #1e1e1e;
                border-top: 1px solid #007acc;
            }
            QPushButton#close_button {
                color: #f48771;
            }
            """
        )

    def _build_shell_ui(self) -> None:
        container = QWidget(self)
        root_layout = QVBoxLayout(container)
        root_layout.setContentsMargins(1, 1, 1, 1)
        root_layout.setSpacing(0)

        self._build_title_bar(root_layout)
        self._build_workspace(root_layout)

        self.setCentralWidget(container)

    def _build_title_bar(self, root_layout: QVBoxLayout) -> None:
        self.title_bar = TitleBarWidget(self)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(0, 0, 0, 0)
        title_layout.setSpacing(0)

        self.window_icon_label = QLabel(WINDOW_ICON_TEXT, self.title_bar)
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

        self.min_button = QPushButton(MINIMIZE_BUTTON_TEXT, self.title_bar)
        self.min_button.setFixedSize(40, 20)
        self.min_button.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.min_button)

        self.max_button = QPushButton(MAXIMIZE_BUTTON_TEXT, self.title_bar)
        self.max_button.setFixedSize(40, 20)
        self.max_button.clicked.connect(self.toggle_maximize)
        title_layout.addWidget(self.max_button)

        self.close_button = QPushButton(CLOSE_BUTTON_TEXT, self.title_bar)
        self.close_button.setObjectName("close_button")
        self.close_button.setFixedSize(40, 20)
        self.close_button.clicked.connect(self.close)
        title_layout.addWidget(self.close_button)

        root_layout.addWidget(self.title_bar)

    def _build_workspace(self, root_layout: QVBoxLayout) -> None:
        workspace_container = QWidget(self)
        workspace_layout = QVBoxLayout(workspace_container)
        workspace_layout.setContentsMargins(0, 0, 0, 0)
        workspace_layout.setSpacing(0)

        self.workspace_splitter = QSplitter(Qt.Orientation.Horizontal, workspace_container)
        self.workspace_splitter.setObjectName("workspace_splitter")
        self.workspace_splitter.setHandleWidth(7)
        self.workspace_splitter.addWidget(self._build_left_panel())
        self.workspace_splitter.addWidget(self._build_right_panel())
        self.workspace_splitter.setSizes([540, 1620])
        workspace_layout.addWidget(self.workspace_splitter)
        root_layout.addWidget(workspace_container, 1)

    def _build_left_panel(self) -> QWidget:
        self.left_panel = QWidget(self)
        left_layout = QVBoxLayout(self.left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.explorer_toolbar = QToolBar("Explorer Toolbar", self.left_panel)
        self.explorer_toolbar.setObjectName("explorer_toolbar")
        self.explorer_toolbar.setMovable(False)

        open_action = QAction("\U0001F4C2", self.explorer_toolbar)
        open_action.setToolTip("Open Folder")
        refresh_action = QAction("\U0001F504", self.explorer_toolbar)
        refresh_action.setToolTip("Refresh Explorer")
        collapse_action = QAction("\u25C0", self.explorer_toolbar)
        collapse_action.setToolTip("Collapse Folders")

        self.explorer_toolbar.addAction(open_action)
        self.explorer_toolbar.addAction(refresh_action)
        self.explorer_toolbar.addAction(collapse_action)
        left_layout.addWidget(self.explorer_toolbar)

        self.explorer_container = QWidget(self.left_panel)
        explorer_layout = QVBoxLayout(self.explorer_container)
        explorer_layout.setContentsMargins(0, 0, 0, 0)
        explorer_layout.setSpacing(0)
        explorer_layout.addWidget(ExplorerTitleBar(self.explorer_container))

        self.explorer_model = QFileSystemModel(self.explorer_container)
        self.explorer_model.setFilter(QDir.AllEntries | QDir.NoDotAndDotDot)
        root_path = str(Path.cwd())
        root_index = self.explorer_model.setRootPath(root_path)

        self.explorer_tree = QTreeView(self.explorer_container)
        self.explorer_tree.setModel(self.explorer_model)
        self.explorer_tree.setRootIndex(root_index)
        self.explorer_tree.setHeaderHidden(True)
        self.explorer_tree.setAnimated(True)
        self.explorer_tree.setIndentation(16)
        for column in range(1, 4):
            self.explorer_tree.hideColumn(column)
        explorer_layout.addWidget(self.explorer_tree, 1)

        left_layout.addWidget(self.explorer_container, 1)
        return self.left_panel

    def _build_right_panel(self) -> QWidget:
        self.right_panel = QWidget(self)
        right_layout = QVBoxLayout(self.right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.vertical_splitter = QSplitter(Qt.Orientation.Vertical, self.right_panel)
        self.vertical_splitter.setObjectName("workspace_vertical_splitter")
        self.vertical_splitter.setHandleWidth(7)
        self.vertical_splitter.addWidget(self._build_editor_area())
        self.vertical_splitter.addWidget(self._build_bottom_panel())
        self.vertical_splitter.setSizes([815, 305])
        right_layout.addWidget(self.vertical_splitter)
        return self.right_panel

    def _build_editor_area(self) -> QWidget:
        self.editor_area = QWidget(self.right_panel)
        editor_layout = QVBoxLayout(self.editor_area)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_layout.setSpacing(0)

        self.editor_tabs = QTabWidget(self.editor_area)
        self.editor_tabs.setTabsClosable(True)
        self.editor_tabs.setMovable(True)
        self.editor_tabs.setDocumentMode(True)

        self.editor_render_page = QWidget(self.editor_tabs)
        render_layout = QVBoxLayout(self.editor_render_page)
        render_layout.setContentsMargins(0, 0, 0, 0)
        render_layout.setSpacing(0)
        self.content_widget = QWidget(self.editor_render_page)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        self.content_layout.setSpacing(16)
        render_layout.addWidget(self.content_widget)

        self.editor_two_page = QWidget(self.editor_tabs)
        editor_two_layout = QVBoxLayout(self.editor_two_page)
        editor_two_layout.setContentsMargins(8, 8, 8, 8)
        editor_two_layout.addWidget(QLabel("Editor Tab 2 Content", self.editor_two_page))

        self.welcome_page = QWidget(self.editor_tabs)
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_layout.setContentsMargins(8, 8, 8, 8)
        welcome_layout.addWidget(QLabel("Welcome to ViewMesh", self.welcome_page))

        self.editor_tabs.addTab(self.editor_render_page, "Editor 1")
        self.editor_tabs.addTab(self.editor_two_page, "Editor 2")
        self.editor_tabs.addTab(self.welcome_page, "Welcome")
        editor_layout.addWidget(self.editor_tabs)
        return self.editor_area

    def _build_bottom_panel(self) -> QWidget:
        self.bottom_panel = QWidget(self.right_panel)
        bottom_layout = QVBoxLayout(self.bottom_panel)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)

        self.bottom_tabs = QTabWidget(self.bottom_panel)

        output_page = QWidget(self.bottom_tabs)
        output_layout = QVBoxLayout(output_page)
        output_layout.setContentsMargins(8, 8, 8, 8)
        self.output_text = QTextEdit(output_page)
        self.output_text.setReadOnly(True)
        self.output_text.setPlainText("Output panel - ready for application output...")
        output_layout.addWidget(self.output_text)

        terminal_page = QWidget(self.bottom_tabs)
        terminal_layout = QVBoxLayout(terminal_page)
        terminal_layout.setContentsMargins(8, 8, 8, 8)
        self.terminal_text = QTextEdit(terminal_page)
        self.terminal_text.setReadOnly(False)
        self.terminal_text.setPlainText("Terminal panel - ready for terminal integration...")
        terminal_layout.addWidget(self.terminal_text)

        self.bottom_tabs.addTab(output_page, "Output")
        self.bottom_tabs.addTab(terminal_page, "Terminal")
        bottom_layout.addWidget(self.bottom_tabs)
        return self.bottom_panel

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
            self.max_button.setText(MAXIMIZE_BUTTON_TEXT)
        else:
            self.showMaximized()
            self.max_button.setText(RESTORE_BUTTON_TEXT)
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
            restore_action.triggered.connect(lambda: (self.showNormal(), self.max_button.setText(MAXIMIZE_BUTTON_TEXT)))
        else:
            maximize_action = menu.addAction("Maximize")
            maximize_action.triggered.connect(
                lambda: (self.showMaximized(), self.max_button.setText(RESTORE_BUTTON_TEXT))
            )

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

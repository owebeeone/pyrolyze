"""VS Code–like light theme for the Phase 1 Studio shell (declarative ``styleSheet``).

Extracted from the imperative ``examples/studio_app.py`` styling; kept as a plain
string so the ``@pyrolyze`` module does not need f-strings or runtime font lookup.
"""

from __future__ import annotations

# Light theme aligned with ``studio_app.py`` ``vs_code_style`` block.
VS_CODE_STUDIO_STYLESHEET = """
QWidget {
    color: #333333;
    background-color: #ffffff;
}

QMainWindow {
    background-color: #f3f3f3;
}

QMenuBar {
    background-color: #f3f3f3;
    border-bottom: 1px solid #e7e7e7;
    padding: 2px;
    spacing: 5px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 5px 8px;
    border-radius: 3px;
}

QMenuBar::item:selected {
    background-color: #e0e0e0;
}

QMenuBar::item:pressed {
    background-color: #d0d0d0;
}

QMenu {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    padding: 3px;
}

QMenu::item {
    padding: 5px 20px 5px 20px;
    border-radius: 3px;
}

QMenu::item:selected {
    background-color: #e8e8f2;
    color: #333333;
}

QStatusBar {
    background-color: #007acc;
    color: white;
    padding: 3px;
    font-size: 9pt;
}

QToolBar {
    background-color: #f3f3f3;
    border-bottom: 1px solid #e7e7e7;
    spacing: 3px;
    padding: 3px;
}

QToolButton {
    background-color: transparent;
    border: none;
    padding: 5px;
    border-radius: 3px;
}

QToolButton:hover {
    background-color: #e0e0e0;
}

QToolButton:pressed {
    background-color: #d0d0d0;
}

QSplitter::handle {
    background-color: #d0d0d0;
}

QTabBar::tab {
    background-color: #ececec;
    border: 1px solid #d0d0d0;
    padding: 6px 14px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-bottom-color: #ffffff;
}

QTreeView {
    background-color: #ffffff;
    alternate-background-color: #f7f7f7;
    border: none;
}

QTextEdit {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
}

QLabel#studio_title_caption {
    color: #333333;
    font-weight: bold;
}

QPushButton#studio_title_min,
QPushButton#studio_title_max,
QPushButton#studio_title_close {
    min-width: 28px;
    max-width: 28px;
    min-height: 22px;
    max-height: 22px;
    border: none;
    background-color: transparent;
    font-size: 11pt;
}

QPushButton#studio_title_min:hover,
QPushButton#studio_title_max:hover,
QPushButton#studio_title_close:hover {
    background-color: #e0e0e0;
}

QWidget#studio_title_bar {
    background-color: #f3f3f3;
    border-bottom: 1px solid #e7e7e7;
    min-height: 36px;
    max-height: 36px;
}
"""

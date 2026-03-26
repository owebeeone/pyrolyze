from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6.QtCore")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton, QWidget

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


SOURCE = """
#@pyrolyze
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import pyrolyze, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


@pyrolyze
def native_counter() -> None:
    count, set_count = use_state(0)

    with Qt.CQMainWindow(windowTitle="Native Counter"):
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                Qt.CQLabel(f"Count: {count}", objectName="count_label")
                with Qt.CQGroupBox("Controls"):
                    with Qt.CQBoxLayout(QBoxLayout.Direction.LeftToRight):
                        Qt.CQPushButton(
                            "Increment",
                            objectName="increment_button",
                            on_clicked=lambda: set_count(lambda current: current + 1),
                        )
"""


EXPLICIT_MOUNT_SOURCE = """
#@pyrolyze
from PySide6.QtCore import Qt as NativeQt
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import mount, pyrolyze, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


@pyrolyze
def mounted_window() -> None:
    count, set_count = use_state(0)

    with Qt.CQMainWindow(windowTitle="Explicit Mount"):
        with mount(Qt.mounts.menu_bar):
            with Qt.CQMenuBar(objectName="main_menu"):
                with mount(Qt.mounts.corner_widget(corner=NativeQt.Corner.TopLeftCorner)):
                    Qt.CQPushButton(
                        f"Corner {count}",
                        objectName="corner_button",
                    )
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                Qt.CQLabel(f"Count: {count}", objectName="count_label")
                Qt.CQPushButton(
                    "Increment",
                    objectName="increment_button",
                    on_clicked=lambda: set_count(lambda current: current + 1),
                )
"""


CONDITIONAL_LAYOUT_SOURCE = """
#@pyrolyze
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import pyrolyze, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


@pyrolyze
def conditional_layout_counter() -> None:
    count, set_count = use_state(0)

    with Qt.CQMainWindow(windowTitle="Conditional Layout Counter"):
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                if count % 2 == 0:
                    Qt.CQLabel(f"Time: {count}", objectName="top_label")
                else:
                    Qt.CQLabel("Count is odd - no time", objectName="top_label")
                with Qt.CQWidget(objectName="count_row_host"):
                    with Qt.CQBoxLayout(QBoxLayout.Direction.LeftToRight):
                        Qt.CQPushButton(
                            "-",
                            objectName="decrement_button",
                            on_clicked=lambda: set_count(lambda current: current - 1),
                        )
                        Qt.CQLabel(f"Count: {count}", objectName="count_label")
                        Qt.CQPushButton(
                            "+",
                            objectName="increment_button",
                            on_clicked=lambda: set_count(lambda current: current + 1),
                        )
                Qt.CQLabel("Description", objectName="bottom_label")
"""


CONDITIONAL_NESTED_LAYOUT_SOURCE = """
#@pyrolyze
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import pyrolyze, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


@pyrolyze
def conditional_nested_layout_counter() -> None:
    count, set_count = use_state(0)

    with Qt.CQMainWindow(windowTitle="Conditional Nested Layout Counter"):
        with Qt.CQWidget(objectName="central_widget"):
            with Qt.CQBoxLayout(QBoxLayout.Direction.TopToBottom):
                if count % 2 == 0:
                    Qt.CQLabel(f"Time: {count}", objectName="top_label")
                else:
                    Qt.CQLabel("Count is odd - no time", objectName="top_label")
                Qt.CQLabel("Page size: 50", objectName="page_label")
                with Qt.CQHBoxLayout(objectName="count_row"):
                    Qt.CQPushButton(
                        "-",
                        objectName="decrement_button",
                        on_clicked=lambda: set_count(lambda current: current - 1),
                    )
                    Qt.CQLabel(f"Count: {count}", objectName="count_label")
                    Qt.CQPushButton(
                        "+",
                        objectName="increment_button",
                        on_clicked=lambda: set_count(lambda current: current + 1),
                    )
                Qt.CQLabel("Description", objectName="bottom_label")
"""


def _load_component():
    namespace = load_transformed_namespace(
        SOURCE,
        module_name="tests.native_counter",
        filename="/virtual/tests/native_counter.py",
    )
    return namespace["native_counter"]


def _load_explicit_mount_component():
    namespace = load_transformed_namespace(
        EXPLICIT_MOUNT_SOURCE,
        module_name="tests.native_explicit_mount",
        filename="/virtual/tests/native_explicit_mount.py",
    )
    return namespace["mounted_window"]


def _load_conditional_layout_component():
    namespace = load_transformed_namespace(
        CONDITIONAL_LAYOUT_SOURCE,
        module_name="tests.native_conditional_layout_counter",
        filename="/virtual/tests/native_conditional_layout_counter.py",
    )
    return namespace["conditional_layout_counter"]


def _load_conditional_nested_layout_component():
    namespace = load_transformed_namespace(
        CONDITIONAL_NESTED_LAYOUT_SOURCE,
        module_name="tests.native_conditional_nested_layout_counter",
        filename="/virtual/tests/native_conditional_nested_layout_counter.py",
    )
    return namespace["conditional_nested_layout_counter"]


def test_native_pyside6_host_mounts_and_rerenders_generated_component_tree() -> None:
    from pyrolyze.pyrolyze_native_pyside6 import create_host, reconcile_window_content

    component = _load_component()
    host = create_host()
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(host, ctx.committed_ui())

    def post_flush(callback):
        QTimer.singleShot(
            0,
            lambda: (
                callback(),
                reconcile_host(),
            ),
        )

    ctx.set_flush_poster(post_flush)
    ctx.mount(lambda: (component._pyrolyze_meta._func(ctx, dirtyof()), reconcile_host()))

    assert isinstance(host.root_widget, QMainWindow)
    label = host.root_widget.findChild(QLabel, "count_label")
    button = host.root_widget.findChild(QPushButton, "increment_button")
    assert label is not None
    assert button is not None
    assert label.text() == "Count: 0"

    button.click()
    for _ in range(10):
        host.app.processEvents()

    label = host.root_widget.findChild(QLabel, "count_label")
    assert label is not None
    assert label.text() == "Count: 1"

    ctx.close_app_contexts()
    host.close()


def test_native_pyside6_host_mounts_explicit_selector_tree_end_to_end() -> None:
    from pyrolyze.pyrolyze_native_pyside6 import create_host, reconcile_window_content

    component = _load_explicit_mount_component()
    host = create_host()
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(host, ctx.committed_ui())

    def post_flush(callback):
        QTimer.singleShot(
            0,
            lambda: (
                callback(),
                reconcile_host(),
            ),
        )

    ctx.set_flush_poster(post_flush)
    ctx.mount(lambda: (component._pyrolyze_meta._func(ctx, dirtyof()), reconcile_host()))

    assert isinstance(host.root_widget, QMainWindow)
    host.show()
    for _ in range(10):
        host.app.processEvents()
    menu_bar = host.root_widget.menuBar()
    assert menu_bar is not None
    assert menu_bar.objectName() == "main_menu"
    assert menu_bar.isVisible() is True
    assert menu_bar.height() > 0
    corner_button = menu_bar.cornerWidget(Qt.Corner.TopLeftCorner)
    assert isinstance(corner_button, QPushButton)
    assert corner_button.objectName() == "corner_button"
    assert corner_button.text() == "Corner 0"

    label = host.root_widget.findChild(QLabel, "count_label")
    button = host.root_widget.findChild(QPushButton, "increment_button")
    assert label is not None
    assert button is not None
    assert label.text() == "Count: 0"

    button.click()
    for _ in range(10):
        host.app.processEvents()

    label = host.root_widget.findChild(QLabel, "count_label")
    assert label is not None
    assert label.text() == "Count: 1"
    corner_button = host.root_widget.menuBar().cornerWidget(Qt.Corner.TopLeftCorner)
    assert isinstance(corner_button, QPushButton)
    assert corner_button.text() == "Corner 1"

    ctx.close_app_contexts()
    host.close()


def test_native_pyside6_conditional_sibling_toggle_keeps_stable_row_order() -> None:
    from pyrolyze.pyrolyze_native_pyside6 import create_host, reconcile_window_content

    component = _load_conditional_layout_component()
    host = create_host()
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(host, ctx.committed_ui())

    def post_flush(callback):
        QTimer.singleShot(
            0,
            lambda: (
                callback(),
                reconcile_host(),
            ),
        )

    ctx.set_flush_poster(post_flush)
    ctx.mount(lambda: (component._pyrolyze_meta._func(ctx, dirtyof()), reconcile_host()))

    assert isinstance(host.root_widget, QMainWindow)
    host.show()
    for _ in range(10):
        host.app.processEvents()

    central = host.root_widget.findChild(QWidget, "central_widget")
    count_row_host = host.root_widget.findChild(QWidget, "count_row_host")
    top_label = host.root_widget.findChild(QLabel, "top_label")
    bottom_label = host.root_widget.findChild(QLabel, "bottom_label")
    increment_button = host.root_widget.findChild(QPushButton, "increment_button")
    count_label = host.root_widget.findChild(QLabel, "count_label")

    assert central is not None
    assert count_row_host is not None
    assert top_label is not None
    assert bottom_label is not None
    assert increment_button is not None
    assert count_label is not None

    layout = central.layout()
    assert layout is not None
    assert layout.indexOf(top_label) == 0
    assert layout.indexOf(count_row_host) == 1
    assert layout.indexOf(bottom_label) == 2

    increment_button.click()
    for _ in range(10):
        host.app.processEvents()

    top_label = host.root_widget.findChild(QLabel, "top_label")
    count_row_host = host.root_widget.findChild(QWidget, "count_row_host")
    bottom_label = host.root_widget.findChild(QLabel, "bottom_label")
    count_label = host.root_widget.findChild(QLabel, "count_label")

    assert top_label is not None
    assert count_row_host is not None
    assert bottom_label is not None
    assert count_label is not None
    assert count_label.text() == "Count: 1"
    assert top_label.text() == "Count is odd - no time"
    assert layout.indexOf(top_label) == 0
    assert layout.indexOf(count_row_host) == 1
    assert layout.indexOf(bottom_label) == 2

    ctx.close_app_contexts()
    host.close()


def test_native_pyside6_conditional_nested_layout_toggle_keeps_row_above_trailing_label() -> None:
    from pyrolyze.pyrolyze_native_pyside6 import create_host, reconcile_window_content

    component = _load_conditional_nested_layout_component()
    host = create_host()
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(host, ctx.committed_ui())

    def post_flush(callback):
        QTimer.singleShot(
            0,
            lambda: (
                callback(),
                reconcile_host(),
            ),
        )

    ctx.set_flush_poster(post_flush)
    ctx.mount(lambda: (component._pyrolyze_meta._func(ctx, dirtyof()), reconcile_host()))

    assert isinstance(host.root_widget, QMainWindow)
    host.show()
    for _ in range(10):
        host.app.processEvents()

    increment_button = host.root_widget.findChild(QPushButton, "increment_button")
    bottom_label = host.root_widget.findChild(QLabel, "bottom_label")
    count_label = host.root_widget.findChild(QLabel, "count_label")

    assert increment_button is not None
    assert bottom_label is not None
    assert count_label is not None

    increment_button.click()
    for _ in range(10):
        host.app.processEvents()

    increment_button = host.root_widget.findChild(QPushButton, "increment_button")
    bottom_label = host.root_widget.findChild(QLabel, "bottom_label")
    count_label = host.root_widget.findChild(QLabel, "count_label")

    assert increment_button is not None
    assert bottom_label is not None
    assert count_label is not None
    assert count_label.text() == "Count: 1"

    row_global_y = increment_button.mapTo(host.root_widget, increment_button.rect().topLeft()).y()
    bottom_global_y = bottom_label.mapTo(host.root_widget, bottom_label.rect().topLeft()).y()

    assert row_global_y < bottom_global_y

    ctx.close_app_contexts()
    host.close()

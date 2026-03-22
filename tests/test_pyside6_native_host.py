from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6.QtCore")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton

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

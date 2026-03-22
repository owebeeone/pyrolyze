from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest

pytest.importorskip("PySide6.QtCore")
pytest.importorskip("PySide6.QtWidgets")

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QMainWindow, QPushButton

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


SOURCE = """
#@pyrolyze
from PySide6.QtWidgets import QBoxLayout

from pyrolyze.api import pyrolyse, use_state
from pyrolyze.backends.pyside6.generated_library import PySide6UiLibrary as Qt


@pyrolyse
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


def _load_component():
    namespace = load_transformed_namespace(
        SOURCE,
        module_name="tests.native_counter",
        filename="/virtual/tests/native_counter.py",
    )
    return namespace["native_counter"]


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

from __future__ import annotations

import pytest

pytest.importorskip("tkinter")
pytest.importorskip("tkinter.ttk")

from tkinter import ttk

from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof


SOURCE = """
#@pyrolyze
from pyrolyze.api import keyed, mount, pyrolyze, use_state
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk

_set_count = None


@pyrolyze
def mounted_notebook() -> None:
    count, set_count = use_state(1)
    global _set_count
    _set_count = set_count

    with Tk.CNotebook():
        for index in keyed(range(count), key=lambda value: value):
            with mount(Tk.mounts.tab):
                Tk.CTtkFrame()
"""


def _load_component():
    namespace = load_transformed_namespace(
        SOURCE,
        module_name="tests.native_tkinter_notebook",
        filename="/virtual/tests/native_tkinter_notebook.py",
    )
    return namespace["mounted_notebook"], namespace


def test_native_tkinter_host_mounts_and_rerenders_explicit_selector_tree_end_to_end() -> None:
    from pyrolyze.pyrolyze_native_tkinter import create_host, reconcile_window_content

    component, namespace = _load_component()
    try:
        host = create_host("Native Tkinter Notebook")
    except Exception as exc:
        pytest.skip(f"Tk root unavailable: {exc}")
    ctx = RenderContext()

    def reconcile_host() -> None:
        reconcile_window_content(host, ctx.committed_ui())

    def post_flush(callback) -> None:
        host.root.after(
            0,
            lambda: (
                callback(),
                reconcile_host(),
            ),
        )

    ctx.set_flush_poster(post_flush)
    ctx.mount(lambda: (component._pyrolyze_meta._func(ctx, dirtyof()), reconcile_host()))

    try:
        assert isinstance(host.root_widget, ttk.Notebook)
        assert len(host.root_widget.tabs()) == 1

        setter = namespace["_set_count"]
        assert callable(setter)
        setter(3)
        for _ in range(10):
            host.root.update_idletasks()
            host.root.update()

        assert len(host.root_widget.tabs()) == 3

        setter(2)
        for _ in range(10):
            host.root.update_idletasks()
            host.root.update()

        assert len(host.root_widget.tabs()) == 2
    finally:
        ctx.close_app_contexts()
        host.close()

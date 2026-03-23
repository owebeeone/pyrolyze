from __future__ import annotations

from types import SimpleNamespace

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


EVENT_RETENTION_SOURCE = """
#@pyrolyze
from tkinter import StringVar

from pyrolyze.api import keyed, mount, pyrolyze, use_state
from pyrolyze.backends.tkinter.generated_library import TkinterUiLibrary as Tk


def _coerce_count(raw_value: str) -> int:
    try:
        return max(0, int(raw_value))
    except ValueError:
        return 0


def _decrement(value: int) -> int:
    return max(0, value - 1)


@pyrolyze
def counter(title: str, count: int, set_count, *, decrement_text: str='-', increment_text: str='+') -> None:
    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(side='left', padx=4, pady=4)):
            Tk.CTtkLabel(text=title)
            Tk.CTtkButton(text=decrement_text, on_command=lambda: set_count(lambda current: _decrement(int(current))))
            Tk.CTtkEntry(
                textvariable=StringVar(value=str(count)),
                width=5,
                on_key_release=lambda event: set_count(_coerce_count(event.widget.get())),
            )
            Tk.CTtkButton(text=increment_text, on_command=lambda: set_count(lambda current: int(current) + 1))


@pyrolyze
def header(cols: int, set_cols, rows: int, set_rows, use_grid: bool, set_use_grid) -> None:
    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(side='left', padx=6, pady=6)):
            Tk.CTtkLabel(text='Grid App')
            counter('Cols', cols, set_cols, decrement_text='Cols -', increment_text='Cols +')
            counter('Rows', rows, set_rows, decrement_text='Rows -', increment_text='Rows +')
            Tk.CTtkButton(
                text='Use Row Layout' if use_grid else 'Use Grid Layout',
                on_command=lambda: set_use_grid(lambda current: not bool(current)),
            )


@pyrolyze
def cell(row_index: int, col_index: int) -> None:
    count, set_count = use_state(0)
    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(side='left', padx=3, pady=3)):
            Tk.CTtkLabel(text=f'R{row_index + 1} C{col_index + 1}')
            Tk.CTtkButton(text='-', on_command=lambda: set_count(lambda current: _decrement(int(current))))
            Tk.CTtkLabel(text=str(count))
            Tk.CTtkButton(text='+', on_command=lambda: set_count(lambda current: int(current) + 1))


@pyrolyze
def grid(cols: int, rows: int, use_grid: bool) -> None:
    with Tk.CTtkFrame():
        if use_grid:
            for row_index in keyed(range(rows), key=lambda value: value):
                for col_index in keyed(range(cols), key=lambda value: value):
                    with mount(Tk.mounts.grid(row=row_index, column=col_index, padx=6, pady=6)):
                        cell(row_index, col_index)
        else:
            for row_index in keyed(range(rows), key=lambda value: value):
                with Tk.CTtkFrame():
                    with mount(Tk.mounts.pack(side='left', padx=6, pady=6)):
                        for col_index in keyed(range(cols), key=lambda value: value):
                            cell(row_index, col_index)


@pyrolyze
def mounted_event_retention_app() -> None:
    cols, set_cols = use_state(2)
    rows, set_rows = use_state(2)
    use_grid, set_use_grid = use_state(False)

    with Tk.CTtkFrame():
        with mount(Tk.mounts.pack(fill='x', padx=8, pady=8)):
            header(cols, set_cols, rows, set_rows, use_grid, set_use_grid)
        with mount(Tk.mounts.pack(fill='both', expand=True, padx=8, pady=8)):
            grid(cols, rows, use_grid)
"""


def _load_component():
    namespace = load_transformed_namespace(
        SOURCE,
        module_name="tests.native_tkinter_notebook",
        filename="/virtual/tests/native_tkinter_notebook.py",
    )
    return namespace["mounted_notebook"], namespace


def _load_event_retention_component():
    namespace = load_transformed_namespace(
        EVENT_RETENTION_SOURCE,
        module_name="tests.native_tkinter_event_retention",
        filename="/virtual/tests/native_tkinter_event_retention.py",
    )
    return namespace["mounted_event_retention_app"], namespace


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
        assert not bool(host.root.winfo_viewable())
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


def test_native_tkinter_host_preserves_live_event_handlers_for_clean_skipped_subtrees() -> None:
    from pyrolyze.pyrolyze_native_tkinter import create_host, reconcile_window_content

    component, _namespace = _load_event_retention_component()
    try:
        host = create_host("Native Tkinter Event Retention")
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

    def _pump() -> None:
        for _ in range(10):
            host.root.update_idletasks()
            host.root.update()

    def _walk(widget):
        yield widget
        for child in widget.winfo_children():
            yield from _walk(child)

    def _dispatch_entry_key_release(entry, *, keysym: str) -> None:
        callback = host.engine._engine._event_callbacks[id(entry)]["on_key_release"]
        assert callable(callback)
        callback(SimpleNamespace(widget=entry, keysym=keysym))

    try:
        _pump()
        assert not bool(host.root.winfo_viewable())

        entries = [widget for widget in _walk(host.root) if isinstance(widget, ttk.Entry)]
        assert len(entries) == 2
        entries[0].delete(0, "end")
        entries[0].insert(0, "3")
        _dispatch_entry_key_release(entries[0], keysym="3")
        entries[1].delete(0, "end")
        entries[1].insert(0, "1")
        _dispatch_entry_key_release(entries[1], keysym="1")
        _pump()

        toggle = next(
            widget
            for widget in _walk(host.root)
            if isinstance(widget, ttk.Button) and str(widget.cget("text")) == "Use Grid Layout"
        )
        toggle.invoke()
        _pump()

        toggles = [
            widget
            for widget in _walk(host.root)
            if isinstance(widget, ttk.Button) and str(widget.cget("text")) == "Use Row Layout"
        ]
        assert len(toggles) == 1
        assert sum(1 for widget in _walk(host.root) if widget.winfo_manager() == "grid") >= 3
    finally:
        ctx.close_app_contexts()
        host.close()

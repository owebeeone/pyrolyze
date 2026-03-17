"""tkinter helpers for mounting frozen v1 PyRolyze UIElements."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import subprocess
import sys
from typing import Any, Callable, Mapping, Sequence

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.ui_nodes import UiNodeSpec, normalize_ui_elements


_module_registry = ModuleRegistry()
_UI_MODULE_ID = _module_registry.module_id("pyrolyze.pyrolyze_tkinter")
_UI_OWNER_SLOT = SlotId(_UI_MODULE_ID, 1)
_TK_ROOT: Any | None = None


@dataclass(slots=True)
class PyrolyzeTkWindow:
    root: Any
    content_frame: Any

    def show(self) -> None:
        self.root.deiconify()

    def close(self) -> None:
        self.root.destroy()

    def run(self) -> None:
        self.show()
        self.root.mainloop()


@lru_cache(maxsize=1)
def tkinter_available() -> bool:
    probe = (
        "import tkinter as tk;"
        "root = tk.Tk();"
        "root.withdraw();"
        "root.destroy()"
    )
    completed = subprocess.run(
        [sys.executable, "-c", probe],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.returncode == 0


def create_window(title: str) -> PyrolyzeTkWindow:
    tk, ttk = _load_tk_modules()
    root = tk.Tk()
    root.withdraw()
    root.title(title)
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True)
    return PyrolyzeTkWindow(root=root, content_frame=frame)


def set_window_content(host: PyrolyzeTkWindow, widgets: Sequence[Any]) -> None:
    for child in tuple(host.content_frame.winfo_children()):
        child.destroy()
    for widget in widgets:
        widget.pack(fill="x")


def render_ui_element(
    element: UIElement | Mapping[str, Any],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> Any:
    spec = normalize_ui_elements(_UI_OWNER_SLOT, (_coerce_ui_element(element),))[0]
    return _render_ui_spec(spec, parent=_get_hidden_root(), on_after_event=on_after_event)


def render_ui_elements(
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> list[Any]:
    specs = normalize_ui_elements(
        _UI_OWNER_SLOT,
        tuple(_coerce_ui_element(element) for element in elements),
    )
    parent = _get_hidden_root()
    return [_render_ui_spec(spec, parent=parent, on_after_event=on_after_event) for spec in specs]


def _render_ui_spec(
    spec: UiNodeSpec,
    *,
    parent: Any,
    on_after_event: Callable[[], None] | None,
) -> Any:
    tk, ttk = _load_tk_modules()

    if spec.kind == "section":
        frame = ttk.LabelFrame(parent, text=str(spec.props["title"]))
        for child in spec.children:
            _render_ui_spec(child, parent=frame, on_after_event=on_after_event).pack(fill="x")
        return frame

    if spec.kind == "row":
        frame = ttk.Frame(parent)
        headline = ttk.Label(frame, text=str(spec.props["headline"]))
        headline.pack(side="left")
        for child in spec.children:
            _render_ui_spec(child, parent=frame, on_after_event=on_after_event).pack(side="left")
        return frame

    if spec.kind == "badge":
        return ttk.Label(parent, text=str(spec.props["text"]))

    if spec.kind == "button":
        button = ttk.Button(parent, text=str(spec.props["label"]))
        if not bool(spec.props["enabled"]):
            button.state(["disabled"])
        on_press = spec.event_props.get("on_press")
        if callable(on_press):
            button.configure(command=lambda: _dispatch(on_press, on_after_event=on_after_event))
        return button

    if spec.kind == "text_field":
        frame = ttk.Frame(parent)
        ttk.Label(frame, text=str(spec.props["label"])).pack(fill="x")
        variable = tk.StringVar(master=frame, value=str(spec.props["value"]))
        entry = ttk.Entry(frame, textvariable=variable)
        if not bool(spec.props["enabled"]):
            entry.state(["disabled"])
        placeholder = spec.props.get("placeholder")
        if placeholder:
            entry.insert(0, str(placeholder))
        guard = {"active": False}
        on_change = spec.event_props.get("on_change")
        if callable(on_change):
            def traced(*_args: Any) -> None:
                if guard["active"]:
                    return
                _dispatch(on_change, variable.get(), on_after_event=on_after_event)

            variable.trace_add("write", traced)
        on_submit = spec.event_props.get("on_submit")
        if callable(on_submit):
            entry.bind(
                "<Return>",
                lambda _event: _dispatch(on_submit, on_after_event=on_after_event),
            )
        entry.pack(fill="x")
        return frame

    if spec.kind == "toggle":
        variable = tk.BooleanVar(master=parent, value=bool(spec.props["checked"]))
        button = ttk.Checkbutton(parent, text=str(spec.props["label"]), variable=variable)
        if not bool(spec.props["enabled"]):
            button.state(["disabled"])
        on_toggle = spec.event_props.get("on_toggle")
        if callable(on_toggle):
            button.configure(
                command=lambda: _dispatch(
                    on_toggle,
                    bool(variable.get()),
                    on_after_event=on_after_event,
                )
            )
        return button

    raise ValueError(f"Unsupported semantic node kind: {spec.kind!r}")


def _dispatch(
    callback: Callable[..., Any],
    payload: Any = None,
    *,
    on_after_event: Callable[[], None] | None,
) -> None:
    if payload is None:
        callback()
    else:
        callback(payload)
    if callable(on_after_event):
        on_after_event()


def _load_tk_modules() -> tuple[Any, Any]:
    if not tkinter_available():
        raise RuntimeError("tkinter root is unavailable in this environment")
    import tkinter as tk
    from tkinter import ttk

    return tk, ttk


def _get_hidden_root() -> Any:
    global _TK_ROOT
    if _TK_ROOT is None:
        tk, _ = _load_tk_modules()
        _TK_ROOT = tk.Tk()
        _TK_ROOT.withdraw()
    return _TK_ROOT


def _coerce_ui_element(value: UIElement | Mapping[str, Any]) -> UIElement:
    if isinstance(value, UIElement):
        return value
    if not isinstance(value, Mapping):
        raise TypeError(f"expected UIElement or mapping, got {type(value).__name__}")

    kind = str(value.get("kind", ""))
    props = dict(value.get("props", {}) or value.get("values", {}) or {})
    if kind == "row" and "row_id" in value and "row_id" not in props:
        props["row_id"] = value["row_id"]
    children = tuple(_coerce_ui_element(child) for child in value.get("children", ()))
    return UIElement(kind=kind, props=props, children=children)


__all__ = [
    "PyrolyzeTkWindow",
    "create_window",
    "render_ui_element",
    "render_ui_elements",
    "set_window_content",
    "tkinter_available",
]

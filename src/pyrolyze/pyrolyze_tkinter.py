"""tkinter helpers for mounting frozen v1 PyRolyze UIElements."""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
import os
import sys
import time
import weakref
from typing import Any, Callable, Mapping, Protocol, Sequence, cast

from pyrolyze.api import UIElement
from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.mount_reconciler import mount_subtree, reconcile_owner
from pyrolyze.runtime.trace import TraceChannel, emit_trace, trace_enabled
from pyrolyze.runtime.ui_nodes import (
    UiBackendAdapter,
    UiNode,
    UiNodeBinding,
    UiNodeSpec,
    UiOwnerCommitState,
    normalize_ui_inputs,
)


_module_registry = ModuleRegistry()
_UI_MODULE_ID = _module_registry.module_id("pyrolyze.pyrolyze_tkinter")
_UI_OWNER_SLOT = SlotId(_UI_MODULE_ID, 1)
_TK_ROOT: Any | None = None
_TK_LAYOUT_METRICS: dict[str, int] = {
    "pack_requests": 0,
    "pack_apply": 0,
    "pack_forget": 0,
    "repack": 0,
    "hidden_skip": 0,
    "detach_unpacked": 0,
}

_TK_SCALING_SHIM = """
namespace eval ::tk {}
if {[llength [info commands ::tk::ScalingPct]] == 0} {
    proc ::tk::ScalingPct {} { return 100 }
}
"""


@dataclass(slots=True)
class _TkPackState:
    packed_widgets: list[Any] = field(default_factory=list)
    index_by_widget_id: dict[int, int] = field(default_factory=dict)


_TK_PACK_STATES: weakref.WeakKeyDictionary[Any, _TkPackState] = weakref.WeakKeyDictionary()


class _TkNodeMapper(Protocol):
    kind: str

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding: ...

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None: ...


@dataclass(slots=True)
class PyrolyzeTkWindow:
    root: Any
    content_frame: Any
    owner_state: UiOwnerCommitState | None = None

    def show(self) -> None:
        self.root.deiconify()

    def close(self) -> None:
        self.root.destroy()

    def run(self) -> None:
        self.show()
        self.root.mainloop()


@lru_cache(maxsize=1)
def tkinter_available() -> bool:
    trace_reconcile = trace_enabled(TraceChannel.RECONCILE)
    if trace_reconcile:
        emit_trace(
            TraceChannel.RECONCILE,
            "tk_probe_start",
            pid=os.getpid(),
            executable=sys.executable,
        )
    try:
        root = _create_tk_root()
    except Exception as exc:
        if trace_reconcile:
            emit_trace(
                TraceChannel.RECONCILE,
                "tk_probe_end",
                pid=os.getpid(),
                ok=False,
                error=str(exc)[:240],
            )
        return False
    root.destroy()
    if trace_reconcile:
        emit_trace(
            TraceChannel.RECONCILE,
            "tk_probe_end",
            pid=os.getpid(),
            ok=True,
        )
    return True


def create_window(title: str) -> PyrolyzeTkWindow:
    tk, ttk = _load_tk_modules()
    root = _create_tk_root(tk)
    root.title(title)
    frame = ttk.Frame(root)
    frame.pack(fill="both", expand=True)
    return PyrolyzeTkWindow(root=root, content_frame=frame)


def set_window_content(host: PyrolyzeTkWindow, widgets: Sequence[Any]) -> None:
    host.owner_state = None
    _drop_pack_state(host.content_frame)
    for child in tuple(host.content_frame.winfo_children()):
        child.destroy()
    for widget in widgets:
        widget.pack(fill="x")


@dataclass(eq=False, slots=True, kw_only=True)
class _TkRootBinding(UiNodeBinding):
    container: Any
    child_side: str = "top"
    child_fill: str = "x"

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        return None

    def place_child(self, child: UiNode, index: int) -> None:
        _pack_child(
            self.container,
            _binding_widget(child.binding),
            index=index,
            side=self.child_side,
            fill=self.child_fill,
        )

    def detach_child(self, child: UiNode) -> None:
        widget = _binding_widget(child.binding)
        if widget.winfo_manager() == "pack":
            _pack_forget(widget, reason="detach")

    def dispose(self) -> None:
        return None


@dataclass(eq=False, slots=True, kw_only=True)
class _TkBindingBase(UiNodeBinding):
    widget: Any
    child_side: str = "top"
    child_fill: str = "x"
    accepts_children: bool = False

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        return None

    def place_child(self, child: UiNode, index: int) -> None:
        if not self.accepts_children:
            raise ValueError(f"{type(self).__name__} does not accept children")
        _pack_child(
            self.widget,
            _binding_widget(child.binding),
            index=index,
            side=self.child_side,
            fill=self.child_fill,
        )

    def detach_child(self, child: UiNode) -> None:
        if not self.accepts_children:
            return
        widget = _binding_widget(child.binding)
        if widget.winfo_manager() == "pack":
            _pack_forget(widget, reason="detach")

    def dispose(self) -> None:
        _drop_pack_state(self.widget)
        self.widget.destroy()


@dataclass(eq=False, slots=True, kw_only=True)
class _TkSectionBinding(_TkBindingBase):
    mapper: _TkNodeMapper
    widget: Any
    accepts_children: bool = True

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        self.mapper.update_binding(
            self,
            next_spec,
            changed_props=changed_props,
            changed_events=changed_events,
        )


@dataclass(eq=False, slots=True, kw_only=True)
class _TkRowBinding(_TkBindingBase):
    mapper: _TkNodeMapper
    widget: Any
    headline: Any
    child_side: str = "left"
    child_fill: str = "none"
    accepts_children: bool = True

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        self.mapper.update_binding(
            self,
            next_spec,
            changed_props=changed_props,
            changed_events=changed_events,
        )


@dataclass(eq=False, slots=True, kw_only=True)
class _TkBadgeBinding(_TkBindingBase):
    mapper: _TkNodeMapper
    widget: Any

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        self.mapper.update_binding(
            self,
            next_spec,
            changed_props=changed_props,
            changed_events=changed_events,
        )


@dataclass(eq=False, slots=True, kw_only=True)
class _TkButtonBinding(_TkBindingBase):
    mapper: _TkNodeMapper
    widget: Any
    on_after_event: Callable[[], None] | None
    on_press: Callable[..., None] | None = None

    def __post_init__(self) -> None:
        self.widget.configure(command=self._handle_press)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        self.mapper.update_binding(
            self,
            next_spec,
            changed_props=changed_props,
            changed_events=changed_events,
        )

    def _handle_press(self) -> None:
        if callable(self.on_press):
            _dispatch(self.on_press, on_after_event=self.on_after_event)


@dataclass(eq=False, slots=True, kw_only=True)
class _TkTextFieldBinding(_TkBindingBase):
    mapper: _TkNodeMapper
    widget: Any
    label: Any
    variable: Any
    entry: Any
    on_after_event: Callable[[], None] | None
    on_change: Callable[..., None] | None = None
    on_submit: Callable[..., None] | None = None
    suppress_events: bool = False

    def __post_init__(self) -> None:
        self.variable.trace_add("write", self._handle_variable_change)
        self.entry.bind("<Return>", self._handle_submit)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        self.mapper.update_binding(
            self,
            next_spec,
            changed_props=changed_props,
            changed_events=changed_events,
        )

    def _handle_variable_change(self, *_args: Any) -> None:
        if self.suppress_events or not callable(self.on_change):
            return
        _dispatch(
            self.on_change,
            self.variable.get(),
            on_after_event=self.on_after_event,
        )

    def _handle_submit(self, _event: Any) -> None:
        if callable(self.on_submit):
            _dispatch(self.on_submit, on_after_event=self.on_after_event)


@dataclass(eq=False, slots=True, kw_only=True)
class _TkToggleBinding(_TkBindingBase):
    mapper: _TkNodeMapper
    widget: Any
    variable: Any
    on_after_event: Callable[[], None] | None
    on_toggle: Callable[..., None] | None = None
    suppress_events: bool = False

    def __post_init__(self) -> None:
        self.widget.configure(command=self._handle_toggle)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        self.mapper.update_binding(
            self,
            next_spec,
            changed_props=changed_props,
            changed_events=changed_events,
        )

    def _handle_toggle(self) -> None:
        if self.suppress_events or not callable(self.on_toggle):
            return
        _dispatch(
            self.on_toggle,
            bool(self.variable.get()),
            on_after_event=self.on_after_event,
        )


@dataclass(eq=False, slots=True, kw_only=True)
class _TkSelectFieldBinding(_TkBindingBase):
    mapper: _TkNodeMapper
    widget: Any
    label: Any
    variable: Any
    combo_box: Any
    on_after_event: Callable[[], None] | None
    on_change: Callable[..., None] | None = None
    suppress_events: bool = False

    def __post_init__(self) -> None:
        self.variable.trace_add("write", self._handle_variable_change)

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        self.mapper.update_binding(
            self,
            next_spec,
            changed_props=changed_props,
            changed_events=changed_events,
        )

    def _handle_variable_change(self, *_args: Any) -> None:
        if self.suppress_events or not callable(self.on_change):
            return
        _dispatch(
            self.on_change,
            self.variable.get(),
            on_after_event=self.on_after_event,
        )


@dataclass(frozen=True, slots=True)
class _TkSectionMapper:
    kind: str = "section"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        parent = _parent_widget(parent_binding)
        frame = backend.ttk.LabelFrame(parent, text=str(spec.props["title"]))
        style_name = _section_style_name(spec.props.get("accent"))
        if style_name is not None:
            frame.configure(style=style_name)
        _set_visible_flag(frame, bool(spec.props["visible"]))
        return _TkSectionBinding(mapper=self, widget=frame)

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        del changed_events
        section = cast(_TkSectionBinding, binding)
        if "title" in changed_props:
            section.widget.configure(text=str(next_spec.props["title"]))
        if "accent" in changed_props:
            section.widget.configure(style=_section_style_name(next_spec.props.get("accent")))
        if "visible" in changed_props:
            _set_visible_flag(section.widget, bool(next_spec.props["visible"]))


@dataclass(frozen=True, slots=True)
class _TkRowMapper:
    kind: str = "row"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        parent = _parent_widget(parent_binding)
        frame = backend.ttk.Frame(parent)
        headline = backend.ttk.Label(frame, text=str(spec.props["headline"]))
        headline.pack(side="left")
        _set_visible_flag(frame, bool(spec.props["visible"]))
        return _TkRowBinding(mapper=self, widget=frame, headline=headline)

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        del changed_events
        row = cast(_TkRowBinding, binding)
        if "headline" in changed_props:
            row.headline.configure(text=str(next_spec.props["headline"]))
        if "visible" in changed_props:
            _set_visible_flag(row.widget, bool(next_spec.props["visible"]))


@dataclass(frozen=True, slots=True)
class _TkBadgeMapper:
    kind: str = "badge"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        parent = _parent_widget(parent_binding)
        label = backend.ttk.Label(parent, text=str(spec.props["text"]))
        _set_visible_flag(label, bool(spec.props["visible"]))
        return _TkBadgeBinding(mapper=self, widget=label)

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        del changed_events
        badge = cast(_TkBadgeBinding, binding)
        if "text" in changed_props:
            badge.widget.configure(text=str(next_spec.props["text"]))
        if "visible" in changed_props:
            _set_visible_flag(badge.widget, bool(next_spec.props["visible"]))


@dataclass(frozen=True, slots=True)
class _TkButtonMapper:
    kind: str = "button"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        parent = _parent_widget(parent_binding)
        button = backend.ttk.Button(parent, text=str(spec.props["label"]))
        _set_widget_enabled(button, bool(spec.props["enabled"]))
        _set_visible_flag(button, bool(spec.props["visible"]))
        return _TkButtonBinding(
            mapper=self,
            widget=button,
            on_after_event=backend.on_after_event,
            on_press=spec.event_props.get("on_press"),
        )

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        button = cast(_TkButtonBinding, binding)
        if "label" in changed_props:
            button.widget.configure(text=str(next_spec.props["label"]))
        if "enabled" in changed_props:
            _set_widget_enabled(button.widget, bool(next_spec.props["enabled"]))
        if "visible" in changed_props:
            _set_visible_flag(button.widget, bool(next_spec.props["visible"]))
        if "on_press" in changed_events:
            button.on_press = next_spec.event_props.get("on_press")


@dataclass(frozen=True, slots=True)
class _TkTextFieldMapper:
    kind: str = "text_field"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        parent = _parent_widget(parent_binding)
        frame = backend.ttk.Frame(parent)
        label = backend.ttk.Label(frame, text=str(spec.props["label"]))
        label.pack(fill="x")
        variable = backend.tk.StringVar(master=frame, value=str(spec.props["value"]))
        entry = backend.ttk.Entry(frame, textvariable=variable)
        _set_widget_enabled(entry, bool(spec.props["enabled"]))
        entry.pack(fill="x")
        _set_visible_flag(frame, bool(spec.props["visible"]))
        return _TkTextFieldBinding(
            mapper=self,
            widget=frame,
            label=label,
            variable=variable,
            entry=entry,
            on_after_event=backend.on_after_event,
            on_change=spec.event_props.get("on_change"),
            on_submit=spec.event_props.get("on_submit"),
        )

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        field = cast(_TkTextFieldBinding, binding)
        if "label" in changed_props:
            field.label.configure(text=str(next_spec.props["label"]))
        if "value" in changed_props:
            next_value = str(next_spec.props["value"])
            if field.variable.get() != next_value:
                field.suppress_events = True
                field.variable.set(next_value)
                field.suppress_events = False
        if "enabled" in changed_props:
            _set_widget_enabled(field.entry, bool(next_spec.props["enabled"]))
        if "visible" in changed_props:
            _set_visible_flag(field.widget, bool(next_spec.props["visible"]))
        if "on_change" in changed_events:
            field.on_change = next_spec.event_props.get("on_change")
        if "on_submit" in changed_events:
            field.on_submit = next_spec.event_props.get("on_submit")


@dataclass(frozen=True, slots=True)
class _TkToggleMapper:
    kind: str = "toggle"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        parent = _parent_widget(parent_binding)
        variable = backend.tk.BooleanVar(master=parent, value=bool(spec.props["checked"]))
        button = backend.ttk.Checkbutton(parent, text=str(spec.props["label"]), variable=variable)
        _set_widget_enabled(button, bool(spec.props["enabled"]))
        _set_visible_flag(button, bool(spec.props["visible"]))
        return _TkToggleBinding(
            mapper=self,
            widget=button,
            variable=variable,
            on_after_event=backend.on_after_event,
            on_toggle=spec.event_props.get("on_toggle"),
        )

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        toggle = cast(_TkToggleBinding, binding)
        if "label" in changed_props:
            toggle.widget.configure(text=str(next_spec.props["label"]))
        if "checked" in changed_props:
            toggle.suppress_events = True
            toggle.variable.set(bool(next_spec.props["checked"]))
            toggle.suppress_events = False
        if "enabled" in changed_props:
            _set_widget_enabled(toggle.widget, bool(next_spec.props["enabled"]))
        if "visible" in changed_props:
            _set_visible_flag(toggle.widget, bool(next_spec.props["visible"]))
        if "on_toggle" in changed_events:
            toggle.on_toggle = next_spec.event_props.get("on_toggle")


@dataclass(frozen=True, slots=True)
class _TkSelectFieldMapper:
    kind: str = "select_field"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_TkBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        parent = _parent_widget(parent_binding)
        frame = backend.ttk.Frame(parent)
        label = backend.ttk.Label(frame, text=str(spec.props["label"]))
        label.pack(fill="x")
        variable = backend.tk.StringVar(master=frame, value=str(spec.props["value"]))
        combo_box = backend.ttk.Combobox(
            frame,
            textvariable=variable,
            values=tuple(str(option) for option in tuple(spec.props["options"])),
            state="readonly" if bool(spec.props["enabled"]) else "disabled",
        )
        combo_box.pack(fill="x")
        _set_visible_flag(frame, bool(spec.props["visible"]))
        return _TkSelectFieldBinding(
            mapper=self,
            widget=frame,
            label=label,
            variable=variable,
            combo_box=combo_box,
            on_after_event=backend.on_after_event,
            on_change=spec.event_props.get("on_change"),
        )

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        select = cast(_TkSelectFieldBinding, binding)
        if "label" in changed_props:
            select.label.configure(text=str(next_spec.props["label"]))
        if "options" in changed_props:
            select.combo_box.configure(values=tuple(str(option) for option in tuple(next_spec.props["options"])))
        if "value" in changed_props or "options" in changed_props:
            next_value = str(next_spec.props["value"])
            if select.variable.get() != next_value:
                select.suppress_events = True
                select.variable.set(next_value)
                select.suppress_events = False
        if "enabled" in changed_props:
            select.combo_box.configure(state="readonly" if bool(next_spec.props["enabled"]) else "disabled")
        if "visible" in changed_props:
            _set_visible_flag(select.widget, bool(next_spec.props["visible"]))
        if "on_change" in changed_events:
            select.on_change = next_spec.event_props.get("on_change")


_TK_KIND_MAPPERS: dict[str, _TkNodeMapper] = {
    "section": _TkSectionMapper(),
    "row": _TkRowMapper(),
    "badge": _TkBadgeMapper(),
    "button": _TkButtonMapper(),
    "text_field": _TkTextFieldMapper(),
    "toggle": _TkToggleMapper(),
    "select_field": _TkSelectFieldMapper(),
}


@dataclass(slots=True)
class _TkBackend(UiBackendAdapter):
    tk: Any
    ttk: Any
    on_after_event: Callable[[], None] | None = None
    backend_id: str = "tkinter"
    mappers: Mapping[str, _TkNodeMapper] = field(default_factory=lambda: _TK_KIND_MAPPERS)

    def _mapper_for(self, kind: str) -> _TkNodeMapper:
        mapper = self.mappers.get(kind)
        if mapper is None:
            raise ValueError(f"Unsupported semantic node kind: {kind!r}")
        return mapper

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        return self._mapper_for(spec.kind).create_binding(
            spec,
            backend=self,
            parent_binding=parent_binding,
        )

    def can_reuse(self, current: UiNode, next_spec: UiNodeSpec) -> bool:
        return current.spec.kind == next_spec.kind

    def assert_ui_thread(self) -> None:
        return None

    def post_to_ui(self, callback: Callable[[], None]) -> None:
        callback()


def reconcile_window_content(
    host: PyrolyzeTkWindow,
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> None:
    specs = normalize_ui_inputs(_UI_OWNER_SLOT, tuple(elements))
    trace_reconcile = trace_enabled(TraceChannel.RECONCILE)
    metrics_before = _layout_metrics_snapshot() if trace_reconcile else None
    started_at = time.perf_counter() if trace_reconcile else 0.0
    if host.owner_state is None:
        for child in tuple(host.content_frame.winfo_children()):
            child.destroy()
        host.owner_state = UiOwnerCommitState(owner_id=_UI_OWNER_SLOT)
    tk, ttk = _load_tk_modules()
    reconcile_owner(
        host.owner_state,
        specs,
        backend=_TkBackend(tk=tk, ttk=ttk, on_after_event=on_after_event),
        parent_binding=_TkRootBinding(container=host.content_frame),
    )
    if trace_reconcile and metrics_before is not None and host.owner_state is not None:
        metrics_after = _layout_metrics_snapshot()
        emit_trace(
            TraceChannel.RECONCILE,
            "tk_layout",
            specs=len(specs),
            root_nodes=len(host.owner_state.mounted_nodes),
            duration_ms=round((time.perf_counter() - started_at) * 1000.0, 3),
            **_layout_metrics_delta(metrics_before, metrics_after),
        )


def render_ui_element(
    element: UIElement | Mapping[str, Any],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> Any:
    return render_ui_elements((element,), on_after_event=on_after_event)[0]


def render_ui_elements(
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> list[Any]:
    tk, ttk = _load_tk_modules()
    backend = _TkBackend(tk=tk, ttk=ttk, on_after_event=on_after_event)
    hidden_root_binding = _TkRootBinding(container=_get_hidden_root())
    specs = normalize_ui_inputs(_UI_OWNER_SLOT, tuple(elements))
    widgets: list[Any] = []
    for spec in specs:
        node = mount_subtree(spec, backend=backend, parent_binding=hidden_root_binding)
        widget = _binding_widget(node.binding)
        setattr(widget, "_pyrolyze_node", node)
        widgets.append(widget)
    return widgets


def render_semantic_node(
    node: Mapping[str, Any],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> Any:
    return render_ui_element(node, on_after_event=on_after_event)


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


def _binding_widget(binding: UiNodeBinding) -> Any:
    widget = getattr(binding, "widget", None)
    if widget is None:
        raise TypeError(f"binding {type(binding).__name__} does not expose a widget")
    return widget


def _parent_widget(parent_binding: UiNodeBinding | None) -> Any:
    if parent_binding is None:
        return _get_hidden_root()
    container = getattr(parent_binding, "container", None)
    if container is not None:
        return container
    return _binding_widget(parent_binding)


def _pack_child(container: Any, widget: Any, *, index: int, side: str, fill: str) -> None:
    _layout_metric_inc("pack_requests")
    state = _pack_state(container)
    if not bool(getattr(widget, "_pyrolyze_visible", True)):
        if widget.winfo_manager() == "pack":
            _pack_forget(widget, reason="hidden")
        _layout_metric_inc("hidden_skip")
        return

    target_index, desired_before, desired_after = _desired_pack_neighbors(
        state,
        widget,
        index=index,
    )
    pack_kwargs: dict[str, Any] = {"side": side}
    if fill != "none":
        pack_kwargs["fill"] = fill

    widget_id = id(widget)
    current_index = state.index_by_widget_id.get(widget_id)
    if widget.winfo_manager() == "pack" and current_index is None:
        state = _resync_pack_state(container)
        current_index = state.index_by_widget_id.get(widget_id)

    if widget.winfo_manager() == "pack":
        if _pack_state_matches(state, widget, desired_before=desired_before, side=side, fill=fill):
            return
        if desired_before is not None:
            widget.pack_configure(before=desired_before, **pack_kwargs)
        else:
            if desired_after is not None:
                widget.pack_configure(after=desired_after, **pack_kwargs)
            else:
                widget.pack_configure(**pack_kwargs)
        _pack_state_reposition(
            state,
            widget,
            target_index=target_index,
            current_index=current_index,
        )
        _layout_metric_inc("repack")
        _layout_metric_inc("pack_apply")
        return

    if desired_before is not None:
        widget.pack(before=desired_before, **pack_kwargs)
    elif desired_after is not None:
        widget.pack(after=desired_after, **pack_kwargs)
    else:
        widget.pack(**pack_kwargs)
    _pack_state_reposition(
        state,
        widget,
        target_index=target_index,
        current_index=None,
    )
    _layout_metric_inc("pack_apply")


def _pack_forget(widget: Any, *, reason: str) -> None:
    container = _pack_parent_container(widget)
    if container is not None:
        state = _pack_state_or_none(container)
        if state is not None:
            _pack_state_remove(state, widget)
    widget.pack_forget()
    _layout_metric_inc("pack_forget")
    if reason == "detach":
        _layout_metric_inc("detach_unpacked")


def _layout_metric_inc(name: str, amount: int = 1) -> None:
    _TK_LAYOUT_METRICS[name] = _TK_LAYOUT_METRICS.get(name, 0) + amount


def _pack_state(container: Any) -> _TkPackState:
    state = _pack_state_or_none(container)
    if state is not None:
        return state
    return _register_pack_state(container, _build_pack_state(container))


def _pack_state_or_none(container: Any) -> _TkPackState | None:
    try:
        return _TK_PACK_STATES.get(container)
    except TypeError:
        return None


def _register_pack_state(container: Any, state: _TkPackState) -> _TkPackState:
    try:
        _TK_PACK_STATES[container] = state
    except TypeError:
        return state
    return state


def _drop_pack_state(container: Any) -> None:
    try:
        _TK_PACK_STATES.pop(container, None)
    except TypeError:
        return


def _build_pack_state(container: Any) -> _TkPackState:
    packed_widgets = list(container.pack_slaves())
    return _TkPackState(
        packed_widgets=packed_widgets,
        index_by_widget_id={id(widget): index for index, widget in enumerate(packed_widgets)},
    )


def _resync_pack_state(container: Any) -> _TkPackState:
    return _register_pack_state(container, _build_pack_state(container))


def _pack_parent_container(widget: Any) -> Any | None:
    container = getattr(widget, "container", None)
    if container is not None and callable(getattr(container, "pack_slaves", None)):
        return container
    container = getattr(widget, "master", None)
    if container is not None and callable(getattr(container, "pack_slaves", None)):
        return container
    return None


def _desired_pack_neighbors(
    state: _TkPackState,
    widget: Any,
    *,
    index: int,
) -> tuple[int, Any | None, Any | None]:
    current_index = state.index_by_widget_id.get(id(widget))
    if current_index is None:
        packed_without = list(state.packed_widgets)
    else:
        packed_without = [
            child for idx, child in enumerate(state.packed_widgets) if idx != current_index
        ]

    target_index = max(0, min(index, len(packed_without)))
    desired_before = packed_without[target_index] if target_index < len(packed_without) else None
    desired_after = packed_without[target_index - 1] if target_index > 0 else None
    return target_index, desired_before, desired_after


def _pack_state_reposition(
    state: _TkPackState,
    widget: Any,
    *,
    target_index: int,
    current_index: int | None,
) -> None:
    widget_id = id(widget)
    if current_index is None:
        current_index = state.index_by_widget_id.get(widget_id)
    if current_index is not None:
        if current_index < len(state.packed_widgets):
            state.packed_widgets.pop(current_index)
        state.index_by_widget_id.pop(widget_id, None)
        if target_index > len(state.packed_widgets):
            target_index = len(state.packed_widgets)
    state.packed_widgets.insert(target_index, widget)
    start = target_index if current_index is None else min(target_index, current_index)
    _reindex_pack_state(state, start=start)


def _pack_state_remove(state: _TkPackState, widget: Any) -> None:
    widget_id = id(widget)
    current_index = state.index_by_widget_id.pop(widget_id, None)
    if current_index is None:
        return
    if current_index < len(state.packed_widgets):
        state.packed_widgets.pop(current_index)
        _reindex_pack_state(state, start=current_index)


def _reindex_pack_state(state: _TkPackState, *, start: int = 0) -> None:
    for index in range(max(0, start), len(state.packed_widgets)):
        state.index_by_widget_id[id(state.packed_widgets[index])] = index


def _pack_state_matches(
    state: _TkPackState,
    widget: Any,
    *,
    desired_before: Any | None,
    side: str,
    fill: str,
) -> bool:
    position = state.index_by_widget_id.get(id(widget))
    if position is None:
        return False
    current_next = state.packed_widgets[position + 1] if position + 1 < len(state.packed_widgets) else None
    if current_next is not desired_before:
        return False

    info = widget.pack_info()
    current_side = str(info.get("side", "top"))
    current_fill = str(info.get("fill", "none") or "none")
    return current_side == side and current_fill == fill


def _layout_metrics_snapshot() -> dict[str, int]:
    return dict(_TK_LAYOUT_METRICS)


def _layout_metrics_delta(before: Mapping[str, int], after: Mapping[str, int]) -> dict[str, int]:
    keys = set(before.keys()) | set(after.keys())
    return {key: int(after.get(key, 0)) - int(before.get(key, 0)) for key in sorted(keys)}


def _set_widget_enabled(widget: Any, enabled: bool) -> None:
    try:
        widget.configure(state="normal" if enabled else "disabled")
    except Exception:
        widget.state(["!disabled"] if enabled else ["disabled"])


def _set_visible_flag(widget: Any, visible: bool) -> None:
    setattr(widget, "_pyrolyze_visible", bool(visible))
    if not visible and widget.winfo_manager() == "pack":
        _pack_forget(widget, reason="hidden")


def _section_style_name(accent: Any) -> str | None:
    if accent is None:
        return None
    _, ttk = _load_tk_modules()
    style_name = f"Pyrolyze.{str(accent).title()}.TLabelframe"
    style = ttk.Style()
    style.configure(style_name, foreground=str(accent))
    return style_name


def _load_tk_modules() -> tuple[Any, Any]:
    if not tkinter_available():
        raise RuntimeError("tkinter root is unavailable in this environment")
    import tkinter as tk
    from tkinter import ttk

    return tk, ttk


def _create_tk_root(tk: Any | None = None) -> Any:
    if tk is None:
        import tkinter as tk
    root = tk.Tk(useTk=False)
    try:
        root.tk.eval(_TK_SCALING_SHIM)
        root.loadtk()
        root.withdraw()
        return root
    except Exception:
        try:
            root.destroy()
        except Exception:
            pass
        raise


def _get_hidden_root() -> Any:
    global _TK_ROOT
    if _TK_ROOT is None:
        tk, _ = _load_tk_modules()
        _TK_ROOT = _create_tk_root(tk)
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
    "reconcile_window_content",
    "render_ui_element",
    "render_ui_elements",
    "render_semantic_node",
    "set_window_content",
    "tkinter_available",
]

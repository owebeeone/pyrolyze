"""DearPyGui helpers for mounting semantic v1 ``UIElement`` trees (``section``, ``row``, …).

Mirrors :mod:`pyrolyze.pyrolyze_pyside6` / :mod:`pyrolyze.pyrolyze_tkinter`: the Pyrolyze compiler
emits the same semantic widget kinds; this module maps them to DearPyGui items via
:class:`~pyrolyze.backends.dearpygui.live_host.LiveDpgHost`.

Requires optional dependency ``dearpygui`` (``uv run --extra dpg ...``).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol, Sequence, cast

from pyrolyze.api import UIElement
from pyrolyze.backends.dearpygui.live_host import LiveDpgHost
from pyrolyze.runtime.context import ModuleRegistry, SlotId
from pyrolyze.runtime.mount_reconciler import mount_subtree, reconcile_owner
from pyrolyze.runtime.ui_nodes import (
    UiBackendAdapter,
    UiNode,
    UiNodeBinding,
    UiNodeSpec,
    UiOwnerCommitState,
    normalize_ui_inputs,
)


_module_registry = ModuleRegistry()
_UI_MODULE_ID = _module_registry.module_id("pyrolyze.pyrolyze_dearpygui")
_UI_OWNER_SLOT = SlotId(_UI_MODULE_ID, 1)
_MAIN_WINDOW_SLOT = "pyrolyze:semantic:main_window"


class _DpgNodeMapper(Protocol):
    kind: str

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_DpgBackend",
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


def _binding_tag(binding: UiNodeBinding) -> int:
    tag = getattr(binding, "tag", None)
    if tag is None:
        msg = f"binding {type(binding).__name__!r} has no DearPyGui tag"
        raise TypeError(msg)
    return int(tag)


def _dpg_place_child(
    host: LiveDpgHost,
    *,
    parent_tag: int,
    child_tag: int,
    index: int,
    child_offset: int,
) -> None:
    sibs = [t for t in host.children_order.get(int(parent_tag), []) if t != int(child_tag)]
    insert_pos = min(child_offset + index, len(sibs))
    before: int = 0
    if insert_pos < len(sibs):
        before = int(sibs[insert_pos])
    host.move_item(child_tag, parent=parent_tag, before=before)


def _dispatch_ui(
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


@dataclass(eq=False, slots=True, kw_only=True)
class _DpgRootBinding(UiNodeBinding):
    host: LiveDpgHost
    window_tag: int

    def update_props(
        self,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        return None

    def place_child(self, child: UiNode, index: int) -> None:
        _dpg_place_child(
            self.host,
            parent_tag=int(self.window_tag),
            child_tag=_binding_tag(child.binding),
            index=index,
            child_offset=0,
        )

    def detach_child(self, child: UiNode) -> None:
        self.host.move_item(
            _binding_tag(child.binding),
            parent=int(self.host.staging_tag),
            before=0,
        )

    def dispose(self) -> None:
        return None


@dataclass(eq=False, slots=True, kw_only=True)
class _DpgSectionBinding(UiNodeBinding):
    host: LiveDpgHost
    tag: int
    mapper: _DpgNodeMapper
    child_offset: int = 1

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

    def place_child(self, child: UiNode, index: int) -> None:
        _dpg_place_child(
            self.host,
            parent_tag=self.tag,
            child_tag=_binding_tag(child.binding),
            index=index,
            child_offset=self.child_offset,
        )

    def detach_child(self, child: UiNode) -> None:
        self.host.move_item(
            _binding_tag(child.binding),
            parent=int(self.host.staging_tag),
            before=0,
        )

    def dispose(self) -> None:
        self.host.delete_item(self.tag)


@dataclass(eq=False, slots=True, kw_only=True)
class _DpgRowBinding(_DpgSectionBinding):
    headline_tag: int


@dataclass(eq=False, slots=True, kw_only=True)
class _DpgButtonBinding(UiNodeBinding):
    host: LiveDpgHost
    tag: int
    mapper: _DpgNodeMapper
    on_after_event: Callable[[], None] | None
    on_press: Callable[..., None] | None = None

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

    def place_child(self, child: UiNode, index: int) -> None:
        raise RuntimeError("DpgButtonBinding does not accept children")

    def detach_child(self, child: UiNode) -> None:
        return None

    def dispose(self) -> None:
        self.host.delete_item(self.tag)

    def _handle_press(self, *_args: Any) -> None:
        if callable(self.on_press):
            _dispatch_ui(self.on_press, None, on_after_event=self.on_after_event)


@dataclass(eq=False, slots=True, kw_only=True)
class _DpgTextFieldBinding(UiNodeBinding):
    host: LiveDpgHost
    tag: int
    input_tag: int
    mapper: _DpgNodeMapper
    on_after_event: Callable[[], None] | None
    on_change: Callable[..., None] | None = None
    on_submit: Callable[..., None] | None = None
    suppress_events: bool = False

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

    def place_child(self, child: UiNode, index: int) -> None:
        raise RuntimeError("DpgTextFieldBinding does not accept children")

    def detach_child(self, child: UiNode) -> None:
        return None

    def dispose(self) -> None:
        self.host.delete_item(self.tag)

    def _handle_change(self, _sender: Any, app_data: Any, _user_data: Any) -> None:
        if self.suppress_events or not callable(self.on_change):
            return
        _dispatch_ui(self.on_change, str(app_data), on_after_event=self.on_after_event)


@dataclass(frozen=True, slots=True)
class _DpgSectionMapper:
    kind: str = "section"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_DpgBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        host = backend.host
        gtag = int(host.create_with_factory("add_group", slot_id=spec.node_id))
        title_tag = int(
            host.create_with_factory(
                "add_text",
                slot_id=(spec.node_id, "section_title"),
                default_value=str(spec.props["title"]),
                wrap=0,
            )
        )
        host.move_item(title_tag, parent=gtag, before=0)
        dpg = host._require_dpg()
        dpg.configure_item(gtag, show=bool(spec.props["visible"]))
        return _DpgSectionBinding(host=host, tag=gtag, mapper=self, child_offset=1)

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        del changed_events
        section = cast(_DpgSectionBinding, binding)
        dpg = section.host._require_dpg()
        if "title" in changed_props:
            # Title is first child text item
            children = dpg.get_item_children(section.tag) or []
            if children:
                dpg.configure_item(children[0], default_value=str(next_spec.props["title"]))
        if "visible" in changed_props:
            dpg.configure_item(section.tag, show=bool(next_spec.props["visible"]))


@dataclass(frozen=True, slots=True)
class _DpgRowMapper:
    kind: str = "row"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_DpgBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        del parent_binding
        host = backend.host
        gtag = int(host.create_with_factory("add_group", slot_id=spec.node_id, horizontal=True))
        headline_tag = int(
            host.create_with_factory(
                "add_text",
                slot_id=(spec.node_id, "row_headline"),
                default_value=str(spec.props["headline"]),
                wrap=220,
            )
        )
        host.move_item(headline_tag, parent=gtag, before=0)
        dpg = host._require_dpg()
        dpg.configure_item(gtag, show=bool(spec.props["visible"]))
        return _DpgRowBinding(host=host, tag=gtag, mapper=self, child_offset=1, headline_tag=headline_tag)

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        del changed_events
        row = cast(_DpgRowBinding, binding)
        dpg = row.host._require_dpg()
        if "headline" in changed_props:
            dpg.configure_item(row.headline_tag, default_value=str(next_spec.props["headline"]))
        if "visible" in changed_props:
            dpg.configure_item(row.tag, show=bool(next_spec.props["visible"]))


@dataclass(frozen=True, slots=True)
class _DpgButtonMapper:
    kind: str = "button"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_DpgBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        del parent_binding
        host = backend.host
        bref: list[_DpgButtonBinding | None] = [None]

        def _cb(*_args: Any) -> None:
            b = bref[0]
            if b is not None:
                b._handle_press()

        btag = int(
            host.create_with_factory(
                "add_button",
                slot_id=spec.node_id,
                label=str(spec.props["label"]),
                callback=_cb,
            )
        )
        binding = _DpgButtonBinding(
            host=host,
            tag=btag,
            mapper=self,
            on_after_event=backend.on_after_event,
            on_press=spec.event_props.get("on_press"),
        )
        bref[0] = binding
        dpg = host._require_dpg()
        dpg.configure_item(btag, show=bool(spec.props["visible"]))
        dpg.configure_item(btag, enabled=bool(spec.props["enabled"]))
        return binding

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        btn = cast(_DpgButtonBinding, binding)
        dpg = btn.host._require_dpg()
        if "label" in changed_props:
            dpg.configure_item(btn.tag, label=str(next_spec.props["label"]))
        if "enabled" in changed_props:
            dpg.configure_item(btn.tag, enabled=bool(next_spec.props["enabled"]))
        if "visible" in changed_props:
            dpg.configure_item(btn.tag, show=bool(next_spec.props["visible"]))
        if "on_press" in changed_events:
            btn.on_press = next_spec.event_props.get("on_press")


@dataclass(frozen=True, slots=True)
class _DpgTextFieldMapper:
    kind: str = "text_field"

    def create_binding(
        self,
        spec: UiNodeSpec,
        *,
        backend: "_DpgBackend",
        parent_binding: UiNodeBinding | None,
    ) -> UiNodeBinding:
        del parent_binding
        host = backend.host
        gtag = int(host.create_with_factory("add_group", slot_id=(spec.node_id, "field_shell")))
        label_tag = int(
            host.create_with_factory(
                "add_text",
                slot_id=(spec.node_id, "field_label"),
                default_value=str(spec.props["label"]),
                wrap=400,
            )
        )
        host.move_item(label_tag, parent=gtag, before=0)
        fref: list[_DpgTextFieldBinding | None] = [None]

        def _cb(sender: Any, app_data: Any, user_data: Any) -> None:
            b = fref[0]
            if b is not None:
                b._handle_change(sender, app_data, user_data)

        itag = int(
            host.create_with_factory(
                "add_input_text",
                slot_id=spec.node_id,
                label="",
                default_value=str(spec.props["value"]),
                width=120,
                callback=_cb,
            )
        )
        binding = _DpgTextFieldBinding(
            host=host,
            tag=gtag,
            input_tag=itag,
            mapper=self,
            on_after_event=backend.on_after_event,
            on_change=spec.event_props.get("on_change"),
            on_submit=spec.event_props.get("on_submit"),
        )
        fref[0] = binding
        dpg = host._require_dpg()
        host.move_item(itag, parent=gtag, before=0)
        dpg.configure_item(gtag, show=bool(spec.props["visible"]))
        dpg.configure_item(itag, enabled=bool(spec.props["enabled"]))
        return binding

    def update_binding(
        self,
        binding: UiNodeBinding,
        next_spec: UiNodeSpec,
        *,
        changed_props: Mapping[str, Any],
        changed_events: Mapping[str, Callable[..., None] | None],
    ) -> None:
        field = cast(_DpgTextFieldBinding, binding)
        dpg = field.host._require_dpg()
        if "label" in changed_props:
            children = dpg.get_item_children(field.tag) or []
            if children:
                dpg.configure_item(children[0], default_value=str(next_spec.props["label"]))
        if "value" in changed_props:
            next_value = str(next_spec.props["value"])
            current = dpg.get_value(field.input_tag)
            if str(current) != next_value:
                field.suppress_events = True
                dpg.set_value(field.input_tag, next_value)
                field.suppress_events = False
        if "enabled" in changed_props:
            dpg.configure_item(field.input_tag, enabled=bool(next_spec.props["enabled"]))
        if "visible" in changed_props:
            dpg.configure_item(field.tag, show=bool(next_spec.props["visible"]))
        if "on_change" in changed_events:
            field.on_change = next_spec.event_props.get("on_change")
        if "on_submit" in changed_events:
            field.on_submit = next_spec.event_props.get("on_submit")


_DPG_KIND_MAPPERS: dict[str, _DpgNodeMapper] = {
    "section": _DpgSectionMapper(),
    "row": _DpgRowMapper(),
    "button": _DpgButtonMapper(),
    "text_field": _DpgTextFieldMapper(),
}


@dataclass(slots=True)
class _DpgBackend(UiBackendAdapter):
    host: LiveDpgHost
    on_after_event: Callable[[], None] | None = None
    backend_id: str = "dearpygui"
    mappers: Mapping[str, _DpgNodeMapper] = field(default_factory=lambda: _DPG_KIND_MAPPERS)

    def _mapper_for(self, kind: str) -> _DpgNodeMapper:
        mapper = self.mappers.get(kind)
        if mapper is None:
            raise ValueError(f"Unsupported semantic node kind for DearPyGui: {kind!r}")
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


@dataclass(slots=True)
class PyrolyzeDpgWindow:
    """DearPyGui viewport + main window + semantic reconciliation state."""

    host: LiveDpgHost
    window_tag: int
    owner_state: UiOwnerCommitState | None = None

    def run(self) -> None:
        self.host._require_dpg().start_dearpygui()

    def close(self) -> None:
        self.owner_state = None
        self.host.stop()


def create_window(
    title: str,
    *,
    width: int = 960,
    height: int = 720,
    show_viewport: bool = True,
) -> PyrolyzeDpgWindow:
    """Start DearPyGui and create a primary ``add_window`` for semantic content."""

    dpg_host = LiveDpgHost(
        title=title,
        width=width,
        height=height,
        show_viewport=show_viewport,
    )
    dpg_host.start()
    dpg = dpg_host._require_dpg()
    win_tag = int(
        dpg.add_window(
            label=title,
            width=width,
            height=height,
            tag=dpg_host.allocate_tag(_MAIN_WINDOW_SLOT),
        )
    )
    return PyrolyzeDpgWindow(host=dpg_host, window_tag=win_tag, owner_state=None)


def reconcile_window_content(
    host: PyrolyzeDpgWindow,
    elements: Sequence[UIElement | Mapping[str, Any]],
    *,
    on_after_event: Callable[[], None] | None = None,
) -> None:
    """Mount or update semantic widgets under the main DearPyGui window."""

    specs = normalize_ui_inputs(_UI_OWNER_SLOT, tuple(elements))
    dpg = host.host._require_dpg()
    if host.owner_state is None:
        for cid in tuple(dpg.get_item_children(host.window_tag) or ()):
            if dpg.does_item_exist(cid):
                host.host.delete_item(int(cid))
        host.owner_state = UiOwnerCommitState(owner_id=_UI_OWNER_SLOT)
    reconcile_owner(
        host.owner_state,
        specs,
        backend=_DpgBackend(host=host.host, on_after_event=on_after_event),
        parent_binding=_DpgRootBinding(host=host.host, window_tag=host.window_tag),
    )


__all__ = [
    "PyrolyzeDpgWindow",
    "create_window",
    "reconcile_window_content",
]

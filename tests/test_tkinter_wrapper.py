from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from pyrolyze.api import UIElement
from pyrolyze.pyrolyze_tkinter import (
    _layout_metrics_delta,
    _layout_metrics_snapshot,
    _pack_child,
    create_window,
    reconcile_window_content,
    render_ui_element,
    render_semantic_node,
    tkinter_available,
)


@dataclass(frozen=True)
class _SlotRef:
    owner: str
    slot_kind: str
    index: int


def _semantic_badge(*, owner: str, index: int, text: str) -> dict[str, object]:
    return {
        "kind": "badge",
        "slot_id": _SlotRef(owner=owner, slot_kind="widget", index=index),
        "values": {"text": text, "tone": "info"},
    }


def _semantic_button(*, owner: str, index: int, label: str) -> dict[str, object]:
    return {
        "kind": "button",
        "slot_id": _SlotRef(owner=owner, slot_kind="widget", index=index),
        "values": {"label": label, "enabled": True, "tone": "default"},
    }


def test_tkinter_available_reports_host_support_as_bool() -> None:
    assert isinstance(tkinter_available(), bool)


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_render_ui_element_builds_tk_button_from_frozen_v1_schema() -> None:
    widget = render_ui_element(
        UIElement(
            kind="button",
            props={"label": "Run", "enabled": False, "visible": True},
        )
    )

    assert str(widget.cget("text")) == "Run"
    assert str(widget.cget("state")) == "disabled"


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_render_semantic_node_builds_tk_select_field_widget() -> None:
    widget = render_semantic_node(
        {
            "kind": "select_field",
            "field_id": "location",
            "slot_id": _SlotRef(owner="weather", slot_kind="widget", index=1),
            "values": {
                "label": "Location",
                "value": "Berlin",
                "options": ("Berlin", "Paris"),
                "enabled": True,
            },
        }
    )

    combo = next(
        child for child in widget.winfo_children() if child.winfo_class() in {"TCombobox", "Combobox"}
    )

    assert str(combo.get()) == "Berlin"
    assert tuple(combo.cget("values")) == ("Berlin", "Paris")


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_reconcile_window_content_updates_badge_in_place() -> None:
    host = create_window("Retained Badge")

    reconcile_window_content(host, [_semantic_badge(owner="root", index=1, text="One")])
    first_widget = host.content_frame.winfo_children()[0]

    reconcile_window_content(host, [_semantic_badge(owner="root", index=1, text="Two")])
    second_widget = host.content_frame.winfo_children()[0]

    assert second_widget is first_widget
    assert str(second_widget.cget("text")) == "Two"

    host.close()


@pytest.mark.skipif(not tkinter_available(), reason="Tk root unavailable in this environment")
def test_reconcile_window_content_reorders_reused_widgets() -> None:
    host = create_window("Retained Reorder")
    first_nodes = [
        _semantic_button(owner="root", index=1, label="One"),
        _semantic_button(owner="root", index=2, label="Two"),
    ]

    reconcile_window_content(host, first_nodes)
    first_widget, second_widget = tuple(host.content_frame.pack_slaves())

    reconcile_window_content(host, list(reversed(first_nodes)))

    assert tuple(host.content_frame.pack_slaves()) == (second_widget, first_widget)

    host.close()


@dataclass(eq=False, slots=True)
class _FakeWidget:
    name: str
    container: "_FakeContainer | None" = None
    manager: str = ""
    side: str = "top"
    fill: str = "none"
    _pyrolyze_visible: bool = True
    pack_calls: list[dict[str, object]] = field(default_factory=list)
    pack_configure_calls: list[dict[str, object]] = field(default_factory=list)
    pack_forget_calls: int = 0

    def winfo_manager(self) -> str:
        return self.manager

    def pack_info(self) -> dict[str, object]:
        return {"side": self.side, "fill": self.fill}

    def pack(self, **kwargs: object) -> None:
        self.pack_calls.append(dict(kwargs))
        self._apply_pack_kwargs(kwargs)

    def pack_configure(self, **kwargs: object) -> None:
        self.pack_configure_calls.append(dict(kwargs))
        self._apply_pack_kwargs(kwargs)

    def pack_forget(self) -> None:
        self.pack_forget_calls += 1
        self.manager = ""
        if self.container is not None:
            self.container.remove(self)

    def _apply_pack_kwargs(self, kwargs: dict[str, object]) -> None:
        self.manager = "pack"
        self.side = str(kwargs.get("side", self.side))
        self.fill = str(kwargs.get("fill", self.fill))
        if self.container is not None:
            self.container.place(self, before=kwargs.get("before"), after=kwargs.get("after"))


@dataclass(slots=True)
class _FakeContainer:
    packed: list[_FakeWidget]

    def __post_init__(self) -> None:
        for widget in self.packed:
            widget.container = self
            widget.manager = "pack"

    def pack_slaves(self) -> list[_FakeWidget]:
        return list(self.packed)

    def remove(self, widget: _FakeWidget) -> None:
        if widget in self.packed:
            self.packed.remove(widget)

    def place(
        self,
        widget: _FakeWidget,
        *,
        before: object | None = None,
        after: object | None = None,
    ) -> None:
        if widget in self.packed:
            self.packed.remove(widget)
        if isinstance(before, _FakeWidget):
            index = self.packed.index(before)
            self.packed.insert(index, widget)
            return
        if isinstance(after, _FakeWidget):
            index = self.packed.index(after) + 1
            self.packed.insert(index, widget)
            return
        self.packed.append(widget)


def test_pack_child_noops_when_already_packed_in_correct_state() -> None:
    first = _FakeWidget("first", manager="pack", side="left", fill="x")
    second = _FakeWidget("second", manager="pack", side="left", fill="x")
    container = _FakeContainer([first, second])
    before = _layout_metrics_snapshot()

    _pack_child(container, second, index=1, side="left", fill="x")

    delta = _layout_metrics_delta(before, _layout_metrics_snapshot())
    assert second.pack_calls == []
    assert second.pack_configure_calls == []
    assert second.pack_forget_calls == 0
    assert delta["pack_requests"] == 1
    assert delta["pack_apply"] == 0
    assert delta["repack"] == 0
    assert delta["pack_forget"] == 0
    assert container.pack_slaves() == [first, second]


def test_pack_child_reorders_existing_widget_with_pack_configure() -> None:
    first = _FakeWidget("first", manager="pack", side="left", fill="x")
    second = _FakeWidget("second", manager="pack", side="left", fill="x")
    third = _FakeWidget("third", manager="pack", side="left", fill="x")
    container = _FakeContainer([first, second, third])
    before = _layout_metrics_snapshot()

    _pack_child(container, third, index=0, side="left", fill="x")

    delta = _layout_metrics_delta(before, _layout_metrics_snapshot())
    assert third.pack_calls == []
    assert len(third.pack_configure_calls) == 1
    assert third.pack_configure_calls[0].get("before") is first
    assert third.pack_forget_calls == 0
    assert delta["pack_apply"] == 1
    assert delta["repack"] == 1
    assert delta["pack_forget"] == 0
    assert container.pack_slaves() == [third, first, second]


def test_pack_child_hides_visible_false_widget_by_forgetting_pack() -> None:
    first = _FakeWidget("first", manager="pack", side="left", fill="x", _pyrolyze_visible=False)
    container = _FakeContainer([first])
    before = _layout_metrics_snapshot()

    _pack_child(container, first, index=0, side="left", fill="x")

    delta = _layout_metrics_delta(before, _layout_metrics_snapshot())
    assert first.pack_calls == []
    assert first.pack_configure_calls == []
    assert first.pack_forget_calls == 1
    assert delta["hidden_skip"] == 1
    assert delta["pack_forget"] == 1
    assert container.pack_slaves() == []

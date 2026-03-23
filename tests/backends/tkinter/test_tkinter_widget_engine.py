from __future__ import annotations

from types import SimpleNamespace

from frozendict import frozendict
import pytest

from pyrolyze.api import UIElement
from pyrolyze.backends.model import (
    AccessorKind,
    ChildPolicy,
    EventPayloadPolicy,
    MountPointSpec,
    MountReplayKind,
    PropMode,
    TypeRef,
    UiEventSpec,
    UiParamSpec,
    UiPropSpec,
    UiWidgetSpec,
)
from pyrolyze.backends.tkinter.engine import MountedWidgetNode, TkinterWidgetEngine, WidgetNodeKey
from pyrolyze.pyrolyze_tkinter import _create_tk_root


@pytest.fixture(scope="module")
def tk_root():
    tkinter = pytest.importorskip("tkinter")
    ttk = pytest.importorskip("tkinter.ttk")
    try:
        root = _create_tk_root(tkinter)
    except Exception as exc:
        pytest.skip(f"Tk root unavailable: {exc}")
    yield tkinter, ttk, root
    root.destroy()


def _button_spec() -> UiWidgetSpec:
    return UiWidgetSpec(
        kind="Button",
        mounted_type_name="tkinter.ttk.Button",
        constructor_params=frozendict(
            {
                "master": UiParamSpec(name="master", annotation=TypeRef("object")),
            }
        ),
        props=frozendict(
            {
                "master": UiPropSpec(
                    name="master",
                    annotation=TypeRef("object"),
                    mode=PropMode.CREATE_ONLY_REMOUNT,
                    constructor_name="master",
                    affects_identity=True,
                ),
                "text": UiPropSpec(
                    name="text",
                    annotation=TypeRef("str"),
                    mode=PropMode.CREATE_UPDATE,
                    setter_kind=AccessorKind.TK_CONFIG,
                    setter_name="configure",
                    getter_kind=AccessorKind.TK_CONFIG,
                    getter_name="cget",
                ),
                "state": UiPropSpec(
                    name="state",
                    annotation=TypeRef("str"),
                    mode=PropMode.CREATE_UPDATE,
                    setter_kind=AccessorKind.TK_CONFIG,
                    setter_name="configure",
                    getter_kind=AccessorKind.TK_CONFIG,
                    getter_name="cget",
                ),
            }
        ),
        methods=frozendict(),
        child_policy=ChildPolicy.NONE,
    )


def _event_button_spec() -> UiWidgetSpec:
    return UiWidgetSpec(
        kind="Button",
        mounted_type_name="tkinter.Button",
        constructor_params=frozendict(
            {
                "master": UiParamSpec(name="master", annotation=TypeRef("object")),
            }
        ),
        props=frozendict(
            {
                "master": UiPropSpec(
                    name="master",
                    annotation=TypeRef("object"),
                    mode=PropMode.CREATE_ONLY_REMOUNT,
                    constructor_name="master",
                    affects_identity=True,
                ),
                "text": UiPropSpec(
                    name="text",
                    annotation=TypeRef("str"),
                    mode=PropMode.CREATE_UPDATE,
                    setter_kind=AccessorKind.TK_CONFIG,
                    setter_name="configure",
                    getter_kind=AccessorKind.TK_CONFIG,
                    getter_name="cget",
                ),
            }
        ),
        methods=frozendict(),
        events=frozendict(
            {
                "on_command": UiEventSpec(
                    name="on_command",
                    signal_name="command",
                    payload_policy=EventPayloadPolicy.NONE,
                )
            }
        ),
        child_policy=ChildPolicy.NONE,
    )


def _frame_spec() -> UiWidgetSpec:
    return UiWidgetSpec(
        kind="Frame",
        mounted_type_name="tkinter.Frame",
        constructor_params=frozendict(),
        props=frozendict(),
        methods=frozendict(),
        events=frozendict(),
        mount_points=frozendict(
            {
                "pack": MountPointSpec(
                    name="pack",
                    accepted_produced_type=TypeRef("tkinter.Widget"),
                    sync_method_name="pack",
                    append_method_name="pack",
                    detach_method_name="pack_forget",
                    replay_kind=MountReplayKind.NONE,
                    prefer_sync=True,
                )
            }
        ),
        default_child_mount_point_name="pack",
        default_attach_mount_point_names=("pack",),
        child_policy=ChildPolicy.NONE,
    )


def _entry_spec() -> UiWidgetSpec:
    return UiWidgetSpec(
        kind="Entry",
        mounted_type_name="tkinter.Entry",
        constructor_params=frozendict(),
        props=frozendict(),
        methods=frozendict(),
        events=frozendict(
            {
                "on_key_release": UiEventSpec(
                    name="on_key_release",
                    signal_name="bind:<KeyRelease>",
                    payload_policy=EventPayloadPolicy.FIRST_ARG,
                )
            }
        ),
        child_policy=ChildPolicy.NONE,
    )


def test_mount_builds_widget_from_custom_tk_spec(tk_root) -> None:
    tkinter, _ttk, root = tk_root
    frame = tkinter.Frame(root)
    frame.pack()
    engine = TkinterWidgetEngine({"Button": _button_spec()})

    node = engine.mount(
        UIElement(kind="Button", props={"master": frame, "text": "Save", "state": "disabled"}),
        slot_id=("root", "button", 1),
        call_site_id=17,
    )

    assert isinstance(node, MountedWidgetNode)
    assert node.key == WidgetNodeKey(slot_id=("root", "button", 1), call_site_id=17, kind="Button")
    assert str(node.widget.cget("text")) == "Save"
    assert str(node.widget.cget("state")) == "disabled"
    assert node.effective_props == {"master": frame, "text": "Save", "state": "disabled"}


def test_update_reuses_widget_and_updates_config_props(tk_root) -> None:
    tkinter, _ttk, root = tk_root
    frame = tkinter.Frame(root)
    frame.pack()
    engine = TkinterWidgetEngine({"Button": _button_spec()})
    node = engine.mount(
        UIElement(kind="Button", props={"master": frame, "text": "Save", "state": "normal"}),
        slot_id=("root", "button", 1),
        call_site_id=17,
    )
    original_widget = node.widget

    updated = engine.update(
        node,
        UIElement(kind="Button", props={"text": "Run", "state": "disabled"}),
    )

    assert updated is node
    assert updated.widget is original_widget
    assert str(updated.widget.cget("text")) == "Run"
    assert str(updated.widget.cget("state")) == "disabled"
    assert updated.effective_props == {"master": frame, "text": "Run", "state": "disabled"}


def test_update_remounts_when_master_changes(tk_root) -> None:
    tkinter, _ttk, root = tk_root
    frame_a = tkinter.Frame(root)
    frame_a.pack()
    frame_b = tkinter.Frame(root)
    frame_b.pack()
    engine = TkinterWidgetEngine({"Button": _button_spec()})
    node = engine.mount(
        UIElement(kind="Button", props={"master": frame_a, "text": "Save", "state": "normal"}),
        slot_id=("root", "button", 1),
        call_site_id=17,
    )
    original_widget = node.widget

    updated = engine.update(
        node,
        UIElement(kind="Button", props={"master": frame_b, "text": "Save", "state": "normal"}),
    )

    assert updated is node
    assert updated.widget is not original_widget
    assert updated.widget.master is frame_b
    assert updated.effective_props == {"master": frame_b, "text": "Save", "state": "normal"}


def test_mount_connects_tk_command_event_and_dispatches_latest_callback(tk_root) -> None:
    _tkinter, _ttk, _root = tk_root
    engine = TkinterWidgetEngine({"Button": _event_button_spec()})
    calls: list[str] = []

    node = engine.mount(
        UIElement(
            kind="Button",
            props={"text": "Run", "on_command": lambda: calls.append("first")},
        ),
        slot_id=("root", "button", 1),
        call_site_id=17,
    )

    node.widget.invoke()
    assert calls == ["first"]

    engine.update(
        node,
        UIElement(
            kind="Button",
            props={"text": "Run", "on_command": lambda: calls.append("second")},
        ),
    )
    node.widget.invoke()

    assert calls == ["first", "second"]


def test_mount_builds_frame_children_with_default_pack_mount(tk_root) -> None:
    tkinter, _ttk, _root = tk_root
    engine = TkinterWidgetEngine(
        {
            "Frame": _frame_spec(),
            "Button": _event_button_spec(),
        }
    )

    node = engine.mount(
        UIElement(
            kind="Frame",
            props={},
            children=(
                UIElement(kind="Button", props={"text": "A"}),
                UIElement(kind="Button", props={"text": "B"}),
            ),
        ),
        slot_id=("root", "frame", 1),
        call_site_id=23,
    )

    assert isinstance(node.widget, tkinter.Frame)
    assert node._mountable_node is not None
    child_nodes = node._mountable_node.child_nodes
    assert [child.mountable.cget("text") for child in child_nodes] == ["A", "B"]
    assert [child.mountable.master for child in child_nodes] == [node.widget, node.widget]
    assert [child.mountable.winfo_manager() for child in child_nodes] == ["pack", "pack"]


def test_mount_connects_tk_bind_event_and_dispatches_current_callback(tk_root) -> None:
    _tkinter, _ttk, root = tk_root
    engine = TkinterWidgetEngine({"Entry": _entry_spec()})
    payloads: list[object] = []

    node = engine.mount(
        UIElement(
            kind="Entry",
            props={"on_key_release": lambda event: payloads.append(event)},
        ),
        slot_id=("root", "entry", 1),
        call_site_id=31,
    )
    node.widget.pack()
    root.update_idletasks()
    root.update()
    assert node.widget.bind("<KeyRelease>")
    callback = engine._engine._event_callbacks[id(node.widget)]["on_key_release"]
    assert callable(callback)
    callback(SimpleNamespace(widget=node.widget, keysym="a"))

    assert len(payloads) == 1

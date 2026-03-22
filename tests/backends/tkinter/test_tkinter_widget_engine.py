from __future__ import annotations

from frozendict import frozendict
import pytest

from pyrolyze.api import UIElement
from pyrolyze.backends.model import AccessorKind, ChildPolicy, PropMode, TypeRef, UiParamSpec, UiPropSpec, UiWidgetSpec
from pyrolyze.backends.tkinter.engine import MountedWidgetNode, TkinterWidgetEngine, WidgetNodeKey


@pytest.fixture(scope="module")
def tk_root():
    tkinter = pytest.importorskip("tkinter")
    ttk = pytest.importorskip("tkinter.ttk")
    try:
        root = tkinter.Tk()
        root.withdraw()
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

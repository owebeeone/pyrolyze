"""Phases 3–5: DearPyGui adapter items, event wiring, and structural mounts (recording host)."""

from __future__ import annotations

from pyrolyze.api import MISSING, UIElement
from pyrolyze.backends.dearpygui.engine import DpgMountableEngine, connect_dpg_event_signal
from pyrolyze.backends.dearpygui.host import (
    RecordingDpgHost,
    dpg_host_reset,
    dpg_host_token,
    dpg_slot_reset,
    dpg_slot_token,
)
from pyrolyze.backends.dearpygui.items import DpgButtonItem, DpgWindowItem
from pyrolyze.backends.dearpygui.specs import FIXTURE_WIDGET_SPECS
from pyrolyze.backends.model import EventPayloadPolicy, UiEventSpec


def _engine() -> tuple[DpgMountableEngine, RecordingDpgHost]:
    host = RecordingDpgHost()
    return DpgMountableEngine(FIXTURE_WIDGET_SPECS, host), host


def test_phase3_dispose_deletes_item() -> None:
    host = RecordingDpgHost()
    tok = dpg_host_token(host)
    st = dpg_slot_token("x")
    try:
        b = DpgButtonItem(label="Z")
        tag = int(b.tag)
        b.dispose()
    finally:
        dpg_slot_reset(st)
        dpg_host_reset(tok)
    assert any(op[0] == "delete_item" and op[1]["item"] == tag for op in host.operations)


def test_phase3_config_vs_value_accessors() -> None:
    eng, host = _engine()
    node = eng.mount(
        UIElement(kind="DpgInputText", props={"label": "L", "value": "one"}, slot_id="in"),
    )
    assert host.value_shadow[int(node.mountable.tag)] == "one"
    eng.update(node, UIElement(kind="DpgInputText", props={"value": "two"}, slot_id="in"))
    assert host.value_shadow[int(node.mountable.tag)] == "two"
    eng.update(node, UIElement(kind="DpgInputText", props={"width": 120}, slot_id="in"))
    assert host.config_shadow[int(node.mountable.tag)].get("width") == 120


def test_phase3_tag_stable_across_updates() -> None:
    eng, _host = _engine()
    el = UIElement(kind="DpgButton", props={"label": "A"}, slot_id="slot-a")
    n = eng.mount(el)
    tag = n.mountable.tag
    eng.update(n, UIElement(kind="DpgButton", props={"label": "B"}, slot_id="slot-a"))
    assert n.mountable.tag == tag


def test_phase3_read_dpg_value_and_config() -> None:
    eng, _host = _engine()
    n = eng.mount(UIElement(kind="DpgInputText", props={"value": "ro"}, slot_id="r"))
    read = eng._read_dpg_prop(n.mountable, n.spec, "value")
    assert read == "ro"
    eng.update(n, UIElement(kind="DpgInputText", props={"value": "next"}, slot_id="r"))
    assert eng._read_dpg_prop(n.mountable, n.spec, "value") == "next"


def test_phase4_button_press_event() -> None:
    eng, host = _engine()
    seen: list[int] = []
    n = eng.mount(
        UIElement(
            kind="DpgButton",
            props={"label": "Go", "on_press": lambda: seen.append(1)},
            slot_id="btn",
        ),
    )
    dispatch = host.config_shadow[int(n.mountable.tag)]["callback"]
    dispatch()
    assert seen == [1]


def test_phase4_input_text_change_passes_dearpygui_app_data() -> None:
    """``add_input_text`` invokes ``callback(sender, app_data, user_data)``."""

    eng, host = _engine()
    seen: list[object] = []
    n = eng.mount(
        UIElement(
            kind="DpgInputText",
            props={
                "label": "",
                "value": "a",
                "on_change": lambda v: seen.append(v),
            },
            slot_id="in",
        ),
    )
    dispatch = host.config_shadow[int(n.mountable.tag)]["callback"]
    dispatch(101, "typed", None)
    assert seen == ["typed"]


def test_phase4_drag_drop_payload_policy() -> None:
    eng, host = _engine()
    drag_seen: list[object] = []
    drop_seen: list[object] = []
    n = eng.mount(
        UIElement(
            kind="DpgButton",
            props={
                "label": "d",
                "on_drag": lambda *a: drag_seen.extend(a),
                "on_drop": lambda *a: drop_seen.extend(a),
            },
            slot_id="d1",
        ),
    )
    tag = int(n.mountable.tag)
    host.config_shadow[tag]["drag_callback"](10, 20)
    host.config_shadow[tag]["drop_callback"]("a", "b")
    assert drag_seen == [10, 20]
    assert drop_seen == ["a", "b"]


def test_phase4_window_close_and_node_editor_delink() -> None:
    eng, host = _engine()
    close_seen: list[int] = []
    wn = eng.mount(
        UIElement(
            kind="DpgWindow",
            props={"label": "W", "on_close": lambda: close_seen.append(1)},
            slot_id="w",
        ),
    )
    host.config_shadow[int(wn.mountable.tag)]["on_close"]()
    assert close_seen == [1]

    delink: list[object] = []
    n = eng.mount(
        UIElement(
            kind="DpgNodeEditor",
            props={"on_delink": lambda *a: delink.extend(a)},
            slot_id="ne",
        ),
    )
    host.config_shadow[int(n.mountable.tag)]["delink_callback"](42)
    assert delink == [42]


def test_phase4_connect_dpg_event_signal_manual() -> None:
    host = RecordingDpgHost()
    tok = dpg_host_token(host)
    st = dpg_slot_token("m")
    try:
        b = DpgButtonItem(label="x")
        spec = UiEventSpec(name="on_press", signal_name="callback", payload_policy=EventPayloadPolicy.NONE)
        out: list[int] = []
        connect_dpg_event_signal(b, spec, lambda: out.append(1))
        host.config_shadow[int(b.tag)]["callback"]()
        assert out == [1]
    finally:
        dpg_slot_reset(st)
        dpg_host_reset(tok)


def test_phase5_window_menu_bar_and_standard_children() -> None:
    eng, host = _engine()
    tree = UIElement(
        kind="DpgWindow",
        props={"label": "App"},
        slot_id="win",
        children=(
            UIElement(kind="DpgMenuBar", props={}, slot_id="mb"),
            UIElement(kind="DpgButton", props={"label": "OK"}, slot_id="ok"),
        ),
    )
    root = eng.mount(tree)
    wtag = int(root.mountable.tag)
    mb_tag = int(root.child_nodes[0].mountable.tag)
    ok_tag = int(root.child_nodes[1].mountable.tag)
    under = {
        op[1]["item"]
        for op in host.operations
        if op[0] == "move_item" and op[1]["parent"] == wtag
    }
    assert mb_tag in under
    assert ok_tag in under


def test_phase5_table_plot_theme_registry_mount_chains() -> None:
    eng, host = _engine()
    table = UIElement(
        kind="DpgTable",
        props={},
        slot_id="tbl",
        children=(
            UIElement(kind="DpgTableColumn", props={}, slot_id="col"),
            UIElement(
                kind="DpgTableRow",
                props={},
                slot_id="row",
                children=(UIElement(kind="DpgButton", props={"label": "c"}, slot_id="cell"),),
            ),
        ),
    )
    eng.mount(table)
    plot = UIElement(
        kind="DpgPlot",
        props={},
        slot_id="pl",
        children=(UIElement(kind="DpgPlotAxis", props={}, slot_id="ax"),),
    )
    eng.mount(plot)
    theme = UIElement(
        kind="DpgTheme",
        props={},
        slot_id="th",
        children=(
            UIElement(
                kind="DpgThemeComponent",
                props={},
                slot_id="tc",
                children=(UIElement(kind="DpgButton", props={"label": "e"}, slot_id="ent"),),
            ),
        ),
    )
    eng.mount(theme)
    reg = UIElement(
        kind="DpgFontRegistry",
        props={},
        slot_id="fr",
        children=(UIElement(kind="DpgButton", props={"label": "f"}, slot_id="font"),),
    )
    eng.mount(reg)
    assert sum(1 for op in host.operations if op[0] == "move_item") >= 7


def test_phase5_node_editor_node_and_link_buckets() -> None:
    eng, host = _engine()
    ed = UIElement(
        kind="DpgNodeEditor",
        props={},
        slot_id="ed",
        children=(
            UIElement(kind="DpgNode", props={}, slot_id="n1"),
            UIElement(kind="DpgNodeLink", props={}, slot_id="l1"),
        ),
    )
    eng.mount(ed)
    moves = [op[1] for op in host.operations if op[0] == "move_item"]
    parents = {m["parent"] for m in moves if m["item"] != m["parent"]}
    assert len(parents) >= 1


def test_phase5_place_child_reorders() -> None:
    host = RecordingDpgHost()
    tok = dpg_host_token(host)
    st0 = dpg_slot_token("pw")
    try:
        parent = DpgWindowItem(label="P")
        ptag = int(parent.tag)
        dpg_slot_reset(st0)
        st_a = dpg_slot_token("pa")
        a = DpgButtonItem(label="a")
        dpg_slot_reset(st_a)
        st_b = dpg_slot_token("pb")
        b = DpgButtonItem(label="b")
        dpg_slot_reset(st_b)
        parent.sync_children((a, b))
        order1 = list(host.children_order[ptag])
        parent.place_child(0, b)
        order2 = list(host.children_order[ptag])
        assert order1 != order2
        assert order2[0] == int(b.tag)
    finally:
        dpg_host_reset(tok)


def test_read_missing_returns_missing() -> None:
    eng, _ = _engine()
    n = eng.mount(UIElement(kind="DpgButton", props={"label": "z"}, slot_id="z"))
    assert eng._read_dpg_prop(n.mountable, n.spec, "nope") is MISSING

"""Phase 6: live DearPyGui host (context, viewport, staging, existence guards).

Requires optional ``dearpygui`` (``uv run --with dearpygui pytest ...``).
"""

from __future__ import annotations

import pytest

pytest.importorskip("dearpygui")

from pyrolyze.api import UIElement
from pyrolyze.backends.dearpygui.engine import DpgMountableEngine
from pyrolyze.backends.dearpygui.host import (
    dpg_host_reset,
    dpg_host_token,
    dpg_slot_reset,
    dpg_slot_token,
)
from pyrolyze.backends.dearpygui.items import DpgButtonItem, DpgWindowItem
from pyrolyze.backends.dearpygui.specs import FIXTURE_WIDGET_SPECS

# Imported after importorskip so collection works without optional dearpygui.
from pyrolyze.backends.dearpygui.live_host import LiveDpgHost


@pytest.fixture
def live_host() -> LiveDpgHost:
    host = LiveDpgHost(title="pytest-dpg", width=64, height=64, show_viewport=False)
    host.start()
    try:
        yield host
    finally:
        host.stop()


def test_live_host_lifecycle_start_stop() -> None:
    host = LiveDpgHost(show_viewport=False)
    host.start()
    assert host.staging_tag != 0
    host.stop()
    host.stop()


def test_live_host_create_with_factory_and_exists(live_host: LiveDpgHost) -> None:
    import dearpygui.dearpygui as dpg

    tok = dpg_host_token(live_host)
    st = dpg_slot_token("s1")
    try:
        tag = live_host.create_with_factory("add_button", "s1", label="x")
        assert dpg.does_item_exist(tag)
        assert live_host.get_config_value(tag, "label") == "x"
    finally:
        dpg_slot_reset(st)
        dpg_host_reset(tok)


def test_live_host_children_order_tracks_move_item(live_host: LiveDpgHost) -> None:
    tok = dpg_host_token(live_host)
    try:
        w = DpgWindowItem(label="W")
        a = DpgButtonItem(label="a")
        b = DpgButtonItem(label="b")
        w.sync_children((a, b))
        ptag = int(w.tag)
        order = list(live_host.children_order[ptag])
        assert int(a.tag) in order and int(b.tag) in order
        w.place_child(0, b)
        order2 = list(live_host.children_order[ptag])
        assert order2[0] == int(b.tag)
    finally:
        dpg_host_reset(tok)


def test_live_host_delete_item_idempotent(live_host: LiveDpgHost) -> None:
    import dearpygui.dearpygui as dpg

    tok = dpg_host_token(live_host)
    st = dpg_slot_token("d0")
    try:
        t = live_host.create_with_factory("add_button", "d0", label="z")
        live_host.delete_item(t)
        assert not dpg.does_item_exist(t)
        live_host.delete_item(t)
        live_host.delete_item(999_999_999)
    finally:
        dpg_slot_reset(st)
        dpg_host_reset(tok)


def test_live_host_configure_missing_item_no_error(live_host: LiveDpgHost) -> None:
    live_host.configure_item(999_999_998, label="nope")
    live_host.set_value(999_999_998, True)


def test_live_engine_mount_button(live_host: LiveDpgHost) -> None:
    eng = DpgMountableEngine(FIXTURE_WIDGET_SPECS, live_host)
    n = eng.mount(UIElement(kind="DpgButton", props={"label": "L"}, slot_id="b"))
    assert live_host.get_config_value(int(n.mountable.tag), "label") == "L"


def test_live_engine_input_text_value_roundtrip(live_host: LiveDpgHost) -> None:
    eng = DpgMountableEngine(FIXTURE_WIDGET_SPECS, live_host)
    node = eng.mount(
        UIElement(kind="DpgInputText", props={"label": "x", "value": "alpha"}, slot_id="in"),
    )
    assert eng._read_dpg_prop(node.mountable, node.spec, "value") == "alpha"
    eng.update(node, UIElement(kind="DpgInputText", props={"value": "beta"}, slot_id="in"))
    assert eng._read_dpg_prop(node.mountable, node.spec, "value") == "beta"

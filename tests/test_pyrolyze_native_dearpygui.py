"""Tests for ``pyrolyze_native_dearpygui`` (optional ``dearpygui``)."""

from __future__ import annotations

import pytest

pytest.importorskip("dearpygui")

import dearpygui.dearpygui as dpg

from pyrolyze.api import UIElement
from pyrolyze.pyrolyze_native_dearpygui import create_host, reconcile_window_content


def test_create_host_reconcile_simple_window() -> None:
    host = create_host(title="t", width=64, height=64, show_viewport=False)
    try:
        tree = UIElement(
            kind="DpgWindow",
            props={"label": "N"},
            slot_id="w",
            children=(UIElement(kind="DpgButton", props={"label": "B"}, slot_id="b"),),
        )
        node = reconcile_window_content(host, (tree,))
        assert dpg.does_item_exist(int(node.mountable.tag))
        tree2 = UIElement(
            kind="DpgWindow",
            props={"label": "N2"},
            slot_id="w",
            children=(UIElement(kind="DpgButton", props={"label": "B2"}, slot_id="b"),),
        )
        node2 = reconcile_window_content(host, (tree2,))
        assert node2 is host.root_node
        assert dpg.does_item_exist(int(node2.mountable.tag))
    finally:
        host.close()


def test_reconcile_requires_single_root() -> None:
    host = create_host(show_viewport=False)
    try:
        with pytest.raises(ValueError, match="exactly one root"):
            reconcile_window_content(host, ())
    finally:
        host.close()

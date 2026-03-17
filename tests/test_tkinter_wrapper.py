from __future__ import annotations

import pytest

from pyrolyze.api import UIElement
from pyrolyze.pyrolyze_tkinter import render_ui_element, tkinter_available


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

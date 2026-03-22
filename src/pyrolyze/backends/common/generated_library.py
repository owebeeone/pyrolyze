from __future__ import annotations

from typing import ClassVar

from frozendict import frozendict

from pyrolyze.api import ui_interface
from pyrolyze.backends.model import UiInterface, UiInterfaceEntry
from pyrolyze.ui.elements_pyr import badge, button, row, section, select_field, text_field, toggle


@ui_interface
class CoreUiLibrary:
    """Shared semantic helper surface for the frozen common UI kinds."""

    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(
        name="CoreUiLibrary",
        owner=None,
        entries=frozendict(
            {
                "section": UiInterfaceEntry(public_name="section", kind="section"),
                "row": UiInterfaceEntry(public_name="row", kind="row"),
                "badge": UiInterfaceEntry(public_name="badge", kind="badge"),
                "button": UiInterfaceEntry(public_name="button", kind="button"),
                "text_field": UiInterfaceEntry(public_name="text_field", kind="text_field"),
                "toggle": UiInterfaceEntry(public_name="toggle", kind="toggle"),
                "select_field": UiInterfaceEntry(public_name="select_field", kind="select_field"),
            }
        ),
    )

    section = section
    row = row
    badge = badge
    button = button
    text_field = text_field
    toggle = toggle
    select_field = select_field


__all__ = ["CoreUiLibrary"]

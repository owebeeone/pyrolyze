"""DearPyGui adapter mountables (tag ownership, staging moves, container ordering)."""

from __future__ import annotations

from typing import Any, ClassVar, Iterable, Sequence

from pyrolyze.backends.dearpygui.host import current_dpg_host, current_dpg_slot_id


class DpgItem:
    """Owns one DearPyGui tag and forwards config/value updates to the active host."""

    def __init__(self) -> None:
        self._host = current_dpg_host()
        self.tag: int | str = self._host.allocate_tag(current_dpg_slot_id())

    @property
    def host(self) -> Any:
        return self._host

    def apply_dpg_config_key(self, key: str, value: Any) -> None:
        self._host.configure_item(self.tag, **{key: value})

    def apply_dpg_value(self, value: Any) -> None:
        self._host.set_value(self.tag, value)

    def dispose(self) -> None:
        self._host.delete_item(self.tag)


class DpgFactoryItem(DpgItem):
    """Creates the backing item via the host ``create_with_factory`` (``add_*`` / ``draw_*``)."""

    FACTORY: ClassVar[str] = ""

    def __init__(self, **kwargs: Any) -> None:
        self._host = current_dpg_host()
        self.tag = self._host.create_with_factory(
            type(self).FACTORY,
            current_dpg_slot_id(),
            **kwargs,
        )


class DpgContainerItem(DpgItem):
    """Container with ordered standard children via ``sync_children`` / ``place_child``."""

    def sync_children(self, children: Iterable[DpgItem]) -> None:
        for child in children:
            self._host.move_item(child.tag, parent=self.tag, before=0)

    def place_child(self, index: int, child: DpgItem) -> None:
        order = list(self._host.children_order.get(int(self.tag), []))
        order = [c for c in order if c != int(child.tag)]
        before = 0
        if 0 <= index < len(order):
            before = order[index]
        elif order:
            before = 0
        self._host.move_item(child.tag, parent=self.tag, before=before)

    def detach_child(self, child: DpgItem) -> None:
        self._host.move_item(child.tag, parent=self._host.staging_tag, before=0)


class DpgFactoryContainerItem(DpgContainerItem):
    FACTORY: ClassVar[str] = ""

    def __init__(self, **kwargs: Any) -> None:
        self._host = current_dpg_host()
        self.tag = self._host.create_with_factory(
            type(self).FACTORY,
            current_dpg_slot_id(),
            **kwargs,
        )


class DpgButtonItem(DpgFactoryItem):
    FACTORY = "add_button"


class DpgInputTextItem(DpgFactoryItem):
    FACTORY = "add_input_text"


class DpgMenuItem(DpgFactoryContainerItem):
    FACTORY = "add_menu"


class DpgMenuBarItem(DpgFactoryContainerItem):
    FACTORY = "add_menu_bar"


class DpgTableItem(DpgFactoryContainerItem):
    FACTORY = "add_table"

    def sync_column_children(self, children: list[DpgItem]) -> None:
        self.sync_children(children)

    def sync_row_children(self, children: list[DpgItem]) -> None:
        self.sync_children(children)


class DpgPlotItem(DpgFactoryContainerItem):
    FACTORY = "add_plot"

    def sync_axis_children(self, children: list[DpgItem]) -> None:
        self.sync_children(children)


class DpgNodeItem(DpgFactoryContainerItem):
    FACTORY = "add_node"


class DpgNodeLinkItem(DpgFactoryItem):
    FACTORY = "add_node_link"


class DpgThemeComponentItem(DpgFactoryContainerItem):
    FACTORY = "add_theme_component"

    def sync_entry_children(self, children: list[DpgItem]) -> None:
        self.sync_children(children)


class DpgThemeItem(DpgFactoryContainerItem):
    FACTORY = "add_theme"

    def sync_component_children(self, children: list[DpgItem]) -> None:
        self.sync_children(children)


class DpgFontRegistryItem(DpgFactoryContainerItem):
    FACTORY = "add_font_registry"

    def sync_registry_children(self, children: list[DpgItem]) -> None:
        self.sync_children(children)


class DpgWindowItem(DpgFactoryContainerItem):
    FACTORY = "add_window"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._menu_bar: DpgItem | None = None

    def attach_menu_bar(self, child: DpgItem) -> None:
        self._menu_bar = child
        self._host.move_item(child.tag, parent=self.tag, before=0)


class DpgTableColumnItem(DpgFactoryItem):
    FACTORY = "add_table_column"


class DpgTableRowItem(DpgFactoryContainerItem):
    FACTORY = "add_table_row"

    def sync_cells(self, children: Sequence[DpgItem]) -> None:
        self.sync_children(children)


class DpgPlotAxisItem(DpgFactoryItem):
    FACTORY = "add_plot_axis"


class DpgNodeEditorItem(DpgFactoryContainerItem):
    FACTORY = "add_node_editor"

    def sync_nodes(self, children: list[DpgItem]) -> None:
        self.sync_children(children)

    def sync_links(self, children: list[DpgItem]) -> None:
        self.sync_children(children)


__all__ = [
    "DpgButtonItem",
    "DpgContainerItem",
    "DpgFactoryContainerItem",
    "DpgFactoryItem",
    "DpgInputTextItem",
    "DpgItem",
    "DpgMenuBarItem",
    "DpgMenuItem",
    "DpgNodeEditorItem",
    "DpgNodeItem",
    "DpgNodeLinkItem",
    "DpgPlotAxisItem",
    "DpgPlotItem",
    "DpgFontRegistryItem",
    "DpgTableColumnItem",
    "DpgTableItem",
    "DpgTableRowItem",
    "DpgThemeComponentItem",
    "DpgThemeItem",
    "DpgWindowItem",
]

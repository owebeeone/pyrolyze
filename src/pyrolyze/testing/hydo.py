"""Stable fake mountable toolkit for backend and reconciler tests.

The Hydo toolkit is intentionally small, deterministic, and dataclass-based so
tests can exercise a broad set of API shapes without depending on a real GUI
toolkit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, Iterable


def _hydo_shape(kind: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        setattr(func, "__hydo_api_shape__", kind)
        return func

    return decorator


@dataclass(frozen=True, slots=True)
class HydoOperation:
    owner_type: str
    owner_name: str
    method: str
    args: tuple[object, ...] = ()
    kwargs: tuple[tuple[str, object], ...] = ()


@dataclass(slots=True)
class _HydoMountable:
    name: str
    operations: list[HydoOperation] = field(default_factory=list, init=False, repr=False)

    def _record(self, method: str, *args: object, **kwargs: object) -> None:
        self.operations.append(
            HydoOperation(
                owner_type=type(self).__name__,
                owner_name=self.name,
                method=method,
                args=tuple(_normalize_hydo_value(arg) for arg in args),
                kwargs=tuple(sorted((key, _normalize_hydo_value(value)) for key, value in kwargs.items())),
            )
        )


def _normalize_hydo_value(value: object) -> object:
    if isinstance(value, _HydoMountable):
        return f"{type(value).__name__}:{value.name}"
    return value


@dataclass(slots=True)
class HydoLayout(_HydoMountable):
    spacing: int = 0
    margin: int = 0
    _active: bool = field(default=True, repr=False)
    widgets: list[HydoWidget] = field(default_factory=list, init=False, repr=False)

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, value: bool) -> None:
        self._active = value
        self._record("active.__set__", value)

    @_hydo_shape("single_value")
    def set_active(self, value: bool) -> None:
        self._active = value
        self._record("set_active", value)

    @_hydo_shape("single_value")
    def set_spacing(self, value: int) -> None:
        self.spacing = value
        self._record("set_spacing", value)

    @_hydo_shape("single_value")
    def set_margin(self, value: int) -> None:
        self.margin = value
        self._record("set_margin", value)

    @_hydo_shape("ordered_mount")
    def add_widget(self, widget: HydoWidget) -> None:
        self.widgets.append(widget)
        self._record("add_widget", widget)

    @_hydo_shape("ordered_mount")
    def insert_widget(self, index: int, widget: HydoWidget) -> None:
        self.widgets.insert(index, widget)
        self._record("insert_widget", index, widget)


@dataclass(slots=True)
class HydoHorizontalLayout(HydoLayout):
    pass


@dataclass(slots=True)
class HydoGridLayout(HydoLayout):
    cells: dict[tuple[int, int], HydoWidget] = field(default_factory=dict, init=False, repr=False)

    @_hydo_shape("keyed_mount")
    def set_cell_widget(
        self,
        row: int,
        column: int,
        widget: HydoWidget,
        *,
        row_span: int = 1,
        column_span: int = 1,
    ) -> None:
        self.cells[(row, column)] = widget
        self._record(
            "set_cell_widget",
            row,
            column,
            widget,
            row_span=row_span,
            column_span=column_span,
        )


@dataclass(slots=True)
class HydoWidget(_HydoMountable):
    title: str = ""
    visible: bool = True
    enabled: bool = True
    layout: HydoLayout | None = field(default=None, init=False)
    children: list[HydoWidget] = field(default_factory=list, init=False, repr=False)
    corner_widgets: dict[str, HydoWidget] = field(default_factory=dict, init=False, repr=False)
    geometry: tuple[int, int, int, int] = field(default=(0, 0, 0, 0), init=False, repr=False)
    range_values: tuple[int, int] = field(default=(0, 0), init=False, repr=False)

    @_hydo_shape("single_value")
    def set_title(self, title: str) -> None:
        self.title = title
        self._record("set_title", title)

    @_hydo_shape("single_value")
    def set_visible(self, visible: bool) -> None:
        self.visible = visible
        self._record("set_visible", visible)

    @_hydo_shape("single_value")
    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        self._record("set_enabled", enabled)

    @_hydo_shape("grouped_value")
    def set_geometry(self, x: int, y: int, width: int, height: int) -> None:
        self.geometry = (x, y, width, height)
        self._record("set_geometry", x, y, width, height)

    @_hydo_shape("grouped_value")
    def set_range(self, minimum: int, maximum: int) -> None:
        self.range_values = (minimum, maximum)
        self._record("set_range", minimum, maximum)

    @_hydo_shape("single_mount")
    def set_layout(self, layout: HydoLayout) -> None:
        self.layout = layout
        self._record("set_layout", layout)

    @_hydo_shape("ordered_mount")
    def add_child(self, child: HydoWidget) -> None:
        self.children.append(child)
        self._record("add_child", child)

    @_hydo_shape("ordered_mount")
    def insert_child(self, index: int, child: HydoWidget) -> None:
        self.children.insert(index, child)
        self._record("insert_child", index, child)

    @_hydo_shape("keyed_mount")
    def set_corner_widget(self, corner: str, widget: HydoWidget) -> None:
        self.corner_widgets[corner] = widget
        self._record("set_corner_widget", corner, widget)

    def iter_widget_children(self) -> tuple[HydoWidget, ...]:
        return tuple(self.children) + tuple(self.corner_widgets.values())


@dataclass(slots=True)
class HydoAppWidget(HydoWidget):
    app_id: str = "hydo-app"


@dataclass(slots=True)
class HydoMenu(HydoWidget):
    menus: list[HydoMenu] = field(default_factory=list, init=False, repr=False)

    @_hydo_shape("ordered_mount")
    def add_menu(self, menu: HydoMenu) -> None:
        self.menus.append(menu)
        self._record("add_menu", menu)

    @_hydo_shape("ordered_mount")
    def insert_menu(self, index: int, menu: HydoMenu) -> None:
        self.menus.insert(index, menu)
        self._record("insert_menu", index, menu)

    def iter_widget_children(self) -> tuple[HydoWidget, ...]:
        return super(HydoMenu, self).iter_widget_children() + tuple(self.menus)


@dataclass(slots=True)
class HydoWindow(HydoWidget):
    main_widget: HydoWidget | None = None
    title_bar_widget: HydoWidget | None = None

    @_hydo_shape("single_mount")
    def set_main_widget(self, widget: HydoWidget) -> None:
        self.main_widget = widget
        self._record("set_main_widget", widget)

    @_hydo_shape("single_mount")
    def set_title_bar_widget(self, widget: HydoWidget) -> None:
        self.title_bar_widget = widget
        self._record("set_title_bar_widget", widget)

    def iter_widget_children(self) -> tuple[HydoWidget, ...]:
        children = list(super(HydoWindow, self).iter_widget_children())
        if self.title_bar_widget is not None:
            children.append(self.title_bar_widget)
        if self.main_widget is not None:
            children.append(self.main_widget)
        return tuple(children)


def build_demo_hierarchy() -> HydoWindow:
    window = HydoWindow(name="studio-window", title="Hydo Studio")
    window.set_layout(HydoGridLayout(name="window-layout"))

    title_bar = HydoWidget(name="title-bar", title="Title")
    title_bar.set_layout(HydoHorizontalLayout(name="title-bar-layout"))

    app_root = HydoAppWidget(name="app-root", title="Workspace")
    app_root.set_layout(HydoGridLayout(name="app-root-layout"))

    explorer = HydoWidget(name="explorer", title="Explorer")
    explorer.set_layout(HydoHorizontalLayout(name="explorer-layout"))

    content = HydoWidget(name="content", title="Content")
    content.set_layout(HydoGridLayout(name="content-layout"))

    stack = HydoWidget(name="stack", title="Stack")
    stack.set_layout(HydoGridLayout(name="stack-layout"))

    menu_root = HydoMenu(name="file-menu", title="File")
    menu_root.set_layout(HydoHorizontalLayout(name="file-menu-layout"))

    recent_menu = HydoMenu(name="recent-menu", title="Recent")
    recent_menu.set_layout(HydoHorizontalLayout(name="recent-menu-layout"))

    pinned_menu = HydoMenu(name="pinned-menu", title="Pinned")
    pinned_menu.set_layout(HydoHorizontalLayout(name="pinned-menu-layout"))

    debug_menu = HydoMenu(name="debug-menu", title="Debug")
    debug_menu.set_layout(HydoHorizontalLayout(name="debug-menu-layout"))

    menu_root.add_menu(recent_menu)
    recent_menu.add_menu(pinned_menu)
    stack.add_child(debug_menu)
    debug_menu.add_menu(menu_root)

    title_bar.add_child(menu_root)
    title_bar.add_child(HydoWidget(name="window-controls", title="Window Controls"))
    title_bar.children[-1].set_layout(HydoHorizontalLayout(name="window-controls-layout"))

    app_root.add_child(explorer)
    app_root.add_child(content)
    content.add_child(stack)

    app_layout = app_root.layout
    assert isinstance(app_layout, HydoGridLayout)
    app_layout.set_cell_widget(0, 0, explorer)
    app_layout.set_cell_widget(0, 1, content, column_span=2)

    content_layout = content.layout
    assert isinstance(content_layout, HydoGridLayout)
    content_layout.set_cell_widget(0, 0, stack)

    title_layout = title_bar.layout
    assert isinstance(title_layout, HydoHorizontalLayout)
    title_layout.add_widget(menu_root)
    title_layout.add_widget(title_bar.children[-1])

    window.set_title_bar_widget(title_bar)
    window.set_main_widget(app_root)

    return window


def walk_hydo_widgets(root: HydoWidget) -> Iterable[HydoWidget]:
    seen: set[int] = set()

    def visit(widget: HydoWidget) -> Iterable[HydoWidget]:
        widget_id = id(widget)
        if widget_id in seen:
            return ()
        seen.add(widget_id)
        nested: list[HydoWidget] = []
        for child in widget.iter_widget_children():
            nested.extend(visit(child))
        return (widget, *nested)

    return visit(root)


def max_hydo_depth(root: HydoWidget) -> int:
    def depth(widget: HydoWidget, seen: set[int]) -> int:
        widget_id = id(widget)
        if widget_id in seen:
            return 0
        next_seen = set(seen)
        next_seen.add(widget_id)
        child_depths = [depth(child, next_seen) for child in widget.iter_widget_children()]
        return 1 + (max(child_depths) if child_depths else 0)

    return depth(root, set())


_HYDO_SURFACE_CLASSES: tuple[type[object], ...] = (
    HydoLayout,
    HydoHorizontalLayout,
    HydoGridLayout,
    HydoWidget,
    HydoAppWidget,
    HydoMenu,
    HydoWindow,
)


def describe_hydo_api_surface() -> dict[str, dict[str, tuple[str, ...]]]:
    surface: dict[str, dict[str, tuple[str, ...]]] = {}
    categories = (
        "constructor_params",
        "single_value_methods",
        "grouped_value_methods",
        "single_mount_methods",
        "ordered_mount_methods",
        "keyed_mount_methods",
        "python_properties",
    )
    shape_name_map = {
        "single_value": "single_value_methods",
        "grouped_value": "grouped_value_methods",
        "single_mount": "single_mount_methods",
        "ordered_mount": "ordered_mount_methods",
        "keyed_mount": "keyed_mount_methods",
    }
    for cls in _HYDO_SURFACE_CLASSES:
        class_surface: dict[str, tuple[str, ...]] = {category: () for category in categories}
        signature = inspect.signature(cls)
        class_surface["constructor_params"] = tuple(
            name for name in signature.parameters if name != "self"
        )
        methods_by_category: dict[str, list[str]] = {category: [] for category in shape_name_map.values()}
        for name, member in inspect.getmembers(cls):
            shape = getattr(member, "__hydo_api_shape__", None)
            if shape is None:
                continue
            methods_by_category[shape_name_map[shape]].append(name)
        for category, names in methods_by_category.items():
            class_surface[category] = tuple(sorted(names))
        class_surface["python_properties"] = tuple(
            sorted(
                name
                for name, member in inspect.getmembers(cls)
                if isinstance(member, property)
            )
        )
        surface[cls.__name__] = class_surface
    return surface


__all__ = [
    "HydoAppWidget",
    "HydoGridLayout",
    "HydoHorizontalLayout",
    "HydoLayout",
    "HydoMenu",
    "HydoOperation",
    "HydoWidget",
    "HydoWindow",
    "build_demo_hierarchy",
    "describe_hydo_api_surface",
    "max_hydo_depth",
    "walk_hydo_widgets",
]

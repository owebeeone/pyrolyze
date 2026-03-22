"""Stable fake mountable toolkit for backend and reconciler tests.

The Hydo toolkit is intentionally small, deterministic, and dataclass-based so
tests can exercise a broad set of API shapes without depending on a real GUI
toolkit.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import inspect
from typing import Any, Callable, Iterable, Mapping

from frozendict import frozendict

from pyrolyze.api import MISSING, UIElement
from pyrolyze.backends.model import (
    AccessorKind,
    ChildPolicy,
    FillPolicy,
    MethodMode,
    MountParamSpec,
    MountPointSpec,
    PropMode,
    TypeRef,
    UiMethodSpec,
    UiParamSpec,
    UiPropSpec,
    UiWidgetSpec,
)


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

    def sync_widgets(self, widgets: Iterable[HydoWidget]) -> None:
        self.widgets = list(widgets)
        self._record("sync_widgets", *self.widgets)

    def place_widget(self, index: int, widget: HydoWidget) -> None:
        self.widgets = [existing for existing in self.widgets if existing is not widget]
        self.widgets.insert(index, widget)
        self._record("place_widget", index, widget)

    def detach_widget(self, widget: HydoWidget) -> None:
        self.widgets = [existing for existing in self.widgets if existing is not widget]
        self._record("detach_widget", widget)


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

    def sync_children(self, children: Iterable[HydoWidget]) -> None:
        self.children = list(children)
        self._record("sync_children", *self.children)

    def place_child(self, index: int, child: HydoWidget) -> None:
        self.children = [existing for existing in self.children if existing is not child]
        self.children.insert(index, child)
        self._record("place_child", index, child)

    def detach_child(self, child: HydoWidget) -> None:
        self.children = [existing for existing in self.children if existing is not child]
        self._record("detach_child", child)

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

    def sync_menus(self, menus: Iterable[HydoMenu]) -> None:
        self.menus = list(menus)
        self._record("sync_menus", *self.menus)

    def place_menu(self, index: int, menu: HydoMenu) -> None:
        self.menus = [existing for existing in self.menus if existing is not menu]
        self.menus.insert(index, menu)
        self._record("place_menu", index, menu)

    def detach_menu(self, menu: HydoMenu) -> None:
        self.menus = [existing for existing in self.menus if existing is not menu]
        self._record("detach_menu", menu)

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


def _layout_constructor_params() -> frozendict[str, UiParamSpec]:
    return frozendict(
        {
            "name": UiParamSpec(name="name", annotation=TypeRef("str")),
            "spacing": UiParamSpec(name="spacing", annotation=TypeRef("int"), default_repr="0"),
            "margin": UiParamSpec(name="margin", annotation=TypeRef("int"), default_repr="0"),
        }
    )


def _widget_constructor_params() -> frozendict[str, UiParamSpec]:
    return frozendict(
        {
            "name": UiParamSpec(name="name", annotation=TypeRef("str")),
            "title": UiParamSpec(name="title", annotation=TypeRef("str"), default_repr="''"),
            "visible": UiParamSpec(name="visible", annotation=TypeRef("bool"), default_repr="True"),
            "enabled": UiParamSpec(name="enabled", annotation=TypeRef("bool"), default_repr="True"),
        }
    )


def _app_widget_constructor_params() -> frozendict[str, UiParamSpec]:
    return frozendict(
        {
            **dict(_widget_constructor_params()),
            "app_id": UiParamSpec(name="app_id", annotation=TypeRef("str"), default_repr="'hydo-app'"),
        }
    )


def _layout_props() -> frozendict[str, UiPropSpec]:
    return frozendict(
        {
            "active": UiPropSpec(
                name="active",
                annotation=TypeRef("bool"),
                mode=PropMode.CREATE_UPDATE,
                setter_kind=AccessorKind.PYTHON_PROPERTY,
                setter_name="active",
                getter_kind=AccessorKind.PYTHON_PROPERTY,
                getter_name="active",
            ),
            "spacing": UiPropSpec(
                name="spacing",
                annotation=TypeRef("int"),
                mode=PropMode.CREATE_UPDATE,
                constructor_name="spacing",
                setter_kind=AccessorKind.METHOD,
                setter_name="set_spacing",
            ),
            "margin": UiPropSpec(
                name="margin",
                annotation=TypeRef("int"),
                mode=PropMode.CREATE_UPDATE,
                constructor_name="margin",
                setter_kind=AccessorKind.METHOD,
                setter_name="set_margin",
            ),
        }
    )


def _widget_props() -> frozendict[str, UiPropSpec]:
    return frozendict(
        {
            "name": UiPropSpec(
                name="name",
                annotation=TypeRef("str"),
                mode=PropMode.CREATE_ONLY,
                constructor_name="name",
            ),
            "title": UiPropSpec(
                name="title",
                annotation=TypeRef("str"),
                mode=PropMode.CREATE_UPDATE,
                constructor_name="title",
                setter_kind=AccessorKind.METHOD,
                setter_name="set_title",
            ),
            "visible": UiPropSpec(
                name="visible",
                annotation=TypeRef("bool"),
                mode=PropMode.CREATE_UPDATE,
                constructor_name="visible",
                setter_kind=AccessorKind.METHOD,
                setter_name="set_visible",
            ),
            "enabled": UiPropSpec(
                name="enabled",
                annotation=TypeRef("bool"),
                mode=PropMode.CREATE_UPDATE,
                constructor_name="enabled",
                setter_kind=AccessorKind.METHOD,
                setter_name="set_enabled",
            ),
            "geometry_x": UiPropSpec(name="geometry_x", annotation=TypeRef("int"), mode=PropMode.CREATE_UPDATE),
            "geometry_y": UiPropSpec(name="geometry_y", annotation=TypeRef("int"), mode=PropMode.CREATE_UPDATE),
            "geometry_width": UiPropSpec(
                name="geometry_width",
                annotation=TypeRef("int"),
                mode=PropMode.CREATE_UPDATE,
            ),
            "geometry_height": UiPropSpec(
                name="geometry_height",
                annotation=TypeRef("int"),
                mode=PropMode.CREATE_UPDATE,
            ),
            "minimum": UiPropSpec(name="minimum", annotation=TypeRef("int"), mode=PropMode.CREATE_UPDATE),
            "maximum": UiPropSpec(name="maximum", annotation=TypeRef("int"), mode=PropMode.CREATE_UPDATE),
        }
    )


def _widget_methods() -> frozendict[str, UiMethodSpec]:
    return frozendict(
        {
            "setGeometry": UiMethodSpec(
                name="setGeometry",
                mode=MethodMode.CREATE_UPDATE,
                params=(
                    UiParamSpec(name="x", annotation=TypeRef("int")),
                    UiParamSpec(name="y", annotation=TypeRef("int")),
                    UiParamSpec(name="width", annotation=TypeRef("int")),
                    UiParamSpec(name="height", annotation=TypeRef("int")),
                ),
                source_props=("geometry_x", "geometry_y", "geometry_width", "geometry_height"),
                fill_policy=FillPolicy.RETAIN_EFFECTIVE,
            ),
            "setRange": UiMethodSpec(
                name="setRange",
                mode=MethodMode.CREATE_UPDATE,
                params=(
                    UiParamSpec(name="minimum", annotation=TypeRef("int")),
                    UiParamSpec(name="maximum", annotation=TypeRef("int")),
                ),
                source_props=("minimum", "maximum"),
                fill_policy=FillPolicy.RETAIN_EFFECTIVE,
            ),
        }
    )


def _standard_mount(accepted_type: str, sync_method_name: str) -> MountPointSpec:
    return MountPointSpec(
        name="standard",
        accepted_produced_type=TypeRef(accepted_type),
        sync_method_name=sync_method_name,
    )


def _widget_mount_points() -> frozendict[str, MountPointSpec]:
    return frozendict(
        {
            "standard": _standard_mount("HydoWidget", "sync_children"),
            "layout": MountPointSpec(
                name="layout",
                accepted_produced_type=TypeRef("HydoLayout"),
                max_children=1,
                apply_method_name="set_layout",
            ),
            "corner_widget": MountPointSpec(
                name="corner_widget",
                accepted_produced_type=TypeRef("HydoWidget"),
                params=(MountParamSpec(name="corner", annotation=TypeRef("str"), keyed=True),),
                max_children=1,
                apply_method_name="set_corner_widget",
            ),
        }
    )


HYDO_MOUNTABLE_SPECS = frozendict(
    {
        "HydoLayout": UiWidgetSpec(
            kind="HydoLayout",
            mounted_type_name=f"{__name__}.HydoLayout",
            constructor_params=_layout_constructor_params(),
            props=_layout_props(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict({"standard": _standard_mount("HydoWidget", "sync_widgets")}),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "HydoHorizontalLayout": UiWidgetSpec(
            kind="HydoHorizontalLayout",
            mounted_type_name=f"{__name__}.HydoHorizontalLayout",
            constructor_params=_layout_constructor_params(),
            props=_layout_props(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict({"standard": _standard_mount("HydoWidget", "sync_widgets")}),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "HydoGridLayout": UiWidgetSpec(
            kind="HydoGridLayout",
            mounted_type_name=f"{__name__}.HydoGridLayout",
            constructor_params=_layout_constructor_params(),
            props=_layout_props(),
            methods=frozendict(),
            child_policy=ChildPolicy.NONE,
            mount_points=frozendict(
                {
                    "standard": _standard_mount("HydoWidget", "sync_widgets"),
                    "cell_widget": MountPointSpec(
                        name="cell_widget",
                        accepted_produced_type=TypeRef("HydoWidget"),
                        params=(
                            MountParamSpec(name="row", annotation=TypeRef("int"), keyed=True),
                            MountParamSpec(name="column", annotation=TypeRef("int"), keyed=True),
                            MountParamSpec(name="row_span", annotation=TypeRef("int")),
                            MountParamSpec(name="column_span", annotation=TypeRef("int")),
                        ),
                        max_children=1,
                        apply_method_name="set_cell_widget",
                    ),
                }
            ),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "HydoWidget": UiWidgetSpec(
            kind="HydoWidget",
            mounted_type_name=f"{__name__}.HydoWidget",
            constructor_params=_widget_constructor_params(),
            props=_widget_props(),
            methods=_widget_methods(),
            child_policy=ChildPolicy.ORDERED,
            mount_points=_widget_mount_points(),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "HydoAppWidget": UiWidgetSpec(
            kind="HydoAppWidget",
            mounted_type_name=f"{__name__}.HydoAppWidget",
            constructor_params=_app_widget_constructor_params(),
            props=_widget_props(),
            methods=_widget_methods(),
            child_policy=ChildPolicy.ORDERED,
            mount_points=_widget_mount_points(),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "HydoMenu": UiWidgetSpec(
            kind="HydoMenu",
            mounted_type_name=f"{__name__}.HydoMenu",
            constructor_params=_widget_constructor_params(),
            props=_widget_props(),
            methods=_widget_methods(),
            child_policy=ChildPolicy.ORDERED,
            mount_points=frozendict(
                {
                    **dict(_widget_mount_points()),
                    "menu": MountPointSpec(
                        name="menu",
                        accepted_produced_type=TypeRef("HydoMenu"),
                        sync_method_name="sync_menus",
                    ),
                }
            ),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
        "HydoWindow": UiWidgetSpec(
            kind="HydoWindow",
            mounted_type_name=f"{__name__}.HydoWindow",
            constructor_params=_widget_constructor_params(),
            props=_widget_props(),
            methods=_widget_methods(),
            child_policy=ChildPolicy.ORDERED,
            mount_points=frozendict(
                {
                    **dict(_widget_mount_points()),
                    "main_widget": MountPointSpec(
                        name="main_widget",
                        accepted_produced_type=TypeRef("HydoWidget"),
                        max_children=1,
                        apply_method_name="set_main_widget",
                    ),
                    "title_bar_widget": MountPointSpec(
                        name="title_bar_widget",
                        accepted_produced_type=TypeRef("HydoWidget"),
                        max_children=1,
                        apply_method_name="set_title_bar_widget",
                    ),
                }
            ),
            default_child_mount_point_name="standard",
            default_attach_mount_point_names=("standard",),
        ),
    }
)


@dataclass(slots=True)
class HydoMountedNode:
    slot_id: Any | None
    call_site_id: int | str | None
    element: UIElement
    spec: UiWidgetSpec
    mountable: _HydoMountable
    effective_props: dict[str, Any] = field(default_factory=dict)
    child_nodes: list["HydoMountedNode"] = field(default_factory=list)


class HydoMountableEngine:
    def __init__(self, mountable_specs: Mapping[str, UiWidgetSpec]):
        self._mountable_specs = mountable_specs

    def mount(
        self,
        element: UIElement,
        *,
        slot_id: Any | None = None,
        call_site_id: int | str | None = None,
    ) -> HydoMountedNode:
        spec = self._spec_for(element.kind)
        effective_props = self._initial_effective_props(spec, element)
        mountable = self._create_mountable(spec, effective_props)
        child_nodes = self._mount_standard_children(
            mountable,
            spec,
            element.children,
            parent_slot_id=slot_id if slot_id is not None else element.slot_id,
        )
        return HydoMountedNode(
            slot_id=slot_id if slot_id is not None else element.slot_id,
            call_site_id=call_site_id if call_site_id is not None else element.call_site_id,
            element=element,
            spec=spec,
            mountable=mountable,
            effective_props=effective_props,
            child_nodes=child_nodes,
        )

    def update(self, node: HydoMountedNode, element: UIElement) -> HydoMountedNode:
        spec = self._spec_for(element.kind)
        if spec.kind != node.spec.kind:
            replacement = self.mount(element, slot_id=node.slot_id, call_site_id=node.call_site_id)
            node.element = replacement.element
            node.spec = replacement.spec
            node.mountable = replacement.mountable
            node.effective_props = replacement.effective_props
            node.child_nodes = replacement.child_nodes
            return node

        next_effective = dict(node.effective_props)
        changed_props: dict[str, Any] = {}
        for name, value in element.props.items():
            if value is MISSING:
                continue
            prop = self._prop_for(spec, name)
            if prop.mode is PropMode.READONLY:
                raise ValueError(f"readonly prop {name!r} may not be updated")
            if prop.mode is PropMode.CREATE_ONLY:
                continue
            if next_effective.get(name, MISSING) == value:
                continue
            next_effective[name] = value
            changed_props[name] = value

        self._apply_changed_props(node.mountable, spec, changed_props)
        self._apply_changed_methods(node.mountable, spec, next_effective, changed_props)
        node.child_nodes = self._mount_standard_children(
            node.mountable,
            spec,
            element.children,
            parent_slot_id=node.slot_id,
        )
        node.element = element
        node.effective_props = next_effective
        return node

    def _spec_for(self, kind: str) -> UiWidgetSpec:
        spec = self._mountable_specs.get(kind)
        if spec is None:
            raise ValueError(f"unsupported mountable kind {kind!r}")
        return spec

    def _prop_for(self, spec: UiWidgetSpec, name: str) -> UiPropSpec:
        prop = spec.props.get(name)
        if prop is None:
            raise ValueError(f"unsupported prop {name!r} for mountable kind {spec.kind!r}")
        return prop

    def _initial_effective_props(self, spec: UiWidgetSpec, element: UIElement) -> dict[str, Any]:
        effective: dict[str, Any] = {}
        for name, value in element.props.items():
            if value is MISSING:
                continue
            prop = self._prop_for(spec, name)
            if prop.mode is PropMode.READONLY:
                raise ValueError(f"readonly prop {name!r} may not be mounted")
            effective[name] = value
        return effective

    def _create_mountable(self, spec: UiWidgetSpec, effective_props: Mapping[str, Any]) -> _HydoMountable:
        mountable_type = _HYDO_TYPES[spec.kind]
        constructor_kwargs = {
            param.name: effective_props[param.name]
            for param in spec.constructor_params.values()
            if param.name in effective_props
        }
        mountable = mountable_type(**constructor_kwargs)
        self._apply_mount_props(mountable, spec, effective_props)
        self._apply_mount_methods(mountable, spec, effective_props)
        return mountable

    def _apply_mount_props(
        self,
        mountable: _HydoMountable,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
    ) -> None:
        method_backed_source_props = {
            source_prop
            for method in spec.methods.values()
            for source_prop in method.source_props
        }
        for name, value in effective_props.items():
            if name in method_backed_source_props:
                continue
            prop = spec.props.get(name)
            if prop is None or prop.setter_kind is None:
                continue
            if prop.mode is PropMode.CREATE_UPDATE:
                self._apply_prop(mountable, prop, value)

    def _apply_mount_methods(
        self,
        mountable: _HydoMountable,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
    ) -> None:
        for method in spec.methods.values():
            resolved = self._resolve_method_args(effective_props, method)
            if resolved is not None:
                self._apply_method(mountable, method, resolved)

    def _apply_changed_props(
        self,
        mountable: _HydoMountable,
        spec: UiWidgetSpec,
        changed_props: Mapping[str, Any],
    ) -> None:
        method_backed_source_props = {
            source_prop
            for method in spec.methods.values()
            for source_prop in method.source_props
        }
        for name, value in changed_props.items():
            if name in method_backed_source_props:
                continue
            prop = spec.props.get(name)
            if prop is None or prop.setter_kind is None:
                continue
            if prop.mode is PropMode.CREATE_UPDATE:
                self._apply_prop(mountable, prop, value)

    def _apply_changed_methods(
        self,
        mountable: _HydoMountable,
        spec: UiWidgetSpec,
        effective_props: Mapping[str, Any],
        changed_props: Mapping[str, Any],
    ) -> None:
        if not changed_props:
            return
        changed_names = set(changed_props)
        for method in spec.methods.values():
            if not changed_names.intersection(method.source_props):
                continue
            resolved = self._resolve_method_args(effective_props, method)
            if resolved is not None:
                self._apply_method(mountable, method, resolved)

    def _resolve_method_args(
        self,
        effective_props: Mapping[str, Any],
        method: UiMethodSpec,
    ) -> tuple[Any, ...] | None:
        args: list[Any] = []
        for source_prop in method.source_props:
            if source_prop not in effective_props:
                if method.fill_policy is FillPolicy.RETAIN_EFFECTIVE:
                    return None
                return None
            args.append(effective_props[source_prop])
        return tuple(args)

    def _apply_prop(self, mountable: _HydoMountable, prop: UiPropSpec, value: Any) -> None:
        if prop.setter_kind is AccessorKind.PYTHON_PROPERTY:
            setattr(mountable, prop.setter_name or prop.name, value)
            return
        setter_name = prop.setter_name
        if setter_name is None:
            raise ValueError(f"prop {prop.name!r} has no setter name")
        getattr(mountable, setter_name)(value)

    def _apply_method(self, mountable: _HydoMountable, method: UiMethodSpec, args: tuple[Any, ...]) -> None:
        for method_name in (method.name, _camel_to_snake(method.name)):
            if hasattr(mountable, method_name):
                getattr(mountable, method_name)(*args)
                return
        raise AttributeError(f"{type(mountable).__name__} has no method for spec {method.name!r}")

    def _mount_standard_children(
        self,
        parent: _HydoMountable,
        spec: UiWidgetSpec,
        children: tuple[UIElement, ...],
        *,
        parent_slot_id: Any | None,
    ) -> list[HydoMountedNode]:
        mount_point = spec.mount_points.get("standard")
        if mount_point is None:
            return []
        child_nodes = [
            self.mount(child, slot_id=_child_slot_id(parent_slot_id, index), call_site_id=child.call_site_id)
            for index, child in enumerate(children)
        ]
        if mount_point.sync_method_name is not None:
            getattr(parent, mount_point.sync_method_name)([child.mountable for child in child_nodes])
        return child_nodes


def _camel_to_snake(name: str) -> str:
    chars: list[str] = []
    for index, char in enumerate(name):
        if char.isupper() and index > 0:
            chars.append("_")
        chars.append(char.lower())
    return "".join(chars)


def _child_slot_id(parent_slot_id: Any | None, index: int) -> Any:
    if parent_slot_id is None:
        return (index,)
    if isinstance(parent_slot_id, tuple):
        return (*parent_slot_id, index)
    return (parent_slot_id, index)


_HYDO_TYPES: dict[str, type[_HydoMountable]] = {
    "HydoLayout": HydoLayout,
    "HydoHorizontalLayout": HydoHorizontalLayout,
    "HydoGridLayout": HydoGridLayout,
    "HydoWidget": HydoWidget,
    "HydoAppWidget": HydoAppWidget,
    "HydoMenu": HydoMenu,
    "HydoWindow": HydoWindow,
}


__all__ = [
    "HYDO_MOUNTABLE_SPECS",
    "HydoAppWidget",
    "HydoGridLayout",
    "HydoHorizontalLayout",
    "HydoLayout",
    "HydoMenu",
    "HydoMountableEngine",
    "HydoMountedNode",
    "HydoOperation",
    "HydoWidget",
    "HydoWindow",
    "build_demo_hierarchy",
    "describe_hydo_api_surface",
    "max_hydo_depth",
    "walk_hydo_widgets",
]

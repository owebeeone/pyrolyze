from __future__ import annotations

"""Mountable-library extraction and code generation.

This tool currently discovers PySide6/Tkinter mountable classes and emits
`UiWidgetSpec`-backed UI libraries. The model type name is still widget-shaped
in code, but the generated surface now includes broader mountable classes and
mount-point metadata where the backend model can represent them.
"""

import argparse
import ast
from dataclasses import dataclass, replace
from functools import lru_cache
import importlib
import importlib.util
import inspect
import pkgutil
from pathlib import Path
import re
from typing import Any, Mapping, Sequence

from frozendict import frozendict

from pyrolyze.backends.model import (
    EventPayloadPolicy,
    FillPolicy,
    MethodMode,
    UiEventLearning,
    UiMethodLearning,
    UiPropLearning,
    UiWidgetLearning,
)


@dataclass(frozen=True, slots=True)
class DiscoveredParameter:
    name: str
    kind: inspect._ParameterKind
    annotation_source: str | None
    default_source: str | None
    coerced_expression: str


@dataclass(frozen=True, slots=True)
class DiscoveredProperty:
    name: str
    type_name: str
    readable: bool
    writable: bool


@dataclass(frozen=True, slots=True)
class DiscoveredSetterMethod:
    owner_class_name: str
    name: str
    parameters: tuple[DiscoveredParameter, ...]


@dataclass(frozen=True, slots=True)
class DiscoveredMountPoint:
    name: str
    accepted_type_name: str
    params: tuple[DiscoveredParameter, ...] = ()
    min_children: int = 0
    max_children: int | None = None
    apply_method_name: str | None = None
    sync_method_name: str | None = None
    place_method_name: str | None = None
    detach_method_name: str | None = None


@dataclass(frozen=True, slots=True)
class DiscoveredWidgetClass:
    module_name: str
    class_name: str
    public_name: str
    parameters: tuple[DiscoveredParameter, ...]
    properties: tuple[DiscoveredProperty, ...] = ()
    setter_methods: tuple[DiscoveredSetterMethod, ...] = ()
    mount_points: tuple[DiscoveredMountPoint, ...] = ()
    omitted_variadic_arguments: bool = False
    prop_learnings: frozendict[str, UiPropLearning] = frozendict()
    method_learnings: frozendict[str, UiMethodLearning] = frozendict()
    event_learnings: frozendict[str, UiEventLearning] = frozendict()


def discover_modules(root_module_name: str) -> list[str]:
    root_module = importlib.import_module(root_module_name)
    module_names = [root_module.__name__]
    package_paths = getattr(root_module, "__path__", None)
    if package_paths is None:
        return module_names
    for module_info in pkgutil.walk_packages(package_paths, prefix=f"{root_module.__name__}."):
        if _should_skip_module(module_info.name):
            continue
        module_names.append(module_info.name)
    return sorted(set(module_names))


def discover_widget_classes(
    root_module_name: str,
    widget_base_specs: tuple[str, ...] | None = None,
) -> list[DiscoveredWidgetClass]:
    base_classes = _resolve_widget_bases(root_module_name, widget_base_specs)
    discovered: list[
        tuple[
            str,
            str,
            tuple[DiscoveredParameter, ...],
            tuple[DiscoveredProperty, ...],
            tuple[DiscoveredSetterMethod, ...],
            tuple[DiscoveredMountPoint, ...],
            bool,
        ]
    ] = []
    seen_classes: set[tuple[str, str]] = set()
    for module_name in discover_modules(root_module_name):
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate.__module__ != module.__name__:
                continue
            if candidate in base_classes and root_module_name.split(".", 1)[0] != "PySide6":
                continue
            if not any(issubclass(candidate, base_class) for base_class in base_classes):
                continue
            dedupe_key = (candidate.__module__, candidate.__qualname__)
            if dedupe_key in seen_classes:
                continue
            seen_classes.add(dedupe_key)
            discovered.append(
                (
                    candidate.__module__,
                    candidate.__name__,
                    _extract_parameters(root_module_name, candidate),
                    _extract_properties(root_module_name, candidate),
                    _extract_multiarg_setter_methods(root_module_name, candidate),
                    _extract_mount_points(root_module_name, candidate),
                    _has_variadic_parameters(root_module_name, candidate),
                )
            )
    ordered = sorted(discovered, key=lambda widget: (widget[1], widget[0]))
    public_names = _assign_public_names(root_module_name, [(module_name, class_name) for module_name, class_name, *_ in ordered])
    return [
        DiscoveredWidgetClass(
            module_name=module_name,
            class_name=class_name,
            public_name=public_name,
            parameters=parameters,
            properties=properties,
            setter_methods=setter_methods,
            mount_points=mount_points,
            omitted_variadic_arguments=omitted_variadic_arguments,
        )
        for (module_name, class_name, parameters, properties, setter_methods, mount_points, omitted_variadic_arguments), public_name in zip(
            ordered,
            public_names,
            strict=True,
        )
    ]


def load_learnings(root_module_name: str) -> frozendict[str, UiWidgetLearning]:
    backend_package = root_module_name.split(".", 1)[0].lower()
    module_name = f"pyrolyze.backends.{backend_package}.learnings"
    try:
        module = importlib.import_module(module_name)
    except Exception:
        learnings_path = (
            Path(__file__).resolve().parents[1]
            / "src"
            / "pyrolyze"
            / "backends"
            / backend_package
            / "learnings.py"
        )
        if not learnings_path.exists():
            return frozendict()
        spec = importlib.util.spec_from_file_location(module_name, learnings_path)
        if spec is None or spec.loader is None:
            return frozendict()
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    learnings = getattr(module, "LEARNINGS", frozendict())
    if isinstance(learnings, frozendict):
        return learnings
    return frozendict(learnings)


def apply_learnings(
    widgets: Sequence[DiscoveredWidgetClass],
    learnings: Mapping[str, UiWidgetLearning],
) -> list[DiscoveredWidgetClass]:
    resolved: list[DiscoveredWidgetClass] = []
    for widget in widgets:
        widget_learning = learnings.get(widget.class_name)
        if widget_learning is None:
            resolved.append(widget)
            continue
        resolved.append(
            replace(
                widget,
                public_name=widget_learning.public_name or widget.public_name,
                prop_learnings=widget_learning.prop_learnings,
                method_learnings=widget_learning.method_learnings,
                event_learnings=widget_learning.event_learnings,
            )
        )
    return resolved


def infer_pyside6_learnings(
    widgets: Sequence[DiscoveredWidgetClass],
) -> frozendict[str, UiWidgetLearning]:
    learned_widgets: dict[str, UiWidgetLearning] = {}
    for widget in widgets:
        method_learnings: dict[str, UiMethodLearning] = {}
        for method in widget.setter_methods:
            learned = _infer_pyside6_method_learning(widget, method)
            if learned is None:
                continue
            method_learnings[method.name] = learned
        if method_learnings:
            learned_widgets[widget.class_name] = UiWidgetLearning(
                method_learnings=frozendict(method_learnings)
            )
    return frozendict(learned_widgets)


_PYSIDE6_BLOCKED_METHOD_NAMES = frozenset(
    {
        "setParent",
        "setTabOrder",
        "setIndexWidget",
        "setItemDelegate",
        "setItemDelegateForColumn",
        "setItemDelegateForRow",
        "setCellWidget",
        "setItemWidget",
        "setCornerWidget",
        "setMenu",
        "setLayout",
        "setModel",
        "setModelColumn",
        "setSelectionModel",
        "setRootModelIndex",
        "setViewport",
        "setCentralWidget",
        "setWidget",
    }
)

_PYSIDE6_BLOCKED_TYPE_FRAGMENTS = (
    "QWidget",
    "QLayout",
    "QModelIndex",
    "QPersistentModelIndex",
    "QAbstractItemModel",
    "QItemSelectionModel",
    "QAbstractItemDelegate",
    "QCompleter",
    "QValidator",
    "QMenu",
    "QAction",
)

_PYSIDE6_DIRECT_METHOD_PROP_CANDIDATES = {
    "setRange": ("minimum", "maximum"),
    "setMinimumSize": ("minimumWidth", "minimumHeight"),
    "setMaximumSize": ("maximumWidth", "maximumHeight"),
}

_PYSIDE6_FALLBACK_PARAM_NAME_MAP = {
    "w": "width",
    "h": "height",
    "min": "minimum",
    "max": "maximum",
    "minw": "min_width",
    "minh": "min_height",
    "maxw": "max_width",
    "maxh": "max_height",
    "f": "flag",
}

_PYSIDE6_MOUNT_TYPE_QUALIFIERS = {
    "QAction": "PySide6.QtGui.QAction",
    "QLayout": "PySide6.QtWidgets.QLayout",
    "QMenu": "PySide6.QtWidgets.QMenu",
    "QMenuBar": "PySide6.QtWidgets.QMenuBar",
    "QStatusBar": "PySide6.QtWidgets.QStatusBar",
    "QWidget": "PySide6.QtWidgets.QWidget",
}

_PYSIDE6_SINGLE_MOUNT_METHODS = {
    "setCentralWidget": ("central_widget", "PySide6.QtWidgets.QWidget"),
    "setCornerWidget": ("corner_widget", "PySide6.QtWidgets.QWidget"),
    "setLayout": ("layout", None),
    "setMenu": ("menu", "PySide6.QtWidgets.QMenu"),
    "setMenuBar": ("menu_bar", "PySide6.QtWidgets.QMenuBar"),
    "setMenuWidget": ("menu_widget", "PySide6.QtWidgets.QWidget"),
    "setStatusBar": ("status_bar", "PySide6.QtWidgets.QStatusBar"),
    "setTitleBarWidget": ("title_bar_widget", "PySide6.QtWidgets.QWidget"),
    "setViewport": ("viewport", "PySide6.QtWidgets.QWidget"),
    "setWidget": ("widget", None),
}

_PYSIDE6_ORDERED_MOUNT_FAMILIES = (
    ("action", "addAction", "insertAction", "removeAction", "PySide6.QtGui.QAction"),
    ("layout", "addLayout", "insertLayout", "removeItem", "PySide6.QtWidgets.QLayout"),
    ("widget", "addWidget", "insertWidget", "removeWidget", "PySide6.QtWidgets.QWidget"),
)

_PYSIDE6_KEYED_MOUNT_PARAM_NAMES = frozenset(
    {
        "area",
        "column",
        "corner",
        "position",
        "role",
        "row",
        "section",
        "side",
    }
)

_PYSIDE6_IGNORED_ORDERING_PARAM_NAMES = frozenset({"before", "index", "pos", "position"})


def _infer_pyside6_method_learning(
    widget: DiscoveredWidgetClass,
    method: DiscoveredSetterMethod,
) -> UiMethodLearning | None:
    if method.name in _PYSIDE6_BLOCKED_METHOD_NAMES:
        return None
    if _pyside6_method_uses_blocked_types(method):
        return None
    source_props, constructor_equivalent = _infer_pyside6_source_props(widget, method)
    return UiMethodLearning(
        source_props=source_props,
        fill_policy=FillPolicy.RETAIN_EFFECTIVE,
        mode=MethodMode.CREATE_UPDATE,
        constructor_equivalent=constructor_equivalent,
    )


def _pyside6_method_uses_blocked_types(method: DiscoveredSetterMethod) -> bool:
    for parameter in method.parameters:
        if parameter.name.startswith("arg__"):
            return True
        annotation_source = parameter.annotation_source or ""
        if any(fragment in annotation_source for fragment in _PYSIDE6_BLOCKED_TYPE_FRAGMENTS):
            return True
    return False


def _infer_pyside6_source_props(
    widget: DiscoveredWidgetClass,
    method: DiscoveredSetterMethod,
) -> tuple[tuple[str, ...], bool]:
    direct = _infer_pyside6_direct_source_props(widget, method)
    if direct is not None:
        return direct, True
    return _infer_pyside6_prefixed_source_props(method), False


def _infer_pyside6_direct_source_props(
    widget: DiscoveredWidgetClass,
    method: DiscoveredSetterMethod,
) -> tuple[str, ...] | None:
    author_settable_names = _pyside6_author_settable_names(widget)
    candidate = _PYSIDE6_DIRECT_METHOD_PROP_CANDIDATES.get(method.name)
    if candidate is None:
        return None
    if len(candidate) != len(method.parameters):
        return None
    if all(name in author_settable_names for name in candidate):
        return candidate
    return None


def _pyside6_author_settable_names(widget: DiscoveredWidgetClass) -> set[str]:
    author_settable = {parameter.name for parameter in widget.parameters}
    author_settable.update(prop.name for prop in widget.properties if prop.writable)
    return author_settable


def _infer_pyside6_prefixed_source_props(
    method: DiscoveredSetterMethod,
) -> tuple[str, ...]:
    prefix = _to_snake_case(method.name[3:] or method.name)
    return tuple(
        f"{prefix}_{_normalized_pyside6_method_param_name(parameter.name)}"
        for parameter in method.parameters
    )


def _normalized_pyside6_method_param_name(name: str) -> str:
    return _PYSIDE6_FALLBACK_PARAM_NAME_MAP.get(name, _to_snake_case(name))


def generate_pyside6_learnings_source(
    learnings: Mapping[str, UiWidgetLearning],
) -> str:
    lines = [
        '"""Manual learnings for the PySide6 backend extraction pipeline."""',
        "",
        "from __future__ import annotations",
        "",
        "from frozendict import frozendict",
        "",
        "from pyrolyze.backends.model import EventPayloadPolicy, FillPolicy, MethodMode, UiEventLearning, UiMethodLearning, UiPropLearning, TypeRef, UiWidgetLearning",
        "",
        "LEARNINGS: frozendict[str, UiWidgetLearning] = frozendict(",
        "    {",
    ]
    for widget_name in sorted(learnings):
        widget_learning = learnings[widget_name]
        lines.extend(
            [
                f'        "{widget_name}": UiWidgetLearning(',
                "            prop_learnings=frozendict(",
                "                {",
            ]
        )
        for prop_name in sorted(widget_learning.prop_learnings):
            learning = widget_learning.prop_learnings[prop_name]
            lines.extend(
                [
                    f'                    "{prop_name}": UiPropLearning(',
                    f"                        public={learning.public!r},",
                    f"                        signature_annotation={_render_type_ref(learning.signature_annotation.expr) if learning.signature_annotation is not None else 'None'},",
                    f"                        signature_default_repr={learning.signature_default_repr!r},",
                    "                    ),",
                ]
            )
        lines.extend(
            [
                "                }",
                "            ),",
                "            method_learnings=frozendict(",
                "                {",
            ]
        )
        for method_name in sorted(widget_learning.method_learnings):
            learning = widget_learning.method_learnings[method_name]
            lines.extend(
                [
                    f'                    "{method_name}": UiMethodLearning(',
                    f"                        source_props={_render_string_tuple(learning.source_props or ())},",
                    f"                        fill_policy=FillPolicy.{(learning.fill_policy or FillPolicy.RETAIN_EFFECTIVE).name},",
                    f"                        mode=MethodMode.{(learning.mode or MethodMode.CREATE_UPDATE).name},",
                    f"                        constructor_equivalent={(learning.constructor_equivalent if learning.constructor_equivalent is not None else False)!r},",
                    "                    ),",
                ]
            )
        lines.extend(
            [
                "                }",
                "            ),",
                "            event_learnings=frozendict(",
                "                {",
            ]
        )
        for event_name in sorted(widget_learning.event_learnings):
            learning = widget_learning.event_learnings[event_name]
            lines.extend(
                [
                    f'                    "{event_name}": UiEventLearning(',
                    f'                        signal_name="{learning.signal_name}",',
                    f"                        payload_policy=EventPayloadPolicy.{learning.payload_policy.name},",
                    "                    ),",
                ]
            )
        lines.extend(
            [
                "                }",
                "            )",
                "        ),",
            ]
        )
    lines.extend(
        [
            "    }",
            ")",
            "",
        ]
    )
    return "\n".join(lines)


def generate_library_source(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
) -> str:
    package_name = root_module_name.split(".", 1)[0]
    class_name = _library_class_name(package_name)
    lines = [
        "#@pyrolyze",
        "",
        '"""Generated UI interface stubs for discovered widgets."""',
        "",
        "from __future__ import annotations",
        "",
        f"import {package_name}",
        "",
        "from typing import Any, ClassVar",
        "",
        "from frozendict import frozendict",
        "",
        "from pyrolyze.api import MISSING, MissingType, PyrolyzeHandler, UIElement, call_native, pyrolyze, ui_interface",
        "from pyrolyze.backends.model import (",
        "    AccessorKind,",
        "    ChildPolicy,",
        "    EventPayloadPolicy,",
        "    FillPolicy,",
        "    MethodMode,",
        "    MountParamSpec,",
        "    MountPointSpec,",
        "    PropMode,",
        "    TypeRef,",
        "    UiEventSpec,",
        "    UiInterface,",
        "    UiInterfaceEntry,",
        "    UiMethodSpec,",
        "    UiParamSpec,",
        "    UiPropSpec,",
        "    UiWidgetSpec,",
        ")",
        "",
        "",
        "@ui_interface",
        f"class {class_name}:",
        f'    ROOT_MODULE: ClassVar[str] = "{root_module_name}"',
        "",
        "    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(",
        f'        name="{class_name}",',
        "        owner=None,",
        "        entries=frozendict({",
    ]
    lines.extend(_render_ui_interface_entries(widgets))
    lines.extend(
        [
            "        }),",
            "    )",
            "",
            "    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({",
        ]
    )
    lines.extend(_render_widget_specs(root_module_name, widgets))
    lines.extend(
        [
            "    })",
        ]
    )
    if package_name == "PySide6" and any(widget.properties for widget in widgets):
        lines.extend(
            [
                "",
                '    QT_PROPERTY_GETTER: ClassVar[str] = "property"',
                '    QT_PROPERTY_SETTER: ClassVar[str] = "setProperty"',
            ]
        )
    lines.extend(
        [
            "",
            "    @classmethod",
            "    # NOTE: a trailing `kwds` parameter enables PyRolyze's tail kwds optimization.",
            "    # The compiler lowers matching wrappers so only actually passed arguments",
            "    # are forwarded into `UIElement.props`. See",
            "    # docs/design/Packed_Kwds_UI_Interface_Optimization.md.",
            "    def __element(cls, *, kind: str, kwds: dict[str, Any]) -> UIElement:",
            "        return UIElement(kind=kind, props=dict(kwds))",
        ]
    )
    for widget in widgets:
        lines.extend(_render_widget_method(package_name, widget))
    return "\n".join(lines) + "\n"


def _render_ui_interface_entries(widgets: Sequence[DiscoveredWidgetClass]) -> list[str]:
    return [
        f'            "{widget.public_name}": UiInterfaceEntry(public_name="{widget.public_name}", kind="{widget.class_name}"),'
        for widget in widgets
    ]


def _render_widget_specs(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
) -> list[str]:
    package_name = root_module_name.split(".", 1)[0]
    lines: list[str] = []
    for widget in widgets:
        lines.extend(_render_single_widget_spec(package_name, widget))
    return lines


def _render_single_widget_spec(
    package_name: str,
    widget: DiscoveredWidgetClass,
) -> list[str]:
    default_child_mount_point_name = _infer_default_child_mount_point_name(package_name, widget.mount_points)
    default_attach_mount_point_names = _infer_default_attach_mount_point_names(package_name, widget.mount_points)
    lines = [
        f'        "{widget.class_name}": UiWidgetSpec(',
        f'            kind="{widget.class_name}",',
        f'            mounted_type_name="{widget.module_name}.{widget.class_name}",',
        "            constructor_params=frozendict({",
    ]
    lines.extend(_render_constructor_params(widget.parameters))
    lines.extend(
        [
            "            }),",
            "            props=frozendict({",
        ]
    )
    lines.extend(_render_widget_props(package_name, widget))
    lines.extend(
        [
            "            }),",
            "            methods=frozendict({",
        ]
    )
    lines.extend(_render_widget_methods(widget.setter_methods, widget.method_learnings))
    lines.extend(
        [
            "            }),",
            "            events=frozendict({",
        ]
    )
    lines.extend(_render_widget_events(widget.event_learnings))
    lines.extend(
        [
            "            }),",
            "            mount_points=frozendict({",
        ]
    )
    lines.extend(_render_mount_points(widget.mount_points))
    lines.extend(
        [
            "            }),",
            f"            default_child_mount_point_name={default_child_mount_point_name!r},",
            f"            default_attach_mount_point_names={default_attach_mount_point_names!r},",
            "            child_policy=ChildPolicy.NONE,",
            "        ),",
        ]
    )
    return lines


def _render_constructor_params(parameters: Sequence[DiscoveredParameter]) -> list[str]:
    return [
        (
            f'                "{parameter.name}": UiParamSpec('
            f'name="{parameter.name}", annotation={_render_type_ref(parameter.annotation_source)}, '
            f"default_repr={parameter.default_source!r}),"
        )
        for parameter in parameters
    ]


def _render_widget_props(package_name: str, widget: DiscoveredWidgetClass) -> list[str]:
    constructor_params = {parameter.name: parameter for parameter in widget.parameters}
    properties = {prop.name: prop for prop in widget.properties}
    prop_names = tuple(dict.fromkeys([*constructor_params, *properties]))
    lines: list[str] = []
    for prop_name in prop_names:
        parameter = constructor_params.get(prop_name)
        discovered_property = properties.get(prop_name)
        annotation_source = (
            parameter.annotation_source
            if parameter is not None
            else discovered_property.type_name if discovered_property is not None else None
        )
        lines.append(
            f'                "{prop_name}": UiPropSpec('
            f'name="{prop_name}", '
            f"annotation={_render_type_ref(annotation_source)}, "
            f"mode={_render_prop_mode(parameter is not None, discovered_property)}, "
            f"constructor_name={repr(parameter.name) if parameter is not None else 'None'}, "
            f"setter_kind={_render_setter_kind(package_name, discovered_property)}, "
            f"setter_name={_render_setter_name(package_name, discovered_property)}, "
            f"getter_kind={_render_getter_kind(package_name, discovered_property)}, "
            f"getter_name={_render_getter_name(package_name, discovered_property)}, "
            f"affects_identity={_render_affects_identity(parameter is not None, discovered_property)}),"
        )
    return lines


def _infer_default_child_mount_point_name(
    package_name: str,
    mount_points: Sequence[DiscoveredMountPoint],
) -> str | None:
    available = {mount_point.name for mount_point in mount_points}
    for candidate in _default_child_mount_priority(package_name):
        if candidate in available:
            return candidate
    return next(iter(available), None)


def _infer_default_attach_mount_point_names(
    package_name: str,
    mount_points: Sequence[DiscoveredMountPoint],
) -> tuple[str, ...]:
    candidate_names = {
        mount_point.name
        for mount_point in mount_points
        if _mount_point_supports_unspecified_attach(mount_point)
    }
    ordered = [
        candidate
        for candidate in _default_attach_mount_priority(package_name)
        if candidate in candidate_names
    ]
    extras = sorted(candidate_names.difference(ordered))
    return tuple([*ordered, *extras])


def _mount_point_supports_unspecified_attach(mount_point: DiscoveredMountPoint) -> bool:
    for param in mount_point.params:
        if param.kind not in {
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        }:
            return False
        if param.default_source is None:
            return False
    return True


def _default_child_mount_priority(package_name: str) -> tuple[str, ...]:
    if package_name == "PySide6":
        return (
            "standard",
            "layout",
            "widget",
            "central_widget",
            "menu",
            "action",
            "menu_bar",
            "status_bar",
            "viewport",
            "title_bar_widget",
            "menu_widget",
            "corner_widget",
        )
    return (
        "standard",
        "widget",
        "layout",
        "menu",
        "action",
    )


def _default_attach_mount_priority(package_name: str) -> tuple[str, ...]:
    if package_name == "PySide6":
        return (
            "standard",
            "menu_bar",
            "status_bar",
            "title_bar_widget",
            "viewport",
            "layout",
            "central_widget",
            "widget",
            "menu",
            "action",
            "menu_widget",
            "corner_widget",
        )
    return (
        "standard",
        "widget",
        "layout",
        "menu",
        "action",
    )


def _render_widget_methods(
    setter_methods: Sequence[DiscoveredSetterMethod],
    method_learnings: Mapping[str, UiMethodLearning],
) -> list[str]:
    lines: list[str] = []
    for method in setter_methods:
        learning = method_learnings.get(method.name)
        source_props = (
            learning.source_props
            if learning is not None and learning.source_props is not None
            else tuple(parameter.name for parameter in method.parameters)
        )
        fill_policy = (
            learning.fill_policy
            if learning is not None and learning.fill_policy is not None
            else FillPolicy.RETAIN_EFFECTIVE
        )
        mode = (
            learning.mode
            if learning is not None and learning.mode is not None
            else MethodMode.CREATE_UPDATE
        )
        constructor_equivalent = (
            learning.constructor_equivalent
            if learning is not None and learning.constructor_equivalent is not None
            else False
        )
        lines.append(f'                "{method.name}": UiMethodSpec(')
        lines.append(f'                    name="{method.name}",')
        lines.append(f"                    mode=MethodMode.{mode.name},")
        lines.append("                    params=(")
        for parameter in method.parameters:
            lines.append(
                "                        "
                f'UiParamSpec(name="{parameter.name}", annotation={_render_type_ref(parameter.annotation_source)}, '
                f"default_repr={parameter.default_source!r}),"
            )
        lines.append("                    ),")
        lines.append(
            "                    "
            f"source_props={_render_string_tuple(source_props)},"
        )
        lines.append(f"                    fill_policy=FillPolicy.{fill_policy.name},")
        lines.append(f"                    constructor_equivalent={constructor_equivalent!r},")
        lines.append("                ),")
    return lines


def _render_mount_points(mount_points: Sequence[DiscoveredMountPoint]) -> list[str]:
    lines: list[str] = []
    for mount_point in mount_points:
        lines.append(f'                "{mount_point.name}": MountPointSpec(')
        lines.append(f'                    name="{mount_point.name}",')
        lines.append(
            "                    "
            f"accepted_produced_type={_render_type_ref(mount_point.accepted_type_name)},"
        )
        lines.append("                    params=(")
        for parameter in mount_point.params:
            keyed = parameter.name in _PYSIDE6_KEYED_MOUNT_PARAM_NAMES
            lines.append(
                "                        "
                f'MountParamSpec(name="{parameter.name}", annotation={_render_type_ref(parameter.annotation_source)}, '
                f"keyed={keyed!r}, default_repr={parameter.default_source!r}),"
            )
        lines.extend(
            [
                "                    ),",
                f"                    min_children={mount_point.min_children!r},",
                f"                    max_children={mount_point.max_children!r},",
                f"                    apply_method_name={mount_point.apply_method_name!r},",
                f"                    sync_method_name={mount_point.sync_method_name!r},",
                f"                    place_method_name={mount_point.place_method_name!r},",
                f"                    detach_method_name={mount_point.detach_method_name!r},",
                "                ),",
            ]
        )
    return lines


def _render_widget_events(
    event_learnings: Mapping[str, UiEventLearning],
) -> list[str]:
    lines: list[str] = []
    for event_name in sorted(event_learnings):
        learning = event_learnings[event_name]
        lines.extend(
            [
                f'                "{event_name}": UiEventSpec(',
                f'                    name="{event_name}",',
                f'                    signal_name="{learning.signal_name}",',
                f"                    payload_policy=EventPayloadPolicy.{learning.payload_policy.name},",
                "                ),",
            ]
        )
    return lines


def write_generated_library(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    *,
    output_dir: Path,
    output_name: str | None = None,
    learnings: Mapping[str, UiWidgetLearning] | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_name = root_module_name.split(".", 1)[0]
    output_file = output_dir / (output_name or f"{package_name.lower()}.py")
    resolved_widgets = apply_learnings(widgets, learnings or load_learnings(root_module_name))
    output_file.write_text(generate_library_source(root_module_name, resolved_widgets))
    return output_file


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate a semantic-library source file from discovered widget classes.",
    )
    parser.add_argument("module", help="Root module or package to inspect.")
    parser.add_argument(
        "--widget-base",
        dest="widget_bases",
        action="append",
        default=None,
        help="Base widget class in module:Class form. May be provided multiple times.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path.cwd(),
        help="Directory to place the generated <package>.py file.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)
    widgets = discover_widget_classes(
        args.module,
        widget_base_specs=tuple(args.widget_bases) if args.widget_bases else None,
    )
    write_generated_library(args.module, widgets, output_dir=args.output_dir)
    return 0


def _resolve_widget_bases(
    root_module_name: str,
    widget_base_specs: tuple[str, ...] | None,
) -> tuple[type[Any], ...]:
    specs = widget_base_specs or _default_widget_base_specs(root_module_name)
    resolved: list[type[Any]] = []
    for spec in specs:
        module_name, separator, attribute_name = spec.partition(":")
        if not separator:
            raise ValueError(f"Invalid widget base spec {spec!r}; expected module:Class")
        module = importlib.import_module(module_name)
        resolved.append(getattr(module, attribute_name))
    return tuple(resolved)


def _default_widget_base_specs(root_module_name: str) -> tuple[str, ...]:
    package_name = root_module_name.split(".", 1)[0]
    if package_name == "PySide6":
        return (
            "PySide6.QtWidgets:QWidget",
            "PySide6.QtWidgets:QLayout",
            "PySide6.QtGui:QAction",
        )
    if package_name == "tkinter":
        return ("tkinter:Widget", "tkinter.ttk:Widget")
    raise ValueError(
        "widget_base_specs is required for non-standard packages; "
        "no default widget base is known for "
        f"{root_module_name!r}"
    )


def _extract_parameters(
    root_module_name: str,
    widget_class: type[Any],
) -> tuple[DiscoveredParameter, ...]:
    package_name = root_module_name.split(".", 1)[0]
    if package_name == "PySide6":
        parameters = _extract_pyside6_parameters(widget_class)
        if parameters:
            return parameters
    return _extract_runtime_parameters(widget_class)


def _extract_properties(
    root_module_name: str,
    widget_class: type[Any],
) -> tuple[DiscoveredProperty, ...]:
    package_name = root_module_name.split(".", 1)[0]
    if package_name == "PySide6":
        return _extract_qt_properties(widget_class)
    return ()


def _extract_runtime_parameters(widget_class: type[Any]) -> tuple[DiscoveredParameter, ...]:
    signature = _widget_signature(widget_class)
    parameters: list[DiscoveredParameter] = []
    for parameter in signature.parameters.values():
        if parameter.name in {"self", "cls"}:
            continue
        if parameter.kind in {
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        }:
            continue
        annotation_source = _annotation_source(parameter.annotation)
        default_source = None
        if parameter.default is not inspect.Parameter.empty:
            default_source = repr(parameter.default)
        parameters.append(
            DiscoveredParameter(
                name=parameter.name,
                kind=parameter.kind,
                annotation_source=annotation_source,
                default_source=default_source,
                coerced_expression=_coerce_expression(
                    parameter.name,
                    annotation_source,
                    default_source,
                ),
            )
        )
    return tuple(parameters)


def _extract_pyside6_parameters(widget_class: type[Any]) -> tuple[DiscoveredParameter, ...]:
    class_node = _find_stub_class(widget_class.__module__, widget_class.__name__)
    if class_node is None:
        return ()
    overloads = _extract_stub_init_overloads(class_node)
    if not overloads:
        return ()
    base_parameters = max(overloads, key=len)
    merged: dict[str, DiscoveredParameter] = {param.name: param for param in base_parameters}
    order = [param.name for param in base_parameters]
    for overload in overloads:
        for parameter in overload:
            if parameter.name not in merged:
                merged[parameter.name] = parameter
                order.append(parameter.name)
    return tuple(merged[name] for name in order)


def _extract_qt_properties(widget_class: type[Any]) -> tuple[DiscoveredProperty, ...]:
    meta_object = getattr(widget_class, "staticMetaObject", None)
    if meta_object is None:
        return ()
    properties: dict[str, DiscoveredProperty] = {}
    for index in range(meta_object.propertyCount()):
        prop = meta_object.property(index)
        name = prop.name()
        properties[name] = DiscoveredProperty(
            name=name,
            type_name=prop.typeName(),
            readable=bool(prop.isReadable()),
            writable=bool(prop.isWritable()),
        )
    return tuple(properties[name] for name in sorted(properties))


def _extract_multiarg_setter_methods(
    root_module_name: str,
    widget_class: type[Any],
) -> tuple[DiscoveredSetterMethod, ...]:
    package_name = root_module_name.split(".", 1)[0]
    if package_name == "PySide6":
        return _extract_pyside6_multiarg_setters(widget_class)
    if package_name == "tkinter":
        return _extract_tkinter_multiarg_setters(widget_class)
    return ()


def _extract_mount_points(
    root_module_name: str,
    widget_class: type[Any],
) -> tuple[DiscoveredMountPoint, ...]:
    package_name = root_module_name.split(".", 1)[0]
    if package_name == "PySide6":
        return _extract_pyside6_mount_points(widget_class)
    return ()


def _has_variadic_parameters(
    root_module_name: str,
    widget_class: type[Any],
) -> bool:
    package_name = root_module_name.split(".", 1)[0]
    if package_name == "PySide6" and _extract_pyside6_parameters(widget_class):
        return False
    signature = _widget_signature(widget_class)
    return any(
        parameter.kind in {
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        }
        for parameter in signature.parameters.values()
    )


def _widget_signature(widget_class: type[Any]) -> inspect.Signature:
    try:
        return inspect.signature(widget_class)
    except (TypeError, ValueError):
        return inspect.signature(widget_class.__init__)


def _extract_pyside6_mount_points(
    widget_class: type[Any],
) -> tuple[DiscoveredMountPoint, ...]:
    named_methods = _extract_pyside6_named_methods(
        widget_class,
        tuple(
            {
                *tuple(_PYSIDE6_SINGLE_MOUNT_METHODS),
                *(family[1] for family in _PYSIDE6_ORDERED_MOUNT_FAMILIES),
                *(family[2] for family in _PYSIDE6_ORDERED_MOUNT_FAMILIES if family[2] is not None),
            }
        ),
    )
    discovered: dict[str, DiscoveredMountPoint] = {}
    for method_name, (mount_name, accepted_type_name) in _PYSIDE6_SINGLE_MOUNT_METHODS.items():
        parameters = named_methods.get(method_name)
        if parameters is None:
            continue
        mount_point = _build_pyside6_single_mount_point(
            method_name,
            mount_name,
            accepted_type_name,
            parameters,
        )
        if mount_point is not None:
            discovered.setdefault(mount_point.name, mount_point)
    for family_name, add_name, insert_name, detach_name, accepted_type_name in _PYSIDE6_ORDERED_MOUNT_FAMILIES:
        preferred_name = insert_name if insert_name in named_methods else add_name
        parameters = named_methods.get(preferred_name)
        if parameters is None:
            continue
        mount_point = _build_pyside6_family_mount_point(
            family_name=family_name,
            preferred_method_name=preferred_name,
            add_method_name=add_name,
            insert_method_name=insert_name,
            detach_method_name=detach_name,
            accepted_type_name=accepted_type_name,
            parameters=parameters,
        )
        if mount_point is not None:
            discovered.setdefault(mount_point.name, mount_point)
    return tuple(discovered[name] for name in sorted(discovered))


def _build_pyside6_single_mount_point(
    method_name: str,
    mount_name: str,
    accepted_type_name: str | None,
    parameters: tuple[DiscoveredParameter, ...],
) -> DiscoveredMountPoint | None:
    object_parameter = _find_mount_object_parameter(parameters, accepted_type_name)
    if object_parameter is None:
        return None
    mount_params = tuple(
        parameter
        for parameter in parameters
        if parameter.name != object_parameter.name and parameter.name not in _PYSIDE6_IGNORED_ORDERING_PARAM_NAMES
    )
    return DiscoveredMountPoint(
        name=mount_name,
        accepted_type_name=accepted_type_name or _normalized_mount_type_name(object_parameter.annotation_source),
        params=mount_params,
        max_children=1,
        apply_method_name=method_name,
    )


def _build_pyside6_family_mount_point(
    *,
    family_name: str,
    preferred_method_name: str,
    add_method_name: str,
    insert_method_name: str | None,
    detach_method_name: str,
    accepted_type_name: str,
    parameters: tuple[DiscoveredParameter, ...],
) -> DiscoveredMountPoint | None:
    object_parameter = _find_mount_object_parameter(parameters, accepted_type_name)
    if object_parameter is None:
        return None
    contextual_params = tuple(
        parameter
        for parameter in parameters
        if parameter.name != object_parameter.name and parameter.name not in _PYSIDE6_IGNORED_ORDERING_PARAM_NAMES
    )
    if any(parameter.name in {"row", "column"} for parameter in contextual_params):
        return DiscoveredMountPoint(
            name=family_name,
            accepted_type_name=accepted_type_name,
            params=contextual_params,
            max_children=1,
            apply_method_name=add_method_name,
        )
    if preferred_method_name != insert_method_name:
        return None
    return DiscoveredMountPoint(
        name=family_name,
        accepted_type_name=accepted_type_name,
        params=contextual_params,
        max_children=None,
        place_method_name=preferred_method_name,
        detach_method_name=detach_method_name,
    )


def _find_mount_object_parameter(
    parameters: Sequence[DiscoveredParameter],
    accepted_type_name: str | None,
) -> DiscoveredParameter | None:
    target_fragments = (
        (accepted_type_name.split(".")[-1],)
        if accepted_type_name is not None
        else tuple(_PYSIDE6_MOUNT_TYPE_QUALIFIERS)
    )
    for parameter in parameters:
        annotation_source = parameter.annotation_source or ""
        if any(fragment in annotation_source for fragment in target_fragments):
            return parameter
    if accepted_type_name is not None and len(parameters) == 1:
        return parameters[0]
    return None


def _extract_pyside6_named_methods(
    widget_class: type[Any],
    method_names: tuple[str, ...],
) -> dict[str, tuple[DiscoveredParameter, ...]]:
    discovered: dict[str, tuple[DiscoveredParameter, ...]] = {}
    wanted = set(method_names)
    for base_class in widget_class.__mro__:
        if not getattr(base_class, "__module__", "").startswith("PySide6."):
            continue
        class_node = _find_stub_class(base_class.__module__, base_class.__name__)
        if class_node is None:
            continue
        grouped: dict[str, list[tuple[DiscoveredParameter, ...]]] = {}
        for node in class_node.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if node.name not in wanted:
                continue
            grouped.setdefault(node.name, []).append(_ast_method_parameters_to_discovered(node.args))
        for method_name, overloads in grouped.items():
            if method_name in discovered:
                continue
            discovered[method_name] = max(overloads, key=_parameter_specificity)
    return discovered


def _normalized_mount_type_name(annotation_source: str | None) -> str:
    if annotation_source is None:
        return "object"
    for fragment, qualified_name in _PYSIDE6_MOUNT_TYPE_QUALIFIERS.items():
        if fragment in annotation_source:
            return qualified_name
    return annotation_source


@lru_cache(maxsize=None)
def _load_stub_module_ast(module_name: str) -> ast.Module | None:
    module = importlib.import_module(module_name)
    module_path = Path(getattr(module, "__file__", ""))
    stub_path = module_path.parent / f"{module_path.name.split('.', 1)[0]}.pyi"
    if not stub_path.exists():
        return None
    return ast.parse(stub_path.read_text())


def _find_stub_class(module_name: str, class_name: str) -> ast.ClassDef | None:
    module_ast = _load_stub_module_ast(module_name)
    if module_ast is None:
        return None
    for node in module_ast.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def _extract_stub_init_overloads(class_node: ast.ClassDef) -> list[tuple[DiscoveredParameter, ...]]:
    overloads: list[tuple[DiscoveredParameter, ...]] = []
    for node in class_node.body:
        if isinstance(node, ast.FunctionDef) and node.name == "__init__":
            overloads.append(_ast_parameters_to_discovered(node.args))
    return overloads


def _extract_pyside6_multiarg_setters(
    widget_class: type[Any],
) -> tuple[DiscoveredSetterMethod, ...]:
    discovered: dict[str, DiscoveredSetterMethod] = {}
    for base_class in widget_class.__mro__:
        if not getattr(base_class, "__module__", "").startswith("PySide6."):
            continue
        class_node = _find_stub_class(base_class.__module__, base_class.__name__)
        if class_node is None:
            continue
        grouped: dict[str, list[tuple[DiscoveredParameter, ...]]] = {}
        for node in class_node.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if not node.name.startswith("set"):
                continue
            if node.name == "setProperty":
                continue
            parameters = _ast_method_parameters_to_discovered(node.args)
            if not _is_multiarg_method(parameters, has_var_keyword=node.args.kwarg is not None):
                continue
            grouped.setdefault(node.name, []).append(parameters)
        for method_name, overloads in grouped.items():
            if method_name in discovered:
                continue
            parameters = max(overloads, key=_parameter_specificity)
            discovered[method_name] = DiscoveredSetterMethod(
                owner_class_name=base_class.__name__,
                name=method_name,
                parameters=parameters,
            )
    return tuple(discovered[name] for name in sorted(discovered))


def _extract_tkinter_multiarg_setters(
    widget_class: type[Any],
) -> tuple[DiscoveredSetterMethod, ...]:
    discovered: dict[str, DiscoveredSetterMethod] = {}
    for base_class in widget_class.__mro__:
        if not getattr(base_class, "__module__", "").startswith("tkinter"):
            continue
        for method_name, function in inspect.getmembers(base_class, inspect.isfunction):
            if not method_name.startswith("set"):
                continue
            if method_name == "setvar":
                continue
            try:
                signature = inspect.signature(function)
            except (TypeError, ValueError):
                continue
            parameters = _signature_method_parameters_to_discovered(signature)
            has_var_keyword = any(
                parameter.kind == inspect.Parameter.VAR_KEYWORD
                for parameter in signature.parameters.values()
            )
            if not _is_multiarg_method(parameters, has_var_keyword=has_var_keyword):
                continue
            discovered.setdefault(
                method_name,
                DiscoveredSetterMethod(
                    owner_class_name=base_class.__name__,
                    name=method_name,
                    parameters=parameters,
                ),
            )
    return tuple(discovered[name] for name in sorted(discovered))


def _ast_parameters_to_discovered(args: ast.arguments) -> tuple[DiscoveredParameter, ...]:
    parameters: list[DiscoveredParameter] = []
    positional = [*args.posonlyargs, *args.args]
    positional_defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    for argument, default in zip(positional, positional_defaults):
        if argument.arg == "self":
            continue
        annotation_source = ast.unparse(argument.annotation) if argument.annotation is not None else None
        default_source = ast.unparse(default) if default is not None else None
        parameters.append(
            DiscoveredParameter(
                name=argument.arg,
                kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                annotation_source=annotation_source,
                default_source=default_source,
                coerced_expression=_coerce_expression(
                    argument.arg,
                    annotation_source,
                    default_source,
                ),
            )
        )
    for argument, default in zip(args.kwonlyargs, args.kw_defaults):
        annotation_source = ast.unparse(argument.annotation) if argument.annotation is not None else None
        default_source = ast.unparse(default) if default is not None else None
        parameters.append(
            DiscoveredParameter(
                name=argument.arg,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation_source=annotation_source,
                default_source=default_source,
                coerced_expression=_coerce_expression(
                    argument.arg,
                    annotation_source,
                    default_source,
                ),
            )
        )
    return tuple(parameters)


def _ast_method_parameters_to_discovered(args: ast.arguments) -> tuple[DiscoveredParameter, ...]:
    parameters = _ast_parameters_to_discovered(args)
    return tuple(parameter for parameter in parameters if parameter.name != "cls")


def _signature_method_parameters_to_discovered(
    signature: inspect.Signature,
) -> tuple[DiscoveredParameter, ...]:
    parameters: list[DiscoveredParameter] = []
    for parameter in signature.parameters.values():
        if parameter.name in {"self", "cls"}:
            continue
        if parameter.kind in {
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        }:
            continue
        annotation_source = _annotation_source(parameter.annotation)
        default_source = None
        if parameter.default is not inspect.Parameter.empty:
            default_source = repr(parameter.default)
        parameters.append(
            DiscoveredParameter(
                name=parameter.name,
                kind=parameter.kind,
                annotation_source=annotation_source,
                default_source=default_source,
                coerced_expression=_coerce_expression(
                    parameter.name,
                    annotation_source,
                    default_source,
                ),
            )
        )
    return tuple(parameters)


def _is_multiarg_method(
    parameters: Sequence[DiscoveredParameter],
    *,
    has_var_keyword: bool,
) -> bool:
    return len(parameters) > 1 or has_var_keyword


def _parameter_specificity(parameters: Sequence[DiscoveredParameter]) -> int:
    return sum(1 for parameter in parameters if parameter.default_source is None)


def _annotation_source(annotation: Any) -> str | None:
    if annotation is inspect.Parameter.empty:
        return None
    if isinstance(annotation, str):
        return annotation
    if annotation is None:
        return "None"
    if getattr(annotation, "__module__", "") == "builtins" and hasattr(annotation, "__name__"):
        return annotation.__name__
    return repr(annotation).replace("typing.", "")


def _coerce_expression(
    name: str,
    annotation_source: str | None,
    default_source: str | None,
) -> str:
    annotation_name = annotation_source or ""
    if annotation_name == "bool" or annotation_name.startswith("bool |") or default_source in {"True", "False"}:
        return f"bool({name})"
    if annotation_name == "int" or annotation_name.startswith("int |"):
        return f"int({name})"
    if annotation_name.startswith("tuple"):
        return f"tuple({name})"
    return name


def _render_widget_method(
    package_name: str,
    widget: DiscoveredWidgetClass,
) -> list[str]:
    public_parameters = _public_parameters_for_widget(package_name, widget)
    signature_lines = _render_signature_lines(public_parameters)
    prop_lines = _render_prop_lines(public_parameters)
    lines = [
        "",
        "    @classmethod",
        "    @pyrolyze",
    ]
    if widget.omitted_variadic_arguments:
        lines.append(
            f"    # NOTE: original signature for {widget.class_name} includes omitted variadic arguments"
        )
    lines.append(f"    def {widget.public_name}(")
    lines.extend(signature_lines)
    lines.extend(
        [
            "    ) -> None:",
            "        call_native(cls.__element)(",
            f'            kind="{widget.class_name}",',
        ]
    )
    lines.extend(prop_lines)
    lines.extend(["        )"])
    return lines


def _render_signature_lines(parameters: Sequence[DiscoveredParameter]) -> list[str]:
    lines = ["        cls,"]
    saw_keyword_only = False
    for parameter in parameters:
        if parameter.kind == inspect.Parameter.KEYWORD_ONLY and not saw_keyword_only:
            lines.append("        *,")
            saw_keyword_only = True
        part = f"        {parameter.name}"
        if parameter.annotation_source is not None:
            part += f": {parameter.annotation_source}"
        if parameter.default_source is not None:
            part += f" = {parameter.default_source}"
        part += ","
        lines.append(part)
    return lines


def _render_prop_lines(parameters: Sequence[DiscoveredParameter]) -> list[str]:
    return [
        f"            {parameter.name}={parameter.name},"
        for parameter in parameters
    ]


def _public_parameters_for_widget(
    package_name: str,
    widget: DiscoveredWidgetClass,
) -> tuple[DiscoveredParameter, ...]:
    parameters: list[DiscoveredParameter] = []
    for parameter in widget.parameters:
        learning = widget.prop_learnings.get(parameter.name)
        if learning is not None and learning.public is False:
            continue
        parameters.append(_apply_parameter_learning(parameter, learning))
    known_names = {parameter.name for parameter in parameters}
    for prop in widget.properties:
        learning = widget.prop_learnings.get(prop.name)
        if learning is not None and learning.public is False:
            continue
        if not prop.writable or prop.name in known_names:
            continue
        parameters.append(
            DiscoveredParameter(
                name=prop.name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation_source=(
                    learning.signature_annotation.expr
                    if learning is not None and learning.signature_annotation is not None
                    else _signature_annotation_for_property(package_name, prop)
                ),
                default_source=(
                    learning.signature_default_repr
                    if learning is not None and learning.signature_default_repr is not None
                    else "MISSING"
                ),
                coerced_expression=prop.name,
            )
        )
        known_names.add(prop.name)
    method_by_name = {method.name: method for method in widget.setter_methods}
    for method_name, learning in widget.method_learnings.items():
        method = method_by_name.get(method_name)
        if method is None or learning.source_props is None:
            continue
        for index, source_prop in enumerate(learning.source_props):
            prop_learning = widget.prop_learnings.get(source_prop)
            if prop_learning is not None and prop_learning.public is False:
                continue
            if source_prop in known_names:
                continue
            method_parameter = method.parameters[index] if index < len(method.parameters) else None
            parameters.append(
                DiscoveredParameter(
                    name=source_prop,
                    kind=inspect.Parameter.KEYWORD_ONLY,
                    annotation_source=(
                        prop_learning.signature_annotation.expr
                        if prop_learning is not None and prop_learning.signature_annotation is not None
                        else _signature_annotation_for_omittable(
                            method_parameter.annotation_source if method_parameter is not None else None
                        )
                    ),
                    default_source=(
                        prop_learning.signature_default_repr
                        if prop_learning is not None and prop_learning.signature_default_repr is not None
                        else "MISSING"
                    ),
                    coerced_expression=source_prop,
                )
            )
            known_names.add(source_prop)
    for event_name in sorted(widget.event_learnings):
        if event_name in known_names:
            continue
        learning = widget.event_learnings[event_name]
        parameters.append(
            DiscoveredParameter(
                name=event_name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation_source=_signature_annotation_for_event(learning),
                default_source="MISSING",
                coerced_expression=event_name,
            )
        )
        known_names.add(event_name)
    return tuple(parameters)


def _signature_annotation_for_event(learning: UiEventLearning) -> str:
    if learning.payload_policy is EventPayloadPolicy.NONE:
        return "PyrolyzeHandler[[], None] | MissingType"
    if learning.payload_policy is EventPayloadPolicy.FIRST_ARG:
        return "PyrolyzeHandler[[Any], None] | MissingType"
    return "PyrolyzeHandler[..., None] | MissingType"


def _apply_parameter_learning(
    parameter: DiscoveredParameter,
    learning: UiPropLearning | None,
) -> DiscoveredParameter:
    if learning is None:
        return parameter
    return DiscoveredParameter(
        name=parameter.name,
        kind=parameter.kind,
        annotation_source=(
            learning.signature_annotation.expr
            if learning.signature_annotation is not None
            else parameter.annotation_source
        ),
        default_source=(
            learning.signature_default_repr
            if learning.signature_default_repr is not None
            else parameter.default_source
        ),
        coerced_expression=parameter.coerced_expression,
    )


def _signature_annotation_for_property(
    package_name: str,
    prop: DiscoveredProperty,
) -> str:
    if package_name == "PySide6":
        return f"{_qt_property_python_type(prop.type_name)} | MissingType"
    return "Any | MissingType"


def _signature_annotation_for_omittable(annotation_source: str | None) -> str:
    if annotation_source is None:
        return "Any | MissingType"
    if "MissingType" in annotation_source:
        return annotation_source
    return f"{annotation_source} | MissingType"


def _qt_property_python_type(type_name: str) -> str:
    mapping = {
        "bool": "bool",
        "int": "int",
        "double": "float",
        "QString": "str",
    }
    return mapping.get(type_name, "Any")


def _render_type_ref(annotation_source: str | None) -> str:
    if annotation_source is None:
        return "None"
    return f'TypeRef(expr={annotation_source!r})'


def _render_string_tuple(values: tuple[str, ...]) -> str:
    if not values:
        return "()"
    rendered = ", ".join(f'"{value}"' for value in values)
    if len(values) == 1:
        rendered += ","
    return f"({rendered})"


def _render_prop_mode(
    has_constructor_parameter: bool,
    discovered_property: DiscoveredProperty | None,
) -> str:
    if discovered_property is None:
        return "PropMode.CREATE_ONLY_REMOUNT"
    if discovered_property.writable:
        return "PropMode.CREATE_UPDATE"
    if has_constructor_parameter:
        return "PropMode.CREATE_ONLY_REMOUNT"
    return "PropMode.READONLY"


def _render_setter_kind(
    package_name: str,
    discovered_property: DiscoveredProperty | None,
) -> str:
    if discovered_property is None or not discovered_property.writable:
        return "None"
    if package_name == "PySide6":
        return "AccessorKind.QT_PROPERTY"
    if package_name == "tkinter":
        return "AccessorKind.TK_CONFIG"
    return "AccessorKind.METHOD"


def _render_setter_name(
    package_name: str,
    discovered_property: DiscoveredProperty | None,
) -> str:
    if discovered_property is None or not discovered_property.writable:
        return "None"
    if package_name == "PySide6":
        return '"setProperty"'
    if package_name == "tkinter":
        return '"configure"'
    return "None"


def _render_getter_kind(
    package_name: str,
    discovered_property: DiscoveredProperty | None,
) -> str:
    if discovered_property is None or not discovered_property.readable:
        return "None"
    if package_name == "PySide6":
        return "AccessorKind.QT_PROPERTY"
    if package_name == "tkinter":
        return "AccessorKind.TK_CONFIG"
    return "AccessorKind.METHOD"


def _render_getter_name(
    package_name: str,
    discovered_property: DiscoveredProperty | None,
) -> str:
    if discovered_property is None or not discovered_property.readable:
        return "None"
    if package_name == "PySide6":
        return '"property"'
    if package_name == "tkinter":
        return '"cget"'
    return "None"


def _render_affects_identity(
    has_constructor_parameter: bool,
    discovered_property: DiscoveredProperty | None,
) -> str:
    if discovered_property is None:
        return "True" if has_constructor_parameter else "False"
    if discovered_property.writable:
        return "False"
    return "True" if has_constructor_parameter else "False"


def _to_snake_case(name: str) -> str:
    step_one = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", step_one).lower()


def _should_skip_module(module_name: str) -> bool:
    return module_name.endswith(".__main__")


def _library_class_name(package_name: str) -> str:
    if package_name == "PySide6":
        return "PySide6UiLibrary"
    if package_name == "tkinter":
        return "TkinterUiLibrary"
    return f"{package_name.capitalize()}UiLibrary"


def _assign_public_names(
    root_module_name: str,
    widgets: Sequence[tuple[str, str]],
) -> tuple[str, ...]:
    package_name = root_module_name.split(".", 1)[0]
    base_names = [f"C{class_name}" for _, class_name in widgets]
    counts: dict[str, int] = {}
    for base_name in base_names:
        counts[base_name] = counts.get(base_name, 0) + 1
    resolved: list[str] = []
    used: set[str] = set()
    for (module_name, class_name), base_name in zip(widgets, base_names, strict=True):
        if counts[base_name] == 1 and base_name not in used:
            resolved_name = base_name
        else:
            module_suffix = _module_suffix_name(package_name, module_name)
            resolved_name = f"C{module_suffix}{class_name}" if module_suffix else base_name
            collision_index = 2
            while resolved_name in used:
                resolved_name = f"C{module_suffix}{class_name}{collision_index}"
                collision_index += 1
        used.add(resolved_name)
        resolved.append(resolved_name)
    return tuple(resolved)


def _module_suffix_name(package_name: str, module_name: str) -> str:
    segments = module_name.split(".")
    if segments and segments[0] == package_name:
        segments = segments[1:]
    if not segments:
        return ""
    return "".join(_capitalize_segment(segment) for segment in segments)


def _capitalize_segment(segment: str) -> str:
    parts = [part for part in re.split(r"[^a-zA-Z0-9]+", segment) if part]
    return "".join(part[:1].upper() + part[1:] for part in parts)


if __name__ == "__main__":
    raise SystemExit(main())

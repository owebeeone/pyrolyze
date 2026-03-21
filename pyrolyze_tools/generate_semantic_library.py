from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from functools import lru_cache
import importlib
import inspect
import pkgutil
from pathlib import Path
import re
from typing import Any, Sequence


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
class DiscoveredWidgetClass:
    module_name: str
    class_name: str
    public_name: str
    parameters: tuple[DiscoveredParameter, ...]
    properties: tuple[DiscoveredProperty, ...] = ()
    omitted_variadic_arguments: bool = False


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
    discovered: list[tuple[str, str, tuple[DiscoveredParameter, ...], tuple[DiscoveredProperty, ...], bool]] = []
    seen_classes: set[tuple[str, str]] = set()
    for module_name in discover_modules(root_module_name):
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for _, candidate in inspect.getmembers(module, inspect.isclass):
            if candidate.__module__ != module.__name__:
                continue
            if candidate in base_classes:
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
            omitted_variadic_arguments=omitted_variadic_arguments,
        )
        for (module_name, class_name, parameters, properties, omitted_variadic_arguments), public_name in zip(
            ordered,
            public_names,
            strict=True,
        )
    ]


def generate_library_source(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
) -> str:
    package_name = root_module_name.split(".", 1)[0]
    class_name = _library_class_name(package_name)
    lines = [
        '"""Generated UI interface stubs for discovered widgets."""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any, ClassVar",
        "",
        "from frozendict import frozendict",
        "",
        "from pyrolyze.api import MISSING, MissingType, UIElement, call_native, pyrolyse, ui_interface",
        "from pyrolyze.backends.model import (",
        "    AccessorKind,",
        "    ChildPolicy,",
        "    PropMode,",
        "    TypeRef,",
        "    UiInterface,",
        "    UiInterfaceEntry,",
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
            "            methods=frozendict(),",
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


def write_generated_library(
    root_module_name: str,
    widgets: Sequence[DiscoveredWidgetClass],
    *,
    output_dir: Path,
    output_name: str | None = None,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    package_name = root_module_name.split(".", 1)[0]
    output_file = output_dir / (output_name or f"{package_name.lower()}.py")
    output_file.write_text(generate_library_source(root_module_name, widgets))
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
        return ("PySide6.QtWidgets:QWidget",)
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
        "    @pyrolyse",
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
    parameters = list(widget.parameters)
    known_names = {parameter.name for parameter in parameters}
    for prop in widget.properties:
        if not prop.writable or prop.name in known_names:
            continue
        parameters.append(
            DiscoveredParameter(
                name=prop.name,
                kind=inspect.Parameter.KEYWORD_ONLY,
                annotation_source=_signature_annotation_for_property(package_name, prop),
                default_source="MISSING",
                coerced_expression=prop.name,
            )
        )
        known_names.add(prop.name)
    return tuple(parameters)


def _signature_annotation_for_property(
    package_name: str,
    prop: DiscoveredProperty,
) -> str:
    if package_name == "PySide6":
        return f"{_qt_property_python_type(prop.type_name)} | MissingType"
    return "Any | MissingType"


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

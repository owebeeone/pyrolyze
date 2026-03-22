from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

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
from pyrolyze.compiler import emit_transformed_source
from pyrolyze.testing.hydo import HYDO_MOUNTABLE_SPECS


def generate_hydo_library_source() -> str:
    specs = [HYDO_MOUNTABLE_SPECS[kind] for kind in sorted(HYDO_MOUNTABLE_SPECS)]
    lines = [
        "#@pyrolyze",
        "",
        '"""Generated UI interface for the Hydo testing toolkit."""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Any, ClassVar",
        "",
        "from frozendict import frozendict",
        "",
        "from pyrolyze.api import MISSING, MissingType, UIElement, call_native, pyrolyze, ui_interface",
        "from pyrolyze.backends.model import (",
        "    AccessorKind,",
        "    ChildPolicy,",
        "    FillPolicy,",
        "    MethodMode,",
        "    MountParamSpec,",
        "    MountPointSpec,",
        "    PropMode,",
        "    TypeRef,",
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
        "class HydoUiLibrary:",
        '    ROOT_MODULE: ClassVar[str] = "pyrolyze.testing.hydo"',
        "",
        "    UI_INTERFACE: ClassVar[UiInterface] = UiInterface(",
        '        name="HydoUiLibrary",',
        "        owner=None,",
        "        entries=frozendict({",
    ]
    for spec in specs:
        public_name = f"C{spec.kind}"
        lines.append(
            f'            "{public_name}": UiInterfaceEntry(public_name="{public_name}", kind="{spec.kind}"),'
        )
    lines.extend(
        [
            "        }),",
            "    )",
            "",
            "    MOUNTABLE_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = frozendict({",
        ]
    )
    for spec in specs:
        lines.extend(_render_mountable_spec(spec))
    lines.extend(
        [
            "    })",
            "    WIDGET_SPECS: ClassVar[frozendict[str, UiWidgetSpec]] = MOUNTABLE_SPECS",
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
    for spec in specs:
        lines.extend(_render_component_method(spec))
    return "\n".join(lines) + "\n"


def write_generated_hydo_library(*, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "generated_hydo_library.py"
    source = generate_hydo_library_source()
    transformed = emit_transformed_source(
        source,
        module_name="pyrolyze.testing.generated_hydo_library",
        filename=str(output_file),
    )
    output_file.write_text(transformed)
    return output_file


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate the Hydo testing UI library.")
    parser.add_argument(
        "--output-dir",
        default="scratch",
        help="Directory for the generated_hydo_library.py output.",
    )
    args = parser.parse_args(argv)
    write_generated_hydo_library(output_dir=Path(args.output_dir))
    return 0


def _render_mountable_spec(spec: UiWidgetSpec) -> list[str]:
    lines = [
        f'        "{spec.kind}": UiWidgetSpec(',
        f'            kind="{spec.kind}",',
        f'            mounted_type_name="{spec.mounted_type_name}",',
        "            constructor_params=frozendict({",
    ]
    for param in spec.constructor_params.values():
        lines.append(
            "                "
            f'"{param.name}": UiParamSpec(name="{param.name}", annotation={_render_type_ref(param.annotation)}, '
            f"default_repr={param.default_repr!r}),"
        )
    lines.extend(
        [
            "            }),",
            "            props=frozendict({",
        ]
    )
    for prop in spec.props.values():
        lines.append(
            "                "
            f'"{prop.name}": UiPropSpec('
            f'name="{prop.name}", '
            f"annotation={_render_type_ref(prop.annotation)}, "
            f"mode=PropMode.{prop.mode.name}, "
            f"constructor_name={prop.constructor_name!r}, "
            f"setter_kind={_render_enum_member('AccessorKind', prop.setter_kind)}, "
            f"setter_name={prop.setter_name!r}, "
            f"getter_kind={_render_enum_member('AccessorKind', prop.getter_kind)}, "
            f"getter_name={prop.getter_name!r}, "
            f"affects_identity={prop.affects_identity!r}),"
        )
    lines.extend(
        [
            "            }),",
            "            methods=frozendict({",
        ]
    )
    for method in spec.methods.values():
        lines.append(f'                "{method.name}": UiMethodSpec(')
        lines.append(f'                    name="{method.name}",')
        lines.append(f"                    mode=MethodMode.{method.mode.name},")
        lines.append("                    params=(")
        for param in method.params:
            lines.append(
                "                        "
                f'UiParamSpec(name="{param.name}", annotation={_render_type_ref(param.annotation)}, '
                f"default_repr={param.default_repr!r}),"
            )
        lines.extend(
            [
                "                    ),",
                f"                    source_props={_render_string_tuple(method.source_props)},",
                f"                    fill_policy=FillPolicy.{method.fill_policy.name},",
                f"                    constructor_equivalent={method.constructor_equivalent!r},",
                "                ),",
            ]
        )
    lines.extend(
        [
            "            }),",
            f"            child_policy=ChildPolicy.{spec.child_policy.name},",
            "            mount_points=frozendict({",
        ]
    )
    for mount_point in spec.mount_points.values():
        lines.extend(_render_mount_point_spec(mount_point))
    lines.extend(
        [
            "            }),",
            "        ),",
        ]
    )
    return lines


def _render_mount_point_spec(mount_point: MountPointSpec) -> list[str]:
    lines = [
        f'                "{mount_point.name}": MountPointSpec(',
        f'                    name="{mount_point.name}",',
        f"                    accepted_produced_type={_render_type_ref(mount_point.accepted_produced_type)},",
        "                    params=(",
    ]
    for param in mount_point.params:
        lines.append(
            "                        "
            f'MountParamSpec(name="{param.name}", annotation={_render_type_ref(param.annotation)}, '
            f"keyed={param.keyed!r}, default_repr={param.default_repr!r}),"
        )
    lines.extend(
        [
            "                    ),",
            f"                    min_children={mount_point.min_children!r},",
            f"                    max_children={mount_point.max_children!r},",
            f"                    apply_method_name={mount_point.apply_method_name!r},",
            f"                    sync_method_name={mount_point.sync_method_name!r},",
            "                ),",
        ]
    )
    return lines


def _render_component_method(spec: UiWidgetSpec) -> list[str]:
    public_name = f"C{spec.kind}"
    required_params: list[str] = []
    optional_params: list[str] = []
    call_args: list[str] = []
    seen_names: set[str] = set()

    for param in spec.constructor_params.values():
        annotation_expr = _annotation_expr(param.annotation)
        if param.default_repr is None:
            required_params.append(f"        {param.name}: {annotation_expr},")
        else:
            optional_params.append(f"        {param.name}: {annotation_expr} = {param.default_repr},")
        call_args.append(f"            {param.name}={param.name},")
        seen_names.add(param.name)

    for prop in spec.props.values():
        if prop.mode is PropMode.READONLY or prop.name in seen_names:
            continue
        optional_params.append(
            f"        {prop.name}: {_annotation_expr(prop.annotation)} | MissingType = MISSING,"
        )
        call_args.append(f"            {prop.name}={prop.name},")
        seen_names.add(prop.name)

    lines = [
        "",
        "    @classmethod",
        "    @pyrolyze",
        f"    def {public_name}(",
        "        cls,",
    ]
    lines.extend(required_params)
    if optional_params:
        lines.append("        *,")
        lines.extend(optional_params)
    lines.extend(
        [
            "    ) -> None:",
            "        call_native(cls.__element)(",
            f'            kind="{spec.kind}",',
        ]
    )
    lines.extend(call_args)
    lines.extend(
        [
            "        )",
        ]
    )
    return lines


def _render_enum_member(enum_name: str, value: object | None) -> str:
    if value is None:
        return "None"
    return f"{enum_name}.{value.name}"


def _render_string_tuple(values: tuple[str, ...]) -> str:
    if not values:
        return "()"
    if len(values) == 1:
        return f"({values[0]!r},)"
    return f"({', '.join(repr(value) for value in values)})"


def _render_type_ref(type_ref: TypeRef | None) -> str:
    if type_ref is None:
        return "None"
    return f"TypeRef(expr={type_ref.expr!r})"


def _annotation_expr(type_ref: TypeRef | None) -> str:
    return type_ref.expr if type_ref is not None else "Any"


if __name__ == "__main__":
    raise SystemExit(main())

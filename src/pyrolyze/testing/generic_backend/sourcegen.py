"""Source generation for the generic testing backend."""

from __future__ import annotations

from typing import Iterable

from .specs import NodeGenSpec, ParamSpec


def build_source_module_text(node_specs: Iterable[NodeGenSpec]) -> str:
    sections = [
        "from __future__ import annotations",
        "",
        "from pyrolyze.api import UIElement, call_native, pyrolyze",
        "",
    ]
    for spec in node_specs:
        sections.append(_render_component_source(spec))
        sections.append("")
    sections.append(
        "__all__ = ["
        + ", ".join(repr(spec.name) for spec in node_specs)
        + "]"
    )
    sections.append("")
    return "\n".join(sections)


def _render_component_source(spec: NodeGenSpec) -> str:
    params = ", ".join(_render_param(param) for param in spec.constructor)
    props = "\n".join(
        f'            "{param.name}": {param.name},'
        for param in spec.constructor
    )
    if params:
        signature = params
    else:
        signature = ""
    return "\n".join(
        [
            "@pyrolyze",
            f"def {spec.name}({signature}) -> None:",
            "    call_native(UIElement)(",
            f'        kind="{spec.name}",',
            "        props={",
            props,
            "        },",
            "    )",
        ]
    )


def _render_param(param: ParamSpec) -> str:
    annotation = "object" if param.annotation is None else param.annotation.expr
    rendered = f"{param.name}: {annotation}"
    if param.default_repr is not None:
        rendered += f" = {param.default_repr}"
    return rendered


__all__ = ["build_source_module_text"]

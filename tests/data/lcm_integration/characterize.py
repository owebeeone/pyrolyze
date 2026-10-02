"""Record I0 runtime behavior, not the intended integration contract."""

from __future__ import annotations

import argparse
from collections.abc import Mapping
from dataclasses import fields, is_dataclass
import json
import os
from pathlib import Path
from typing import Any

from pyrolyze.api import UIElement, pyrolyze
from pyrolyze.backends.model import TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.runtime import RenderContext, dirtyof
from pyrolyze.runtime import context as selected_runtime
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro_ui,
)


def _json_value(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _json_value(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    raise TypeError(f"unsupported characterization value: {type(value).__qualname__}")


def _error(exc: Exception) -> dict[str, str]:
    return {"type": type(exc).__name__, "message": str(exc)}


def _ui(context: RenderContext) -> Any:
    return _json_value(run_pyro_ui(context.committed_ui()))


def _children(context: RenderContext, parent: object = None) -> list[dict[str, Any]]:
    result = []
    for slot_id in context.debug_children_of(parent):
        result.append(
            {
                "ui": _json_value(run_pyro_ui(context.debug_ui(slot_id))),
                "children": _children(context, slot_id),
            }
        )
    return result


def _observe(context: RenderContext, events: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "ui": _ui(context),
        "children": _children(context),
        "events": _json_value(events),
    }


def _backend() -> BuildPyroNodeBackend:
    backend = BuildPyroNodeBackend(
        (
            NodeGenSpec(
                name="node",
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
            ),
            NodeGenSpec(
                name="text",
                base_name="node",
                constructor=(
                    ParamSpec(name="name", annotation=TypeRef("str")),
                    ParamSpec(name="text", annotation=TypeRef("str")),
                ),
            ),
            NodeGenSpec(
                name="row",
                base_name="node",
                constructor=(ParamSpec(name="name", annotation=TypeRef("str")),),
                mounts=(
                    MountSpec(
                        name="child",
                        accepted_base="node",
                        interface=MountInterfaceKind.ORDERED,
                        default=True,
                    ),
                ),
            ),
        ),
        module_name="tests.lcm_integration.backend",
    )
    backend.source_namespace()
    return backend


def _program(
    backend: BuildPyroNodeBackend, events: list[tuple[str, str]]
) -> dict[str, Any]:
    return load_transformed_namespace(
        f"""
from pyrolyze.api import pyrolyze
from {backend.module_name} import row, text

@pyrolyze
def child(label):
    events.append(("child", label))
    text("leaf", label)

@pyrolyze
def failing_child(label, fail):
    text("nested", label)
    if fail:
        raise ValueError("nested failure")

@pyrolyze
def panel(label, fail):
    with row("root"):
        child(label)
        if fail:
            raise ValueError("parent failure after child")
""",
        module_name="tests.lcm_integration.authored",
        filename="tests/data/lcm_integration/authored.py",
        globals_dict={"pyrolyze": pyrolyze, "events": events},
    )


def _parent_failure(
    backend: BuildPyroNodeBackend,
    program: dict[str, Any],
    events: list[tuple[str, str]],
) -> dict[str, Any]:
    harness = backend.context(program["panel"], "old", False)
    harness.get()
    result = {"before": _observe(harness._render_context, events)}
    try:
        harness.run("new", True)
    except Exception as exc:
        result["error"] = _error(exc)
    result["after_failure"] = _observe(harness._render_context, events)
    try:
        harness.run("recovered", False)
    except Exception as exc:
        result["recovery_error"] = _error(exc)
    result["after_recovery"] = _observe(harness._render_context, events)
    return result


def _repeated_passes(
    backend: BuildPyroNodeBackend,
    program: dict[str, Any],
    events: list[tuple[str, str]],
) -> list[dict[str, Any]]:
    harness = backend.context(program["panel"], "first", False)
    harness.get()
    result = [_observe(harness._render_context, events)]
    for label in ("second", "second", "third"):
        harness.run(label, False)
        result.append(_observe(harness._render_context, events))
    return result


def _caught_failure(program: dict[str, Any]) -> dict[str, Any]:
    # The compiler does not lower authored try statements; catch at a runtime boundary.
    context = RenderContext()
    slot_id = selected_runtime.SlotId(
        selected_runtime.ModuleId("tests.lcm_integration.caught"), 1
    )
    caught: list[str] = []

    def render(label: str, fail: bool) -> None:
        with context.pass_scope():
            try:
                context.component_call(
                    slot_id,
                    program["failing_child"],
                    label,
                    fail,
                    dirty_state=dirtyof(label=True, fail=True),
                )
            except ValueError as exc:
                caught.append(str(exc))
            context.call_native(
                UIElement, kind="tail", props={"label": label}, children=()
            )

    context.mount(lambda: render("old", False))
    result = {"before": _observe(context, [])}
    try:
        context.mount(lambda: render("new", True))
    except Exception as exc:
        result["boundary_error"] = _error(exc)
    result["caught"] = caught
    result["after_caught_failure"] = _observe(context, [])
    try:
        context.mount(lambda: render("recovered", False))
    except Exception as exc:
        result["recovery_error"] = _error(exc)
    result["after_recovery"] = _observe(context, [])
    return result


def characterize() -> dict[str, Any]:
    backend = _backend()
    events: list[tuple[str, str]] = []
    program = _program(backend, events)
    result = {
        "selector": os.environ.get("PYROLYZE_CONTEXT_IMPL", "lcm"),
        "reported_implementation": selected_runtime.__PYROLYZE_CONTEXT_IMPLEMENTATION__,
        "render_context_module": RenderContext.__module__,
        "parent_failure": _parent_failure(backend, program, events),
    }
    events.clear()
    result["repeated_passes"] = _repeated_passes(backend, program, events)
    result["caught_nested_failure"] = _caught_failure(program)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, help="Write an explicitly requested I0 baseline."
    )
    options = parser.parse_args()
    source = json.dumps(characterize(), indent=2, sort_keys=True) + "\n"
    if options.output is None:
        print(source, end="")
    else:
        options.output.parent.mkdir(parents=True, exist_ok=True)
        options.output.write_text(source, encoding="utf-8")


if __name__ == "__main__":
    main()

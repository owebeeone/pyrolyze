from __future__ import annotations

from pyrolyze.api import pyrolyze
from pyrolyze.backends.model import TypeRef
from pyrolyze.compiler import load_transformed_namespace
from pyrolyze.testing.generic_backend import (
    BuildPyroNodeBackend,
    MountInterfaceKind,
    MountSpec,
    NodeGenSpec,
    ParamSpec,
    run_pyro,
)


def _harness_specs() -> tuple[NodeGenSpec, ...]:
    return (
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
    )


def test_harness_auto_increments_generation_and_allows_explicit_override() -> None:
    backend = BuildPyroNodeBackend(_harness_specs(), module_name="example.generic_backend.harness")
    backend.source_namespace()

    namespace = load_transformed_namespace(
        f"""
from pyrolyze.api import pyrolyze
from {backend.module_name} import row, text

@pyrolyze
def panel(label):
    with row("root"):
        text("leaf", label)
""",
        module_name="example.generic_backend.harness.panel",
        filename="/virtual/example/generic_backend/harness_panel.py",
        globals_dict={"pyrolyze": pyrolyze},
    )

    ctx = backend.context(namespace["panel"], "hello", initial_generation=10)

    first = run_pyro(ctx.get())
    assert ctx.generation == 10
    assert first.generation == 10

    second = run_pyro(ctx.run().get())
    assert ctx.generation == 11
    assert second.generation == 10

    third = run_pyro(ctx.run("world").get())
    assert ctx.generation == 12
    assert third.generation == 12

    fourth = run_pyro(ctx.run("again", generation=25).get())
    assert ctx.generation == 25
    assert fourth.generation == 25

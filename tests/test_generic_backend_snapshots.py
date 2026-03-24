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
    run_pyro_ui,
)


def _snapshot_specs() -> tuple[NodeGenSpec, ...]:
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


def test_snapshot_helpers_extract_ui_and_mounted_graph_from_harness_result() -> None:
    backend = BuildPyroNodeBackend(_snapshot_specs(), module_name="example.generic_backend.snapshots")
    backend.source_namespace()

    namespace = load_transformed_namespace(
        f"""
from pyrolyze.api import pyrolyze
from {backend.module_name} import row, text

@pyrolyze
def panel():
    with row("root"):
        text("leaf", "hello")
""",
        module_name="example.generic_backend.snapshots.panel",
        filename="/virtual/example/generic_backend/snapshots_panel.py",
        globals_dict={"pyrolyze": pyrolyze},
    )

    ctx = backend.context(namespace["panel"], initial_generation=3)
    result = ctx.get()

    ui_snapshot = run_pyro_ui(result)
    graph_snapshot = run_pyro(result)

    assert ui_snapshot.kind == "row"
    assert ui_snapshot.children[0].kind == "text"
    assert graph_snapshot.node_type == "row"
    assert graph_snapshot.generation == 3
    assert graph_snapshot.mounts["child"][0].entries[0].node.node_type == "text"

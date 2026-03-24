# Generic backend testing (`pyrolyze.testing.generic_backend`)

## Purpose

End-to-end tests for `mount(...)`, `advertise_mount(...)`, selector families,
rerenders, and mountable-engine behavior need **real** `@pyrolyze` compilation
and runtime—not a full PySide6 or tkinter stack.

`pyrolyze.testing.generic_backend` builds a **minimal generated UI library**
from declarative specs: Python source is synthesized, passed through
`load_transformed_namespace`, and executed with `RenderContext` via
`PyroNodeEngine` and `PyroRenderHarness`.

Use it when a scenario is clearer with a tiny custom mount graph than with a
large checked-in backend. `AGENTS.md` already points contributors here for
mount-advert and dynamic mount tests.

## Code map

| Area | Location |
|------|----------|
| Public exports | [`src/pyrolyze/testing/generic_backend/__init__.py`](../../src/pyrolyze/testing/generic_backend/__init__.py) |
| Spec model | [`specs.py`](../../src/pyrolyze/testing/generic_backend/specs.py) — `NodeGenSpec`, `MountSpec`, `ParamSpec`, `MountParam`, `MountInterfaceKind` |
| Source generation | [`sourcegen.py`](../../src/pyrolyze/testing/generic_backend/sourcegen.py) |
| Builder API | [`api.py`](../../src/pyrolyze/testing/generic_backend/api.py) — `BuildPyroNodeBackend` |
| Engine | [`engine.py`](../../src/pyrolyze/testing/generic_backend/engine.py) — `PyroNodeEngine` |
| Harness | [`harness.py`](../../src/pyrolyze/testing/generic_backend/harness.py) — `PyroRenderHarness`, `PyroRenderResult` |
| Snapshots | [`snapshots.py`](../../src/pyrolyze/testing/generic_backend/snapshots.py) — `run_pyro`, `run_pyro_ui`, `PyroUiElement`, … |
| Runtime types | [`runtime.py`](../../src/pyrolyze/testing/generic_backend/runtime.py) — includes `PyrolyzeMountCompatibilityError` |

## Spec model (short)

- **`NodeGenSpec`**: one generated component kind (`name`), optional
  `base_name` for inheritance, `constructor` params, and `mounts` accepted by
  instances of that kind.
- **`MountSpec`**: mount point name, accepted child kind or base
  (`accepted_kind` / `accepted_base`), `MountInterfaceKind` (`ORDERED`,
  `SINGLE`, `KEYED`), optional constructor-style `params`, `default` flag, and
  replay / sync options used by the engine.
- **`ParamSpec` / `MountParam`**: mirror backend `TypeRef` and mount-parameter
  shapes for generated signatures.

`validate_node_specs` runs when constructing `BuildPyroNodeBackend`.

## `BuildPyroNodeBackend`

Typical workflow:

1. Construct `BuildPyroNodeBackend(tuple_of_node_specs, module_name="…")`.
   Choose a unique `module_name` per test module to avoid `sys.modules`
   collisions.
2. Call **`source_namespace()`** once (lazily compiles generated source via
   `load_transformed_namespace`) so imports like `from <module_name> import row`
   resolve inside dynamically compiled test code.
3. Obtain **`pyro_func("name")`** for generated `@pyrolyze` component refs,
   **`pyro_class("name")`** for runtime classes, and
   **`selector_family("mount_name")`** for `MountSelector.named(...)` values to
   pass into `advertise_mount(...)` / tests.
4. Build **`engine()`** or **`context(component, *args, **kwargs)`** for
   `PyroRenderHarness`.

Other helpers:

- **`source_module_text()`**: inspect or assert on generated source.
- **`engine(strict_compatibility=...)`**: toggle stricter mount compatibility
  checks (`PyrolyzeMountCompatibilityError`).

## Render harness and snapshots

- **`PyroRenderHarness`**: wraps `RenderContext`, bumps generation on `run()`,
  and exposes **`get()`** → `PyroRenderResult` (`ui_roots`, `mounted_roots`).
- **`run_pyro(result)`**: snapshot the **mounted** mountable graph (harness,
  `PyroRenderResult`, or mounted roots) into plain `PyroNode`-shaped data for
  assertions.
- **`run_pyro_ui(result)`**: snapshot the **`UIElement`** tree (including mount
  directives and mount advertisements).

See `tests/test_generic_backend_harness.py` and
`tests/test_generic_backend_snapshots.py`.

## Worked pattern (from tests)

Define specs, load a panel that imports generated symbols, then assert on
`run_pyro` / `run_pyro_ui`:

```python
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

def _specs():
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

def test_flow():
    backend = BuildPyroNodeBackend(_specs(), module_name="example.generic_backend.demo")
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
        module_name="example.generic_backend.demo.panel",
        filename="/virtual/example/generic_backend/demo_panel.py",
        globals_dict={"pyrolyze": pyrolyze},
    )

    ctx = backend.context(namespace["panel"], "hello")
    graph = run_pyro(ctx.get())
    # assert on graph.mounts, generations, etc.
```

Mount-advert variants inject `advertise_mount`, `mount`, and
`backend.selector_family(...)` via `globals_dict` or imports; see
`tests/test_generic_backend_mount_advert_readable.py`.

## Test index (by topic)

- Specs / model: `tests/test_generic_backend_specs.py`,
  `tests/test_generic_backend_model.py`
- Source generation: `tests/test_generic_backend_sourcegen.py`,
  `tests/test_generic_backend_generation.py`
- Harness / runtime: `tests/test_generic_backend_harness.py`,
  `tests/test_generic_backend_runtime.py`
- Mount selector families / branching: `tests/test_generic_backend_mount_selector_families.py`,
  `tests/test_generic_backend_mount_branching.py`
- Adapter replay / compatibility: `tests/test_generic_backend_mount_adapter_replay.py`,
  `tests/test_generic_backend_mount_compatibility.py`
- Mount adverts: `tests/test_generic_backend_mount_advert_*.py`
- API surface of the builder: `tests/test_generic_backend_api.py`

## User-facing docs

Author documentation for `mount(...)` and `advertise_mount(...)` lives in
[`docs/user/Mount_And_Mount_Points.md`](../user/Mount_And_Mount_Points.md). This
contributor page is only for the test harness.

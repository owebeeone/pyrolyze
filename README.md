# PyRolyze

PyRolyze is a compile-time reactive Python package.

It lets you write declarative Python functions, compile them into explicit
reactive runtime code, and reconcile committed UI into native backends without
hand-writing the update machinery yourself.

The project is built around a simple idea:

- author straightforward Python
- compile it into inspectable transformed code
- rerun only the boundaries that became dirty
- keep the runtime model explicit and testable

That makes PyRolyze useful both as an application framework and as a platform
for experimenting with reactive Python compilation, backend adapters, and
versioned AST support.

## Why It Is Interesting

PyRolyze is trying to make reactive Python feel direct rather than ceremonial.

Instead of forcing authors to manually thread state updates through an
imperative widget tree, PyRolyze lets authors describe components, helpers,
containers, loops, hooks, and native UI emission in source form, then lowers
that source into a context-graph runtime with explicit slot ownership and
committed UI.

The result is a package that aims to stay:

- author-friendly at the source level
- explicit at the runtime level
- inspectable at the compiler level
- practical to test across Python versions

## What Works Today

Implemented in the current package:

- source opt-in with `#@pyrolyze`
- component lowering with `@pyrolyse`
- slotted helper lowering with `@pyrolyze_slotted`
- versioned AST compiler kernels
- helper-source emission and checked-in golden tests
- runtime context graph with:
  - plain-call slots
  - container slots
  - keyed loop slots
  - component-call slots
  - effect and external-store bindings
  - invalidation scheduling
  - committed UI tracking
- backend adapters for:
  - PySide6
  - Tkinter
- graph capture and diff tooling for integrated tests
- versioned Python test runs through a uv-based harness

Current packaged example:

- [`examples/grid_app.py`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/examples/grid_app.py)

## Start Here

Package-local documentation:

- [`docs/README.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/README.md)

Recommended reading order:

1. [`docs/overview/What_Is_PyRolyze.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/overview/What_Is_PyRolyze.md)
2. [`docs/overview/System_Map.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/overview/System_Map.md)
3. [`docs/user/Authoring_Overview.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/user/Authoring_Overview.md)
4. [`docs/design/Architecture.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/design/Architecture.md)
5. [`docs/contributor/Versioned_Test_Runs.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/contributor/Versioned_Test_Runs.md)

The nested docs tree is split into:

- `overview/` for orientation and motivation
- `design/` for implementation details
- `user/` for authoring guidance
- `contributor/` for maintainer workflows
- `reference/` for quick lookup

There is also parent-repo design material in
[`../docs/`](/Users/owebeeone/limbo/py-rolyze-dev2/docs/README.md), but the
package-local docs above are the best starting point for the current
implementation.

## Quick Example

```python
#@pyrolyze
from pyrolyze.api import UIElement, call_native, pyrolyse, use_state


@pyrolyse
def counter() -> None:
    count, set_count = use_state(0)
    call_native(UIElement)(
        kind="button",
        props={
            "label": f"Count: {count}",
            "enabled": True,
            "tone": "default",
            "visible": True,
            "on_press": lambda: set_count(lambda current: current + 1),
        },
    )
```

The source stays small. The compiler lowers it into explicit runtime calls, and
the runtime decides what reruns and what committed UI changes.

## Local Development

Install the package in editable mode:

```bash
uv pip install -e .
```

Run the full suite:

```bash
uv run --with pytest --with pytest-cov pytest -q
```

Run a focused test:

```bash
uv run --with pytest --with pytest-cov pytest tests/test_examples_grid_app.py -q
```

## Versioned AST Testing

AST transforms are more version-sensitive than most Python APIs because parser
and AST node details shift across interpreter releases. PyRolyze keeps the
compiler split into versioned kernels and provides a uv-based harness for
running the suite across Python versions.

Detailed workflow:

- [`tests/README.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/tests/README.md)
- [`docs/contributor/Versioned_Test_Runs.md`](/Users/owebeeone/limbo/py-rolyze-dev2/py-rolyze/docs/contributor/Versioned_Test_Runs.md)

Quick commands:

```bash
uv run python tests/versioned_test_harness.py list-versions
uv run python tests/versioned_test_harness.py regen-goldens
uv run python tests/versioned_test_harness.py run-tests --python 3.14 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests-all --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests-all --show-output --pytest-args -q
```

Current state:

- minimum supported runtime is Python `3.12`
- only kernel `v3_14` is checked in today
- Python `3.12`, `3.13`, `3.14`, and `3.15.0a5` have all been verified against
  that same `v3_14` kernel

## Current Boundaries

PyRolyze is already useful, but it is still a focused package rather than a
finished everything-framework.

Important current boundaries:

- the source contract is intentionally explicit
- the reconciler ships with a narrow frozen v1 UI node model
- versioned AST support is designed for change, not assumed away
- some higher-level compiler features are still being expanded

That is deliberate. The package prefers inspectable mechanics, strong tests, and
clear maintenance boundaries over pretending the hard parts are solved by magic.

# PyRolyze

PyRolyze is a compile-time reactive Python framework.

Write declarative Python components, compile them into inspectable runtime code,
and reconcile committed UI into native backends without hand-written update
machinery.

> [!WARNING]
> Pre-release status: this repository is active and usable, but the package
> version is currently `0.0.0` and APIs may change.

## Why PyRolyze

- Declarative source authoring with explicit opt-in (`#@pyrolyze`, `@pyrolyze`)
- Compiler output that is inspectable and testable
- Runtime model based on explicit context-graph ownership and invalidation
- Version-aware AST kernel strategy for Python interpreter changes

## Quick Start

### Prerequisites

- Python `3.12+`
- [uv](https://docs.astral.sh/uv/)

### Install

```bash
git clone https://github.com/owebeeone/py-rolyze-wip.git
cd py-rolyze-wip   # use your actual checkout directory name if different
uv pip install -e .
```

Optional DearPyGui support (for `--backend dearpygui` and DPG-focused tests):

```bash
uv pip install -e ".[dpg]"
```

### Run the Example App

```bash
uv run python examples/run_grid_app.py
```

Optional backends:

```bash
uv run python examples/run_grid_app.py --backend tkinter
uv run python examples/run_grid_app.py --backend dearpygui
```

(`dearpygui` requires the `dpg` extra, as in the install section above.)

### Run Tests

```bash
uv run --with pytest --with pytest-cov pytest -q
```

Focused example test:

```bash
uv run --with pytest --with pytest-cov pytest tests/test_examples_grid_app.py -q
```

## Minimal Example

```python
#@pyrolyze
from pyrolyze.api import UIElement, call_native, pyrolyze, use_state


@pyrolyze
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

The compiler lowers this source into explicit runtime calls, and the runtime
decides what reruns and what committed UI changes.

## What Works Today

- Source opt-in with `#@pyrolyze`
- Component lowering with `@pyrolyze`
- Slotted helper lowering with `@pyrolyze_slotted`
- Versioned AST compiler kernels
- Helper-source emission and checked-in golden tests
- Runtime context graph with:
  - plain-call slots
  - container slots
  - keyed loop slots
  - component-call slots
  - effect and external-store bindings
  - invalidation scheduling
  - committed UI tracking
- Backend adapters for PySide6, Tkinter, and DearPyGui (optional `dpg` extra)
- Graph capture and diff tooling for integrated tests
- Versioned Python test runs through a uv-based harness

Packaged example:

- [`examples/grid_app.py`](examples/grid_app.py)

## Documentation

Primary docs index:

- [`docs/README.md`](docs/README.md)

Suggested reading order:

1. [`docs/overview/What_Is_PyRolyze.md`](docs/overview/What_Is_PyRolyze.md)
2. [`docs/overview/System_Map.md`](docs/overview/System_Map.md)
3. [`docs/user/Authoring_Overview.md`](docs/user/Authoring_Overview.md)
4. [`docs/design/Architecture.md`](docs/design/Architecture.md)
5. [`docs/contributor/Versioned_Test_Runs.md`](docs/contributor/Versioned_Test_Runs.md)

## Maintainer and Contributor Workflow

Contributor entry point:

- [`docs/contributor/README.md`](docs/contributor/README.md)

Versioned AST testing workflow:

- [`tests/README.md`](tests/README.md)
- [`docs/contributor/Versioned_Test_Runs.md`](docs/contributor/Versioned_Test_Runs.md)

Quick commands:

```bash
uv run python tests/versioned_test_harness.py list-versions
uv run python tests/versioned_test_harness.py regen-goldens
uv run python tests/versioned_test_harness.py run-tests --python 3.14 --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests-all --pytest-args -q
uv run python tests/versioned_test_harness.py run-tests-all --show-output --pytest-args -q
```

Current state:

- Minimum supported runtime is Python `3.12`
- Only kernel `v3_14` is checked in today
- Python `3.12`, `3.13`, `3.14`, and `3.15.0a5` have all been verified against
  that same `v3_14` kernel

## Current Scope

PyRolyze is intentionally focused.

- The source contract is explicit and opt-in
- The reconciler ships with a narrow v1 UI node model
- Versioned AST support is treated as an explicit maintenance concern
- Higher-level compiler features are still expanding

The project prioritizes inspectable mechanics, strong testing, and clear
maintenance boundaries.

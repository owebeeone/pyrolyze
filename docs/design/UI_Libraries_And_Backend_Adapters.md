# UI Libraries And Backend Adapters

## Purpose

Describe how backend adapters consume committed UI and turn it into native
widgets.

## Current implementation

The package currently ships two backend adapters:

- `src/pyrolyze/pyrolyze_pyside6.py`
- `src/pyrolyze/pyrolyze_tkinter.py`

Both adapters:

- define a backend-specific window/container host
- implement `UiBackendAdapter`
- create bindings for normalized UI node specs
- dispatch widget events back into authored callbacks
- support owner-scoped reconciliation

The example app host in `examples/run_grid_app.py` mounts a transformed root,
then reconciles `ctx.committed_ui()` into the chosen backend after initial
render and after flushed invalidations.

## Code map

- PySide6 backend
  - `src/pyrolyze/pyrolyze_pyside6.py`
- Tkinter backend
  - `src/pyrolyze/pyrolyze_tkinter.py`
- shared reconciliation model
  - `src/pyrolyze/runtime/ui_nodes.py`
- example host
  - `examples/run_grid_app.py`

## Primary tests

- `tests/test_pyside6_wrapper.py`
- `tests/test_tkinter_wrapper.py`
- `tests/test_examples_grid_app.py`
- `tests/test_ui_node_bindings.py`
- `tests/test_ui_reconciliation.py`

## Known limitations

- shipped backends target the frozen v1 UI node model
- backend coverage is intentionally narrow
- custom UI libraries require explicit registry and binding work

## Future proposals

- more backend adapters
- more ergonomic backend authoring helpers
- richer backend diagnostics for reconciliation failures

# UI Libraries And Backend Adapters

## Purpose

Describe how backend adapters consume committed UI and turn it into native
widgets.

For the concrete `UiInterface` schema and the current interface families, see
[UI_Interface_Schema.md](UI_Interface_Schema.md).

## Current implementation

The package ships three native backend adapters:

- `src/pyrolyze/pyrolyze_pyside6.py`
- `src/pyrolyze/pyrolyze_tkinter.py`
- `src/pyrolyze/pyrolyze_dearpygui.py` (requires the optional `dearpygui`
  dependency; install with e.g. `uv pip install -e ".[dpg]"`)

Each adapter:

- defines a backend-specific window/container host
- implements `UiBackendAdapter`
- creates bindings for normalized UI node specs
- dispatches widget events back into authored callbacks
- supports owner-scoped reconciliation

The example app host in `examples/run_grid_app.py` mounts a transformed root,
then reconciles `ctx.committed_ui()` into the chosen backend (`--backend
pyside6`, `tkinter`, or `dearpygui`) after initial render and after flushed
invalidations.

## Code map

- PySide6 backend
  - `src/pyrolyze/pyrolyze_pyside6.py`
- Tkinter backend
  - `src/pyrolyze/pyrolyze_tkinter.py`
- DearPyGui backend
  - `src/pyrolyze/pyrolyze_dearpygui.py`
  - generated mount catalog: `src/pyrolyze/backends/dearpygui/generated_library.py`
- shared reconciliation model
  - `src/pyrolyze/runtime/ui_nodes.py`
- example host
  - `examples/run_grid_app.py`

## Primary tests

- `tests/test_pyside6_wrapper.py`
- `tests/test_tkinter_wrapper.py`
- `tests/test_pyrolyze_native_dearpygui.py`
- `tests/test_examples_grid_app.py`
- `tests/test_ui_node_bindings.py`
- `tests/test_ui_reconciliation.py`

## Known limitations

- shipped backends target the frozen v1 UI node model
- backend coverage is intentionally narrow
- custom UI libraries require explicit registry and binding work

## Future proposals

- more first-party backend adapters
- more ergonomic backend authoring helpers
- richer backend diagnostics for reconciliation failures

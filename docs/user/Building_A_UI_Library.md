# Building A UI Library

To support a new UI library, you need two things:

1. a stable `UIElement` vocabulary
2. backend bindings that reconcile normalized specs into native widgets

## Current architecture

The shared reconciler lives in:

- `src/pyrolyze/runtime/ui_nodes.py`

Current backend examples:

- `src/pyrolyze/pyrolyze_pyside6.py`
- `src/pyrolyze/pyrolyze_tkinter.py`

## Minimum pieces

- define or reuse UI kinds in a `UiNodeDescriptorRegistry`
- normalize authored `UIElement` values into `UiNodeSpec`
- implement `UiBackendAdapter`
- implement per-kind bindings that:
  - create native widgets
  - update props
  - place children
  - detach children
  - dispose resources

## Testing a UI library

At minimum:

- binding tests
- reconciliation tests
- one example-host test

Current examples:

- `tests/test_ui_node_bindings.py`
- `tests/test_ui_reconciliation.py`
- `tests/test_examples_grid_app.py`

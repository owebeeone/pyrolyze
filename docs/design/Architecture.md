# Architecture

## Purpose

Describe the current package architecture and the boundaries between source API,
compiler, runtime, backend adapters, and tests.

## Current implementation

The package is split into five layers:

- author-facing source API
  - `src/pyrolyze/api.py`
  - `src/pyrolyze/hooks.py`
- compiler
  - `src/pyrolyze/compiler/`
- runtime
  - `src/pyrolyze/runtime/`
  - `src/pyrolyze/visitor.py`
- backend adapters
  - `src/pyrolyze/pyrolyze_pyside6.py`
  - `src/pyrolyze/pyrolyze_tkinter.py`
- verification
  - `examples/`
  - `tests/`

The author writes source using `#@pyrolyze`, `@pyrolyze`, and related
annotations. The compiler lowers that source into generated helper functions and
runtime calls. The runtime manages slot ownership, invalidation, and committed
UI. Backend adapters reconcile committed UI into native widgets.

## Code map

- Source contract
  - `src/pyrolyze/api.py`
  - `src/pyrolyze/hooks.py`
- Compiler facade
  - `src/pyrolyze/compiler/facade.py`
  - `src/pyrolyze/compiler/kernel_loader.py`
- Runtime core
  - `src/pyrolyze/runtime/context.py`
  - `src/pyrolyze/runtime/app_context.py`
  - `src/pyrolyze/runtime/ui_nodes.py`
  - `src/pyrolyze/runtime/trace.py`
- Graph capture
  - `src/pyrolyze/visitor.py`
- Examples
  - `examples/grid_app.py`
  - `examples/run_grid_app.py`

## Primary tests

- `tests/test_ast_*`
- `tests/test_context_graph_*`
- `tests/test_ui_node_bindings.py`
- `tests/test_ui_reconciliation.py`
- `tests/test_examples_grid_app.py`
- `tests/test_visitor_context_graph*.py`

## Known limitations

- Only one AST kernel is checked in today: `v3_14`.
- The runtime and source contract are ahead of some author-facing compiler
  features.
- Backend support is narrow and centered on the frozen v1 UI node model.

## Future proposals

- more backend adapters
- additional AST kernels when version-specific behavior diverges
- broader source-level diagnostics and richer emitted debug artifacts

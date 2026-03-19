# Reconciler And UI Node Model

## Purpose

Explain the frozen v1 UI node model, normalization, identity rules, and owner
reconciliation.

## Current implementation

The reconciler lives in `src/pyrolyze/runtime/ui_nodes.py`.

Current flow:

1. authored code emits `UIElement`
2. committed UI is normalized into `UiNodeSpec`
3. the backend reconciles an owner region
4. nodes are reused, updated, replaced, or removed by `UiNodeId`

Important structures:

- `UiNodeDescriptorRegistry`
- `FROZEN_V1_REGISTRY`
- `UiNodeSpec`
- `UiNodeId`
- `UiOwnerCommitState`
- `reconcile_owner(...)`

The frozen v1 registry currently defines:

- `section`
- `row`
- `badge`
- `button`
- `text_field`
- `toggle`
- `select_field`

## Code map

- descriptors, normalization, reconciliation
  - `src/pyrolyze/runtime/ui_nodes.py`
- backend binding implementations
  - `src/pyrolyze/pyrolyze_pyside6.py`
  - `src/pyrolyze/pyrolyze_tkinter.py`

## Primary tests

- `tests/test_ui_node_bindings.py`
- `tests/test_ui_reconciliation.py`
- `tests/test_context_graph_phase7_native_ui.py`

## Known limitations

- the shipped registry is intentionally small
- custom UIElement kinds are not automatic; they require descriptor and backend work

## Future proposals

- more registry kinds
- backend-independent helpers for custom kinds
- richer identity and diff policies where needed

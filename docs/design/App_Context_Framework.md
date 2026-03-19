# App Context Framework

## Purpose

Explain app-scoped values and generation tracking.

## Current implementation

The app-context framework lives in `src/pyrolyze/runtime/app_context.py`.

It provides:

- `AppContextKey[T]`
  - identity-based key
  - `factory`
  - optional `close`
- `AppContextStore`
  - lazy initialization
  - reverse-order closing
- `GenerationTracker`
  - begin/commit/rollback generation ids

`RenderContext` owns one shared app-context store per scheduler root. Runtime
contexts and plain-call runtime contexts can read from that store through:

- `get_app_context(...)`
- `has_app_context(...)`
- `current_generation_id()`

This keeps generation tracking optional and app-scoped rather than making it a
hardwired global requirement.

## Code map

- app-context definitions
  - `src/pyrolyze/runtime/app_context.py`
- runtime integration
  - `src/pyrolyze/runtime/context.py`

## Primary tests

- `tests/test_app_context_framework.py`
- `tests/test_visitor_context_graph.py`
- `tests/test_visitor_context_graph_integrated.py`

## Known limitations

- no nested app-context override model
- app-context close semantics are simple and root-scoped

## Future proposals

- nested context layering if a real need appears
- broader library-facing helpers around app-scoped values

# Tracing And Debugging

## Purpose

Explain the current tracing and graph-debugging tools.

## Current implementation

Runtime tracing lives in:

- `src/pyrolyze/runtime/trace.py`

Current trace channels:

- `invalidation`
- `flush`
- `boundary`
- `reconcile`

Tracing can be enabled through:

- runtime API
  - `configure_trace(...)`
  - `enable_trace(...)`
- environment
  - `PYROLYZE_TRACE`

Committed graph capture and diff live in:

- `src/pyrolyze/visitor.py`

That tooling is useful when a transform is correct but a rerender or backend
update still behaves unexpectedly.

## Code map

- trace primitives
  - `src/pyrolyze/runtime/trace.py`
- graph capture
  - `src/pyrolyze/visitor.py`
- runtime integration
  - `src/pyrolyze/runtime/context.py`

## Primary tests

- `tests/test_runtime_trace.py`
- `tests/test_visitor_context_graph.py`
- `tests/test_visitor_context_graph_integrated.py`

## Known limitations

- trace output is event-oriented, not a full time-travel debugger
- some lifecycle cases still need richer capture

## Future proposals

- richer trace sinks
- better correlation between graph diffs and trace events

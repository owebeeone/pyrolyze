# Integrated Test Environment

## Purpose

Explain the committed context-graph capture tools and the current integrated
source-backed graph tests.

## Current implementation

The integrated graph tooling is split between:

- runtime capture support in `src/pyrolyze/runtime/context.py`
- visitor helpers in `src/pyrolyze/visitor.py`

Current capabilities:

- capture a detached committed context graph
- include generation ids
- include UI records with:
  - `slot_id`
  - `render_owner_slot_id`
  - `generation_id`
- diff two captured graphs
- run source-backed integration tests from files under `tests/data/`

This is used to validate:

- rerender isolation
- keyed-loop stability
- committed UI changes
- graph changes across state updates

## Code map

- graph capture and diff
  - `src/pyrolyze/visitor.py`
- runtime graph walk integration
  - `src/pyrolyze/runtime/context.py`
- integrated source-backed tests
  - `tests/test_visitor_context_graph.py`
  - `tests/test_visitor_context_graph_integrated.py`
  - `tests/data/`

## Primary tests

- `tests/test_visitor_context_graph.py`
- `tests/test_visitor_context_graph_integrated.py`

## Known limitations

- lifecycle tracing for async effects is still narrower than synchronous graph capture
- some richer effect/grip scenarios are still being expanded

## Future proposals

- more integrated source-backed scenarios
- more focused diff filters
- broader effect and async lifecycle capture

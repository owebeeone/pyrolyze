# Event Management And Scheduler

## Purpose

Explain how events, invalidations, reruns, and post-flush work in the current
runtime.

## Current implementation

The event and rerun path is runtime-driven.

Key pieces:

- `EventHandlerSlotContext`
  - stages callbacks
  - commits them after a successful pass
  - exposes a stable dispatch function
- `_InvalidationScheduler`
  - tracks queued, deferred, and active boundaries
- `RenderContext.run_pending_invalidations()`
  - drains queued invalidations
- post-commit callbacks
  - used by effect bindings after committed passes

UI backend bindings call the authored event callback and then trigger the
backend-specific "after event" hook. Example hosts can use that to drain
invalidations and reconcile native widgets.

## Code map

- scheduler and handler state
  - `src/pyrolyze/runtime/context.py`
- trace support for invalidation, boundary, flush, and reconcile
  - `src/pyrolyze/runtime/trace.py`
- backend event dispatch
  - `src/pyrolyze/pyrolyze_pyside6.py`
  - `src/pyrolyze/pyrolyze_tkinter.py`
- example host wiring
  - `examples/run_grid_app.py`

## Primary tests

- `tests/test_context_graph_phase5a_invalidation_kernel.py`
- `tests/test_context_graph_phase8_scheduler.py`
- `tests/test_examples_grid_app.py`
- `tests/test_pyside6_wrapper.py`
- `tests/test_tkinter_wrapper.py`

## Known limitations

- source-level event boundary lowering is narrower than the runtime event model
- most user-facing event flows currently appear through backend event props

## Future proposals

- broader compiler support for explicit event-boundary lowering
- richer trace and lifecycle inspection for event commits and deactivations

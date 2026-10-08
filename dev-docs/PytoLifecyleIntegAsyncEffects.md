# Async Effect Completion Checkpoint

Status: implemented behind a separate private proof gate. Normal rendering,
shared legacy handlers, and mount admission are unchanged. Verification results
are recorded below; this is not default-runtime activation.

## Contract

- Preserve `UseEffectAsyncRequest(start, deps, cleanup)` and `AsyncEffectHandle`.
  This API accepts a callback-driven operation, not an asyncio coroutine.
  Preserve existing duck-typed cancellable handles; do not require nominal
  inheritance from the abstract handle class at runtime.
- The immutable managed invocation selects the request. The existing private
  owned wrapper controls its explicitly counted resource. No second manager or
  parallel committed/staged request stores are introduced.
- New requests remain inert until proven full outer publication. Failed renders
  discard pending requests without starting or cancelling the accepted operation.
- Non-None equal dependencies reuse an already-started resource, even after it
  completes. None reruns; an empty tuple runs once while selected. Pending requests
  always select the latest callback, rather than reusing an inert predecessor.
- Completion uses the existing scheduler invalidation path. The callback holds
  only a weak resource reference; the resource holds a weak host reference, so
  retaining an external callback cannot retain the render graph.
- Replacement/removal fences completion callbacks before cancellation and cleanup.
  Retaining a value snapshot does not retain operation ownership. Rollback keeps
  the accepted operation and its completion callback active.

## Delivery And Failures

The synchronous-effect completion loop now selects a delivery resource through
a small protocol. Async admission specializes binding, resource ownership, and
that selection only; publication evidence, retirement, independent delivery,
and reentry fencing stay shared.

Async completion is allowed during `start`. Its returned handle must not
resurrect an already-finished operation. A failed start fences any escaped
completion callback. Startup cannot recover an undisclosed handle from a raising
user function; that function remains responsible for its partial external work.

Cancellation errors do not suppress the request's cleanup or other independent
actions. Retain each original ordinary/system exception, preserve a lone error,
and group independent failures. As with synchronous effects, a failed old
teardown blocks that slot's replacement startup, but not other slots. A failure
after publication never claims that published fields were undone; reuse is
quarantined. Unpublished requests do not run their cleanup callback because
their operation never started.

The shared legacy handler remains unchanged. Its synchronous-completion handle
assignment and cancel-error short-circuit are not copied into the new route:
the new route preserves the intended completed-handle and resilient cleanup
contracts without changing the public request/handle API.

## Evidence

Canonical fixture:
`tests/data/lcm_integration/async_effect_selection_lifecycle.py`, with authored
expected events in `tests/data/lcm_integration/baselines/`.

It pins provisional local success, stable dependencies, failed replacement and
removal, completion invalidation, stale and cancellation-time callbacks, retained
snapshots, superseded requests, None/empty dependencies, and removal cleanup.
The mounted-render trace also flushes actual scheduler work after completion and
proves unchanged dependencies do not restart the operation on that rerender.

Narrow fault coverage:
`tests/test_runtime_context_state_lcm_async_effects.py` covers start errors and
escaped callbacks, independent delivery, cancel plus cleanup errors, synchronous
completion, graph collection, startup reentry, and replacement transaction fencing.

Run from the repository root, selecting either assembly backend:

```sh
env PYTHONDONTWRITEBYTECODE=1 ASTICHI_LOWER_ENGINE=native \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/test_runtime_context_state_lcm_async_effects.py \
  tests/test_lcm_integration_characterization.py::test_async_effect_selection_lifecycle_golden
```

## Remaining Gates

Mount bindings and other invocation paths still require their own migration.
Normal-route activation and deletion of compatibility holders remain later work.
No lifecycle-library or compiler change is required for this checkpoint.

## Verification

- New async canonical trace plus resource fault tests and existing affected
  subscription/synchronous-effect goldens on Python assembly: **27 passed**.
- Full native default suite: **1007 passed, 2 known placement failures,
  20 skipped**. The failures are the deliberately faulted generic nested-row
  ordering case and the existing PySide6 mixed-widget/layout placement case.
- After adding actual scheduler flushing to the canonical trace, that extended
  trace passes on both assembly backends. Existing goldens remain unchanged.
- Shared legacy handlers, normal routing, and the lifecycle/compiler libraries
  are unchanged. No separate review agent or release has been initiated.

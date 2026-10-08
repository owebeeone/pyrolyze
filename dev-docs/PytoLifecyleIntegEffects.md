# Synchronous Effect Completion Checkpoint

Status: implemented and tested. Separate review is deferred to the larger
integration review, as directed by the operator. This is
not independent acceptance or default-runtime activation.

## Compatibility Boundary

Continue the subscription proof with a separate synchronous-effect gate. The
existing effect API, shared handlers, legacy routes, async effects, mounts, and
runtime selector stay unchanged. Preserve setup/cleanup and dependency behavior:
stable non-None dependency tuples reuse the active effect; None reruns on each
new request; an empty tuple runs once while the slot remains selected. Keep
Python dependency equality rather than adopting React identity comparison.

The already approved completion change is intentional: successful local/nested
passes remain provisional until the shared outer render publishes. A caught
entered-child failure poisons that render, so no provisional effect can start.

## State And Ownership

- The managed invocation stores one immutable selected effect request/binding.
  No parallel committed/staged request stores or legacy binding mutations.
- One private `owned` binding-owner field holds the existing hybrid wrapper.
  Subscription and effect resources share that small ownership bridge; snapshots
  hold the explicit resource, not the Python-lifetime owning wrapper.
- A new effect resource is inert until post-publication delivery. Rollback or
  superseding an unpublished request releases it without executing setup.
- Equal dependencies reuse only an already-started effect. Multiple unpublished
  requests select the latest callback, including when their dependencies match;
  an earlier inert resource must not deliver the superseded callback.
- An active effect's cleanup belongs to its resource. Replacement/removal drops
  ownership; a retained snapshot cannot postpone cleanup. Explicit resource
  counts prevent double cleanup and support genuine independent ownership.
- Dependency equality runs during evaluation with the original render-owner
  fence before candidate writes. It cannot target a replacement transaction.

## Completion And Failure

1. Evaluate and stage the selected request plus its private resource owner.
   Local success does not deliver effects. Omitted/explicit removal stages empty
   selection using the resource checkpoint's existing retirement path.
2. Lifecycle applies/discards fields. Accepted replacement/removal releases the
   previous owner; rollback preserves it. Resource cleanup errors are collected,
   not thrown from field application or falsely treated as undo of publication.
3. Consume coherent actual publication evidence and finalize generation through
   the existing completion owner. Deliver only the current selected, not-yet-
   started effects after proven publication. Unknown/partial publication cannot
   authorize setup.
4. Drain independent effect actions with render completion closed to reentry.
   Preserve a lone original error; group independent ordinary/system failures.
   Do not start a replacement whose own prior cleanup failed, matching the
   legacy per-effect sequence, but continue other independent effects.
5. Setup/delivery failures after publication preserve published fields and
   quarantine reuse. An effect that raises before returning its cleanup handle
   must unwind its own partial external work; no caller can recover an
   undisclosed handle. There is no invented rollback of performed side effects.

## Verification And Deferred Review

The authored canonical fixture pins successful local exit before outer setup,
stable dependencies, failed replacement/removal, retained snapshots, superseded
requests with different and equal dependencies, None/empty dependencies, and
explicit/omitted cleanup events. Keep
historical snapshots and the legacy effect tests unchanged.

Narrow fault tests cover dependency-equality token replacement, caught child
failure, invalid cleanup results, setup/cleanup exceptions, independent delivery,
completion reentry, and continued rejection of async requests before start.

Run the expanded native integration and legacy resource compatibility, affected
Python assembly, and full regression. Include synchronous effects together with
subscription ownership in the aggregate review before normal-route activation;
record results without claiming a separate review verdict.

## Verification

- Expanded native integration and existing resource compatibility: **234 passed**.
- After extending the golden with equal-dependency pending requests, the effect
  golden and narrow fault tests: **8 passed**.
- Subscription, effect, slot-call, and characterization tests on Python
  assembly, including the extended golden: **49 passed**.
- Full default native regression after the separate graph accessor correction:
  **1000 passed, 2 recorded host sibling-order failures, 20 skipped, 1 warning**.
  The remaining failures are
  `tests/test_generic_backend_host_surface_runtime.py::test_buggy_reconcile_mode_keeps_retained_nested_row_above_trailing_sibling`
  and
  `tests/test_pyside6_native_host.py::test_native_pyside6_conditional_nested_layout_toggle_keeps_row_above_trailing_label`.
- No lifecycle/compiler library, shared legacy handler, runtime-selector, or
  historical snapshot changes. The graph accessor correction in the monolithic
  reference is a separate compatibility fix, not resource activation.
- No separate reviewer was dispatched. Aggregate integration review remains
  required before normal-route activation.

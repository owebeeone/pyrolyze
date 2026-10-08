# Override Publication Checkpoint

Status: implemented behind `_enable_override_render`, extending the component
proof. Normal rendering and earlier proof gates remain unchanged. Aggregate
implementation review remains deferred.

## Authoritative State

The override state manager is lifecycle-decorated. One immutable managed record
holds fixed keys and selected values under `PASS_TX_KEY`. Failed staging marks
the original render attempt failed even if the caller catches the structure
error. Fixed-key/arity/type validation remains domain code.

Lexical lookup reads candidates while its scope is active; outside that scope it
reads the accepted record. Stable Drips preserve reference/subscription identity.
A reference read inside an active lexical scope can see the candidate, just as
lexical `get_authored_app_context()` does; this does not emit notifications.
Rollback does not restore Drip snapshots or overwrite independent parent events.
Legacy pending/current stores remain compatibility-only until normal adoption.

## Completion Timeline

1. Existing graph/mount validation and original-token fences run before capture.
2. Lifecycle publishes/discards fields under the shared outer decision.
3. Generation becomes accepted and graph registry caches are rebuilt.
4. The domain delivery point detaches removed/changed parent links across a
   captured batch, then updates accepted override Drips. Transparent children
   cannot receive an intermediate parent event when becoming concrete.
5. Existing resource retirement and effect-delivery adapters continue.

Priority observers therefore see the accepted graph and generation. Reentrant
render writes are rejected by the existing completion gate. Independent keys
continue after a notification/link failure; failures preserve actual publication
evidence and quarantine reuse, not fictitious rollback. Drip's existing default
logging/error policy is unchanged.

Parent events arriving independently during a render still propagate through
accepted links. Synchronous observers read that event rather than the lexical
candidate. Managed parent links use weak callbacks and finalization, so a live
stream does not retain the render graph or leave its subscription behind.
Explicit retirement detaches links idempotently. Legacy links retain their
existing behavior.

## Scope And Verification

This is I6a plus the narrow publication/registry delivery seam it needs, not all
of I6b. Structural directives, arbitrary post-commit queues, class-name dispatcher
deletion, default-route adoption, and legacy compatibility deletion remain pending.
The single-cohort amendment supersedes older I6 wording about independently
publishing child boundaries. No compiler or lifecycle-library changes are needed.

`tests/data/lcm_integration/override_selection_lifecycle.py` and its authored JSON
baseline cover lexical values, transparent nesting, rollback, stable identity,
generation/registry visibility during notifications, concrete transition, and
omission. Narrow faults cover caught validation, independent parent events,
observer failure/draining, reentry, graph lifetime, and parent-detach ordering.
Verification results are recorded in the handoff after the expanded runs.

Final verification: full native **1071 passed, 2 unchanged host-ordering failures,
20 skipped**. The expanded Python compatibility/component/override/golden run
passes **53 tests**; the final override-only run (including the last transition
regression) passes **8 tests** on Python assembly. Formatting and diff checks pass.

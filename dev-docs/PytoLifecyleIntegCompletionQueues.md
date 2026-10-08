# I6b: Directives And Completion Queues

## Existing Timeline

Before this checkpoint, directive local exit validates selectors/no-emit,
copies selectors into a plain holder, and projects children. Legacy base exit
completes child bindings by owner class name, then publishes local fields.
Legacy render exit rebuilds mount advertisements and flushes its callback list;
one callback failure skips subsequent callbacks. Root boundary completion
accepts generation separately. Independently queued invalidations belong to the
scheduler, not to that callback list.

The preceding private lifecycle checkpoints instead validate/project local
candidate graph state, publish through one outer owner, accept generation,
clear pass scratch, and rebuild accepted registries. Override notifications run
at that point. Resource adapters then retire discarded owners and deliver
accepted effects. Local pass exit does not publish.

## This Checkpoint

Extend the private override gate to directives and general post-commit queues.
Directive selectors use managed storage alongside inherited graph/UI fields;
projection and no-emit validation read candidate children before publication.
Retain legacy selector compatibility storage only on unactivated routes.

Capture callback source render/expression and callback in enqueue order under the original
attempt. After the existing completion/resource chain returns (or reports its
failures), deliver only a published, retained render's captured callbacks.
Generation and registry reconciliation precede delivery. Drain independent
ordinary and system failures, preserve lone exception identity, and quarantine
reuse after delivery failure. Discard failed-attempt batches; uncertain
publication retains evidence without delivery. Reentrant render/queue writes
are rejected during completion. Independent invalidations are not discarded:
remember their dirty marks separately and reapply them to retained states after
local pass scratch is cleared, on both acceptance and rollback. The scheduler
queue remains authoritative; the existing `_queued_invalidations` list is a
debugging history, not a delivery batch.

Replace legacy owner-class-name dispatch with private state-manager completion
methods without activating the new route or changing directive legacy binding
timing. This is not removal of all legacy storage or default-route adoption.

## Verification

Use a canonical directive/queue timeline plus focused faults: no-emit candidate
children, caught selector failure, rollback/retry, late/reentrant enqueue,
independent invalidation, retired source callbacks, callback draining and
post-publication failure evidence. Run both assembly engines and the full
regression suite. Existing mixed host-child ordering failures remain unrelated.

## Deletion And Scope

Base end/rollback no longer selects completion methods by owner class name.
Compatibility-only polymorphic methods preserve the legacy domain completion
calls; lifecycle gates bypass them. Directive selector save/restore only remains
on the unactivated compatibility route, not on the I6b gate. No lifecycle-library
or compiler change is required, and historical baselines are unchanged.

The scheduler's existing failure-path repost policy is not redesigned: a failing
scheduled boundary can still require an explicit later flush for remaining work.
This checkpoint preserves queued work and dirty marks, not a new automatic retry
contract after delivery failure. Delivery failure quarantines the new completion
owner; it does not pretend accepted state was undone.

## Checkpoint Status

Implemented behind `_enable_completion_render`. Separate review
remains deferred to aggregate integration review, and normal routing is unchanged.
Native full regression: **1083 passed, 2 unchanged host-ordering failures,
20 skipped**. Affected Python assembly and compatibility checks: **43 passed**;
the earlier broader characterization run passed **72 tests**. The new canonical
fixture is `tests/data/lcm_integration/directive_completion_lifecycle.py`, checked
against its authored JSON baseline by `test_lcm_integration_characterization.py`.
No historical baseline was regenerated.

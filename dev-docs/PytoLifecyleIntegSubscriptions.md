# Subscription Completion Checkpoint

Status: implemented and tested; independent review deferred by the operator to
the larger integration review. This checkpoint is not independently accepted.
The operator approved one
bounded subscription migration after the accepted plain-value slot-call checkpoint
at `050ec5bdfc36b434fd0ad4b32d99de50cc5352f0`. Review the implementation, not a
new broad design campaign. Read the single-cohort amendment and SC3/L0 contracts.

## Boundary

- Add a separate private subscription-enabled gate extending the accepted
  callback/plain-value gate. Keep existing gates, runtime selection, shared
  handlers, legacy call sites, effects, async effects, and mounts unchanged.
- Preserve one managed invocation record for identity/schema/arguments/value
  selection. Add an `owned(compare="identity", tx_key=PASS_TX_KEY)` subscription
  private ownership wrapper using `yidl_lifecycle.bindings.BindingBase`; lifecycle
  owns its pending, staged, and current references. The wrapper adopts one resource
  reference using the existing `yidl_lifecycle.bindings_refcount.BindingBase`.
  There is no second transaction manager or new refcount engine.
- The operator approved this hybrid ownership model: ordinary Python references
  manage the private wrapper, and explicit resource references manage unsubscribe.
  Detached value bindings retain only the resource, never its owning wrapper.
  Keeping an old snapshot, diagnostic, or resource object alive therefore does
  not keep the subscription active. A genuinely independent owner needs its own
  wrapper and explicit retain. Document this distinction in the source, including
  why failed candidate wrappers are released rather than left to finalization.
- The resource owns the unsubscribe callback. Detached value bindings
  can share that resource, but do not mutate accepted value/ref snapshots. Matching
  store identity reuses the selected subscription; replacing it creates a new
  subscription without unsubscribing the accepted one during evaluation.
- Subscribe/get remain synchronous during evaluation, since the callable result
  needs a value. Failed get after successful subscribe releases that candidate.
  A subscribe callable that raises before returning its cleanup handle must undo
  its own partial work; no caller can recover an undisclosed handle.
- Notifications hold weak links to the handle and host, preventing a store's
  callback registry from retaining the context graph. Notification revision lives
  on the handle, outside render rollback. A refresh produces a detached candidate
  snapshot; failed refresh does not consume the accepted snapshot's revision.
- Use the already selected handler exactly once for admission. Fence the captured
  render owner after user recognition, identity equality, subscribe/get, and value
  comparison, before any candidate writes. Stale work must not enter a new token.

## Completion Timeline

1. Evaluate candidate bindings and stage invocation plus owned handle under the
   original outer render owner. Local success does not publish either field.
2. Before participant capture, stage empty selection for omitted slot-call states.
   Explicit removal also stages empty selection; never deactivate the accepted
   resource early. Component/graph replacement remains blocked by older gates.
3. Lifecycle preparation marks owned handles accepted using existing behavior.
   This is not external activation or final publication; subscribing already
   happened during evaluation. Acceptance alone cannot certify render success.
4. Lifecycle applies or discards its fields. Replacement/removal releases the old
   ownership references; rollback releases candidate references and retains current.
   Keeping a value snapshot alive does not retain ownership. Independent ownership
   wrappers keep the resource active until their last explicit reference releases.
   Wrappers created only for this attempt are also inventoried for idempotent
   release if not published: incidental traceback or diagnostic references must
   not retain a failed attempt's subscription. This
   inventory owns external creations, not another field-publication authority.
   The resource's cleanup callback is attempted once.
5. Consume actual publication evidence for generation and reconcile the graph via
   the existing owner. Resource finalization failures are collected independently,
   preserve the original error, and quarantine reuse without pretending published
   values were rolled back. A later release of an independently owned wrapper
   cannot retroactively fail a completed render; its cleanup error blocks future
   reuse if the completion owner remains alive.
   Keep completion closed to reentry through the entire resource-draining phase.
   Unknown publication quarantines new handles rather than inventing undo of
   possibly published resources.

## Proof And Faults

Author `subscription_selection_lifecycle.py` and its JSON before implementation.
Cover current/candidate values, notification refresh after failed render, failed
replacement, retry, successful replacement, same-identity reuse, shared retained
snapshots without retained ownership, explicit/omitted removal, and graph collection while the store remains
alive. Assert actual subscribe/get/unsubscribe events and owned-field facts.
Do not rewrite historical snapshots or duplicate these successes as unit tests.
Use a narrow ownership-mechanics test for two private wrappers retaining one
resource, idempotent release, and exactly one unsubscribe at explicit count zero.

Narrow faults cover subscribe/get/recognition/comparison errors, replacement-token
reentry, throwing cleanup with independent cleanup draining, and unchanged effect/
mount rejection. Preserve exact errors and fail closed on uncertain authority.

Run the expanded focused native baseline, affected Python assembly, existing
subscription/effect/mount compatibility, and full regression. Attribute known
failures by identity. Per the operator's later directive, defer a separate bounded
Code/State review and include this checkpoint in the larger integration review.
Keep the proof gates and legacy/default routes unchanged until their activation
contract is satisfied; deferring review is not runtime-activation approval.

## Verification

- Expanded native integration and existing resource compatibility: **226 passed**.
- Subscription, slot-call, and characterization tests on Python assembly:
  **41 passed**.
- Full default native regression at the subscription checkpoint: **981 passed,
  13 recorded visitor/host-order failures, 20 skipped, 1 warning**. The later
  synchronous-effect checkpoint and separate graph accessor correction reran
  the full suite: **1000 passed, 2 recorded host-order failures, 20 skipped,
  1 warning**; see [the later verification](PytoLifecyleIntegEffects.md).
- Source ownership rationale, formatting, and diff checks are complete. No
  dependency source, shared legacy handler, or historical JSON was changed.
- No reviewer was dispatched for this checkpoint. Aggregate review must cover
  hybrid ownership, cleanup errors/reentry, and publication-versus-discard evidence.

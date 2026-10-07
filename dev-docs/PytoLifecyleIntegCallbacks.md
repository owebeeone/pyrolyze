# Callback Selection Migration

Status: **accepted at Pyrolyze `6be1b8f610c13eda18a451688377370cb1dbb087`
after Code/State GO/GO; bounded callback-selection migration and private proof
only**, 2026-10-08. The operator approved
implementation followed by a focused implementation review, not another design
review campaign. Baseline: Pyrolyze `dd3d3a7`; accepted completion consumer
`b1461a1128da15c21dad482d41bd5792253904cd`. Dependencies remain the tuple in
`PytoLifecyleIntegSC3-L0Consumer.md`.

## Scope

Replace the decomposed LCM event-handler selection stores with lifecycle
fields. Keep the original/monolithic implementation and historical JSON intact.
This is I3b's storage/caller migration plus the first bounded D5 adapter proof,
not a callback API redesign, I3a completion, or general resource activation.
No library/compiler work is needed.

- `_callback` and `_callback_key` are managed by `PASS_TX_KEY`; both use
  identity storage comparison so dirty-forced value-equal replacements retain
  the exact new callback/key. Selection eligibility still uses the reference's
  key equality rule.
- `_dispatch` is ordinary local storage and keeps its existing strong closure
  and stable identity. It reads `.current._callback`, never pending selection.
- Bound-method keys preserve receiver identity and function identity. The
  historical A then pending B/A quirk is preserved; no effective-candidate fix.
- Reselection cancels explicit pending retirement, including a callback equal
  to current. User-executable key properties/equality finish before the same
  captured render owner/token is rechecked immediately before selection writes.
- Delete the four manual stores, `commit_handler`/`rollback_handler`, their
  facade forwarding methods, and both base/component transfer callers. Keep
  component resource cleanup/visitation bookkeeping; do not claim I5 complete.
- On the retained unactivated route only, caught component invocation failure
  masks its provisional selection with the accepted callback/key through managed
  setters. This temporary local-discard adapter preserves parent-catch behavior;
  it neither writes physical current storage nor restores a transfer engine.
  The private route instead discards once through the outer completion owner.
  Argument preparation belongs to that captured owner too: a failure before
  child-boundary entry must be recorded even if the parent catches it.
- Event handlers contribute no UI. Use the existing polymorphic empty-UI
  surface instead of reading an undeclared `ui_state` from a handler.

## Completion Timeline

A separate private callback-enabled gate extends the accepted field-only
completion owner. The original field-only gate stays unchanged. Only exact
event-handler slots are additionally admitted; bindings, effects, mounts,
overrides, legacy call sites, component replacement/retirement remain blocked.
Nested field-only renders may select callbacks on the same manager/key.
Pending handler arguments may materialize component-owned selection too;
omitted owned handlers are removed from candidate membership before retirement
selection is staged. No legacy call-site binding/acceptance is involved.
Owned-handler argument visitation is scoped to the attempt that evaluated it;
only participating component owners can authorize omission normalization. Its
order/visitation scratch is reset after coherent completion under the existing
cleanup/reuse fence, not interpreted again by an unrelated later write scope.

1. Local evaluation stages selection and candidate membership. Existing dispatch
   still invokes the previously accepted callback; new dispatch is inactive.
2. After all local scopes exit, identify registered handlers absent from the
   final candidate graph and stage their selection as None before manager
   preparation freezes membership. This is domain retirement selection, not a
   manual field-application loop. Fence reentry and original-token authority.
3. Lifecycle publishes or discards fields once at outer completion. No event
   callback runs because of commit. A failed render preserves retained accepted
   handlers; new/omitted handlers cannot become callable outside accepted
   membership after coherent completion. Partial/uncertified outcomes keep the
   existing quarantine policy, not a new whole-graph atomicity claim.
4. Generation follows actual publication evidence, then the existing owner
   clears local scratch and reconciles registration caches. No field writes or
   user notification are introduced after finalization.

Explicit handler deactivation stages selection/membership removal in the owning
write scope. During a private attempt, do not eagerly unregister the accepted
cache entry or clear current selection; cache reconciliation follows completion.
Out-of-pass explicit removal owns its own supported write scope. No new
out-of-render registration API, weak-reference policy, close protocol, or
subscription/effect teardown is introduced.

## Verification And Review

Add `tests/data/lcm_integration/callback_selection_lifecycle.py` to the existing
JSON harness. Reuse reference selection cases with an injectable root factory;
their historical results stay unchanged. Add canonical checks for dirty-forced
equal callables, real nested success/parent failure, caught child failure,
new-handler discard, omission/removal success and failure, current/generation
visibility, empty UI, and exact marker/manager ownership. Narrow fault tests
cover admission, stale-token writes, and retirement-preparation failure.

Use strict red/green, run the accepted seven-file suite plus new narrow tests
on native and the canonical/affected subset on Python. Run full default and
the same broader unactivated comparison. Record any resolved callback-related
baseline failures explicitly; do not regenerate historical goldens or fix
unrelated debt. Settle one implementation checkpoint and conduct a tightly
scoped implementation review. Resource categories not named here stay gated.
No push, tag, worktree, or parent-pointer update is part of this checkpoint.

## Initial Candidate Evidence

The canonical JSON and narrow faults were added red before implementation.
Dirty-forced equal-key replacement and retirement-preparation error/reentry
checks each exposed a bounded correction before green. Historical JSON and
the runtime selector are unchanged. Dependencies are unchanged.

- Focused native suite (the previous seven targets plus
  `tests/test_runtime_context_state_lcm_callbacks.py`): **155 passed**.
- Affected harness and narrow callback tests on the Python backend:
  **19 passed**.
- Full default native suite: **945 passed, 13 failed, 20 skipped**. The same
  13 baseline failures remain: eleven visitor/visualizer missing
  `own_committed_ui_entries` cases and two host-order cases.
- Broader unactivated decomposed comparison: **44 passed, 11 failed**, versus
  the previous 41/14. The three resolved cases are the component-owned handler
  identity test and two scheduler/handler tests formerly blocked by handler
  `ui_state` lookup. Remaining failures are nine `_scope_active` override
  cases, one mount-advertisement count, and one generation relocation case.

The implementation review is restricted to this candidate diff, its callback
contract, and affected completion/admission behavior. It is not another design
review of the accepted library or the whole integration.

## Implementation Review

Candidate `e1cce818e3c99712d54b37976a5794a8d85cfb57` received Code/State
NO-GO. Their five P2 findings map to four roots: retained local failed-selection
discard, stale owned-handler omission scratch (independent convergence),
explicit retirement cancellation, and callback user-code authority loss.
Verbatim reports and the one combined remediation plan are in
`history/lifecycle-integration/PytoLifecyleIntegCallbacks-ReviewCode.md`,
`-ReviewState.md`, and `-RemPlan-1.md`.

All counterexamples were red before correction. The revised canonical fixture
adds child-only/retained component reuse, unrelated removal after failed omission,
and identical/value-equal deactivate-reselect success and failure. A separate
owned-selection reference JSON compares original, monolithic, and unactivated
decomposed routes. Narrow equality/property faults reject replacement-token
contamination. The new private target is extended; historical JSON is unchanged.
The first re-verdicts and their remaining finding are recorded below.

Corrected-tree verification: **160 focused native passed**, **24 affected
Python passed**; full default native **950 passed, the same 13 failures,
20 skipped, one warning**; broader unactivated **44 passed, the same 11
failures**. Black/diff checks pass. No dependencies, historical snapshots,
default selector, or other resource admission changed.

Remediation-1 re-verdicts (`-ReviewCode-1.md`, `-ReviewState-1.md`) closed
every original finding. Both independently found one additional pre-child
argument-preparation failure gap, mapped to Code P2-4 / State P2-3. The single
correction in `-RemPlan-2.md` captures the private invocation owner and records
the exception there before rethrowing. The canonical fault was red first,
then passed for both initially absent and accepted first handlers: exact cause,
no leaked registration/selection, unchanged generation/invocation, clean retry.
This does not change unactivated parent-catch semantics or restore manual
membership/current writes. Final re-verdicts closed that finding on the tuple
below.

After the second correction the same gates were rerun: **160 native focused**,
**24 Python affected**, full default **950/13 unchanged failures/20 skipped**,
broader unactivated **44/11 unchanged failures**. Black/diff checks pass.

## Accepted Checkpoint

| Repository | Reviewed Revision |
| --- | --- |
| Pyrolyze runtime/fixtures | `6be1b8f610c13eda18a451688377370cb1dbb087` |
| yidl-lifecycle (unchanged) | `05554397d1837ecbeafa36e4685477dd5ff30fc6` |
| YIDL (unchanged) | `a7cc1de7b630b55bd194940ecad83f3f1738cf8a` |
| Astichi (unchanged) | `1c47f781d3804130fdd61cbee07a3b2e4529158a` |

Both reviewers independently replayed their original counterexamples and the
pre-child fault on native/Python, ran the 24-test affected subset on both,
and reported **GO** with no new findings. Reports are preserved verbatim:
[Code](history/lifecycle-integration/PytoLifecyleIntegCallbacks-ReviewCode-2.md)
and [State](history/lifecycle-integration/PytoLifecyleIntegCallbacks-ReviewState-2.md).
Remediation rounds used: **2/2**. Independent convergence occurred on stale
omission scratch and pre-child failure recording. Broad counts are implementer
evidence, not independently repeated broad acceptance.

This accepts the managed selection stores, caller deletion, retained-route
compatibility adapter, and private handler-enabled proof. It does not certify
I3a/I5 completion, subscriptions/effects/overrides/legacy call sites, component
retirement, or default-runtime activation. The original field-only gate remains
unchanged. No push, tag, worktree, library change, or parent-pointer update.

Next bounded checkpoint: I3c invocation values, starting with leaf/rerunnable
argument and identity stores. Resource-dependent invocation routes remain
blocked until their own adapters; no wholesale snapshot deletion follows.

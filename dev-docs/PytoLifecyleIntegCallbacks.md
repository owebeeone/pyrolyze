# Callback Selection Migration

Status: bounded implementation contract, 2026-10-08. The operator approved
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
- Delete the four manual stores, `commit_handler`/`rollback_handler`, their
  facade forwarding methods, and both base/component transfer callers. Keep
  component resource cleanup/visitation bookkeeping; do not claim I5 complete.
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

## Implementation Evidence

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

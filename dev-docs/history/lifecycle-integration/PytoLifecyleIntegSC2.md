# SC2: Gated Field-Only Render Wiring

Status: **DRAFT implementation checkpoint; acceptance requires dual Code/State review.**
Date: 2026-10-04.

## Authority And Activation

The operator approved a private, graph-level field-only proof gate on
2026-10-04. This refines SC2 in `PytoLifecyleIntegSingleCohortPlan.md`:
the existing decomposed routes remain unactivated until SC3. No public context
option, selector, default switch, or dependency change is introduced.

Enable the gate on a fresh scheduler root, before mounting, allocating slots,
or entering a pass. It is immutable for that graph. Nested render constructors
receive the root's existing manager before lifecycle initialization. Do not
construct another manager and overwrite a generated slot afterward.

Activation requires an unowned scheduler root. Slot constructors validate both
the parent graph and the supplied nearest render root before initialization
or registration. Owned nested renders must supply their actual activated
scheduler root; omitted or conflicting ownership never creates another manager.
Direct constructors also reject occupied current, candidate, or registry slot
IDs before lifecycle initialization or graph attachment. Reuse goes through
the existing ensure path, not a second constructor.
Owned renders reject a second child before lifecycle initialization. A first
root may be constructed before installation, but execution, publication scopes,
child attachment, and owner UI propagation require its component's child pointer
to refer back to that exact root; caught admission errors still poison the
outer attempt.

The proof admits the exact existing root, native leaf, plain structural slot,
and component-call classes. External containers, mount directives, bindings,
callbacks, authored app-context overrides, native containers, and keyed-loop
handles remain outside this checkpoint and must fail before resource work on
an activated graph. Component identity/schema replacement and retirement are gated;
SC2 does not invent a resource disposal protocol. There is no fallback to a
legacy local completion path inside an activated graph.

## Ownership And Local State

The graph coordinator delegates transaction ownership to the accepted SC1
`_RenderAttempt`. Scheduler boundaries, standalone passes, and publication
write scopes use the same admission and completion path. Nested scopes do not
begin, validate, commit, or roll back the manager independently.
Lexical pass scopes, no-op re-entry, publication scopes, and the entire native
invocation retain an execution claim until their own exit, even if the body
explicitly releases its local pass early. A direct outer local completion
request waits for the last execution claim. Later failure preserves its primary
error and discards the attempt rather than publishing an unfinished body.

Local activity is the existence of an entered local handle, not key activity.
Scoped re-entry does not reset twice. Direct duplicate entry diagnoses even
when there are no children. Local reset/assembly errors and escaping render
callback errors poison the attempt before cleanup; caught child errors cannot
publish. Retain the original failure as the abort cause.

The legacy dirty/visitation snapshots remain context-local until outer
completion. This is not SC4's dirty/site-metadata migration. The coordinator
stores execution handles and participating contexts, not copies of managed
values or membership maps. Successful local release does not erase the
snapshots needed if the outer body subsequently fails.
Each local pass retains the preceding candidate child references solely for
retirement admission. Repeated passes may revisit the same component, but
omitting it requires the same retirement preflight as a committed component.
This inventory is never used to restore membership and clears at outer cleanup.

Published UI/debug/membership readers use `current` on activated graphs;
internal parent UI assembly, deactivation traversal, and parent-map edits read
candidate fields. All child-map updates are replacement writes. Slot
registration is a lookup cache, not publication:
after a known clean completion, reconcile that cache from current graph
membership. Track affected render roots on registry/publication writes as well
as local-pass entry, including nested roots that a discard made unreachable.
Cancel scheduler bookkeeping for unpublished orphan boundaries on clean
discard; preserve existing published boundaries and queue entries. Published
slot-specific debug lookup traverses current membership, not the candidate
cache. No resource close/deactivation callback is part of reconciliation.
Direct disposal/deactivation and subtree removal preflight component descendants
before scheduler, callback, pointer, or membership edits.
This includes newly introduced unseen candidates selected by the local pass's
membership filter, not only preceding or currently published children.

## Completion And Failure

Admission rejects an externally active render key before generation/reset.
Only the outer owner completes the lifecycle key and then the generation
tracker. Clean discard also discards that generation. Uncertain application,
lost ownership, or incomplete cleanup quarantines the last attempt, prevents
retry, and does not fabricate generation rollback. Other keys are untouched.

SC2's generated participant audit must establish that the admitted classes
have no user apply/after callbacks. Validation fault injection may use the
real manager's supported participant protocol, but cannot mock completion
semantics or imply that a throwing application is recoverable.

## Canonical Proof And Baselines

`tests/data/lcm_integration/common_pass_single_cohort.py` and its authored JSON
target own successful end-to-end observations. Cover nested manager sharing,
candidate/current visibility, one publication, caught child failure, parent
failure after child success, later sibling non-recovery, clean retry, local
re-entry, standalone/queued attempts, independent roots, other-key permissions,
and real validator failure. Narrow tests cover gate rejection/cleanup faults.

The SC2 live-test transition ledger is amended as follows: the historical
independent-manager, external-borrowed-entry, leaf order, and mixed-resource
characterization tests stay live unchanged on unactivated graphs. The new
canonical fixture explicitly enables the gate and owns the new contract.
SC3 must transition those live routes in the same checkpoint that activates
them; preserving them here is not a waiver or an unconditional skip.

Preflight: the accepted pinned dependency tuple and the six-file focused
baseline passed 64 tests in 12.02 seconds. Unrelated
`dev-docs/RenderingBackendBugList.md` and dirty dependency work are excluded.
Record red/green/full-suite results and the settled tuple in the review ledger.

## Verification Before Settling

- Canonical red: missing private gate; then authored membership/order targets
  exposed plain-slot traversal and repeat-pass order gaps. The expected JSON
  was authored from the contract, not copied from runtime output.
- Narrow red: seven direct resource constructors bypassed admission; late
  activation and adapter-cleanup retry were admitted; lexical local completion
  published prematurely; unowned nested roots and component retirement were
  admitted. Each counterexample was run red before its bounded correction.
- Focused: **80 passed in 13.64s**, including the accepted SC1 mechanisms and
  the unchanged construction/slot/legacy characterization tests.
- Full default: **870 passed, 13 failed, 20 skipped, 1 warning in 46.23s**.
  The failure identities remain the prior eleven visitor/export failures and
  two host-order cases; no full green claim or baseline waiver.
- Broader decomposed eight-file subset: **41 passed, 14 failed in 2.19s**,
  with the same nine app-context, one mount-advert, one generation, and three
  event-handler failures. This run does not activate the private gate.
- Black 26.3.1 formatted only the three new Python files; existing modules
  retain scoped edits. Diff whitespace checks pass. No historical JSON was
  regenerated and no dependency source was changed.

### Final Bounded Remediation Evidence

Round 1 returned NO-GO on localized candidate-membership, repeated-pass
retirement, publication-only cache, and direct-constructor collision omissions.
Both reviewers classified these as non-architectural. Round 2 adds the
counterexamples before their corrections; SC2 remains unaccepted pending fresh
dual review, and no third architectural patch is authorized.

- Initial round-2 red: **7 failed, 32 passed** on the narrow/canonical subset.
  Two further detached-root registry-clear/removal cases also failed red before
  affected-root bookkeeping was extended to publication and registry writes.
- Final focused seven-file run: **107 passed in 14.12s**.
- Final full default: **897 passed, 13 failed, 20 skipped, 1 warning in 43.45s**.
- Final broader decomposed, unactivated: **41 passed, 14 failed in 2.23s**.
- Full and broader failure identities remain the baselines above. No failure
  waiver, historical target regeneration, resource activation, or dependency
  source change is included.

### Reproduction

Use clean committed source exports (not the dirty workspace dependencies):
yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`, YIDL
`95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`, and Astichi
`387ca5e1da76204ee60922094734c13ee36383c0`. Set `snapshot` to a temporary
directory containing those repository exports, and run from the Pyrolyze root:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH="src:$snapshot/yidl-lifecycle/src:$snapshot/yidl/src:$snapshot/astichi/src" \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_render_attempt.py \
  tests/test_runtime_context_state_lcm_field_only_render.py \
  tests/test_runtime_context_state_lcm_construction.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py \
  tests/test_lcm_integration_characterization.py
```

Omit test paths for the full default suite. The broader command uses the
eight paths in `PytoLifecyleIntegI0Findings.md`, with
`PYROLYZE_CONTEXT_IMPL=bare_refactor_lcm`. The canonical proof is also directly
readable/runnable at `tests/data/lcm_integration/common_pass_single_cohort.py`.
It records actual candidate/current/generation observations, real manager
validation/discard events, and the admitted generated classes' no-converter,
no-transaction-hook metadata. Its sole injected validator has audited
nonthrowing apply/after/rollback bodies; only validation throws.

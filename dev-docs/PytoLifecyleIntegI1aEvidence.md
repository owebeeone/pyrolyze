# I1a: Constructor Injection At Existing Boundaries

## Scope And Status

The user authorized proceeding with holder-first integration. This checkpoint
implements its first constructor prerequisite, not completed holder replacement,
I1b attachment migration, manager unification, or runtime activation.

Controlling plan: `dev-docs/PytoLifecyleIntegPlan.md`, accepted at Pyrolyze
`78e3184132eae33169ae3c329be35f3146ed338a`, blob
`81d004dc44bc84516a3484e2a64be9667f0657bc`. The plan-only dual review and exact
dependency tuple are recorded in the HolderFirstPlan review-loop ledger.
Those plan bytes remain unchanged.

Review tier for this interior implementation checkpoint: **one read-only Code
review**, automatically escalating to a second State reviewer on any P0/P1/P2.
No author-facing API, durable format, publication contract, or generic library
API is frozen here. Commit before dispatch and pin the exact source tuple;
only review output files may be uncommitted during inspection.

## Changes And Removed Authority

- `StateMgrBase.create(owner=..., **kwargs)` supplies the runtime-only
  construction entry point. The generated constructor remains the initializer.
- `ContextBaseStateMgr.create` resolves the existing render boundary manager and
  passes `transaction_manager=` before generated field/factory initialization.
  It preserves the old bootstrap's precedence when a render manager is present.
  Without one, an explicitly supplied manager or the existing constructor
  allocation path remains valid.
- The owner facade's `_init_state_mgr` uses that entry point. Existing call sites
  provide keyword construction inputs; no user initializer chaining is added.
- Removed `_bootstrap_transaction_manager_bad_program` and the
  `_transaction_manager_bootstrap_bad_program` dummy lifecycle field. There is
  no replacement private-state write or throwaway allocation then overwrite.
- Ordinary/decorated derived construction and rerunnable multiple inheritance
  use the same seam. Standalone state tests needing render-boundary resolution
  use `create`; direct generated constructors still accept explicit managers.

Nested render and call-site allocations, pass begin/end/rollback logic, callback
holders, resource delivery, and attachment factories are unchanged. Those
mechanisms remain obligations of subsequent checkpoints. No library, YIDL,
Astichi, parent pointer, selector default, or historical snapshot is changed.

## Verification

Environment and dependency tuple match the holder-first review package; existing
dirty YIDL cleanup and unrelated parent changes are excluded.

- Red: two narrow factory tests fail with missing `create` before source edits.
  The early-factory test overrides the first initialization factory to observe
  its manager, rather than checking only the completed object.
- Green: context-base and slot-expression mechanics initially pass all 13 tests.
- Added narrow identity checks for explicit-manager construction and preserved
  independent nested-render completion cohorts.
- Seven focused LCM files plus canonical characterization: **43 passed in 2.36s**.
- Pre-edit full default suite: **809 passed, 13 failed, 20 skipped, 1 warning in
  30.55s**; failure names match I0's eleven visitor/export and two ordering defects.
- Source-search finds no bootstrap function/dummy field or
  `state._y_transaction_manager =` write in the active decomposed dependency path.
- Diff whitespace check passes; canonical baseline JSON files are unchanged.

The initial decorated test helper had a leading underscore, exposing existing
generated-name mangling during class build. It was renamed before the intended
red tests ran. No lifecycle generator fix is included; this is separate library
debt, not a construction-seam failure or an excuse to widen I1a.

Post-edit full default suite: **813 passed, 13 failed, 20 skipped, 1 warning in
28.96s**. All 13 failure names match the immediately pre-edit full run. Broader
eight-file decomposed subset: **41 passed, 14 failed in 0.83s**, matching I0's
existing override, mount, generation, and event-UI failure clusters. The four
extra passes are the new narrow construction checks, not repaired baseline bugs.

Full-suite failures remain integration debt; this checkpoint is not an
I7/default-routing acceptance.

## Independent Acceptance

Status: **I1a accepted at Pyrolyze
`30cb868c168d70907ad2fceff1bb8e2841dda16e` after
`dev-docs/PytoLifecyleIntegI1a-ReviewCode.md` reported GO; this accepts constructor
injection on existing completion boundaries only.**

The settled dependency tuple was yidl-lifecycle
`cdf08544deea846bca4fa7e0c468ebee8d41e138`, YIDL
`95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` (committed view only), Astichi
`387ca5e1da76204ee60922094734c13ee36383c0`, and parent
`a20f8cfb633a268925464eb27728d1934a70aea9` (context only). The reviewer checked
the tuple at both ends; excluded dirty YIDL and parent bytes were unchanged.

- The fresh, read-only Code review found zero P0/P1/P2/P3 issues and independently
  ran the two constructor test files: **15 passed in 0.58s**.
- No blocker triggered State escalation. Implementation remediation rounds: 0.
  The preceding plan campaign used one round, recorded separately in its ledger.
- The report is filed verbatim; the prompt is adjacent. Lane-owner broad/full
  results above are not presented as reviewer-executed checks.
- No library behavior, publication/rollback boundary, runtime selector default,
  parent pointer, tag, push, or merge is part of this acceptance.

I1b/I3a, authoritative holder replacement, and later U1/U2 manager unification
remain open. The leading-underscore generated-name issue observed during test
setup is separate pre-existing library debt, not an escaped I1a defect. No I1a
defect was found by independent review; the existing I0 failures remain open.

## Reproduction

Run from the Pyrolyze repository root using the established environment:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py \
  tests/test_lcm_integration_characterization.py
```

The integration plan lists the seven-file focused and broader/full commands.
No golden regeneration is needed for this checkpoint. The next holder work is
I1b/I3a: common slot declarations and explicit graph attachment, followed by
callback and invocation-holder replacement on existing completion boundaries.

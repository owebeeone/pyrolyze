# Pyrolyze Callback Selection Remediation 2 — STATE-AXIS REVIEW

**Review object:** Pyrolyze `6be1b8f610c13eda18a451688377370cb1dbb087`, branch `lcm-resume`, final bounded remediation. Changed range: `aa073c8df5ba1a2dc7f8697425298a02c5772f2f..6be1b8f610c13eda18a451688377370cb1dbb087`. Controlling contract: `dev-docs/PytoLifecyleIntegCallbacks.md`; remediation plan: `dev-docs/history/lifecycle-integration/PytoLifecyleIntegCallbacks-RemPlan-2.md`, both at reviewed HEAD.
**Baseline:** Prior revision `aa073c8df5ba1a2dc7f8697425298a02c5772f2f`; unchanged yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`, YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`, Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Sources inspected through `git show`, changed-range diffs, and numbered clean tracked-file reads.
**Date:** 2026-10-08
**Axis:** STATE: original-owner authority, provisional selection/membership, caught-failure propagation, and recovery legality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — all three prior P2 findings are closed; no new findings in the bounded changed range.

---

## 0. Evidence base

- Verified all four HEADs and `git status --short --branch` at start and end. The exact tuple remained unchanged; tracked trees stayed clean, with only the same two excluded untracked documents. Neither was read.
- Read Remediation Plan 2 and the corrected contract clauses. Reused this reviewer’s prior evidence; no other-axis report was opened.
- Inspected `src/pyrolyze/runtime/context_state_lcm/component_call_slot_context.py:100-249`, especially owner capture at lines 120-123 and failure recording at lines 185-189.
- Read canonical preparation coverage at `tests/data/lcm_integration/callback_selection_lifecycle.py:285-387` and its JSON addition.
- Confirmed the only changed runtime source is the component invocation module. The preceding corrections in `callback_render.py`, `event_handler_slot_context.py`, and `field_only_render.py` have an empty changed-range diff.
- Working directory for tests/probes: Pyrolyze repository root (`.`). Used the prescribed virtualenv/local-source environment, both context selectors unset, bytecode disabled, and each assembly backend.
- Command: `python -m pytest -p no:cacheprovider -q --tb=short tests/test_lcm_integration_characterization.py tests/test_runtime_context_state_lcm_callbacks.py`.
  Results: **24 passed native; 24 passed Python**.
- Independently replayed the original pre-child preparation counterexample using direct component invocation, not the fixture. Tested accepted A and additionally no initial handler on both backends.
- Independently replayed the original failed-omission/unrelated-removal sequence, equality-token replacement sequence, and property-token replacement variant on both backends.
- `git diff --check aa073c8d 6be1b8f6` passed. No files were written, broad suites rerun, builds performed, or git state mutated. Lane-owner broader counts were not independently repeated.

## 1. Prior-Finding Closure

| Finding | Status | Concrete Evidence |
| --- | --- | --- |
| P2-1: stale omission scratch authorizes unrelated removal | **Closed, retained** | Direct unrelated removal immediately after failed omission preserved accepted handler membership, callback identity, and dispatch. Visitation/order scratch was reset; subsequent genuine omission still retired the handler. Both backends agreed. |
| P2-2: user key evaluation contaminates replacement token | **Closed, retained** | Equality and property attacks received neither selection write. Committing the equality attack’s replacement still retained A and dispatched only A. Original ownership loss remained `published=None`, `reuse_ready=False`. Both backends agreed. |
| P2-3: caught pre-child preparation failure escapes outer discard | **Closed** | Staging B then throwing from the second callback’s property, caught by the parent, now caused outer `RenderAttemptAborted` with the identical error as its cause. A/dispatch/invocation/generation survived; new handlers disappeared; coherent discard certified reuse. Both backends agreed. |

## 2. Invariant Analysis

### Changed-Range Analysis

The invocation captures its original private owner before argument materialization. Its exception handler records the caught exception on that captured owner before the private rollback bypass and rethrows it. It does not borrow a later active owner.

The independent P2-3 replay demonstrated:
- The child did not execute during failed preparation.
- `first_failure` retained the exact property exception; outer abort retained that exception as its cause.
- Accepted callback A and stable dispatch survived; the committed invocation object retained identity and committed generation did not advance.
- Newly materialized handlers were absent from accepted registration. With no initial handler, the held provisional dispatch remained inactive.
- Completion certified `published=False` and `reuse_ready=True`.
- A clean retry published B, executed the child once, and advanced generation once. Accepted-handler dispatch identity remained stable.

The correction adds no publication engine, physical-current writes, membership restoration, admission, interface, or manager behavior. The unactivated local-discard branch is unchanged; its reference comparisons passed in the permitted harness.

Canonical coverage also retained ordinary A/B/A selection, retirement cancellation, nested/caught failures, preparation-reentry rejection, and nonhandler admission gates. No new architectural root cause was identified.

## 3. Risks And Next Action

GO applies only to the bounded callback-selection implementation at the exact tuple. It does not certify activation, stronger atomicity, external registration, other resource categories, or unrelated baseline failures.

Next action: record this State acceptance for the bounded checkpoint. No further State remediation is required.

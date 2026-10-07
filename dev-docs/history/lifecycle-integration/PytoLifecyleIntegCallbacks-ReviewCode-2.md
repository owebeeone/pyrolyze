# Bounded Callback Selection, Remediation 2 — CODE-AXIS REVIEW

**Review object:** Pyrolyze `6be1b8f610c13eda18a451688377370cb1dbb087`; changed range `aa073c8df5ba1a2dc7f8697425298a02c5772f2f..6be1b8f610c13eda18a451688377370cb1dbb087`. Controlling contract: `dev-docs/PytoLifecyleIntegCallbacks.md`; remediation authority: `dev-docs/history/lifecycle-integration/PytoLifecyleIntegCallbacks-RemPlan-2.md`, both at the settled SHA. Final re-verdict pending in those documents.
**Baseline:** Pyrolyze `aa073c8df5ba1a2dc7f8697425298a02c5772f2f`. Unchanged dependencies: yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`; yidl `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`; astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`.
**Date:** 2026-10-08
**Axis:** Caller compatibility, captured completion ownership, and changed exception paths. Independent, adversarial, read-only. Nothing here relies on the other axis’s current-round report. Filed verbatim by the lane owner as `dev-docs/history/lifecycle-integration/PytoLifecyleIntegCallbacks-ReviewCode-2.md`.

**Verdict: GO** — All four prior Code findings are closed. No new actionable defect or architectural root cause identified within this bounded re-review.

---

## 0. Evidence Base

- Verified all four HEADs and statuses at start and end. The tuple remained exact; tracked trees were clean; only the two excluded Pyrolyze documents were untracked. Neither excluded document nor the other axis’s current-round report was read. Nothing was modified.
- Read the round-2 plan and contract changes using `git show 6be1b8f:…`; inspected the complete runtime/test changed range and invocation context at `src/pyrolyze/runtime/context_state_lcm/component_call_slot_context.py:120-249`.
- Inspected `_RenderAttempt.fail` at `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:106-108` to confirm exact first-error retention; did not reopen accepted manager/core-owner architecture.
- Read the new canonical `_preparation_failure` section and JSON additions. `git diff --check aa073c8 6be1b8f` passed.
- Working directory: Pyrolyze repository root (`.`). Used selectors unset, `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src`, and separate native/Python engine invocations.
- Ran `../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short tests/test_lcm_integration_characterization.py tests/test_runtime_context_state_lcm_callbacks.py`: **24 passed native; 24 passed Python**.
- Independently replayed P2-4 through `root.component_call` on both engines, on isolated roots, without invoking the canonical fixture. Also tested the accepted-A variant and clean retry.
- Replayed each original P2-1/P2-2/P2-3 counterexample independently on both engines. Confirmed their correction code, reference implementations, runtime selector, and historical callback snapshots were unchanged.

## 2. Invariant Analysis

### Prior-Finding Closure

| Prior Code Finding | Status | Independently Observed Evidence, Both Engines |
| --- | --- | --- |
| P2-1: failed owned selection published on unactivated route | **Closed** | Caught child failure followed by parent success retains A: `["A", "A"]` across original, monolithic, and decomposed routes. Dispatch remains stable and registered. Successful retry replaces it with B: `["A", "A", "B"]`. |
| P2-2: stale visitation retires retained owned handler | **Closed** | Failed omission followed immediately by child-only rerun preserves callable, registered A. Order/attempt scratch is empty. Retained-component reuse without invocation preserves A; subsequent successful parent omission retires it. |
| P2-3: equal reselection cannot cancel retirement | **Closed** | Explicit deactivate/reselect of exact A with `dirty=False` leaves accepted membership callable. Private dispatch identity remains stable. Canonical value-equal and failed-reselection cases also pass. |
| P2-4: private pre-child preparation failure escapes outer discard | **Closed** | First binding stages successfully; second callback key property throws; parent catches it. Outer completion now aborts with the exact error as cause, reports `published=False`, and allows coherent retry. New handlers do not remain accepted or callable. |

### Changed-Range Analysis

The sole runtime change captures `invocation_owner` before argument materialization at `component_call_slot_context.py:121-122`. The exception handler records the error on that captured owner before the private rollback bypass at `:185-188`. It does not obtain replacement authority in the exception path.

The independent P2-4 replay used the original stable two-argument component schema and throwing second-handler `__self__` property. With no initial handler, neither new handler survived acceptance and both retained candidate dispatches were inactive. Child executions remained one, accepted invocation identity was unchanged, and generation remained one. Retry accepted B, producing `["B"]`, two executions, and generation two.

With accepted A, the same failure preserved the exact callback, dispatch, and invocation objects. Calls before retry were `["A", "A"]`; successful retry produced `["A", "A", "B"]`. Both variants preserved exact error identity and reported reuse-ready nonpublication.

The correction adds no interface, resource admission, manager behavior, physical-current write, or membership restoration. On the unactivated route the captured owner is absent, so existing local discard and parent-catch semantics remain intact.

Previously established current-only dispatch, historical A/B/A selection, bound identity, dirty-forced exact replacement, retirement cancellation, and original field-only admission remain covered by the passing affected harness.

## 3. Risks And Next Action

This GO is limited to bounded callback selection and its reviewed completion paths. It does not certify activation, deferred resource categories, stronger atomicity, or unrelated failures. Broad suite counts remain lane-owner evidence, not independently rerun.

Next action: record Code-axis acceptance of the settled tuple and retain the existing activation and resource-category gates.

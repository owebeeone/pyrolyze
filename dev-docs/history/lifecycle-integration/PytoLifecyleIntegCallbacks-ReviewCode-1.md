# Bounded Callback Selection, Remediation 1 — CODE-AXIS REVIEW

**Review object:** Pyrolyze `aa073c8df5ba1a2dc7f8697425298a02c5772f2f`; changed range `e1cce818e3c99712d54b37976a5794a8d85cfb57..aa073c8df5ba1a2dc7f8697425298a02c5772f2f`. Controlling documents: `dev-docs/PytoLifecyleIntegCallbacks.md` and `dev-docs/history/lifecycle-integration/PytoLifecyleIntegCallbacks-RemPlan-1.md`, read at the settled SHA; implementation re-verdict pending.
**Baseline:** Prior candidate `e1cce818e3c99712d54b37976a5794a8d85cfb57`. Unchanged dependencies: yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`; yidl `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`; astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`.
**Date:** 2026-10-08
**Axis:** Interfaces, caller compatibility, completion ownership, and changed error paths. Independent, adversarial, read-only. Nothing here relies on the other axis’s current-round report. Filed verbatim by the lane owner as `dev-docs/history/lifecycle-integration/PytoLifecyleIntegCallbacks-ReviewCode-1.md`.

**Verdict: NO-GO** — All three prior Code findings are closed; one new P2 finding blocks. I pre-commit to GO on a revision that resolves P2-4 as specified.

---

## 0. Evidence Base

- Verified all four HEADs and statuses at start and end: tuple unchanged; tracked trees clean; only the two excluded Pyrolyze documents untracked. Neither excluded document nor the other axis’s current-round report was read. No filesystem or Git mutation occurred.
- Reused prior review context and read the merged remediation plan, contract changes, complete runtime/test changed range, and surrounding completion cleanup.
- Inspected `src/pyrolyze/runtime/context_state_lcm/event_handler_slot_context.py:31-108`, `callback_render.py:48-130`, `component_call_slot_context.py:120-245`, and `field_only_render.py:260-341`.
- `git diff --check e1cce818 aa073c8` passed. Reference implementations, runtime selector, and historical `callback_selection.json` have no changes.
- Working directory for every command: Pyrolyze repository root (`.`). Used the prescribed environment with selectors unset, bytecode disabled, and local source exports.
- Ran `../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short tests/test_lcm_integration_characterization.py tests/test_runtime_context_state_lcm_callbacks.py`: **24 passed native; 24 passed Python**.
- Independently replayed each original counterexample on freshly initialized roots on both engines, rather than relying on the extended combined golden.
- Reproduced P2-4 on both engines through `root.component_call`. As a controlled in-memory comparison, substituted only the prior candidate’s `rollback_owned_event_handlers` method, extracted with `git show` and AST parsing; no source files changed.

## 1. Findings

### [P2-4] Private rollback skips failures that precede child-boundary entry

**Location:** `src/pyrolyze/runtime/context_state_lcm/component_call_slot_context.py:208-209`; affected caller at `:131-185`.

**Root cause and invariant:** The new private early return assumes the outer owner already recorded the invocation failure. Argument materialization runs before `child_context._run_boundary()` establishes its attempt scope, so that assumption is false. Private failed invocation work must be discarded by the outer owner even when its exception is caught by the parent.

**Reproduction:**
1. Enable the private callback gate and accept a component with a stable two-argument schema, initially `(None, None)`.
2. In another parent pass, invoke the same component with two pending handlers. The first callback stages successfully; the second callback’s `__self__` property raises `ValueError` during key evaluation.
3. Catch that error inside the parent pass and allow normal parent exit.

**Observed impact:** The child executes only once, during initial acceptance. Nevertheless, the failed invocation’s two new handlers become registered, completion reports `published=True` and `first_failure=None`, and the first handler’s dispatch invokes its failed candidate callback. Both native and Python reproduce this. Substituting only the prior rollback method yields no new registrations and no callable leaked candidate, isolating the regression to the changed rollback path.

**Required correction:** Capture the private invocation’s original owner and record argument-materialization failures on that owner before bypassing local rollback. Preserve the unactivated local-discard adapter and private outer discard; introduce no physical-current writes or membership restoration loop.

**Closure test:** Add a separate canonical private case with successful first-handler materialization followed by a throwing second-handler key property, caught by the parent. Require outer abort, preservation of the original error, nonpublication, no new accepted handlers, unchanged accepted state/generation, and clean retry. Run on both engines.

## 2. Invariant Analysis

### Prior-Finding Closure

| Prior Code Finding | Status | Independent Counterexample Evidence, Both Engines |
| --- | --- | --- |
| P2-1: failed owned selection published on unactivated route | **Closed** | Caught child failure followed by parent success now produces `["A", "A"]` on original, monolithic, and decomposed routes. Dispatch stays stable and registered. Subsequent successful replacement produces `["A", "A", "B"]`. |
| P2-2: stale visitation retires retained owned handler | **Closed** | Isolated failed omission followed immediately by child-only `_run_boundary()` keeps A callable and registered. Visitation is restored; order and attempt-owner scratch are empty. Retained-component reuse without invocation preserves A; later successful omission retires it. |
| P2-3: equal reselection cannot cancel explicit retirement | **Closed** | Isolated deactivate/reselect using exact A with `dirty=False` now completes with registered, callable A. The private dispatch remains stable. Canonical identical/value-equal success/failure cases also pass. |

### Changed-Range Analysis

- `_discard_selection()` uses generated managed setters to mask provisional selection with accepted values; it does not manually apply physical storage. Its unactivated caller closes P2-1.
- Owned-handler participation is recorded per attempt. Only participating owners normalize omissions; coherent registry cleanup resets their scratch under existing cleanup fencing. This closes P2-2 without restoring managed membership.
- Pending retirement is a reset condition, while ordinary eligibility still compares against current. The historical A/B/A, bound-receiver identity, and dirty-forced exact replacement tests remain green.
- Callback properties, equality, and boolean conversion complete before revalidating the captured private owner. Replacement-token fault tests pass; this assessment comes from source inspection and executed tests, not another report.
- The private rollback early return creates P2-4 because pre-boundary exceptions have no enclosing child attempt to poison.
- Admission and selector remain bounded and unchanged. The accepted manager/core-owner architecture was not reopened.

## 3. Risks And Next Action

Full/default/broader results remain lane-owner evidence, not independently rerun. Activation, deferred resource categories, and stronger atomicity remain outside this verdict.

Next action: correct private pre-boundary failure recording, add the isolated regression, and submit the settled revision for focused re-verdict.

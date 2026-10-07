# Pyrolyze Callback Selection Remediation 1 — STATE-AXIS REVIEW

**Review object:** Pyrolyze `aa073c8df5ba1a2dc7f8697425298a02c5772f2f`, branch `lcm-resume`; remediation range `e1cce818e3c99712d54b37976a5794a8d85cfb57..aa073c8df5ba1a2dc7f8697425298a02c5772f2f`. Controlling contract: `dev-docs/PytoLifecyleIntegCallbacks.md`; merged plan: `dev-docs/history/lifecycle-integration/PytoLifecyleIntegCallbacks-RemPlan-1.md`, both at reviewed HEAD.
**Baseline:** Prior candidate `e1cce818e3c99712d54b37976a5794a8d85cfb57`; unchanged yidl-lifecycle `05554397d1837ecbeafa36e4685477dd5ff30fc6`, YIDL `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`, Astichi `1c47f781d3804130fdd61cbee07a3b2e4529158a`. Documents read through `git show HEAD:`, source through the changed-range diff and numbered clean tracked-file reads.
**Date:** 2026-10-08
**Axis:** STATE: publication authority, provisional membership, failure propagation, and recovery legality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — both original P2 findings are closed; one newly observed P2 blocks. I pre-commit to GO on a revision resolving P2-3 as specified.

---

## 0. Evidence base

- Verified all four HEADs and `git status --short --branch` at start and end. The tuple remained exact; tracked trees stayed clean, with only the same two excluded untracked documents. Neither was read.
- Reused the original State review context. Read the corrected contract and merged plan, not the other axis’s report. No accepted dependency implementation or architecture was reopened.
- Main source: `src/pyrolyze/runtime/context_state_lcm/callback_render.py:1-130`, `event_handler_slot_context.py:1-108`, `component_call_slot_context.py:120-245`, `field_only_render.py:80-102,263-341`, and `_support.py:372-377`.
- Read affected test changes in `tests/test_runtime_context_state_lcm_callbacks.py`, `tests/test_lcm_integration_characterization.py`, and `tests/data/lcm_integration/callback_selection.py`, `callback_owned_selection.py`, and `callback_selection_lifecycle.py`.
- Working directory for tests/probes: Pyrolyze repository root (`.`). Used the prescribed virtualenv/local-source environment, unset both context selectors, disabled bytecode, and selected each assembly backend.
- Command: `python -m pytest -p no:cacheprovider -q --tb=short tests/test_lcm_integration_characterization.py tests/test_runtime_context_state_lcm_callbacks.py`. Results: **24 passed native; 24 passed Python**.
- Independently replayed the original omission sequence, equality replacement sequence, and property replacement variant on **both backends**, as separate in-memory probes. The omission replay performed unrelated removal directly after failure, without the new canonical child-only rerun.
- Replayed retirement-prefix failure between callback/key writes and original field-only rejection on both backends. Ran the additional preparation-failure probe below on both.
- `git diff --check e1cce818 aa073c8d` passed. No files were written, broad suites rerun, builds performed, or git state mutated. Broader lane-owner counts were not independently repeated.

### Prior-Finding Closure

| Original Finding | Status | Independent Closure Evidence |
| --- | --- | --- |
| P2-1: stale failed-pass visitation authorizes unrelated removal | **Closed** | After failed omission, membership/visitation/selection were `True/True/True`; after immediate unrelated removal, membership/selection/reuse remained `True/True/True`. Callback identity survived, owned-pass scratch was cleared, and subsequent genuine omission still retired the handler. Native and Python agreed. |
| P2-2: user key evaluation contaminates replacement token | **Closed** | Equality and property variants rejected ownership loss before either selection write. Equality replay additionally committed the replacement: A remained accepted, dispatch called only A, and the original owner retained `published=None`, `reuse_ready=False`. Native and Python agreed. |

## 1. Findings

### [P2-3] Caught argument-preparation failure never poisons the private attempt

**Location:** `src/pyrolyze/runtime/context_state_lcm/component_call_slot_context.py:183-185,207-209`; owned argument materialization occurs earlier at lines 131-139.

**Root cause:** The changed private rollback branch returns immediately, relying on outer discard, but the invocation exception path does not record its failure on that owner. Argument preparation can fail before the child boundary establishes failure evidence.

**Violated invariant:** `dev-docs/PytoLifecyleIntegCallbacks.md:31-35` requires private invocation failure to discard through the outer owner. Catching that failure must not turn provisional selection into accepted success.

**Reproduction, confirmed independently on native and Python:**
1. Enable the private callback gate. Accept a component invoked as `child(context, handler, second)` with owned callback A and `second=None`; hold its dispatch.
2. In another root pass, prepare two pending owned bindings: replacement B for the accepted handler, then a new callable whose `__self__` property raises a specific `ValueError`.
3. Invoke the same component with those two bindings and catch the `ValueError` inside the parent pass.
4. B has already been staged when the second binding fails. The child never reruns, but the active owner’s `first_failure` remains `None`.
5. Parent exit completes successfully: B becomes current, held dispatch calls B, the new inactive handler is registered, generation advances by one, and `published=True` / `reuse_ready=True`.

**Impact:** Failed component preparation invents accepted callback progress rather than preserving A. This is newly observed in the changed private-failure route, not a claim that the behavior was newly introduced by this revision.

**Required correction:** Record the caught preparation/invocation exception on the original private attempt before rethrowing. Cover preparation before child execution, retain exactly one outer discard, and preserve the unactivated route’s separate parent-catch behavior. Do not add physical current writes or a membership restoration loop.

**Closure test:** A narrow fault test must stage B, fail the next binding’s key preparation, and catch that error in the parent. Outer exit must abort with the original cause; A and its dispatch must survive, the new handler must disappear, generation must remain unchanged, and coherent discard must permit reuse. Run both backends.

## 2. Invariant analysis

### Changed-Range Analysis

- Attempt-specific owned-pass tracking restricts normalization to participating owners. Coherent registry cleanup resets order/visitation under existing cleanup fencing; the exact original unrelated-removal counterexample now holds.
- Selection retains its original owner across complete user key evaluation and revalidates before writes. Both original replacement attacks fail without contamination, including deliberate replacement commit.
- Pending retirement is now a reset condition. Canonical identical/value-equal reselection success and failure passed, alongside unchanged ordinary A/B/A behavior and current-only dispatch visibility.
- Unactivated selection discard uses generated managed setters, not physical current writes. Canonical reference comparisons passed; the distinct private pre-child failure gap is P2-3.
- Retirement-prefix faults preserved both accepted handlers, propagated the identical preparation exception, certified nonpublication, and allowed clean reuse. Field-only handler rejection still poisoned caught admission failure.
- Known/candidate traversal, original owner evidence, selector, historical snapshots, dependencies, and nonhandler admission were not widened.

## 3. Risks and next action

Both original closure conditions are satisfied, but P2-3 prevents overall GO. This remains a bounded callback implementation review, not activation or stronger atomicity certification.

Next action: add the pre-child preparation fault regression, record that failure on the private owner, and rerun the permitted native/Python subset before re-verdict.

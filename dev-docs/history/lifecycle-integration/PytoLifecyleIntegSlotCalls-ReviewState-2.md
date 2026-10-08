# Bounded Slot-Call Value Migration — State-AXIS REVIEW

**Review object:** Corrected private plain-value slot-call adapter at `050ec5bdfc36b434fd0ad4b32d99de50cc5352f0`; diff from `337bdb7fdbc578f056ca6f2bfd4a20caa6391665`. Controlling DRAFT: `dev-docs/PytoLifecyleIntegInvocation.md`, Slot-Call Value Checkpoint; acceptance pending. Remediation authority: `dev-docs/history/lifecycle-integration/PytoLifecyleIntegSlotCalls-RemPlan-1.md`.
**Baseline:**
- `pyrolyze`: `050ec5bdfc36b434fd0ad4b32d99de50cc5352f0`
- `yidl-lifecycle`: `05554397d1837ecbeafa36e4685477dd5ff30fc6`
- `yidl`: `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`
- `astichi`: `1c47f781d3804130fdd61cbee07a3b2e4529158a`

Sources inspected through the bounded Git diff and clean tracked working files. HEADs and statuses were verified at start and end; the tuple did not move.
**Date:** 2026-10-08
**Axis:** State, restricted to original P2-1 closure and correction-introduced regressions. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on its current report. Filed verbatim by the lane owner.

**Verdict: GO** — P2-1 is closed; no correction-introduced findings.

---

## 0. Evidence base

- Read both applicable `AGENTS.md` files, the available read-only review-agent skill, documentation index, controlling checkpoint, and merged remediation plan.
- Inspected corrected admission in `src/pyrolyze/runtime/context_state_lcm/slot_call_render.py:29–33`, base-gate signature in `field_only_render.py:91–92`, and binding construction in `slot_call_slot_context.py:242–289`, including surrounding evaluation/write fencing at lines 93–193.
- Read regression coverage in `tests/test_runtime_context_state_lcm_slot_calls.py:34–112`; compared the private implementation with unchanged shared dispatch in `src/pyrolyze/runtime/slot_call_core.py:168–192` and `slot_call_semantics.py:400–422`.
- Ran the original three permitted pytest files with the prescribed cache-free environment: **56 passed on native**, **56 passed on Python**. No full-suite rerun.
- Independently reran the original stateful-recognition counterexample on both backends, for successful completion and parent failure. Additional native stdin probes attacked dirty calculation, recognition/comparison failure, replacement-token fencing, quarantine, and legacy dispatch.
- No files or Git state were modified. Excluded documents and the current parallel report were not read.

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| P2-1 | Retain admission’s exact approved handler and bind through it without changing shared legacy dispatch. | Original proxy switching `__class__` to `ExternalStoreRef` after eight reads rerun on native/Python, on success and parent failure: exactly eight reads, no resource callbacks, only `SlotValueBinding`. Failure preserved the original accepted record/binding and permitted clean retry. | CLOSED |

## Changed-range analysis

Admission now returns the exact validated `SlotValueHandler`. The private adapter binds through that returned instance, preserving detached binding construction and producing the existing `SlotCallCommitResult`. Unactivated evaluation still calls the unchanged shared dispatcher.

The base gate changes only its return annotation and retains rejection. Tests add both original counterexample outcomes and post-rejection retry. Documentation records the bounded disposition; archived first-round reports add historical evidence.

No shared handler/core API, ownership mechanism, runtime selector, dependency source, or canonical baseline changed. All implementation changes fit the merged disposition. **No new architectural root cause or other correction-introduced defect was identified.**

## 2. Invariant analysis

- The original bypass no longer reaches subscription binding. Successful completion publishes the proxy as a shallow plain value; parent failure discards its candidate without altering the accepted binding.
- First selection remains dirty, equal-result replacement remains clean, changed results remain dirty, and repeated candidate inputs elide. Accepted bindings remain detached from pending writes.
- Recognition and result-comparison exceptions remain sticky despite later successful work. Outer discard preserves accepted selection and supports fresh retry.
- Recognition/comparison token replacement prevents candidate writes, preserves the replacement token, and quarantines subsequent evaluation.
- Exact plain-value binding safely avoids shared replacement retirement: the handler reuses its detached prior binding or creates one when absent.
- An in-memory legacy dispatch trace confirmed four shared-dispatch calls, immediate binding reuse through parent failure, and unchanged external selection/retirement with `subscribe`, `get`, then `unsubscribe`.

## 3. Risks and next action

This closure does not widen admission or certify deferred resources, graph retirement, deep referent rollback, or default activation. The owner’s full-suite run remains separate verification; no result from it is claimed here.

Next action: record State P2-1 closure and incorporate the owner’s full-suite outcome before advancing the checkpoint.

# Bounded Slot-Call Value Migration — Code-AXIS REVIEW

**Review object:** Bounded re-verdict of Code P2-1 and correction-introduced regressions at Pyrolyze `050ec5bdfc36b434fd0ad4b32d99de50cc5352f0`, diff `337bdb7..050ec5b`. Controlling DRAFT: `dev-docs/PytoLifecyleIntegInvocation.md`, “Slot-Call Value Checkpoint,” acceptance pending; merged disposition: `dev-docs/history/lifecycle-integration/PytoLifecyleIntegSlotCalls-RemPlan-1.md`.

**Baseline:**
- `pyrolyze`: `050ec5bdfc36b434fd0ad4b32d99de50cc5352f0`; previously reviewed `337bdb7fdbc578f056ca6f2bfd4a20caa6391665`
- `yidl-lifecycle`: `05554397d1837ecbeafa36e4685477dd5ff30fc6`
- `yidl`: `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`
- `astichi`: `1c47f781d3804130fdd61cbee07a3b2e4529158a`

Tracked sources were inspected directly and through `git show`/`git diff`; comparison source was executed only in memory.

**Date:** 2026-10-08  
**Axis:** Code: original repeated-classification defect and correction-introduced regressions only. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — P2-1 is closed; zero new findings within this bounded re-review.

---

## 0. Evidence base

- Verified all four HEADs and Pyrolyze status at start and end: exact tuple unchanged, tracked diff empty, only the two excluded untracked documents present. Neither excluded document nor any current-round parallel report was read.
- Read workspace/repository `AGENTS.md`, the controlling checkpoint and merged remediation plan. The first-round authority and deferrals remain unchanged.
- Inspected correction ranges: `src/pyrolyze/runtime/context_state_lcm/field_only_render.py:10-14,88-91`, `slot_call_render.py:1-33`, `slot_call_slot_context.py:93-289`, and `tests/test_runtime_context_state_lcm_slot_calls.py:1-200`.
- Re-traced unchanged shared behavior in `src/pyrolyze/runtime/slot_call_core.py:168-196` and `slot_call_semantics.py:400-421`.
- Ran the original prescribed three-file native pytest command: **56 passed**. Ran the affected fault/characterization files with Python lowering: **29 passed**. Both used the prescribed source paths, disabled bytecode, and disabled pytest cache.
- Independently reran the **original** counter-backed `__class__` probe on both lower engines, for success and parent failure. Also ran a recognition-time replacement-token probe and compared legacy resource observations against `git show 337bdb7:` source in memory.
- No edits, builds, git mutations, or full-suite rerun. The owner’s broader verification counts are not substituted for these independent results.

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| P2-1 | Retain the admitted plain-value handler and bind through that exact object; preserve shared legacy dispatch. | Original probe returns `object` for its first eight `__class__` reads, then `ExternalStoreRef`. Native and Python, success and parent failure: exactly eight reads, no external callbacks, candidate/current binding remains `SlotValueBinding`. Success publishes the plain referent; failure preserves the original accepted binding/value. Both completion paths report reuse-ready. | Closed |

## Changed-range analysis

Admission now returns its selected exact `SlotValueHandler`. The private adapter calls that handler directly and constructs the existing `SlotCallCommitResult`; the unactivated branch still calls unchanged shared dispatch.

Detachment, invocation-record publication, public/current visibility, and ownership fences remain unchanged. Bypassing shared replacement deactivation is equivalent for the admitted path: the selected handler reuses the exact detached `SlotValueBinding`, whose resource lifecycle methods are no-ops.

Coverage adds the two stateful-recognition completion cases and clean retry after ordinary resource rejection. Documentation records the correction, remediation, and first-round evidence. Canonical targets/snapshots, facade getters, selectors, shared core/handlers, and compiler/library sources are unchanged.

No behavioral change falls outside the merged disposition. No new root-cause candidate, architectural or otherwise, survived the bounded attacks.

## 2. Invariant analysis

- The original bypass no longer reaches external binding: recognition occurs once, and its approved handler governs binding.
- Candidate binding is detached from accepted selection; parent failure preserves accepted identity and value without requiring external cleanup.
- Recognition-time transaction replacement still produces the ownership diagnostic. The replacement token remains untouched, accepted invocation/binding survives, and completion rejects reuse.
- Legacy store reuse/replacement, parent-failure behavior, effect commit/rollback/cleanup, async start/cancellation, and in-pass deactivation matched `337bdb7` event-for-event.
- Canonical and narrow tests retained elision, dirty projection, context injection, failure discard, retry, and existing token fences.

## 3. Risks and next action

This GO closes the bounded Code remediation only. It does not certify deferred resource activation, graph retirement/replacement, referent rollback, default routing, or full-suite fitness.

**Next action:** Record P2-1 as closed and incorporate this verdict into the owner’s acceptance decision after the independently required gates finish.

# Bounded Slot-Call Value Migration — Code-AXIS REVIEW

**Review object:** Pyrolyze bounded private plain-value slot-call checkpoint, `e550cd3..337bdb7fdbc578f056ca6f2bfd4a20caa6391665`; controlling DRAFT: `dev-docs/PytoLifecyleIntegInvocation.md`, “Slot-Call Value Checkpoint,” acceptance pending, 2026-10-08.

**Baseline:**
- `pyrolyze`: `337bdb7fdbc578f056ca6f2bfd4a20caa6391665`
- `yidl-lifecycle`: `05554397d1837ecbeafa36e4685477dd5ff30fc6`
- `yidl`: `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`
- `astichi`: `1c47f781d3804130fdd61cbee07a3b2e4529158a`

Sources were inspected through tracked-file reads and `git show`; compatibility baseline source was executed only in memory. The exact tuple matched at both start and end.

**Date:** 2026-10-08  
**Axis:** Code: architecture, interfaces, call graphs, and compatibility reality. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks. I pre-commit to GO on a revision that resolves P2-1 as specified.

---

## 0. Evidence base

- Read workspace/repository `AGENTS.md`, `dev-docs/README.md`, the invocation checkpoint, single-cohort authority/supersession and ownership clauses, integration-plan I3c/I4 clauses, and SC3 resource/writer audits. The named review-loop skill was absent from the supplied inventory and local skill search.
- Inspected the complete checkpoint diff, including documentation and coverage changes. No shared handler/core, compiler, library, or runtime-selector file changed.
- Primary inspection: `src/pyrolyze/runtime/context_state_lcm/slot_call_slot_context.py:1-344`, `slot_call_render.py:1-31`, `field_only_render.py:1-290`, `callback_render.py:1-130`, and `src/pyrolyze/runtime/context_bare_refactor_lcm.py:490-660`.
- Caller/support inspection: state-manager `_base.py:1-133`, `slot_context.py:1-59`, `context_base.py:260-440`, `directive_slot_context.py:1-102`, `_support.py:116-265`, `render_context.py:330-394`; runtime `slot_call_core.py:1-196`, `slot_call_semantics.py:59-149,353-471`, and `context.py:1-50`.
- Coverage inspection: `tests/test_runtime_context_state_lcm_slot_calls.py:1-145`, canonical `slot_call_values_lifecycle.py:1-175`, characterization harness `:1-114`, and compatibility tests `test_runtime_context_bare_refactor_phase1.py:1-220`.
- Ran the prescribed three-file native pytest command: **54 passed**. Ran the affected fault/characterization files with Python lowering: **27 passed**. Both used the prescribed source paths, disabled bytecode, and disabled pytest cache.
- In-memory probes reproduced P2-1 on both lower engines and tested successful publication and parent-failure discard. A separate legacy store/effect/async comparison against `e550cd3` matched subscription, reuse, replacement, rollback, delivery, cleanup, cancellation, and in-pass deactivation observations.
- No full-suite rerun, edits, builds, or git mutations. Final tracked diff was empty; status retained only the two excluded untracked documents, which were not read. No current parallel report was accessed.

## 1. Findings

### [P2-1] Binding reselects the handler after private admission

**Location:** `src/pyrolyze/runtime/context_state_lcm/slot_call_render.py:29-31`; `slot_call_slot_context.py:249-263`; downstream `src/pyrolyze/runtime/slot_call_core.py:175-177`.

**Violated invariant:** The private gate must reject external-resource selection before binding side effects. It validates one handler selection, discards that selection, then calls shared completion code that selects again. Handler recognition executes user-observable `isinstance` checks, so these selections need not agree.

**Reproduction:** Enable `_enable_slot_call_render` on a fresh root and return an object with a counter-backed `__class__` property: return `object` for its first eight reads, then `ExternalStoreRef`. Give it `identity`, `subscribe`, and `get`; have subscription/get record events. The first selection admits `SlotValueHandler`; the second chooses `ExternalStoreHandler`. No monkeypatch or shared-handler modification is required.

Observed on native and Python lowering: events `['subscribe', 'get']`, selected binding `ExternalStoreBinding`, and successful publication. With an already accepted plain value followed by parent failure, the accepted binding survives, but events still contain subscription/get without unsubscribe; completion reports `published=False` and `reuse_ready=True`.

**Impact:** The plain-value-only gate admits an explicitly forbidden resource. Failed candidate work can leave a live subscription outside the migrated completion protocol. This is runtime-initiated handler activity, not merely an arbitrary callable side effect.

**Required correction:** Bind through the exact handler approved by admission, without re-running recognition. Keep the correction bounded to the private adapter and preserve legacy selection/completion behavior; do not activate external-resource cleanup as a workaround.

**Closure test:** Add a narrow stateful-recognition regression on both lower engines, covering success and parent failure. Assert no external bind/subscription/get occurs, no external binding publishes, and accepted selection survives failure. Retain ordinary resource-rejection tests and legacy compatibility coverage.

## 2. Invariant analysis

- Canonical comparisons held for public current versus internal candidate reads, candidate-based elision, detached value bindings, repeated reselection, dirty-forced execution, context injection, failure discard, and retry.
- Existing narrow tests held for ordinary resource rejection, sticky preparation failure, and replacement-token fencing during preparation, equality, callable execution, and projection. They do not cover recognition changing between admission and binding.
- Constructor declarations retain managed invocation identity comparison on `PASS_TX_KEY`, constant configuration, runtime-local storage, and shared manager identity.
- Legacy resource observations matched the in-memory baseline. The private gate remains separate from unchanged default routing and earlier field/callback admission.

## 3. Risks and next action

These focused results do not certify deferred resource activation, graph replacement/retirement, deep referent rollback, or full-suite fitness.

**Next action:** Resolve P2-1 with single-selection private binding and its regression test, then re-review the settled tuple. No resource migration or architecture redesign is required.

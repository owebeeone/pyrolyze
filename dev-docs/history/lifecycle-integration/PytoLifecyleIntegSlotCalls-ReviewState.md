# Bounded Slot-Call Value Migration — State-AXIS REVIEW

**Review object:** Pyrolyze bounded private plain-value slot-call checkpoint, `e550cd3..337bdb7fdbc578f056ca6f2bfd4a20caa6391665`. Controlling DRAFT: `dev-docs/PytoLifecyleIntegInvocation.md`, “Slot-Call Value Checkpoint”; implementation authorized, acceptance pending.
**Baseline:**
- `pyrolyze`: `337bdb7fdbc578f056ca6f2bfd4a20caa6391665`
- `yidl-lifecycle`: `05554397d1837ecbeafa36e4685477dd5ff30fc6`
- `yidl`: `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`
- `astichi`: `1c47f781d3804130fdd61cbee07a3b2e4529158a`

Sources read from clean tracked working files, the bounded `git diff`, and `git show e550cd3:` for compatibility comparison. All four HEADs matched at review start and end.
**Date:** 2026-10-08
**Axis:** State: completion semantics, selection publication, failure recovery, admission, and token containment. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks. I pre-commit to GO on a revision that resolves P2-1 as specified.

---

## 0. Evidence base

- Read both applicable `AGENTS.md` files and the available read-only review-agent skill. The named review-loop skill was not present in the installed skill roots inspected.
- Read `dev-docs/README.md`; invocation checkpoint lines 91–134; single-cohort ownership, failure, key, and resource-gate sections; integration-plan I3c/I4 clauses; and the SC3 resource/writer audit.
- Inspected the complete bounded diff, especially `src/pyrolyze/runtime/context_state_lcm/slot_call_slot_context.py:33–344`, `slot_call_render.py:1–31`, and facade properties in `context_bare_refactor_lcm.py:525–646`. Supporting inspection covered field/callback completion, render ownership, membership/removal, and shared slot-call preparation/binding dispatch.
- Read the new fault tests and canonical fixture/baseline. Ran the three permitted pytest files with the specified cache-free environment: **54 passed on native**, **54 passed on Python**. The full suite was not rerun.
- Executed read-only stdin probes for caught equality/projection failures, replacement-token containment, quarantine, standalone and nested evaluation, independent-key permissions, admission/removal, and changing result classification. The gate-bypass finding reproduced on both backends.
- No files or Git state were modified. Excluded documents and the parallel report were not read.

## 1. Findings

### [P2-1] Admission and binding dispatch independently classify the result

**Location:** `src/pyrolyze/runtime/context_state_lcm/slot_call_slot_context.py:250–263`, specifically admission at line 251 followed by shared dispatch at line 258. Admission selects a handler in `slot_call_render.py:29–31`; `slot_call_core.py:176–177` selects again before binding.

**Violated invariant:** The private plain-value gate must reject external resource results before binding-side effects. The admitted selection must govern the subsequent bind.

**Reproduction:** Create a private root and an accepted plain-value slot. Evaluate a callable returning this object; `events` is an initially empty list and `ExternalStoreRef` is imported from the shared semantics module:

```python
class Result:
    n = 0
    identity = object()

    @property
    def __class__(self):
        self.n += 1
        return type(self) if self.n <= 8 else ExternalStoreRef

    def subscribe(self, callback):
        events.append("subscribe")
        return lambda: events.append("unsubscribe")

    def get(self):
        events.append("get")
        return 42
```

The first classification reads `__class__` eight times and selects `SlotValueHandler`. The second selects `ExternalStoreHandler`. Observed: evaluation returns `42`, calls `subscribe` and `get`, and stages an `ExternalStoreBinding`. Successful outer completion publishes that binding and reports reuse-ready. If the parent instead raises, the original plain binding survives, but no unsubscribe runs; events remain `["subscribe", "get"]` and completion still reports reuse-ready.

**Impact:** The new gate admits an explicitly deferred resource route. Failed outer completion can leave an uncleaned subscription despite otherwise successful managed-value discard. These effects come from runtime binding dispatch, not arbitrary effects performed by the user callable.

**Required correction:** Bind using the validated handler without reclassification, or construct the detached plain-value binding directly after admission. A post-bind check is insufficient because subscription effects have already occurred. Preserve shared legacy dispatch behavior.

**Closure test:** Add narrow stateful-classification coverage on native and Python assembly. Exercise both successful outer completion and parent failure; assert no external binding or resource callback occurs, and verify accepted-selection preservation and clean retry after rejection.

## 2. Invariant analysis

- Ordinary admitted values retained one-record identity/schema/argument/binding publication. Candidate elision and reselection worked; pending evaluation did not rebind the accepted binding.
- Caught argument equality, result equality, and projection failures remained sticky despite later successful evaluation. Outer completion discarded candidates, preserved the original binding, and allowed clean standalone retry.
- Replacement during preparation, argument equality, callable execution, result equality, and projection prevented candidate writes. Replacement tokens remained untouched; subsequent attempts were quarantined.
- An independently active default key did not authorize invocation-field writes and remained active across standalone completion. Nested slot-call success remained provisional through parent failure.
- Older gates still rejected slot-call admission. Failed first selection left no accepted binding or membership; omitted membership remained provisional until successful removal.
- Same-slot equality reentry also exposed a stale-elision limitation, but an in-memory execution of the `e550cd3` implementation reproduced it. It is not reported as a migration-created finding.

## 3. Risks and next action

Shallow argument/value referents, legacy immediate binding behavior, and deferred resource/retirement categories remain outside this checkpoint’s guarantees. Passing canonical tests do not establish stable admission across repeated user-observable classification.

Next action: resolve P2-1 with pre-effect binding selection and its regression test, then re-review the revised exact tuple.

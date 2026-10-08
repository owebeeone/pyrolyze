# Bounded I3c Leaf Invocation - Code-Axis Review

**Review object:** Leaf implementation diff `0828f03..b188301216486aee3b43c1ecc7b7fe89307d0273`, controlled by `dev-docs/PytoLifecyleIntegInvocation.md` at the reviewed revision. Implementation checkpoint only.

**Baseline:**

| Repository | Reviewed HEAD |
| --- | --- |
| pyrolyze | `b188301216486aee3b43c1ecc7b7fe89307d0273` |
| yidl-lifecycle | `05554397d1837ecbeafa36e4685477dd5ff30fc6` |
| yidl | `a7cc1de7b630b55bd194940ecad83f3f1738cf8a` |
| astichi | `1c47f781d3804130fdd61cbee07a3b2e4529158a` |

**Date:** 2026-10-08  
**Axis:** Code: interfaces, call paths, ownership, compatibility, and bounded-contract compliance. Independent, adversarial, read-only. No current-round peer report was accessed. Filed verbatim by the lane owner.

**Verdict: GO** - Zero P0, P1, P2, or P3 findings.

---

## 0. Evidence Base

- Verified all four owning HEADs and statuses at review start and end. Tuple and statuses were unchanged. Pyrolyze contained only the two excluded untracked documents; neither was read. Other owning worktrees were clean.
- Read repository instructions, documentation precedence, the controlling invocation document, the single-cohort ownership/failure clauses, and integration-plan I3/I3c interpreted through those amendments.
- Inspected the complete diff, historical leaf implementation, and retained reference behavior. Principal source objects: `b188301:src/pyrolyze/runtime/context_state_lcm/leaf_slot_context.py`, lines 14–107; `b188301:src/pyrolyze/runtime/context_bare_refactor_lcm.py`, lines 862–902.
- Traced constructor/attachment, inherited lifecycle declarations, argument readers, local-pass entry/exit, and outer completion. Read the new canonical fixture/baseline and all six parametrized fault cases.
- `git diff --check 0828f03 b188301216486aee3b43c1ecc7b7fe89307d0273`: passed.
- Ran the permitted pytest command against `tests/test_lcm_integration_characterization.py` and `tests/test_runtime_context_state_lcm_invocations.py`, with both runtime selectors unset, bytecode disabled, cacheprovider disabled, and the prescribed `PYTHONPATH`: **23 passed on native assembly; 23 passed on Python assembly**.
- Ran permitted stdin probes for callable keyword order and transaction replacement during sorting and later keyword expansion. No files were written; no builds or full suites were run.

## 1. Findings

No findings.

## 2. Invariant Analysis

- **Declaration and construction:** One frozen managed argument record has `init=False`, identity comparison, and `PASS_TX_KEY`. The separate local-store record serves unactivated callers. Constructor/attachment retains the graph manager; canonical observations confirm declaration and manager identity.
- **Accepted/candidate coherence:** Private facade getters read lifecycle current; internal readers expose the candidate. Canonical coverage demonstrates paired publication/discard, provisional local success, parent failure, caught child failure, and fresh retry.
- **Normalization authority:** Both entry points capture the owner before normalization and recheck open state and transaction identity before assignment. Replacement during `items()` is covered by fault tests. An additional replacement from a string-key comparison during sorting produced no callable execution, preserved accepted/candidate arguments, and left the replacement transaction untouched.
- **Compatibility:** Unactivated paths retain last-attempt arguments, including callable failures and sequential positional updates when keyword preparation fails. Probes confirmed that both entry points preserve callable keyword insertion order while storing sorted keyword pairs.
- **Execution boundaries:** Plain invocation returns the callable result without introducing a leaf-local pass. Native invocation retains its `None` return requirement. Repeated identical native calls still execute. Historical baselines remain unchanged.
- **Scope containment:** No physical-current assignment, resource-admission change, compiler/library modification, or runtime-selector change appears in the diff.

## 3. Risks And Next Action

A hostile dict subclass can replace the transaction during subsequent `**kwargs` expansion and still reach the callable before an ownership error. The identical trace was reproduced with the baseline and reviewed leaf implementations for both entry points; this is pre-existing, not a finding against this diff.

Full regression verification remains with the lane owner and was not duplicated. This verdict does not accept deferred migrations, generic recovery from external transaction interference, or default-runtime activation.

**Next action:** File this independent Code GO for the unchanged tuple and complete the lane-owner verdict merge.

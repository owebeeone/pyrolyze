# PytoLifecyleIntegPlan.md — CONSISTENCY-AXIS REVIEW

**Review object:** `pyrolyze/dev-docs/PytoLifecyleIntegPlan.md` at `7f373420d9fde14559985792125559cd4f60a3cb`; proposed integration plan, not implementation authorization.
**Baseline:**
- Workspace: `a20f8cfb633a268925464eb27728d1934a70aea9`
- Pyrolyze: `7f373420d9fde14559985792125559cd4f60a3cb`
- yidl-lifecycle: `cdf08544deea846bca4fa7e0c468ebee8d41e138`
- yidl: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`
- astichi: `387ca5e1da76204ee60922094734c13ee36383c0`

Sources were read using `git show <pinned-sha>:<path>` and pinned `git grep`, never dirty yidl working sources.
**Date:** 2026-10-03
**Axis:** Consistency against the controlling document graph, claimed existing facilities, and independently verifiable checkpoints. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks. I pre-commit to GO on a revision that resolves P2-1 as specified.

---

## 0. Evidence base

- All five HEADs were checked with `git rev-parse HEAD` at the start and end; every value matched the exact tuple. Pyrolyze and yidl-lifecycle were clean at both checks. Parent/submodule dirtiness and dirty yidl sources were excluded.
- Read the controlling plan, `pyrolyze/dev-docs/PytoLifecyleIntegPlan.md:1-632`; workspace `AGENTS.md:1-13`; and `pyrolyze/AGENTS.md:1-88`. Used the supplied canonical review prompt/template. No current-round review report was read.
- Read compatibility controls: `pyrolyze/dev-docs/ContextLifecyleMetaprogrammingPlan.md:1-824`, `LifecyleAdoptionPatterns.md:1-493`, `ApiDesignRules.md:1-83`, and `PackageStructureRules.md:1-169`.
- Examined extracted lifecycle contracts: `yidl-lifecycle/dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:1-405,581-790,949-978`, `YidlTransactionalYidlPhaseGPlan.md:1-454`, and `YidlTransactionalYidlPhaseHPlan.md:1-409`.
- Checked runtime routing and migration dependencies: `pyrolyze/src/pyrolyze/runtime/context.py:9-50`, `context_lcm.py:2729-2833`, `context_bare_refactor_lcm.py:63-195`, `context_state_lcm/context_base.py:88-193,255-477`, `render_context.py:23-182,257-410`, component/resource state managers, and `call_site_context.py:8-226`.
- Checked lifecycle implementation and coverage: `yidl-lifecycle/src/yidl_lifecycle/transaction_yidl.py:1-463`, `bindings.py:17-47`, `yidl/lifecycle_core.yidl:420-521,634-659`, `yidl/lifecycle_owned.yidl:271-287`, `lifecycle_harvester.py:434-521`, `tests/test_lifecycle_decorator.py:315-364,775-1044`, and `tests/test_transaction_yidl.py:15-199`.
- Inspected named test imports, decomposed state-manager tests, `pyrolyze/src/pyrolyze/testing/generic_backend/harness.py:11-110`, package manifests, and `yidl-lifecycle/src/yidl_lifecycle/regenerate_lifecycle_base.py:75-99`. No tests, builds, imports, regeneration, writes, or Git mutations were performed. Historical test totals were not independently rerun.

## 1. Findings

### [P2-1] The plan treats unimplemented drain-first failure handling as an existing TM guarantee

**Location:** `pyrolyze/dev-docs/PytoLifecyleIntegPlan.md:186-189`, specifically the instruction at lines 188-189 to preserve the manager’s structured errors and after-hook resilience. This supports the hook integration in I4 (`:400-410`) and failure/recovery acceptance in I6 (`:440-443`) and the canonical scenario (`:510-511`).

**Violated invariant:** A plan must distinguish an available facility from a controlling design requirement that the pinned implementation does not satisfy. Phase F-1 explicitly requires draining remaining participants and grouping failures: `yidl-lifecycle/dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:639-674,735-769`. The pinned TM instead calls after-commit hooks without per-participant exception handling (`yidl-lifecycle/src/yidl_lifecycle/transaction_yidl.py:138-142`). Rollback callbacks and after-rollback hooks are also fail-fast (`:85-103`).

**Reproduction:** Source-derived, not executed: enlist three decorated participants A, B, and C under `DEFAULT_TRANSACTION`, with equal commit-order keys and A enlisted first. Give A an after-commit hook that raises and B/C hooks that record required notifications or retirement. Commit applies all prepared values, then A’s hook raises. B/C’s hooks are never attempted; the TM nevertheless clears its active transaction and begin count in `finally` (`transaction_yidl.py:230-234`). The result is the first raw exception, not the Phase F-1 grouped failure. Existing decorator coverage tests only one throwing participant (`tests/test_lifecycle_decorator.py:865-885`), so it does not establish resilience across participants.

**Impact:** Moving domain cleanup or notifications into lifecycle hooks can silently skip later participants after publication, despite the plan presenting resilience as something merely to preserve. The analogous fail-fast rollback path can skip remaining cleanup while resetting the manager (`transaction_yidl.py:252-264`). This is a concrete recovery/diagnosability prerequisite missing from the plan, not a demand that the integration already be implemented.

**Required correction:** Record the actual fail-fast baseline in “Existing TM Limits.” Explicitly fence the missing Phase F-1 drain-first/grouped-error behavior as lifecycle-owned prerequisite work for affected slices, and require reconciliation with that controlling contract before hooks become responsible for cleanup or delivery. Keep any policy decision user-gated; do not silently substitute a Pyrolyze-wide callback engine.

**Closure/regression test:** The revised plan must name this prerequisite and its slice gate. Its future verification must include three participants with an early throwing after-commit hook, proving later hooks are attempted and published values remain committed, plus an early rollback-callback failure proving remaining cleanup is attempted and a subsequent transaction can recover. Those tests were not run during this review.

## 2. Invariant analysis

- **Routing attack failed:** The plan accurately distinguishes default monolithic `lcm` from the decomposed target (`:45-55`). The selector confirms that distinction (`pyrolyze/src/pyrolyze/runtime/context.py:13-28`). Direct-import test hazards are explicitly acknowledged (`plan:460-461,520-523,558-561`).
- **Transaction-space attack failed:** Explicit keys, class-local indexes, separate local scope activity, non-atomic multi-key completion, and lack of child savepoints are correctly distinguished (`plan:90-98,151-214`; `transaction_yidl.py:185-265,356-435`). The construction example correctly relies on the TM automatically including the default space.
- **Ownership attack failed:** The binding/owned distinction agrees with Phase H (`plan:255-286`; Phase H `:7-37,113-123`). Deterministic retirement, reference cycles, referent participation, and ownership-model mixing are expressly fenced rather than falsely delegated to garbage collection.
- **Construction attack failed:** Shared constructor injection and named factory dependencies exist (`lifecycle_core.yidl:634-647`; `tests/test_lifecycle_decorator.py:315-364`). The plan identifies manager patching and attachment factories as scaffolding to remove.
- **Scope/control attack failed:** Domain rendering remains separate from generic lifecycle mechanics. I0 gates semantic outcomes; I7 retains the original fallback; I8 updates superseded documentation. No additional defect was established from those boundaries or from the stated test commands.

## 3. Risks and next action

Graph-wide parity and historical test totals remain unverified under the permitted inspection-only commands. Boundary semantics, caught failures, resource mapping, and notification ordering remain legitimate user decisions, not findings merely because they are unresolved.

**Next action:** Revise the plan to resolve P2-1 and re-review that revision. Do not begin implementation or roll-build execution on this verdict.

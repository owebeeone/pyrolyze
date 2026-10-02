# PytoLifecyleIntegPlan.md — CONSISTENCY-AXIS REVIEW

**Review object:** `pyrolyze/dev-docs/PytoLifecyleIntegPlan.md` at `aecb23366f17123b2cb48fd6e862d79bcbc1deee`; controlling DRAFT and proposed integration plan, not implementation authorization.
**Baseline:**
- Workspace: `a20f8cfb633a268925464eb27728d1934a70aea9`
- Pyrolyze: `aecb23366f17123b2cb48fd6e862d79bcbc1deee`
- yidl-lifecycle: `cdf08544deea846bca4fa7e0c468ebee8d41e138`
- yidl: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`
- astichi: `387ca5e1da76204ee60922094734c13ee36383c0`

Sources were read from pinned commits using `git show`, plus the explicitly requested committed plan diff.
**Date:** 2026-10-03
**Axis:** Focused Consistency re-verdict on this lane’s original finding and the remediation’s changed ranges. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on its current-round re-verdict. Filed verbatim by the lane owner as `dev-docs/PytoLifecyleIntegPlan-ReviewConsistency-1.md`.

**Verdict: GO** — Consistency P2-1 is verified closed at the plan level. No blocking finding remains in this focused review; no new finding was established.

---

## Prior-finding Closure Table

| ID | Disposition Claimed | Verified on Corrected Tree | Status |
| --- | --- | --- | --- |
| P2-1 | Accepted: replace the nonexistent TM guarantee with an accurate baseline and lifecycle-owned prerequisite (`pyrolyze/dev-docs/PytoLifecyleIntegPlan-RemPlan-1.md:23`) | Original after-commit and rollback sequences retraced. The corrected plan identifies skipped work and ineffective manager reset (`:211-221`), requires multi-participant failure evidence (`:378-395`), and gates dependent integration (`:430`, `:464-465`, `:501-502`, `:694-696`). | **Closed as a plan defect.** Runtime correction remains future work. |

## Changed-range Analysis

The requested diff from `7f373420d9fde14559985792125559cd4f60a3cb` to `aecb23366f17123b2cb48fd6e862d79bcbc1deee` replaces the false existing-facility claim with an explicit distinction between the intended Phase F-1 contract and the pinned TM (`pyrolyze/dev-docs/PytoLifecyleIntegPlan.md:186-191`). The new limits accurately describe fail-fast dispatch and explain that neither manager reset nor an unchanged render repairs skipped mandatory work (`:211-221`).

L0 names the owning repository, preserves user approval, specifies failure-context preservation, and requires after-commit, rollback, after-rollback, prepare, and unexpected-apply evidence (`:364-395`). Its requirements are enforced at the resource boundary, affected slices, integration scenarios, and acceptance checklist (`:305-308`, `:430`, `:464-465`, `:501-502`, `:588-594`, `:694-696`).

The I1/I2 changes move local entry/reset/finalization safety before live nested sharing and distinguish preparatory constructor seams from a completed operational checkpoint (`:397-435`). They remain consistent with the existing separation of local scope activity from shared key activity. This assessment does not independently dispose of another lane’s findings.

**Architecture/interface classification:** The correction specifies existing prerequisites and checkpoint safety. It does not change the intended one-root-TM architecture, publication/pass split, ownership boundaries, or public interface. **No NEW ARCHITECTURAL root cause was found.**

## 0. Evidence Base

- Verified all five HEADs at the start and end with `git rev-parse HEAD`; every value matched the corrected tuple.
- Read the committed remediation plan, `pyrolyze/dev-docs/PytoLifecyleIntegPlan-RemPlan-1.md:1-63`, and the exact requested plan diff. Checked corrected plan ranges `:171-227`, `:291-308`, `:334-444`, `:462-517`, `:570-598`, and `:677-718`.
- Re-read the controlling drain-first contract in `yidl-lifecycle/dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:632-769`.
- Re-read actual dispatch and teardown in `yidl-lifecycle/src/yidl_lifecycle/transaction_yidl.py:80-142,211-264`, and the single-participant hook-failure test in `tests/test_lifecycle_decorator.py:865-885`.
- Checked the unchanged local-scope dependency in `pyrolyze/src/pyrolyze/runtime/context_state_lcm/context_base.py:255-312` and `_support.py:408-424` against the revised I1/I2 ordering.
- No dirty sources, current-round peer re-verdict, tests, builds, imports, generated outputs, edits, or Git mutations were used. Remediation statements about earlier test runs were not treated as closure evidence.

## 2. Invariant Analysis

**Original after-commit counterexample:** Enlist A, B, and C under one publication key, with equal order keys and A first. Apply publishes their prepared values; A’s after-commit hook raises. The pinned loop still skips B/C, then clears the active transaction (`transaction_yidl.py:138-142,230-234`). The runtime counterexample remains real. The corrected plan now states precisely this limitation and forbids relying on resilience before L0 verification (`plan:217-221,378-381,391-395`). Closure rests on that enforceable prerequisite, not on claiming the runtime changed.

**Original rollback counterexample:** A’s rollback callback raises before B/C cleanup. The pinned manager skips remaining cleanup and clears its transaction (`transaction_yidl.py:85-103,259-264`). The corrected plan explicitly requires independent rollback-callback and after-rollback failure cases, later cleanup attempts, token/key cleanup, preserved error context, and subsequent recovery (`plan:382-386`). It no longer treats reset as repair.

**Contract and checkpoint coherence:** L0 reconciles the existing Phase F-1 contract in the lifecycle project, while Pyrolyze retains domain-level scope and resource responsibilities. I2/I4/I6 cannot complete without its evidence. Library mechanics and application integration tests remain complementary rather than duplicated (`plan:391-395,591-594`).

## 3. Risks and Next Action

The pinned runtime still lacks the required failure-completion behavior. Its implementation and regression tests are future plan deliverables; their absence is not a reopened documentation finding. I0 approval and the remaining semantic decisions are still required (`plan:355-369,702-714`).

**Next action:** Accept this lane’s closure disposition. Execution remains gated by user authorization, I0 decisions, and the documented prerequisite checkpoints.

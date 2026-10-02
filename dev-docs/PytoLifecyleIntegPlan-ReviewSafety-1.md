# Pyrolyze YIDL Lifecycle Integration Plan — SAFETY-AXIS REVIEW

**Review object:** Proposed `pyrolyze/dev-docs/PytoLifecyleIntegPlan.md` at `aecb23366f17123b2cb48fd6e862d79bcbc1deee`; controlling DRAFT at the same revision.
**Baseline:** Workspace `a20f8cfb633a268925464eb27728d1934a70aea9`; pyrolyze `aecb23366f17123b2cb48fd6e862d79bcbc1deee`; yidl-lifecycle `cdf08544deea846bca4fa7e0c468ebee8d41e138`; yidl `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; astichi `387ca5e1da76204ee60922094734c13ee36383c0`. Sources were read through `git show <pinned-sha>:<path>`, not dirty working sources.
**Date:** 2026-10-03
**Axis:** Safety: failure containment, irreversible resource operations, recovery, and migration checkpoint integrity. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — both prior P2 findings are verified closed for the plan. Zero open P0/P1/P2 findings; no new findings in this focused re-review. This does not approve implementation, unresolved semantics, or roll-build activation.

---

## Prior-finding closure

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| P2-1 | Accept; document missing failure completion and gate dependent migration (`pyrolyze/dev-docs/PytoLifecyleIntegPlan-RemPlan-1.md:24`). | Corrected plan explicitly records fail-fast dispatch at `:211-221`; L0 requires the original three-participant after-commit sequence and independent rollback failures at `:378-395`; I2/I4/I6 depend on verification at `:430`, `:464-465`, and `:501-502`. | **Closed for plan**; runtime correction remains a future prerequisite. |
| P2-2 | Accept; move local-scope safety before live shared-TM activation (`pyrolyze/dev-docs/PytoLifecyleIntegPlan-RemPlan-1.md:25`). | Corrected plan requires local entry/reset/finalization before sharing at `:399-402`; original rerender/removal/failure sequences are I1 exit checks at `:418-424`; I2 explicitly cannot receive postponed prerequisite work at `:433-435`. | **Closed for plan**; operational verification remains an I1 deliverable. |

Plan citations in the table refer to `pyrolyze/dev-docs/PytoLifecyleIntegPlan.md` at the corrected SHA.

## Changed-range analysis

The requested original-to-corrected diff replaces the nonexistent resilience guarantee, documents the pinned limitation, adds approval-gated lifecycle checkpoint L0, and makes its evidence a dependency of coordinator and resource-hook migration. It also moves local-scope safety into I1 and strengthens corresponding acceptance checks (`pyrolyze/dev-docs/PytoLifecyleIntegPlan.md:186-221`, `:355-435`, `:464-465`, `:501-502`, `:588-594`, `:683-696`).

These corrections specify existing prerequisites and checkpoint safety. They do not change the intended root-TM/local-scope/publication-key architecture or introduce a public interface. L0 requires future runtime work to reconcile an existing intended contract with missing implementation; it does not claim that capability already exists. Approval remains explicit at `:366-369`.

**NEW ARCHITECTURAL root cause:** None identified in the changed ranges. No new finding is raised.

## 0. Evidence base

- Verified all five HEADs at start and end; every value matched the corrected tuple. No tuple movement occurred.
- Read the supplied canonical review template, committed `AGENTS.md:1-13`, and `pyrolyze/AGENTS.md:1-88`.
- Read the prior Safety report, `pyrolyze/dev-docs/PytoLifecyleIntegPlan-ReviewSafety.md:1-61`, and merged remediation plan, `pyrolyze/dev-docs/PytoLifecyleIntegPlan-RemPlan-1.md:1-63`. No other current-round re-verdict was read or requested.
- Inspected the exact requested `git diff` between `7f373420d9fde14559985792125559cd4f60a3cb` and the corrected SHA for the plan. Checked numbered corrected text covering Boundary Ownership, Existing TM Limits, Resources, I0/L0/I1/I2/I4/I6, failure fixtures, acceptance, and decision gates.
- Rechecked dispatch and teardown in `yidl-lifecycle/src/yidl_lifecycle/transaction_yidl.py:80-143` and `:211-265`, against intended drain-first behavior in `yidl-lifecycle/dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:664-674` and `:735-769`.
- Retraced nested scope behavior in `pyrolyze/src/pyrolyze/runtime/context_state_lcm/context_base.py:255-263`, `:294-347`, and `:712-741`; `_support.py:408-424`; `render_context.py:23-40`; and compiler scope construction in `pyrolyze/src/pyrolyze/compiler/kernels/v3_14/rewrite.py:528-532` and `:1870-1883`.
- No tests, builds, imports, writes, Git mutations, new threads, or delegation occurred. Counterexamples were retraced statically; future regression requirements were not treated as passing results.

## 2. Invariant analysis

**P2-1 counterexample retraced:** Order publication participants A, B, C so A’s after-commit runs first. All prepare/apply successfully; A throws. Pinned dispatch still skips B’s retirement and C’s completion, then clears the transaction (`yidl-lifecycle/src/yidl_lifecycle/transaction_yidl.py:138-142`, `:230-234`). An unchanged render need not revisit either resource. Early rollback failure likewise skips later cleanup and after-rollback before teardown (`:85-103`, `:259-264`).

The corrected plan defeats the planning defect by acknowledging precisely this failure, rejecting reset/next-render repair assumptions, and forbidding dependent migration without multi-participant evidence. L0 requires later attempts, cardinality, retained publication, failure context, owned-key/token cleanup, and recovery; the integration fixture additionally requires local-scope cleanup (`pyrolyze/dev-docs/PytoLifecyleIntegPlan.md:217-221`, `:378-395`, `:588-594`). Closure is the enforceable prerequisite, not an assertion that the pinned runtime is repaired.

**P2-2 counterexample retraced:** With only constructor sharing changed, a parent’s active pass key makes nested `pass_scope()` select `activate=False`. The handle skips nested begin/end; old UI survives the missing reset and new native emissions append. Visitation and local finalization are also bypassed (`pyrolyze/src/pyrolyze/runtime/context_state_lcm/context_base.py:255-263`, `:309-312`, `:733-740`; `_support.py:413-424`).

The corrected I1 expressly prohibits that operational checkpoint. Local entry/exit, invocation reset, visitation, candidate finalization, and completion ownership must work before sharing. Changed native emissions, child removal, failing-pass recovery, and joined-scope ownership are exit checks in the same checkpoint, not deferred to I2 (`pyrolyze/dev-docs/PytoLifecyleIntegPlan.md:399-424`, `:433-435`). The original unsafe intermediate slice therefore cannot qualify as completed I1.

Joined-boundary ownership and caught-failure outcomes remain honestly fenced, without invented savepoints or premature commits (`pyrolyze/dev-docs/PytoLifecyleIntegPlan.md:193-200`, `:704-714`). This correction does not silently choose those outcomes.

## 3. Risks and next action

The pinned runtime still exhibits the identified failure mechanisms. GO applies only to the corrected plan’s representation and dependency fences; it is not runtime certification. L0 and I1 evidence must be produced before their dependent checkpoints can pass.

**Next action:** Record the required I0/user decisions before considering execution. Implementation and roll-build activation remain separately gated.

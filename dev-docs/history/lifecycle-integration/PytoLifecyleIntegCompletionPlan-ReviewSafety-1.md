# Lifecycle Integration Completion Plan — Safety-AXIS REVIEW

**Review object:** Pyrolyze dev-docs/PytoLifecyleIntegPlan.md at b0019be76927795eceb085379c3ea4f8fde4c85c; DRAFT plan; 2026-10-03  
**Baseline:** Pyrolyze `b0019be76927795eceb085379c3ea4f8fde4c85c`; yidl-lifecycle `cdf08544deea846bca4fa7e0c468ebee8d41e138`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent `a20f8cfb633a268925464eb27728d1934a70aea9` (context only). Tracked sources were read through `git show <listed-sha>:<path>`.  
**Date:** 2026-10-03  
**Axis:** Safety: degraded paths, irreversible completion, skipped cleanup, stuck states, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero open Safety findings. Original P2-1 is closed at the document gate only. This verdict neither approves D1-D5 nor authorizes implementation or activation.

---

## Prior-finding closure table

| ID | Disposition claimed | Original counterexample verified on corrected tree | Status |
| --- | --- | --- | --- |
| P2-1 | Accept; require generated per-hook draining and separate domain per-action draining | Independently retraced notification hook → exception → skipped subscription retirement, its after-rollback counterpart, and first-failing batch entry → skipped unsubscribe. Corrected L0 requires isolation inside generated callbacks; I4/I6 require isolation inside domain batches. Manager-only evidence can no longer satisfy the exit criteria. | Closed for this plan; runtime regressions remain mandatory implementation obligations. |

## Changed-range analysis

- **Candidate-view staging:** Pyrolyze `dev-docs/PytoLifecyleIntegPlan.md:400-459,825` changes the staging guard to effective default/working reads. Published dispatch remains `.current`; write authorization and callback identity/key semantics remain unchanged.
- **Completion granularity:** `:644-702,873-879,946-962,1065-1071,1231-1233,1249` explicitly assigns generated-hook draining to L0 and domain-batch draining to I4/I6, with exactly-once attempts, contextual failures, inherited composition, and recovery proofs.
- **Outside those dispositions:** Only the review-status link at `:26-28` and archival review/package/prompt/ledger/remediation documents were added. The complete name-status diff contains no runtime, I0 evidence, dependency, or D1-D5 outcome changes.
- **NEW ARCHITECTURAL ROOT CAUSE:** None. The original Safety classification remains architectural: failure isolation was coarser than the required-work unit. Historical architectural-root-cause count remains **one**.
- The clarification identifies obligations at existing invocation boundaries under Phase F-1; it introduces no shared API, storage engine, transaction owner, or new mutation boundary. Fresh dual reviewers are not required for this bounded correction. Future implementation must still satisfy its own review gates.

## 0. Evidence base

- Verified all five HEADs at start and end using the prescribed `rev-parse HEAD` commands; all matched. Repository statuses were unchanged: yidl-lifecycle and Astichi clean; Pyrolyze contained only the two permitted untracked review prompts; YIDL’s excluded dirty cleanup remained outside authority. Neither current peer prompt nor re-verdict was opened.
- Read operator authority `review-loop/SKILL.md` and `review-loop/references/review-prompt-template.md`. Retained committed workspace/submodule `AGENTS.md` evidence from the original review.
- Inspected the exact plan diff from `723460d6c1dce75b70f03e355daf20c248bde8ad` to the reviewed revision and the complete changed-file list. Re-read corrected plan ranges identified above, plus boundary/containment/resource requirements at `:212-303,467-538,740-800` and execution gates at `:1181-1267`.
- Read Pyrolyze `dev-docs/PytoLifecyleIntegCompletionPlan-RemPlan-1.md:1-53`, archived Safety report `:1-70`, initial Consistency report `:1-70`, review package `:1-65`, and ledger `:1-65`. Prior-round inputs were not treated as closure evidence.
- Retained unchanged controlling evidence: Pyrolyze `dev-docs/ContextLifecyleMetaprogrammingPlan.md:1-824`, `dev-docs/LifecyleAdoptionPatterns.md:1-493`, `dev-docs/PytoLifecyleIntegI0Findings.md:1-205`, `dev-docs/PytoLifecyleIntegI0Inventory.md:1-234`, and `tests/data/lcm_integration/README.md:1-74`. Their preservation follows from the scoped diff.
- Re-read yidl-lifecycle `src/yidl_lifecycle/lifecycle_harvester.py:357-431`; `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:241-278,466-503,1109-1131`; `src/yidl_lifecycle/transaction_yidl.py:85-142,211-265`; and `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:632-769,950-980,1014-1057`.
- Re-read Pyrolyze’s existing fail-fast batches in `src/pyrolyze/runtime/context_state_lcm/render_context.py:257-261` and `src/pyrolyze/runtime/context_state_lcm/slot_expr_slot_context.py:98-131`.
- Ran no tests, imports, builds, regeneration, or mutations. The owner-reported four I0 tests, 4 passed in 1.58s, and documentation checks remain narrow reported evidence, not verification of future runtime fixes.

## 2. Invariant analysis

**Original generated-hook attack:** After fields publish, A’s first notification hook raises before A’s second retirement hook. Previously, draining B/C could satisfy L0 while leaving the subscription active. Corrected `:670-684` requires the generated invocation boundary to attempt the second independent hook before reporting collected failures; participant draining remains separately required. The same obligation covers after-rollback provisional cleanup and inherited/local composition. Required generated coverage at `:686-702` prevents substituting manager-only or single-hook tests.

**Original domain-batch attack:** Capturing a batch and clearing its source does not prevent its first exception from skipping unsubscribe. Corrected `:873-879,946-962` requires per-action draining owned by domain code. Scenario 14 at `:1065-1071` requires observable later cleanup, exactly-once attempts, preserved state outcomes, error context, key/scope finalization, and subsequent recovery. An incomplete throwing action remains reported; arbitrary hook internals and dependent preparation are not falsely declared repaired.

**Candidate visibility attack:** With published A, local selection B followed by A with `dirty=False` now compares against candidate B and stages A. Default getters read the working overlay; `.current` getters do not. Dispatch therefore continues to observe A before publication, without exposing B or changing publication ownership.

**Other safety boundaries:** Nested exits still cannot publish borrowed outer work; containment must preserve earlier working changes and include framework/shared/ancestor effects. Cleanup uncertainty invalidates pre-publication acceptance. Old resources cannot retire prematurely, generation preparation precedes irrevocable publication, and reentrant completion writes require an explicit gate. These retained requirements were not weakened by remediation.

## 3. Risks and next action

The pinned runtime remains fail-fast; this review closes inadequate plan obligations, not deployed behavior. D1-D5, concrete containment facilities, deterministic resource lifetime, and activation remain gated. A throwing cleanup action can remain incomplete and must be reported accurately.

**Next action:** File this Safety closure and merge the independent document-gate verdicts at the exact tuple. Any plan acceptance must remain explicitly separate from semantic approval and runtime execution.

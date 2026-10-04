# SC3-L0 Lifecycle Completion Contract — SAFETY-AXIS REVIEW

**Review object:** Corrected DRAFT `dev-docs/PytoLifecyleIntegSC3-L0Plan.md` and controlling-document pointers at `715a0074625844afae05d08afc86557d196bdecd`; merged remediation 1, dated 2026-10-04. Focused verification of the originating Safety counterexamples, not the fresh full design gate.
**Baseline:** Pyrolyze `715a0074625844afae05d08afc86557d196bdecd`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`. Change baseline: `2dc64f19542180e9c68f58073eeb484e1b9a2ed0`. Documents and dependency sources were read through pinned `git show` views.
**Date:** 2026-10-04
**Axis:** Safety: preparation-write integrity, completion evidence, cleanup, and reuse after the original counterexamples. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on its current review. Filed verbatim by the lane owner.

**Verdict: GO** — the originating Safety P2-1 is verified closed for the document gate; zero open P0/P1/P2/P3 findings in this focused review. This is neither implementation acceptance nor a substitute for fresh dual design review.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| Safety P2-1 | Replace captured-membership write permission with a manager-owned before-hook window and target preparation boundary; check existing overlays before mutation; require both original generated regressions | Re-traced A-before-B with B writing A’s untouched `y` and previously staged `x`. Lines 174-198 require A’s permission to close before field preparation and require both setters to reject before changing working storage. Lines 274-279 specify failure cleanup; lines 395-404 require the exact regression scenarios | Closed for document acceptance. Implementation and executed regression proof remain pending |

The original Safety report contained one P2 and no P3 findings. No originating finding is omitted.

## Changed-range analysis

The corrected plan adds the candidate-write boundary at lines 172-209, its rejection/cleanup trace at lines 274-279, and canonical regression obligations at lines 395-404. The ownership map now includes generated writer enforcement and effective managed-layer helpers at lines 51-60.

Other changes specify entered-phase flags, disjoint consumer predicates, exact historical supersession, and failure-attempt ordering. These correspond to the merged remediation dispositions. The integration-plan and single-cohort changes are bounded precedence pointers. The SC3 audit and Pyrolyze runtime/test bytes are unchanged.

The write-boundary correction is a material mutation-boundary change, warranting the separately required fresh review. It corrects the original root rather than introducing another architectural root. **NEW ARCHITECTURAL root causes: none identified in this focused verification.** No new blocking defect was found in the closure path; this report does not independently close the other axis’s findings.

## 0. Evidence base

- Read `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:1-444`, `dev-docs/PytoLifecyleIntegSC3-L0Plan-RemPlan-1.md:1-56`, and the originating `dev-docs/PytoLifecyleIntegSC3-L0Plan-ReviewSafety.md:1-63`.
- Checked corrected pointers in `dev-docs/PytoLifecyleIntegPlan.md:750-774` and `dev-docs/PytoLifecyleIntegSingleCohortPlan.md:38-56`.
- Re-read pinned yidl-lifecycle `src/yidl_lifecycle/yidl/lifecycle_core.yidl:419-443,466-521`; `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:241-306,388-438,460-503,1109-1130,1346-1356`; and `src/yidl_lifecycle/transaction_yidl.py:80-143,242-337`.
- Rechecked Pyrolyze `AGENTS.md` and the canonical review-loop remediation/closure requirements.
- Start/end `rev-parse HEAD` checks matched all four required revisions. Reviewed committed document diffs were unchanged. Reviewed working-document diffs, `git diff -- src tests`, and baseline-to-corrected source/test diffs were empty. Status retained only excluded process/backend-document noise.
- No writes, tests, builds, imports, git mutations, or subagents were used. No current peer/fresh report was read. Verification below is a source-and-contract retrace, not an executed test result.

## 2. Invariant analysis

**Original untouched-field counterexample:** Start with A’s `x` staged and `y` untouched, with A prepared before B. Under the old permission, B could set `A.y = 2` without re-enlisting A; application would leave that unstaged working value behind while clearing A’s working transaction ID. The corrected contract closes A’s write permission before its first field preparation. During B’s hook, the open hook window does not reopen A’s permission. The common generated write check must reject `A.y = 2` before storage mutation, even though A already has a working token. The stale-overlay sequence is therefore no longer permitted.

**Original staged-field counterexample:** Substitute `A.x = 2` in B’s hook after A has staged 1. The same target check rejects before overwriting A’s working value. The former sequence that published 1 while silently losing the later write is likewise excluded.

**Failure and recovery:** The rejection is B’s preparation failure. Lines 217-221 and 274-279 require no application, discard of both captured participants, eligible after-rollback draining, contextual error retention, and no artificial ownership-loss claim solely from the rejected write. With successful discard/actions and preserved finalized ownership, the consumer’s line-328 predicate selects unpublished clean discard and generation rollback. Incomplete cleanup instead selects quarantine. Callback return or token clearing alone cannot certify reuse.

**Supported staging and bounds:** Self-staging remains permitted before the target’s field preparation; a captured later, unprepared participant can still receive staging during the permitted hook window. Conversion, application, discard, and after callbacks cannot use that window. No automatic re-preparation or copied-field repair is introduced.

The new golden obligations explicitly cover both original variants, supported staging, existing overlays, and materializing getters. These are requirements for later execution, not evidence that the unchanged library already enforces them.

## 3. Risks and next action

The pinned implementation still lacks the proposed enforcement. Retained mutable payload aliases cannot be intercepted by property guards; the corrected text explicitly restricts those callbacks and disclaims automatic detection. Consumer compatibility, generated enforcement, cleanup draining, and clean retry still require implementation evidence.

**Next action:** Record this originating Safety document closure and complete the separately required fresh dual design gate on the same corrected tuple. No runtime implementation, resource activation, or implementation acceptance follows from this focused GO.

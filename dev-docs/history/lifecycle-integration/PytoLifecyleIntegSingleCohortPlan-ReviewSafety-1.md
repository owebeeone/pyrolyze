# PytoLifecyleIntegSingleCohortPlan — Safety-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegSingleCohortPlan.md` at Pyrolyze `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`. Focused re-verdict on the gated DRAFT DESIGN dated 2026-10-03, following the original review at `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`. Not runtime implementation acceptance.

**Baseline:**
- Pyrolyze: `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`
- yidl-lifecycle: `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`
- Parent workspace, context only: `a20f8cfb633a268925464eb27728d1934a70aea9`

Product and dependency sources were inspected through `git show <exact-sha>:<path>`, not dirty working files.

**Date:** 2026-10-03

**Axis:** Safety: attack text-authorized ownership, publication, recovery, isolation, and rollout failures. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on its current-round work. Filed verbatim by the lane owner.

**Verdict: GO** — Zero P0, P1, P2, or P3 Safety findings. No prior Safety finding needs closure. This approves only the gated draft design, not implementation feasibility, I3a completion, or activation.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| None (Safety) | Original Safety review reported no findings | Independently inspected the delta and affected gates; no prior Safety defect requires correction | No closure required |

The authorized prior-round Consistency dispositions were read as context. This report does not certify their owning-axis closure or rely on a peer closure claim.

## Changed-range analysis

The delta is a **bounded clarification of the already reviewed design**, not a new architecture, public interface, transaction API, or mutation boundary. It makes the existing completion-policy supersession and test-transition obligations more explicit.

- Lines 27 and 29 enumerate the two old clauses precisely. Render-owned publication/removal follows the selected outer owner, while all-key atomicity remains unclaimed and callback visibility, closure lifetime, cleanup, and after-commit write restrictions remain mandatory.
- Lines 221–238 clarify independently accepted non-render registration versus provisional render-driven removal. They require field/registry, entry-point, key, owner, authorization, and removal-order evidence before live routing. They do not authorize implicit key activation or a second overlay for one field.
- Lines 305–329 identify live-test transitions and pin historical reproduction to the original source revision. Expectations change with their actual routes, not beforehand. Mixed-resource observations must be separated without skipping unmigrated coverage or declaring approved differences unrelated baseline debt.

No **NEW ARCHITECTURAL root cause** was found. The delta does not invalidate the original Safety analysis or require stopping for a fresh architectural review round.

## 0. Evidence base

- Ran `pwd` and all five repositories’ `rev-parse HEAD` and `status --short` at start and end. Every HEAD matched the revised tuple; every status listing remained unchanged. Pyrolyze had only the two untracked review prompts. Neither prompt was read.
- Inspected the complete amendment diff from `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7` to `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`, and reread the revised amendment, lines 1–404.
- Read only `Round 1 Verdicts And Bounded Corrections` in `dev-docs/PytoLifecyleIntegSingleCohortPlan-ReviewPackage.md`, lines 49–64. No current-round peer prompt or report was read.
- Traced supersession against `PytoLifecyleIntegPlan.md`, lines 357–381 and 513–547. Retained the original isolated review’s inspection of controlling documents, construction, ownership, failure, generation, resource, and permission gates. Workspace/repository `AGENTS.md` remained the process authority; the canonical review-loop skill was unavailable during the original review.
- Read revised-tree tests: `test_runtime_context_state_lcm_context_base.py`, lines 1–223; `test_runtime_context_state_lcm_leaf_rerender.py`, lines 1–69; `test_lcm_integration_characterization.py`, lines 1–68; and `tests/data/lcm_integration/characterize.py`, lines 1–244.
- Rechecked pinned product evidence: `context_state_lcm/slot_context.py`, lines 1–53; `render_context.py`, lines 67–83, 171–182, and 257–261; and `runtime/call_site_context.py`, lines 146–226. Rechecked pinned yidl-lifecycle `transaction_yidl.py`, lines 211–265, 353–387, and 420–452.
- Inspected original-revision fixture README reproduction instructions, lines 54–160, and revised-tree preflight reproduction instructions, lines 220–273. These instructions were not executed.
- Ran no tests, builds, exports, writes, or git mutations. Historical green results were not treated as feature correctness evidence. Dirty lifecycle, YIDL, workspace, and unrelated submodule work remained excluded.

## 2. Invariant analysis

**Accepted registration cannot be erased by render failure.** The attacked sequence was independently accept registration, stage render-time removal, then fail the render. Lines 226–238 explicitly preserve the registration and prohibit immediate detachment masquerading as rollback-sensitive membership. Existing eager unregister operations remain migration evidence, not certified target behavior.

**Independent key completion cannot defeat removal ordering.** A render may stage removal before another permitted entry changes the accepted registry. The new audit expressly rejects assuming separate keys protect against stale removal. Authorization and ordering must be settled before live routing; two entry points cannot create two independent overlays for the same field.

**Removal deferral does not approve a lifetime redesign.** The added supersession row retains callback visibility, dispatch lifetime, supported cleanup, and the ban on managed-field writes from after-commit. SC3/D5 review still precedes changed retirement behavior; unrelated accepted removal retains its own owner.

**Fixture splitting cannot activate an unsafe mixed route.** The ledger requires splitting before changed caught-failure routing runs mixed-resource characterization. Unaffected observations remain live, and unmigrated production routes retain their expectations until SC3/I4 replace them. Lines 331–347 still prohibit half-wired owners, separate resource publication, and unclassified throwing callbacks.

**Historical evidence cannot conceal a regression.** The historical whole observation is tied to the original source and fixture revision. Original and monolithic characterization remain live. Target abort behavior belongs to the new canonical fixture, not regenerated historical JSON or the unrelated 13/14 failure debt.

**Original ownership and phase guards remain intact.** Sticky failure, borrower tracking, token identity checks, external-active-key rejection, explicit render-key completion, generation ordering, incomplete-cleanup reuse gates, and no-fictitious-undo rules were not weakened. The pinned manager still lacks a phase-aware outcome; wider callback/resource routes remain gated accordingly.

## 3. Risks and next action

Implementation must still prove registration/removal authorization and ordering, complete cleanup, resource retirement, and preservation of independent invalidations. The new audit requirement does not establish that current registries or legacy holders implement these properties. No runtime recovery or cross-key atomicity is certified.

The next action is for the lane owner to file this report and evaluate the independent dual-review acceptance gate on the revised tuple. Runtime implementation and activation require subsequent authorization and checkpoint evidence.

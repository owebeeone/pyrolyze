# SC3-L0 Lifecycle Completion Contract — SAFETY-AXIS REVIEW

**Review object:** `407592f..2dc64f19542180e9c68f58073eeb484e1b9a2ed0`; controlling `dev-docs/PytoLifecyleIntegSC3-L0Plan.md` and adjacent `dev-docs/PytoLifecyleIntegSC3.md`. DRAFT design review, not runtime acceptance.
**Baseline:** Pyrolyze `2dc64f19542180e9c68f58073eeb484e1b9a2ed0`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`. Documents and dependency sources were read through `git show` at these revisions; Pyrolyze source/test working-tree and baseline-to-HEAD diffs were empty.
**Date:** 2026-10-04
**Axis:** Safety: degraded paths, irreversible actions, recovery evidence, ownership, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks; zero P0/P1/P3 findings. I pre-commit to GO on a revision that resolves P2-1 as specified without widening the reviewed scope.

---

## 0. Evidence base

- Read workspace and Pyrolyze `AGENTS.md`, and the configured canonical `review-loop/SKILL.md`, including peer blindness, read-only review, remediation limits, and reviewer-owned closure.
- Read `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:1-305`, `dev-docs/PytoLifecyleIntegSC3.md:1-173`, and the committed `dev-docs/PytoLifecyleIntegSC3-L0Plan-ReviewLoop.md:1-45`.
- Checked controlling authority in `dev-docs/PytoLifecyleIntegPlan.md:1-39,237-389,750-809,1025-1058,1398-1432`; read `dev-docs/PytoLifecyleIntegSingleCohortPlan.md:1-416`; checked private-proof acceptance and exclusions in `dev-docs/PytoLifecyleIntegSC2-ReviewLoop.md:1-59,238-326`.
- In yidl-lifecycle, read `src/yidl_lifecycle/transaction_yidl.py:1-518`; inspected generated transaction/write boundaries in `src/yidl_lifecycle/yidl/lifecycle_core.yidl:292-353,419-527,1000-1068,1290-1319`; managed setters, staging, application, and hook composition in `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:241-306,388-438,460-503,1097-1130,1320-1368,1424-1443,1526-1541`; and owned-field preparation/application/discard in `src/yidl_lifecycle/yidl/lifecycle_owned.yidl:141-168,271-289,346-362`.
- Inspected yidl-lifecycle `tests/test_transaction_yidl.py:109-358` and regeneration entry points. Checked pinned YIDL resource compilation in `src/yidl/concept_parser.py:704-750,2390-2414` and Astichi frontend entry points in `src/astichi/frontend/api.py:1-175`.
- Traced Pyrolyze `render_attempt.py:1-360`, `field_only_render.py:1-320`, and relevant completion callers in `context_base.py`, `render_context.py`, handler/component contexts, slot-call/slot-expression contexts, `slot_call_core.py`, `slot_call_semantics.py`, and `call_site_context.py`. Inspected `tests/data/lcm_integration/transaction_failures.py:1-152`.
- At start and end, all four `rev-parse HEAD` results matched the required tuple. `git status --short` retained only excluded process/document noise. `git diff 407592f..HEAD -- dev-docs` was unchanged; both `git diff -- src tests` and `git diff 407592f..HEAD -- src tests` were empty.
- No tests, builds, imports, writes, or git mutations were performed. Counterexamples below are source-traced sequences, not execution claims. No current peer prompt/report or excluded dirty dependency source was read.

## 1. Findings

### [P2-1] Captured membership permits writes after the target participant has already been prepared

**Location:** `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:114-132`, especially line 125, combined with application readiness at lines 148-152 and the clean-publication consumer disposition at line 222.

**Violated invariant:** A successful completion must publish the supported candidate work and leave no unowned working overlay. Capturing participant identities does not freeze their field preparation. The draft expressly permits preparation hooks to stage more fields on an already captured participant without distinguishing whether that participant has already been prepared.

**Reproduction/state sequence:**
1. Use two generated participants, A and B, on one key. A has managed integer fields `x` and `y`, initially zero; B has another managed field. Give A a higher commit-order key.
2. Stage `A.x = 1` and B’s field, capturing both participants. Leave `A.y` untouched.
3. Prepare A. Its generated preparation stages `x`; `y` has no working value and receives no staged value.
4. B’s before-commit hook executes `A.y = 2`. This is permitted by line 125: A is already captured, no membership changes, and application has not started.
5. The setter succeeds without calling manager `enlist`: `lifecycle_core.yidl:436-442` enlists only when the participant’s working transaction ID is absent. A still has that ID.
6. Apply A and B normally. `lifecycle_managed.yidl:421-427` publishes and clears only fields with staged values. A’s `y` remains working value 2 while `A.current.y` remains 0; `lifecycle_core.yidl:490` nevertheless clears A’s working transaction ID.
7. Every application/after callback can return normally, ownership remains intact, and finalization succeeds. The specified evidence therefore admits the clean full-publication disposition despite stale working state.

Writing `A.x = 2` instead demonstrates the same root without adding a field: application publishes the previously staged 1 and silently discards the later write.

**Impact:** Completion evidence can certify clean publication while losing an explicitly permitted preparation write or leaving a candidate visible through the default facade after token teardown. The later owner can advance generation and admit reuse because neither application failure nor membership/ownership loss occurred. This is not confined to deferred resources; ordinary generated managed fields suffice.

**Required correction:** Replace the blanket captured-participant permission with an explicit write boundary tied to the target’s preparation state. Define and enforce when preparation writes remain legal, and reject writes that would invalidate an already-prepared target before changing its working storage. Enforcement must cover existing overlays, not merely manager `enlist`/`drop`. Preserve supported before-hook staging; do not introduce automatic re-preparation, copied-field repair, or implicit undo. Name any necessary generated writer changes within the bounded library scope.

**Closure/regression test:** For this document gate, revise the permission and enforcement contract and add this exact counterexample to the planned acceptance obligations. At implementation acceptance, extend the canonical generated failure fixture with A-before-B ordering and B writing A’s previously untouched field and previously staged field. The rejected late write must occur before application, retain contextual failure evidence, drain discard, leave current/default facades coherent, and permit a fresh transaction only after complete cleanup. Existing supported self-staging before field preparation must remain covered.

## 2. Invariant analysis

- **Publication versus cleanup:** Mutation-before-raise cannot become successful publication: application invocation marks `publication_started` first, any application failure prevents `publication_complete`, and partial outcomes prohibit automatic retry. After-action failure cannot fabricate generation rollback after full publication.
- **Identity and nesting:** Evidence belongs to the retained transaction, not the latest token for a key. Nonfinal nested completion leaves evidence absent; stale scope exits cannot replace terminal evidence or roll back a replacement. These clauses defeated the stale-token certification attack.
- **Empty and missing callbacks:** Successful empty application explicitly counts as publication-complete. Missing required application/discard callbacks are failures; missing optional callbacks remain no-ops. Neither token clearing nor vacuous after-action success independently certifies cleanup.
- **Cleanup eligibility and errors:** Failed discard blocks its dependent after-rollback action while independent participants continue. Original failures, system exceptions, and generated groups must survive aggregation. These are contractual requirements, not claims about the unchanged baseline implementation.
- **Generated versus domain draining:** The draft requires per-declaration generated after-hook draining and separately forbids claiming that it repairs an interrupted domain batch. Actual same-key helper composition was traced through `lifecycle_managed.yidl`; wrapping only a manager dispatch cannot satisfy that requirement.
- **Scope containment:** Resource admission, D5 timelines, legacy I4 replacement, registry authorization/stale-removal policy, dirty snapshots, and default routing remain separate gates. The audit does not authorize relocating existing resource methods wholesale or assigning two overlays to one field.

The successful attack is the preparation write boundary: membership stays legal and all callbacks succeed, so the draft’s uncertainty protections do not activate.

## 3. Risks and next action

Implementation acceptance must still verify BaseException propagation, grouped/repeated errors, inherited hook draining, and incomplete-cleanup quarantine. Resource adapters must establish their own partial-application cleanup and delivery dependencies; document acceptance supplies no resource-readiness proof.

**Next action:** Make one bounded draft correction for P2-1, settle the revised document tuple, and obtain original-counterexample re-verification. Do not implement or activate resource routes under this verdict.

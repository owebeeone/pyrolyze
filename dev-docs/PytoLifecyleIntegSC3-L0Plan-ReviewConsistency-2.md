# SC3-L0 Lifecycle Completion Contract — CONSISTENCY-AXIS REVIEW

**Review object:** `2dc64f19542180e9c68f58073eeb484e1b9a2ed0..715a0074625844afae05d08afc86557d196bdecd`; `dev-docs/PytoLifecyleIntegSC3-L0Plan.md` and adjacent `dev-docs/PytoLifecyleIntegSC3.md`. DRAFT design review, not runtime acceptance.
**Baseline:** Pyrolyze `715a0074625844afae05d08afc86557d196bdecd`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`. Documents and dependency sources were inspected through pinned `git show` views; Pyrolyze source/tests were read from the frozen checkout.
**Date:** 2026-10-04
**Axis:** Consistency: internal coherence, controlling-contract agreement, supersession precision, and satisfiable evidence requirements. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero open P0/P1/P2/P3 findings from this review. This verdict approves the bounded DRAFT design only.

---

## Prior-finding closure table

IDs are axis-qualified because the original reports number findings independently. Verification below is source retracing of the original counterexamples, not execution or implementation acceptance.

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| Consistency P2-1 | Replace captured-membership permission with a target-preparation write boundary | Re-traced A preparing `x=1`, then B assigning `A.x=2`. L0 lines 174–198 reject the assignment before mutation because A’s preparation permission has closed, even with an existing overlay. Lines 274–279 require unpublished discard and contextual reporting; lines 397–404 require the regression golden. | Resolved for this design review |
| Safety P2-1 | Apply the same boundary to untouched fields and existing overlays | Re-traced A preparing `x` while `y` remains untouched, then B assigning `A.y=2`. Permission is participant-bound, not staged-field-bound, so the new rule rejects this assignment before working storage changes. Both original variants are explicit golden obligations. | Resolved for this design review |
| Consistency P2-2 | Define entered/unentered flags and disjoint consumer predicates | Re-traced empty successful commit: flags are started=False, publication=True, discard=False, after=True. It selects only publication. Empty rollback and pre-application abort instead have publication=False, started=False, discard=True, after=True and select unpublished discard. Authority failures override the table. | Resolved for this design review |
| Consistency P2-3 | Name exact Phase F-1 replacements and precedence | Checked the cited historical clauses. Re-traced the corrected sequences: first preparation failure skips B preparation but discards both; failed A application still attempts B application, then discards A; failed A discard skips only A’s dependent after action. L0 lines 20–41 and controlling-plan pointers establish the replacement policies. | Resolved for this design review |
| Consistency P3-1 | Name the effective managed-layer hook resources | Followed managed matcher overrides at lines 1350–1355 through contributions 1109–1130 to helper resources 466–503. L0 lines 51–62 and 395–404 now name that path and require separate inherited/local after-call wrappers in complete-decorator output. | Resolved for this design review |

## Changed-range analysis

The product-document changes are the L0 contract and precedence pointers in `PytoLifecyleIntegPlan.md` and `PytoLifecyleIntegSingleCohortPlan.md`. The adjacent SC3 audit is unchanged. Remaining committed changes are prior-round prompts, reports, remediation mapping, and ledger records.

The material preparation-write refinement addresses the previously identified architectural root; it is not a **NEW ARCHITECTURAL root cause**. Entered-phase flags, authority-first predicates, explicit failure traces, mixed eligible-after ordering, and corrected generated ownership all implement the recorded dispositions. I found no change outside those dispositions that expands resource admission, compiler scope, field authority, or activation. No new architectural root was identified for the cap.

## 0. Evidence base

- At start and end, all four `rev-parse HEAD` results matched the baseline above. `git diff -- src tests` was empty. `git status --short` contained only the authorized process ledger/prompts and excluded backend documents; their status was unchanged.
- Inspected and rechecked `git diff 2dc64f19542180e9c68f58073eeb484e1b9a2ed0..HEAD -- dev-docs`; the final comparison was unchanged. No tests, builds, imports, writes, or git mutations were performed. No current-round peer prompt/report or originating reviewer’s in-progress closure report was read.
- Read workspace/Pyrolyze `AGENTS.md` and the configured canonical review-loop skill. Read L0 lines 1–444, SC3 audit 1–173, both original reports, RemPlan-1, and the committed L0 review ledger 1–143.
- Checked IntegrationPlan precedence 14–39, completion/key rules 237–390, L0 750–815, delivery constraints 1038–1062, test strategy 1166–1225, and D4/D5 1404–1438. Read SingleCohortPlan’s ownership, publication, migration, checkpoint, and verification sections; checked SC1 ledger 1–167 and SC2 ledger 1–80,230–326.
- In yidl-lifecycle, read `src/yidl_lifecycle/transaction_yidl.py:1–518`, `dev-docs/TransactionScopeOwnership.md:1–52`, and historical Phase F-1 lines 632–769. Verified the cited supersession ranges against their actual wording and pipeline bodies.
- Traced core active/write and preparation boundaries at `lifecycle_core.yidl:420–527`; managed writers/staging/helpers/contributions and overrides at `lifecycle_managed.yidl:241–503,1030–1140,1322–1380,1424–1443,1526–1541`; owned writers/preparation/discard at `lifecycle_owned.yidl:141–289,346–362`; and transient materializing writers at `lifecycle_transient.yidl:204–249`.
- Corroborated those paths in the pinned generated decorator and phase-F hook golden output. Read manager tests 1–359, the phase-F hook fixture 1–257, and `tests/test_yidl_goldens.py:1–114`. Checked pinned YIDL template/contribution handling and Astichi frontend entry points; no execution-based compiler-feasibility claim is made.
- Traced Pyrolyze `render_attempt.py:1–387`, `field_only_render.py:1–333`, and the audited pass, binding, handler, component-retirement, generation, subscription, effect, mount, override, and legacy call-site callers. Read the historical failure probe 1–152, characterization harness 1–72, and SC2 canonical fixture’s participant/owner scenarios. Recorded test results were not independently rerun.

## 2. Invariant analysis

- **Preparation writes:** The original staged-field and untouched-field attacks fail under the revised contract. Target permission closes before field preparation, and writer checks precede mutation/materialization rather than relying on enlistment. Before-hook self-staging and writes to captured later-unprepared participants remain permitted. Retained-alias mutation is explicitly a callback-contract restriction, not an advertised detection capability.
- **Phase evidence:** Successful empty commit cannot enter the rollback-generation branch. Incomplete discard can coexist with successful eligible-after dispatch without certifying reuse. Full publication followed by after-action failure remains publication; partial application remains uncertain.
- **Controlling precedence:** The supersession table resolves the original preparation-count and after-eligibility conflicts. It preserves continued independent application, pending-only discard, original failures, and independent generated-after draining. The integration pointers do not convert these design differences into blanket Phase F-1 implementation or D5 acceptance.
- **Ownership and compatibility:** Original-token retention, nonfinal nested returns, stale exceptional exits, explicit keys, and sequential multi-key completion remain consistent with the pinned manager and SC1 proofs. Completion evidence does not repeal the render owner’s admission and sole-ownership checks. Missing required callbacks cannot become silent success.
- **Generated composition and errors:** Effective managed helpers are now included. Per-declaration after wrappers can preserve direct references and declaration order; before-hook/conversion work remains dependent. Original/system exceptions and nested hook provenance are contractual implementation obligations, not claims that the unchanged baseline already drains them.
- **Audit versus policy:** The checked source supports the audit’s fail-fast callback observations, local delivery before outer generation completion, early subscription/replacement effects, and legacy call-site authority. The draft does not claim that manager draining repairs an interrupted domain batch or reverses those external effects.
- **Evidence and checkpoint scope:** Library mechanics, generated composition, and consumer generation observations have distinct coverage owners. Historical failure expectations must transition with the consuming checkpoint. Dirty generated artifacts, private consumer acceptance, resource adapters, D5 timing, SC4 migration, and default activation remain separately gated.

## 3. Risks and next action

Implementation remains unverified. Generated writer coverage, exception identity/grouping, ownership fencing, and inherited-hook output must still satisfy the specified runtime gates. Retained mutable aliases remain subject to callback discipline; resource cleanup and readiness require their own adapters.

**Next action:** merge the independent design verdicts and required originating-counterexample closure records at this exact tuple. Only a completed design gate permits seeking authorization for the bounded library implementation checkpoint; it does not authorize resource activation.

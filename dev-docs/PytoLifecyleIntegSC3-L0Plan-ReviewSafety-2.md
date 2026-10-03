# SC3-L0 Lifecycle Completion Contract — SAFETY-AXIS REVIEW

**Review object:** `2dc64f19542180e9c68f58073eeb484e1b9a2ed0..715a0074625844afae05d08afc86557d196bdecd`; controlling `dev-docs/PytoLifecyleIntegSC3-L0Plan.md` and adjacent `dev-docs/PytoLifecyleIntegSC3.md`. DRAFT design review, not runtime acceptance.
**Baseline:** Pyrolyze `715a0074625844afae05d08afc86557d196bdecd`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`. Object documents and dependency sources were read through pinned `git show` views.
**Date:** 2026-10-04
**Axis:** Safety: degraded paths, irreversible actions, ownership, recovery evidence, and blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero open P0/P1/P2/P3 findings in this document review. This verdict does not accept implementation, consumer adoption, or resource activation.

---

## Prior-finding closure table

IDs are axis-qualified because the original reports reuse numbering. Verification means independently retracing the original counterexample against the corrected contract and pinned source, not executing tests or supplying originating-reviewer sign-off.

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| Safety P2-1 | Enforce a before-hook window and target preparation boundary, including existing overlays | Re-traced A preparing before B, then B assigning A’s staged field and untouched field. Both writes must now fail before mutation; application remains unentered, both participants receive discard, and eligible after-rollback actions drain. Lines 174-198, 274-279 and 395-404 require enforcement and both regression scenarios. | Verified corrected for the document gate |
| Consistency P2-1 | Same write-boundary correction, with retained-alias restrictions | Re-traced the staged-value overwrite variant through the managed setter and apply resources. The target boundary prevents the permitted-write loss; lines 200-209 explicitly prohibit alias bypass without claiming detection or introducing copied-field repair. | Verified corrected for the document gate |
| Consistency P2-2 | Define unentered flags and disjoint consumer predicates | Re-traced empty commit as `(started=False, publication=True, discard=False, after=True)`; empty rollback/abort as `(False, False, True, True)`. Only commit selects publication; rollback/abort select unpublished discard. Authority checks precede classification. | Verified corrected for the document gate |
| Consistency P2-3 | Precisely supersede preparation and after-action eligibility clauses | Re-traced all three original cases: first preparation failure suppresses later preparation; failed application does not suppress later application; failed discard suppresses only its participant’s after-rollback. Lines 20-41 and 263-272 establish one policy, with controlling precedence pointers added. | Verified corrected for the document gate |
| Consistency P3-1 | Identify the effective managed-layer hook resources | Followed managed matcher overrides through helper contributions and per-key helpers. Lines 51-60 and 395-397 now require the complete decorator’s effective path and a wrapper per inherited/local after call. | Verified corrected for the document gate |

## Changed-range analysis

The object changes the L0 draft’s preparation-write boundary, phase flags, consumer predicates, effective generated-hook ownership map, failure ordering, and planned regression obligations. The two integration documents receive bounded precedence pointers. The SC3 audit and all source/test bytes are unchanged; remaining additions are process artifacts.

The material mutation-boundary refinement addresses the prior shared P2-1 root. The specified manager-owned check covers existing overlays and materializing getters before factories/thaw execute. Additional callback-order and empty-phase requirements remain within the merged dispositions. No out-of-disposition safety defect or **NEW ARCHITECTURAL root cause** was identified.

## 0. Evidence base

- Read workspace and Pyrolyze `AGENTS.md` and the configured canonical `review-loop/SKILL.md`, including read-only review, peer blindness, original-counterexample verification, and the remediation cap.
- Read committed `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:1-444`, `PytoLifecyleIntegSC3.md:1-173`, original Safety and Consistency reports, `PytoLifecyleIntegSC3-L0Plan-RemPlan-1.md:1-56`, and the committed L0 review ledger through line 143.
- Checked `dev-docs/PytoLifecyleIntegPlan.md:1-39,237-389,750-815,1405-1438`; read `PytoLifecyleIntegSingleCohortPlan.md:1-422`; checked accepted private scope in `PytoLifecyleIntegSC2-ReviewLoop.md:1-65,238-326`.
- At pinned yidl-lifecycle, read `src/yidl_lifecycle/transaction_yidl.py:1-518` and `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:630-780`.
- Traced core generated transaction/write resources at `src/yidl_lifecycle/yidl/lifecycle_core.yidl:292-355,400-560,1000-1075,1280-1330`; managed setters, staging/application, and effective hook composition at `lifecycle_managed.yidl:230-510,1090-1135,1310-1375,1420-1447,1520-1543`; owned preparation/application/discard and transient writer resources.
- Read pinned `tests/test_transaction_yidl.py:1-359` and `tests/data/gold_src/yidl_transactional_phase_f_hooks.py:1-257`. Inspected pinned YIDL resource compilation and contribution-hole discovery, plus Astichi frontend entry points; no compiler execution was performed.
- Traced Pyrolyze `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:1-387`, `field_only_render.py:1-333`, base/render completion, handler and component cleanup, slot binding completion, registry writers, `slot_call_core.py:168-192`, relevant effect/subscription/mount methods, and `call_site_context.py:170-226`.
- Read `tests/data/lcm_integration/transaction_failures.py:1-152`; treated its restaging and recorded test results as historical observations, not cleanup or acceptance proof.

Start and end checks matched all four required HEADs. `git status --short` remained limited to authorized process noise and excluded backend documents. The full `git diff 2dc64f19542180e9c68f58073eeb484e1b9a2ed0..HEAD -- dev-docs` matched the retained initial result. Working and baseline-to-HEAD source/test diffs were empty; the final working diff of the object/control documents was empty.

No tests, builds, imports, writes, or git mutations were performed. No current-round peer prompt/report, originating reviewer’s in-progress closure report, or excluded dirty dependency source was read.

## 2. Invariant analysis

- **Preparation integrity:** Both original A/B setter attacks now encounter a required check before candidate mutation. Self-staging and writes to captured later-unprepared targets remain permitted. Conversion, application, discard, and after callbacks cannot reopen permission. Alias mutation is explicitly a callback-contract violation, not a promised detectable failure.
- **Partial publication:** A callback that mutates then raises sets publication-started before invocation and prevents publication-complete. Later application attempts drain; failed applications receive pending-only discard. Neither successful cleanup nor later successful applications authorize undo, generation success, or automatic retry.
- **Cleanup eligibility:** Preparation failure discards even unprepared captured participants. Failed discard blocks its dependent after-rollback callback without suppressing independent participants. An empty eligible after dispatch may complete while discard remains incomplete; the consumer predicates still quarantine.
- **Identity and missing evidence:** Inner successful completion remains nonterminal. Records belong to the retained transaction, not the latest token for a key. Missing/incoherent evidence, ownership loss, and incomplete finalization override apparent success; stale exits cannot certify or roll back a replacement.
- **Empty and missing callbacks:** Empty commit cannot enter the rollback disposition. Missing required application/discard callbacks are failures; optional prepare/after callbacks remain no-ops. Clearing the active token alone supplies no readiness proof.
- **Hook and error draining:** Effective inherited/local after calls each require independent BaseException handling. Original preparation/body errors precede actual cleanup errors; nested groups and exception identity must survive. This does not resume statements inside a throwing hook or repair `_flush_post_commit`’s detached fail-fast batch.
- **Consumer and scope containment:** The later owner must replace both `first_failure` publication inference and the reuse-gated generation assumption. Actual early acceptance, unsubscribe, retirement, UI-writing completion, and transient-clearing paths remain adapter gates. The audit requires writer/key/entry identity constraints and does not turn an accepted registry into a disposable cache.

## 3. Risks and next action

The contract still depends on compliant custom callbacks and retained-alias discipline. Mixed legacy/generated consumers require the specified compatibility audit; unchanged pinned runtime code does not implement these protections. Implementation must prove BaseException handling, repeated/grouped errors, generated writer coverage, and inherited hook draining. Resource cleanup and D5 visibility remain separately unaccepted.

**Next action:** complete the lane’s required independent sign-offs on this exact draft tuple; only after design acceptance proceed to the bounded lifecycle-library implementation gate. Do not activate resource routes or consume completion records under this document verdict alone.

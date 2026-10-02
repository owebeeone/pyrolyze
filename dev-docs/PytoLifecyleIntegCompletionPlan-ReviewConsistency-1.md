# Lifecycle Integration Completion Plan — Consistency-AXIS REVIEW

**Review object:** Pyrolyze dev-docs/PytoLifecyleIntegPlan.md at b0019be76927795eceb085379c3ea4f8fde4c85c; DRAFT plan; 2026-10-03  
**Baseline:** Authoritative tracked bytes read through `git -C <repo> show <exact-sha>:<path>` and exact-revision diffs.
| Repository | SHA |
| --- | --- |
| Pyrolyze | `b0019be76927795eceb085379c3ea4f8fde4c85c` |
| yidl-lifecycle | `cdf08544deea846bca4fa7e0c468ebee8d41e138` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent, context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

**Date:** 2026-10-03  
**Axis:** Consistency: internal coherence, controlling-contract agreement, supersession, and satisfiability of checkpoint evidence. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on its current review. Filed verbatim by the lane owner.

**Verdict: GO** — original Consistency/P2-1 is closed for the DRAFT-document gate; no open or new Consistency findings. This accepts the plan only, not runtime execution, activation, or D1-D5 outcomes.

---

## Prior-finding closure table

| ID | Disposition claimed | Original counterexample verified on corrected tree | Status |
| --- | --- | --- | --- |
| Consistency/P2-1 | Accept: compare callback staging against the effective candidate; retain published-only dispatch and dirty/key semantics | Independently retraced published A, local B, then local A with `dirty=False`: corrected guard reads working B and assigns A. Dispatch still reads published A. I3b explicitly requires the original sequence, retained dispatch, failure coverage, and dirty-forced distinct/equal replacement. | CLOSED for this draft gate; runtime regression remains mandatory at I3b |

## Changed-range analysis

- Candidate-view correction: Pyrolyze `dev-docs/PytoLifecyleIntegPlan.md:412-419,443-454,825` changes staging-elision reads, explains the counterexample, and adds canonical evidence. It does not change dispatch visibility, field ownership, or publication lifetime.
- Draining clarification: the same document at `:670-702,873-879,946-962,1065-1071,1231-1233,1249` distinguishes manager-level participant draining, generated per-hook draining, and domain per-action draining. Commit/rollback, inherited composition, exactly-once attempts, diagnostics, and recovery are explicit obligations.
- Outside those dispositions: `:26-28` adds the review-ledger link and authorization disclaimer; seven campaign documentation files are added. No runtime source, tests, controlling adoption documents, I0 observations, or D1-D5 outcomes changed.
- **NEW ARCHITECTURAL ROOT CAUSE: none identified in this re-review.** The prior Safety classification remains one architectural root cause; this report neither reclassifies it nor closes Safety/P2-1.
- Fresh dual reviewers are **not required by these changes**: no new shared interface or ownership/mutation boundary is introduced. The correction specifies isolation at existing invocation boundaries under Phase F-1’s existing all-after-hooks contract, rather than transferring an old proof to a new architecture.

## 0. Evidence base

- Start and end: parent `git rev-parse HEAD`; each submodule’s `rev-parse HEAD` and `status --short`. Every SHA matched throughout. Pyrolyze retained only the two permitted untracked re-review prompts; yidl-lifecycle and Astichi remained clean. YIDL’s excluded dirty inventory was unchanged and was not authoritative evidence.
- Inspected the complete Pyrolyze plan diff from `723460d6c1dce75b70f03e355daf20c248bde8ad` to the reviewed revision. Overall diff: eight documentation files, 622 insertions and 12 deletions.
- Read corrected plan ranges `dev-docs/PytoLifecyleIntegPlan.md:190-244,382-470,644-708,818-842,861-886,920-980,1030-1080,1190-1267`; reread Pyrolyze `AGENTS.md:1-88`.
- Read committed `dev-docs/PytoLifecyleIntegCompletionPlan-RemPlan-1.md:1-53`, initial `ReviewConsistency.md:1-70`, initial `ReviewSafety.md:1-70`, and `ReviewLoop.md:1-65`, with filenames sharing that completion-plan prefix. Neither current peer prompt nor current peer verdict was opened.
- Retained first-round controlling-graph evidence is enumerated in the initial Consistency report at `:23-29`. Exact-revision diff returned no changes for Pyrolyze `src`, `tests`, `AGENTS.md`, `ContextLifecyleMetaprogrammingPlan.md`, `LifecyleAdoptionPatterns.md`, or the I0 findings/inventory.
- Rechecked yidl-lifecycle `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:233-303,466-475,498-503,1109-1132`; `lifecycle_harvester.py:357-431`; and `transaction_yidl.py:85-142,211-265`, with source filenames sharing `src/yidl_lifecycle/`.
- Verified the literal controlling failure-table clauses in yidl-lifecycle `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:950-980`, especially both all-after-hooks requirements at `:960-961`.
- Inspection only. No tests, imports, builds, regeneration, writes, or git mutations. Lane-owner documentation checks and four I0 passes are reported evidence, not independently rerun integration verification.

## 2. Invariant analysis

**Original counterexample:** With ordinary unequal callables A and B, published callback/key start at A. First local selection B stages B. The second selection A now reads candidate key B through the default getter, so its guard succeeds and both setters restore candidate A. Default setters compare against working state, not merely current state (`lifecycle_managed.yidl:241-262`). Outer publication therefore selects A rather than stale B.

**Visibility and replacement:** The retained dispatch still reads only `.current` (`PytoLifecyleIntegPlan.md:425-434`). Candidate comparison cannot expose B during staging. Rollback preserves published A; dirty-forced distinct-but-equal callbacks remain supported by the callback field’s identity comparison (`:402-405,451-454`). The prescribed canonical obligation retains success/failure and identity coverage (`:825`).

**Failure-isolation layers:** The pinned manager and generated hook calls remain fail-fast baseline evidence, not newly claimed capabilities. The corrected plan requires separate generated-hook and domain-action protection; it no longer credits participant draining with resuming an unwound callback. Its distinction agrees with Phase F-1 without requiring continuation of dependent preparation or arbitrary statements inside a throwing hook.

**Gates and evidence:** L0’s generated commit/rollback/inheritance proof is mandatory before dependent I2/I4/I6 completion (`:690-702`). Domain-batch failure/recovery belongs to canonical integration coverage (`:1065-1071`), complementing library mechanics rather than duplicating success tests. D4/D5 remain pending, thrown incomplete actions are reported rather than declared repaired, and checkpoint tagging cannot hide unfinished prerequisites (`:1193-1198,1241-1259`).

**Unchanged controlling graph:** The focused changes do not weaken the previously verified containment, constructor/shared-TM, local-scope, ownership, supersession, or runtime-routing obligations. Historical I0 observations remain intact; passing characterization tests still do not establish integration readiness.

## 3. Risks and next action

Generated/runtime regressions remain unimplemented obligations, not passing evidence. D1-D5, concrete containment facilities where necessary, and resource/completion timelines remain execution gates.

**Next action:** The lane owner should combine this independent Consistency GO with the independently returned Safety re-verdict and update the ledger accordingly. This report does not authorize implementation or activation.

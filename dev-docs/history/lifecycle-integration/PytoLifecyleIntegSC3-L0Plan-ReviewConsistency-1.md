# SC3-L0 Lifecycle Completion Contract — CONSISTENCY-AXIS REVIEW

**Review object:** `dev-docs/PytoLifecyleIntegSC3-L0Plan.md`, its controlling-document pointers, and `dev-docs/PytoLifecyleIntegSC3-L0Plan-RemPlan-1.md` at Pyrolyze `715a0074625844afae05d08afc86557d196bdecd`. Corrected committed DRAFT; focused remediation-1 counterexample verification, not a fresh full design gate or runtime acceptance.
**Baseline:** Pyrolyze `715a0074625844afae05d08afc86557d196bdecd`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`. Documents and dependency sources were read through `git show` at these revisions.
**Date:** 2026-10-04
**Axis:** Consistency: original counterexamples against the corrected contract, controlling-document agreement, supersession precision, and satisfiable evidence requirements. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — all three original P2 findings and the original P3 finding are reviewer-verified closed at the document level. No new blocking defect was found within this focused review. This verdict does not replace the required fresh dual design gate or accept implementation.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tree | Status |
| --- | --- | --- | --- |
| P2-1 | Before-hook window, per-target preparation boundary, generated-writer enforcement, and retained-alias restrictions | Yes. Re-traced A preparing 1 before B attempts `A.value = 2`: corrected rules reject before working mutation despite A’s existing token; application is unattempted and captured cleanup follows. Also checked untouched-field rejection and permitted self/later-target staging. | Closed: design |
| P2-2 | Entered/unentered flag semantics and disjoint consumer predicates | Yes. Re-traced empty commit, empty rollback, and pre-application abort. Empty commit uniquely selects publication/generation commit; the other two select unpublished discard/generation rollback when cleanup succeeds. Authority failures override these predicates. | Closed: design |
| P2-3 | Exact Phase F-1 replacements, controlling pointers, and explicit failure sequences | Yes. Checked cited historical clauses directly and re-traced the two-potential-prepare-failure, failed-apply, and failed-discard sequences. Each now has one controlling callback/error policy. | Closed: design |
| P3-1 | Name effective managed-layer hook resources and require complete-decorator per-call wrappers | Yes. Followed the pinned matcher overrides through helper contributions into per-key resources. The corrected ownership map and golden requirements now target that effective path. No regenerated output was claimed or inspected as a remediation result. | Closed: design |

“Verified” here means source/document re-tracing of the original counterexample, not execution of promised implementation tests.

## Changed-range analysis

The substantive patch changes the L0 draft and adds six-line precedence pointers to each of `dev-docs/PytoLifecyleIntegPlan.md` and `dev-docs/PytoLifecyleIntegSingleCohortPlan.md`. It adds the preparation-write boundary, phase defaults and outcome matrix, historical supersession table, deterministic failure traces, effective hook ownership, and corresponding future coverage obligations. These changes address the four original dispositions.

The adjacent `dev-docs/PytoLifecyleIntegSC3.md` audit and committed source/test bytes are unchanged. Additional committed changes file prior-round process artifacts and the remediation ledger; they do not grant runtime authority.

**NEW ARCHITECTURAL root causes: none found in the corrected ranges.** The materially refined mutation boundary belongs to existing P2-1, not a new root cause. Its required fresh dual review remains distinct from this originating-reviewer closure verification.

## 0. Evidence base

- At start and end, all four `rev-parse HEAD` checks matched the exact tuple above. Both working-tree `git diff -- src tests` and committed revision-range source/test diffs were empty. The complete `2dc64f19542180e9c68f58073eeb484e1b9a2ed0..715a0074625844afae05d08afc86557d196bdecd` document/source/test diff was identical at both checks.
- `git status --short` showed only the excluded process ledger/prompts and unrelated backend documents. Current peer/fresh prompts and reports were not read. No writes, tests, builds, imports, git mutations, or subagents were used.
- Read workspace/repository `AGENTS.md` and the configured canonical review-loop skill. Read the original Consistency report at `dev-docs/PytoLifecyleIntegSC3-L0Plan-ReviewConsistency.md:1–71`, corrected L0 draft `1–444`, and remediation plan `1–56`.
- Checked controlling pointers and surrounding requirements in IntegrationPlan `745–800` and SingleCohortPlan `30–55,195–225`; inspected their precise committed changes and the unchanged SC3 audit diff.
- Read pinned lifecycle sources: `src/yidl_lifecycle/transaction_yidl.py:175–385`; `yidl/lifecycle_core.yidl:420–520`; managed setters/materialization/preparation/application at `220–440`, hook resources at `458–510`, contributions at `1100–1138`, and overrides at `1340–1360`. Checked owned writer/preparation and transient materializing-getter resources.
- Read pinned `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:632–775`, verifying the supersession references against the actual historical wording and loops. Dependencies’ dirty working files were not used.

## 2. Invariant analysis

**Preparation writes:** The original bypass remains demonstrable in the pinned implementation: `_y_ensure_working_transaction` skips enlistment when the working token already exists, while application publishes staged storage and clears working storage. The corrected design no longer relies on enlistment to catch it. L0 `172–209` requires the write check before mutation or materializing factory/thaw, including existing overlays, and closes A’s target permission before field preparation. Consequently B’s attempted write becomes B’s preparation failure, followed by discard A/B and eligible after-rollback actions, with no application (`274–279`). Valid before-hook self-staging and captured later-unprepared-target staging remain permitted. Retained aliases are explicitly restricted without promising interception.

**Completion classification:** L0 `127–133` makes empty commit’s flags `(publication_started=False, publication_complete=True, discard_complete=False, after_actions_complete=True)`. Empty rollback and clean pre-application abort instead have `(False, False, True, True)`. After the authority/finalization check, predicates at `324–330` are disjoint: publication-complete cases cannot enter either unpublished branch. The matrix and future consumer coverage preserve SingleCohortPlan `206–210` generation decisions without `first_failure` inference.

**Supersession and failure ordering:** L0 `20–41`, IntegrationPlan `757–761`, and SingleCohortPlan `46–50` establish bounded design precedence. Re-tracing L0 `270–272` yields: preparation A fails, B preparation is unattempted, discard A/B and after-rollback A/B run, retaining only actual `E_A`; application A fails, application B still runs, then discard A, after-rollback A, after-commit B; explicit discard A fails, discard B and after-rollback B run, but A’s after action is ineligible. These sequences agree with the replacements, preserve incomplete-cleanup evidence, and do not imply D5 approval or current-value undo.

**Generated ownership:** Pinned managed matchers `1350–1355` select contributions `1109–1131`, which emit `TransactionHookHelperCall` into the per-key after helpers. L0 `51–62,395–404` now names this path and requires one wrapper per effective inherited/local call. The original core-only ownership error is removed; generated draining remains an implementation obligation.

## 3. Risks and next action

The pinned runtime has not received these corrections. Generated-writer enforcement, per-hook wrappers, consumer generation behavior, artifact isolation, and historical-test transition still require implementation and regression evidence. Alias restrictions remain contractual, not an interception guarantee.

**Next action:** complete the already-required fresh peer-blind dual design gate on this settled tuple before implementation. This report closes the originating Consistency findings only; resource admission, D5 timing, consumer adoption, and activation remain gated.

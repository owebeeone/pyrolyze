# SC3-L0 Lifecycle Completion Contract — CONSISTENCY-AXIS REVIEW

**Review object:** `407592f..2dc64f19542180e9c68f58073eeb484e1b9a2ed0`; `dev-docs/PytoLifecyleIntegSC3-L0Plan.md` and adjacent `dev-docs/PytoLifecyleIntegSC3.md`. DRAFT design review, not runtime acceptance.
**Baseline:** Pyrolyze `2dc64f19542180e9c68f58073eeb484e1b9a2ed0`; yidl-lifecycle `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`. Reviewed documents and dependency sources were read through `git show` at these revisions.
**Date:** 2026-10-04
**Axis:** Consistency: internal coherence, controlling-contract agreement, supersession precision, and satisfiable evidence requirements. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — three P2 findings block; one additional P3 finding. I pre-commit to GO on a revision that resolves P2-1, P2-2, and P2-3 as specified.

---

## 0. Evidence base

- At both start and end, all four `rev-parse HEAD` checks matched the exact baseline above. `git diff -- src tests` was empty. `git status --short` showed only the excluded process ledger/prompts and unrelated backend documents; those prompts and backend documents were not read.
- `git diff 407592f..HEAD -- dev-docs` was inspected and rechecked. It contains the L0 draft, SC3 audit, committed L0 review ledger, and integration-plan status pointer. No tests, builds, source imports, writes, or git mutations were performed.
- Read Pyrolyze workspace/repository `AGENTS.md`, the configured canonical review-loop skill, L0 draft lines 1–305, SC3 audit lines 1–173, committed L0 ledger lines 1–45, SingleCohortPlan lines 1–416, SC2 acceptance ledger lines 1–326, and SC1 ownership acceptance sections. IntegrationPlan inspection covered precedence, completion semantics, L0 lines 750–809, migration gates, test strategy, and D4/D5 lines 1398–1424.
- In yidl-lifecycle, read `src/yidl_lifecycle/transaction_yidl.py:1–518`; relevant core YIDL declarations/dispatch; managed YIDL setters, preparation/application, hook helpers and matcher overrides; owned preparation/discard resources; `dev-docs/TransactionScopeOwnership.md:1–52`; and `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:632–769`.
- Checked the library protocol tests, golden harness, and `tests/data/gold_src/yidl_transactional_phase_f_hooks.py:1–257`. Inspected pinned YIDL contribution targeting and Astichi statement-suite materialization; no compiler modification was demonstrated necessary.
- Traced Pyrolyze `render_attempt.py:1–340`, `field_only_render.py:1–280`, base/render completion callers, component retirement, handler/binding transfer callers, external-store/effect/async/mount operations, and legacy call-site acceptance. Read the historical failure probe and characterization harness. The recorded 127-test result and ephemeral probes were not independently rerun.

## 1. Findings

### [P2-1] Captured membership does not make late preparation writes safe

**Location and invariant:** `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:114–132,148–152` permits preparation hooks to stage additional fields of any captured participant while retaining a fixed, once-only preparation/application order. Permitted candidate writes must not disappear during successful completion.

**Reproduction and impact:** Capture generated participants A and B, ordered A before B. Stage `A.value = 1`. A prepares its staged value as 1; B’s before-commit hook then assigns `A.value = 2`. A remains captured, its working token remains set, and the generated setter does not re-enlist it, so the proposed membership guards do not reject this write. A subsequently applies staged 1 and clears working 2. This follows pinned `lifecycle_core.yidl:436–443,466–491` and `lifecycle_managed.yidl:249–262,388–427`. Every callback can return normally, producing complete publication evidence despite silently dropping an explicitly permitted write.

**Required correction and closure:** Define a preparation-write boundary, not merely a membership boundary. Restrict hook writes to a clearly identified safe preparation window and reject changes to already-prepared participants before mutation; specify restrictions on retained mutable working aliases. Extend the generated golden with this A/B sequence, proving contextual rejection and complete discard rather than successful publication of stale staged data. Preserve permitted own-participant preparation writes.

### [P2-2] Skipped-phase flag semantics leave empty completion dispositions ambiguous

**Location and invariant:** `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:83–86,218–224`. Terminal records must select one consumer disposition without reconstructing a phase from exceptions or callback counts.

**Reproduction and impact:** Begin and successfully commit a key with no dirty participants. The specified facts are `publication_started=False` and `publication_complete=True`. The draft does not define `discard_complete` when discard is unentered; its empty-phase wording permits treating the empty discard obligation as complete. With successful after actions and preserved ownership, the record then matches both “No application, successful discard” and “Full publication.” Their generation decisions are opposite. This conflicts with SingleCohortPlan `200–204`, where a clean attempt completes the key and commits generation. A consumer branching first on `publication_started` can roll back a successful empty attempt.

**Required correction and closure:** Specify flags for unentered phases and give disjoint boolean predicates for the disposition table. Successful empty commit must follow `publication_complete`, while the unpublished-discard branch must exclude it; ownership/finalization failures must override success. Add an outcome matrix for empty commit, empty rollback, and pre-application abort, with corresponding consumer generation assertions. Do not repair this by retaining `first_failure` inference.

### [P2-3] Phase F-1 policy changes lack an explicit supersession boundary

**Location and invariant:** `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:9–12,140–144,154–173`. IntegrationPlan `750–755` describes L0 as reconciliation of the existing Phase F-1 manager contract; SingleCohortPlan `38–44` leaves that generic proposal separate. A specialization must identify controlling clauses it replaces.

**Reproduction and impact:** The pinned library’s `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:666–667` says verbatim: “prepare failures prevent current-value mutation, but every participant still gets a prepare attempt so the manager can report all broken participants.” Its preparation loop at `691–704` implements that policy. The new draft stops subsequent preparation. Likewise, Phase F-1 `712–716,745–754` dispatches after callbacks across the phase’s participant sequence, whereas the draft restricts them to successful application/discard participants. For A and B with independent preparation failures, the two documents require different attempt counts and failure records. The current diff only updates the integration-plan status pointer; it provides no precise reconciliation.

**Required correction and closure:** Add an exact supersession table identifying these Phase F-1 clauses and their replacement preparation and after-hook eligibility policies. State that design acceptance approves these bounded D4 differences, not blanket Phase F-1 implementation acceptance or D5 approval. Closure requires tracing the two-preparation-failure, failed-apply, and failed-discard examples through the revised controlling graph and recording one expected callback/error sequence for each.

### [P3-1] The generated-hook ownership map names the wrong active layer

**Location and invariant:** `dev-docs/PytoLifecyleIntegSC3-L0Plan.md:27–29` locates generated independent-hook dispatch in `src/yidl_lifecycle/yidl/lifecycle_core.yidl`. The implementation ownership map must identify the resources used by the complete decorator.

**Reproduction and impact:** The complete generated path overrides the core hook matchers in `lifecycle_managed.yidl:1350–1355`. Calls are emitted by `TransactionHookHelperCall` at `498–503`, through contributions at `1109–1130`, into helpers at `466–475`. Editing only the named core hook resource leaves these calls unwrapped and the first throwing hook still skips the second. The error can misdirect the bounded patch or produce a false compiler-limitation diagnosis.

**Required correction and closure:** Name the managed-layer helper resources/contributions alongside any relevant core changes. Verify that the planned inherited/local failure golden exercises the complete decorator and that regenerated output contains a separate wrapper for each effective hook call.

## 2. Invariant analysis

The token-binding attack failed: the draft retains the original transaction object, leaves inner successful commits nonterminal, preserves terminal evidence across stale exits, and does not authorize rollback of a replacement. These rules agree with the pinned scope fences and accepted SC1 ownership contract.

The audit’s fail-fast observations agree with the manager source: application and after-hook loops can stop early, while finalization clears ownership. Its warning that teardown is not publication/discard proof is justified.

The authority-expansion attack failed: document GO is explicitly separate from library implementation acceptance, private consumer acceptance, resource admission, I3a completion, and default activation. D5 timing, legacy I4 authority, registration/removal authorization, resource lifetime, and dirty/metadata policies remain gated.

Golden ownership and historical transition are coherent: generic manager mechanics belong to library tests; generated composition belongs to library goldens; Pyrolyze generation behavior belongs to its canonical fixture. The historical failure expectation must transition with consumption of the new library tuple, not be hidden as unrelated debt.

Manager draining is not represented as repairing statements inside one throwing domain function. The explicit `_flush_post_commit` deferral agrees with its actual detached, fail-fast loop. These failed attacks do not close the preparation-write, outcome-classification, or supersession findings.

## 3. Risks and next action

These are design findings, not evidence of newly active runtime corruption. P2-1 concerns the preparation mutation boundary; P2-2/P2-3 concern outcome and authority precision; P3-1 is a localized ownership-map correction. Deferred resource ordering and lifetime decisions are not additional findings.

**Next action:** produce one merged document remediation at a new settled tuple and obtain reviewer verification of these original counterexamples before accepting the design. Keep implementation and resource activation blocked. The four reviewed HEADs and source/test isolation remained unchanged through the end check.

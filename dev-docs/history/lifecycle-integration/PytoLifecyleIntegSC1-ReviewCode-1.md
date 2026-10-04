# SC1 Remediation Round 1 — CODE-AXIS REVIEW

**Review object:** Private unwired render owner plus bounded manager prerequisite. Pyrolyze `1fe5f6b..7a5d16cb5f6fea9a4d9640e6d443b7e5165a4ead`; yidl-lifecycle `1439d2fd..335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`. Controlling document: `dev-docs/PytoLifecyleIntegSC1-Remediation.md` at the reviewed Pyrolyze HEAD, implemented and pending fresh dual acceptance.
**Baseline:**

| Repository | Reviewed HEAD |
| --- | --- |
| Pyrolyze | `7a5d16cb5f6fea9a4d9640e6d443b7e5165a4ead` |
| yidl-lifecycle | `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent, context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

Lifecycle base: `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`. Original SC1 object: Pyrolyze `84d4ab6116e0a743394a6269f09e026607402d80`. Documents/diffs were read through committed Git views; dependency execution used supplied committed exports, never dirty dependency source.
**Date:** 2026-10-04
**Axis:** Code: architecture, interfaces, ownership, call graphs, compatibility, and failure contracts. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero new P0, P1, P2, or P3 findings. Original Code P2-1, P2-2, and P2-3 are closed by independent counterexample verification. This verdict covers private mechanics and the bounded manager prerequisite only.

---

## Prior-finding closure table

| ID | Disposition claimed | Verified on corrected tuple | Status |
| --- | --- | --- | --- |
| Code P2-1 | Certify ownership on exceptional validation; preserve failure and replacements; block reuse | Independently reran validator commit/discard/replace followed by the original failure. Current value remained respectively `9/1/1`; original error remained observable; uncertainty was true; reuse and `next_attempt()` were rejected. Replacement and other-key identities survived. | Closed |
| Code P2-2 | Nonpublishing sole-owner observation plus stale-scope fencing | Independently poisoned A after retaining an external same-token begin. A discarded candidate `9`, refused reuse, and rejected B through `next_attempt()`. A separately opened replacement with candidate `10` remained unpublished and active after the old normal exit raised; the old exceptional exit returned `False` without touching it. | Closed |
| Code P2-3 | Guard local terminal transitions and account for release failures | Independently reran recursive finish, recursive abort, and finish-during-abort. Exit/abort callbacks ran once; catching the recursive finish error could not publish `9`. Abort retained the primary cause and blocked reuse on cleanup failure. Injected release-bookkeeping failures were also retained and blocked publication/reuse. | Closed |

## Changed-range analysis

- Pyrolyze changes are confined to ownership checks and completion bookkeeping in `render_attempt.py`, its mechanics tests, and controlling/review documentation. Important corrected ranges are `94–117`, `173–266`, and `315–370`. The owner now checks sole ownership before completion and failed discard, including exceptional validation.
- Lifecycle changes are exactly the committed manager source/test and ownership document. `transaction_yidl.py:186–230` binds exits to original identities; `242–307` guards terminal completion and fences normal commit after validation; `340–363` retains every multi-key token; `432–442` preflights multi-key begin barriers.
- The amended plan explicitly supersedes the no-library-change assumption. No live context wiring, selector/default change, generated-source migration, or golden rewrite appears in these ranges.
- **New architectural root causes: none identified.** The changed shared-manager call graph was attacked afresh; closure was not inherited from prior tests or reports.

## 0. Evidence base

- Read parent/Pyrolyze/lifecycle `AGENTS.md`, the supplied standing rules, review-loop skill, and canonical reviewer template.
- Read the remediation document `1–94`, remediation plan, amended Single Cohort Plan, historical SC1 document, original Code/State reports, and committed review-ledger amendments. Read lifecycle `TransactionScopeOwnership.md` in full.
- Read Pyrolyze `render_attempt.py:1–387`, owner tests `1–770`, `lifecycle_adapter.py:1–33`, and existing `context_base.py:170–310` for call-site context. Read committed lifecycle `transaction_yidl.py:1–518`, manager tests `1–359`, core dispatch/facade templates `405–605`, and managed preparation/application/discard templates `372–488`.
- Ran the authorized owner pytest target with both selectors unset, bytecode disabled, pinned-export `PYTHONPATH`, and `-p no:cacheprovider -q --tb=short`: **35 passed in 2.45s**. Ran the authorized manager target from the committed lifecycle export with the same write-suppression flags: **18 passed in 0.03s**.
- Ran independent in-memory probes using the real manager, generated `RenderValues`, and existing protocol fixtures. Beyond the original counterexamples, these covered five balanced nesting configurations, six validator identity-mutation cases, five terminal phases with six reentry attempts each, callback mutation of a later multi-key token, stale/valid token mixtures, caught local reentry, release faults, validation-time borrowing, clean-discard retry, and retained legacy participant signatures. All assertions passed.
- Source searches found no production caller of `_RenderAttempt` outside its own module and no private manager-field access in the owner or its tests.
- Provided main-session evidence, not independently rerun: focused **64 passed**; full Pyrolyze **854 passed/13 failed/20 skipped**; broader decomposed **41 passed/14 failed**; lifecycle **273 passed/1 failed/46 skipped**. The supplied evidence reproduces the lifecycle owned-field golden failure at the old lifecycle SHA with identical dependencies. No full-suite green claim or failure waiver is made.
- Verified all five HEADs at start and end: unchanged. Product source remained unchanged. End status showed a new tracked edit to `dev-docs/PytoLifecyleIntegSC1-ReviewLoop.md`; its dirty contents were not opened or used. Excluded dirty dependency statuses remained unchanged. No current-round peer prompt/report was read; this reviewer wrote no files, caches, or Git state.

## 2. Invariant analysis

- **Exact identity, not integer/key equivalence:** Stale exits could not commit or discard replacements. Normal and exceptional validator mutation paths preserved replacement identities; original validation failures remained observable.
- **Nonpublishing ownership observation:** Outstanding same-token borrowing was detected before failed discard certification. Ordinary sole-owner validation failure still discarded completely and admitted a fresh successful attempt publishing `11`.
- **Nested compatibility and independent keys:** Balanced single-key, multi-key, overlapping, default/all-key, and deduplicated nesting preserved provisional inner success. Other-key tokens survived render failures and completion-barrier attacks. Multi-key exits continued attempting valid original tokens when another token was stale.
- **Terminal barriers and callback mutation:** Prepare/apply/after/rollback/after-rollback reentry rejected same-key begin, commit, commit-only, rollback, ownership certification, and mixed-key begin. Rejected multi-key begin did not increment the independent key’s count; balanced other-key operations remained available.
- **Local one-shot completion and recovery:** Recursive or competing terminal calls remained sticky even when caught. Release errors entered cleanup accounting. Opaque prepare/apply/after failures retained uncertainty and blocked reuse without fabricated undo. Legacy callback argument order remained compatible.

## 3. Risks and next action

The ownership check is a synchronous observation, not a lock or lease. This review establishes neither parallel-render safety nor generic participant-mutation safety, cross-key atomicity, resource/registration completion, generation coordination, field migration, or default activation. Existing suite failures remain visible and outside this bounded verdict.

**Next action:** Merge this Code GO with the independent State verdict. Only a dual GO at this exact tuple accepts the private mechanics and bounded manager prerequisite; SC2 live wiring remains a subsequent gated checkpoint.

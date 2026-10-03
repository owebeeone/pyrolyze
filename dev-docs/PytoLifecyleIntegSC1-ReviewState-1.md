# PytoLifecyleIntegSC1 Remediation Round 1 — STATE-AXIS REVIEW

**Review object:** Private, unwired render owner plus bounded manager prerequisite. Pyrolyze `1fe5f6b..7a5d16cb5f6fea9a4d9640e6d443b7e5165a4ead`; lifecycle `1439d2fd..335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`. Controlling DRAFT: Pyrolyze Git object `7a5d16cb:dev-docs/PytoLifecyleIntegSC1-Remediation.md`, implemented and pending acceptance, dated 2026-10-04.

**Baseline:**

| Repository | Exact HEAD |
| --- | --- |
| Pyrolyze | `7a5d16cb5f6fea9a4d9640e6d443b7e5165a4ead` |
| yidl-lifecycle | `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent, context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

Inspection used committed `git show HEAD:<path>` views and supplied committed dependency exports, never dirty dependency source. Original SC1 was Pyrolyze `84d4ab6116e0a743394a6269f09e026607402d80`, with lifecycle base `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`.

**Date:** 2026-10-04  
**Axis:** State: ownership, exceptional transitions, synchronous reentrancy, cleanup, recovery legality, and fail-closed publication/reuse. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — zero P0, P1, P2, or P3 findings. Both original State findings and the shared manager prerequisite counterexample are verified closed for this scope.

---

## Prior-finding closure table

| Prior ID | Disposition claimed | Original counterexample verified on corrected tuple | Status |
| --- | --- | --- | --- |
| State P2-1; Code P2-1 | Check ownership after exceptional validation; quarantine loss without undo | Generated `@validate_commit` externally committed, discarded, or replaced its token, then raised. All three preserved the validator error, marked uncertainty, blocked retry, and preserved published values/replacements. Normal-return variants also rejected completion. | Closed |
| State P2-2; Code P2-3 | Guard local terminal transitions; account for release failures | Replayed recursive finish, recursive abort, and finish-during-abort. Exit/abort callbacks did not repeat; caught finish failure prevented publication; abort cleanup errors retained the body cause and blocked reuse. Additional caught-reentry and release-fault probes held. | Closed |
| Code P2-2, shared prerequisite | Observe sole ownership nonpublishing; fence stale scope exits | Failed attempt plus retained external same-key begin could not admit `next_attempt()`. After an independently opened replacement with candidate `10`, stale normal exit raised and stale exceptional exit returned `False`; neither published nor discarded the replacement. | Verified closed independently |

## Changed-range analysis

Pyrolyze changes ownership observation and discard certification, the owner/local terminal guards, release-error accounting, mechanics tests, and five ownership/review documents. Lifecycle changes only its committed manager, manager tests, and ownership document.

The relevant new boundaries are owner lines 106–117, 173–266, and 315–370; manager lines 186–230, 242–308, 340–363, 403–405, and 432–442. Token-bound exits, completion barriers, and multi-key begin preflight implement the approved prerequisite. Source search found no live production caller of the private owner. Both reviewed diffs passed `git diff --check`. No out-of-disposition product change or new architectural root cause was identified.

## 0. Evidence base

- Read parent, Pyrolyze, and lifecycle `AGENTS.md`; the supplied review-loop skill and canonical template; controlling remediation and RemPlan-1 documents; amended SingleCohortPlan; historical SC1 and original Code/State reports; and lifecycle TransactionScopeOwnership.
- Read Pyrolyze Git objects `HEAD:src/pyrolyze/runtime/context_state_lcm/render_attempt.py:1–387`, its mechanics tests through line 770, and lifecycle adapter through line 33. Read lifecycle manager through line 518 and manager tests through line 359.
- Read pinned lifecycle decorator implementation through line 288, core transaction templates at lines 420–565, and managed prepare/apply/discard templates at lines 372–488.
- Ran the authorized owner pytest target with selectors unset, supplied pinned-source `PYTHONPATH`, `PYTHONDONTWRITEBYTECODE=1`, and `-p no:cacheprovider -q --tb=short`: **35 passed in 2.27s**.
- Ran the authorized manager pytest target from the full committed lifecycle export with pinned YIDL/Astichi sources and the same no-bytecode/no-cache settings: **18 passed in 0.03s**.
- Ran asserted, in-memory probes using the actual manager and generated fields: six generated-validator ownership-loss cases; three original recursive-terminal cases; the retained-borrower counterexample; 35 completion-barrier combinations; four mixed stale/valid multi-key exits; two callback-time sibling replacements; two normal-commit validation fences; six caught/escaping local reentry cases; and two injected release failures. Complete probes passed. An initial probe logging `NameError` was corrected before the complete replay.
- Broader supplied evidence was not independently rerun: focused 64 passes; default Pyrolyze 854 passes/13 unchanged failures/20 skips; decomposed 41 passes/14 unchanged failures; lifecycle 273 passes/1 baseline-owned golden failure/46 skips. The reported old-SHA reproduction remains supplied evidence, not a green-suite claim or waiver.
- Verified all five HEADs at start and end: exact tuple unchanged. Status inspections likewise remained unchanged between inspection and completion. No files, caches, bytecode, builds, Git state, or artifacts were written. No current-round peer prompt/report or main-agent conversation was read.

## 2. Invariant analysis

**Publication certification held.** Both validation return and exception paths reobserve ownership. External publication remained visible as `current == 9`, never fabricated back to `1`; external discard/replacement left `current == 1`. Every ownership-loss case blocked reuse, and an independently active other key survived.

**Terminal processing held.** Recursive or competing local completion poisoned the owner before a caught rejection could permit publication. Instrumented successful releases occurred once. Release faults before and after removal were recorded once, discarded unpublished candidates, and blocked retry. Ordinary complete discard still permitted reuse.

**Stale-scope fencing held.** Single/multi-key scopes retained original tokens. Mixed exits completed or discarded valid original keys independently while preserving replacements. Replacing an earlier key from a later key’s completion callback did not let the enclosing old scope finish that replacement. Normal commit also preserved replacements after validation returned or raised.

**Completion barriers held.** Across prepare, apply, after-commit, rollback, and after-rollback, probes rejected same-key begin, commit, commit-only, rollback, sole-owner certification, explicit multi-key begin, and implicit all-key begin. Rejected begins did not increase an existing other key’s nesting. Fresh transactions remained legal after completion.

**Opaque failures remained fail-closed.** The committed prepare/apply/after fault tests retained uncertainty and blocked retry. Already-applied generated values stayed published; the owner performed no speculative rollback. Ordinary sticky failures, reverse leak cleanup, first-cause preservation, and independent-key behavior remained covered by the passing mechanics target.

## 3. Risks and next action

This is a synchronous, in-memory ownership checkpoint, not a lock, lease, filesystem durability protocol, or process-crash recovery guarantee. It does not certify parallel rendering, cross-key atomicity, resource completion, generation coordination, live wiring, activation, or full I3a. Existing baseline failures remain visible and unwaived.

**Next action:** Merge this independent State GO with the separately formed Code verdict on this exact tuple before recording acceptance of the private mechanics and bounded prerequisite.

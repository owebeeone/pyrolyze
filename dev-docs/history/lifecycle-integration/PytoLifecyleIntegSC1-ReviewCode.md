# PytoLifecyleIntegSC1 — CODE-AXIS REVIEW

**Review object:** Pyrolyze diff `0ab81be3a83eb8a5f3f1ab426353c9eb90c758a7..84d4ab6116e0a743394a6269f09e026607402d80`; private completion owner, tests, and controlling DRAFT `dev-docs/PytoLifecyleIntegSC1.md`, pending acceptance.
**Baseline:** Pyrolyze `84d4ab6116e0a743394a6269f09e026607402d80`; yidl-lifecycle `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`; YIDL `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi `387ca5e1da76204ee60922094734c13ee36383c0`; parent, context only, `a20f8cfb633a268925464eb27728d1934a70aea9`. Sources inspected through pinned `git show`; execution used the supplied dependency exports.
**Date:** 2026-10-03
**Axis:** Code: architecture, interfaces, ownership, call graphs, compatibility, and failure contracts. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — three P2 findings block acceptance. No P0, P1, or P3 findings.

---

## 0. Evidence base
- Verified `rev-parse HEAD` and `status --short` for all five repositories at start and end. All HEADs remained pinned; Pyrolyze source/tests remained clean. An authorized untracked SC1 review-loop ledger appeared at end and was not read. Excluded dependency and parent changes were not inspected.
- Read Pyrolyze `AGENTS.md`; `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:1–338`; `tests/test_runtime_context_state_lcm_render_attempt.py:1–599`; and `lifecycle_adapter.py`. Inspected existing `context_base.py:180–305` for compatibility context, without treating its deferred behavior as findings.
- Read `dev-docs/PytoLifecyleIntegSC1.md:1–142`; the accepted plan at `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`, particularly Ownership And Admission, Local Pass And Failure Rules, Publication, and SC1–SC4; and the committed design review-loop ledger. The plan and live-test transition ledger remain unchanged.
- Read pinned yidl-lifecycle `src/yidl_lifecycle/transaction_yidl.py:1–463`, generated lifecycle dispatch templates in `src/yidl_lifecycle/yidl/lifecycle_core.yidl:410–525`, and managed preparation/application/discard templates in `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:372–488`.
- Ran the authorized focused pytest command with both selectors unset, `PYTHONDONTWRITEBYTECODE=1`, supplied pinned-export `PYTHONPATH`, and `-p no:cacheprovider -q --tb=short`: **26 passed in 2.17s**. Broader owner-reported gates were not independently rerun.
- Ran read-only in-memory probes using `runpy.run_path("tests/test_runtime_context_state_lcm_render_attempt.py")`, reusing its actual manager, generated `RenderValues`, and protocol fault participant. Findings below reproduce without manager mocks or generated-state writes.
- Diff inspection confirmed only three added files, no live wiring or library changes; source reference search found no production callers. `git diff --check` passed. No files, reports, caches, or Git state were written by this reviewer.

## 1. Findings
### [P2-1] Validation exceptions bypass ownership-loss certification
**Location:** `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:204–213`, especially the exceptional path’s readiness assignment; `_discard_owned:157–163`. **Violated invariant:** Missing/replaced or externally completed ownership must block reuse and must not be classified as proven pre-publication discard.

**Reproduction:** Start an attempt, write generated `value=9`, and enlist `_FaultParticipant` whose `on_validate` calls `manager.commit_only(RENDER_KEY)` and then raises `ValueError`. The external commit publishes `current.value=9`; validation raises an `ExceptionGroup`. Because validation raised, the subsequent `_require_identity()` never runs. `_discard_owned()` silently skips the now-missing transaction. Observed completion: `reuse_ready=True`, `publication_uncertain=False`; `next_attempt()` succeeds. Variants where the validator rolls back, or rolls back and begins a replacement before raising, likewise certify reuse; the replacement remains active.

**Impact:** SC2 can receive a false recovery certificate after publication or ownership corruption. **Required correction:** Check and record ownership loss on validation’s exceptional path while preserving the validator failure, leaving replacements untouched, marking uncertainty, and blocking reuse. **Closure test:** Parameterize validator publication, external discard, and replacement followed by an exception; assert retained primary failure, incomplete ownership classification, unchanged replacement identity, and rejected retry. Published values must not be “undone.”

### [P2-2] Failed completion certifies reuse despite an external nested borrower
**Location:** `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:165–179`; contrast the clean-path external-nesting guard at `225–232`. **Violated invariant:** The external borrower’s unsupported completion contract cannot become reuse-safe merely because the owned attempt was already poisoned. SC1’s document expressly withholds that certification at `dev-docs/PytoLifecyleIntegSC1.md:69–71`.

**Reproduction:** Start attempt A; retain `external = manager.begin(RENDER_KEY)`, which returns A’s same transaction object and increments nesting. Poison A and finish normally. A rolls back and raises `RenderAttemptAborted`, but reports `reuse_ready=True`. Call `B = A.next_attempt()` and write generated `value=10`. Calling `external.__exit__(None, None, None)` then publishes B’s candidate before B completes: observed `current.value=10`, inactive render key; B subsequently reports `RenderAttemptIncomplete`.

**Impact:** A stale external scope can complete the next attempt admitted by the owner’s readiness gate. This finding concerns the new certification, not a request to fix the generic manager’s scope implementation. **Required correction:** Enforce or certify sole ownership through a nonpublishing mechanism on failed cleanup as well as success; an outstanding external borrower must prevent reuse. Do not probe with `commit_only`, which could publish poisoned candidates. If the pinned supported interface cannot establish this, return the limitation to the design gate instead of silently widening manager/API scope. **Closure test:** Repeat the sequence above and prove B cannot start through A’s readiness gate while the stale borrower remains unaccounted for; retain ordinary clean-discard retry coverage.

### [P2-3] Local terminal callbacks can reenter completion and escape sticky failure
**Location:** `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:297–321`. **Violated invariant:** Local exit failures must poison the owner before cleanup raises; terminal processing must not execute twice or replace the primary failure.

**Reproduction:** Obtain a direct `begin_scope` handle whose `on_exit` calls that handle’s `finish()` once recursively. Write generated `value=9`, then call the outer `scope.finish()`. Both calls see `_active=True`; `on_exit` executes twice. The inner call releases the handle, and the outer release raises `ValueError("list.remove(x): x not in list")` outside the guarded block. Catch that error and finish the owner: observed `first_failure=None`, `current.value=9`, `reuse_ready=True`. A second probe called `scope.finish()` from `on_abort`: successful-exit processing ran during abort, the release error replaced the primary exception without cause/context, and completion still certified reuse.

**Impact:** A caught local completion failure can publish candidates, and recursive cleanup can lose diagnostics. **Required correction:** Add a local terminal-transition guard before invoking callbacks, reject duplicate/reentrant terminal calls, and include release failures in sticky-failure and cleanup accounting without masking the primary exception. **Closure test:** Exercise recursive finish and finish-during-abort through direct handles; assert callbacks execute at most once, caught exit failures prevent publication, primary errors survive cleanup errors, and incomplete cleanup cannot certify reuse.

## 2. Invariant analysis
- **Explicit-key ownership held on ordinary paths:** One owner begin, retained transaction identity, no borrower begins, and explicit render-key validate/commit/rollback calls. Wrong-manager and externally active admission reject before reset.
- **Local provisional success and observable failure poisoning held:** Entered child failure remains sticky despite caught exceptions, fallback writes, and successful siblings. Ordinary scoped reentry is a no-op; direct duplicate admission poisons the attempt.
- **Ordinary teardown held:** Leaked scopes unwind in reverse order; callback cleanup failures do not prevent remaining cleanup; propagating primary exceptions remain represented. The terminal-reentrancy counterexamples are the exception.
- **Publication-phase caution held for opaque commit errors:** Real prepare/apply/after fault tests preserve the raised error and block reuse without speculative owner rollback. Already-applied values remain visible. This does not certify deferred throwing/resource routes.
- **Isolation held:** Another active semantic key survives render success and failure. A no-op error caught before any genuinely entered scope reports failure remained unobservable, consistently with the plan.
- **Scope boundaries held:** No field/map/dirty snapshots, public API additions, default activation, premature live-test transitions, or production wiring were introduced. Passing scenario tests do not cover the combined exceptional interleavings above.

## 3. Risks and next action
This review accepts neither SC2 feasibility nor resource, registration, generation, dirty-policy, or full-I3a behavior. Existing baseline failures remain deferred. The pinned manager’s lack of a public per-key nesting certificate is material to P2-2; acceptance must not assume that interface exists.

**Next action:** Keep SC1 pending and SC2 unwired; remediate P2-1 through P2-3, resolving the ownership-observation limitation explicitly, then obtain independent re-verdicts on a new pinned tuple.

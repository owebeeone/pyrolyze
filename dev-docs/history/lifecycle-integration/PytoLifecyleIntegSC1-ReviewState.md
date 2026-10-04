# Pyrolyze SC1 Private Render Completion Mechanics — STATE-AXIS REVIEW

**Review object:** Pyrolyze diff `0ab81be3a83eb8a5f3f1ab426353c9eb90c758a7..84d4ab6116e0a743394a6269f09e026607402d80`: private owner, tests, and `dev-docs/PytoLifecyleIntegSC1.md`. Implementation draft pending independent acceptance, dated 2026-10-03.

**Baseline:**

| Repository | HEAD |
| --- | --- |
| Pyrolyze | `84d4ab6116e0a743394a6269f09e026607402d80` |
| yidl-lifecycle | `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent, context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

Sources were inspected with `git show <SHA>:<path>`; execution used the supplied pinned dependency exports, not dirty dependency code.

**Date:** 2026-10-03  
**Axis:** State: ownership transitions, failure ordering, synchronous reentrancy, cleanup completeness, and fail-closed reuse. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — two P2 findings block acceptance. I pre-commit to GO on a revision that resolves P2-1 and P2-2 as specified.

---

## 0. Evidence base

- Read Pyrolyze `AGENTS.md`, supplied workspace instructions, and the canonical review-loop skill.
- Read `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:1–338`, `tests/test_runtime_context_state_lcm_render_attempt.py:1–599`, and `src/pyrolyze/runtime/context_state_lcm/lifecycle_adapter.py:1–33`.
- Read `dev-docs/PytoLifecyleIntegSC1.md:1–142`; controlling `dev-docs/PytoLifecyleIntegSingleCohortPlan.md:1–404` at `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`; and `dev-docs/PytoLifecyleIntegSingleCohortPlan-ReviewLoop.md:1–98`. Verified the controlling plan remained unchanged, including its live-test transition ledger.
- Read pinned yidl-lifecycle `src/yidl_lifecycle/transaction_yidl.py:1–463`, `src/yidl_lifecycle/lifecycle.py:1–270`, relevant validator-marker definitions, `src/yidl_lifecycle/yidl/lifecycle_core.yidl:430–560`, and managed-field preparation/application/discard templates at `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:385–440`. Searched the pinned generated implementation for transaction operations.
- Ran the authorized `$PYTHON -m pytest -p no:cacheprovider -q --tb=short tests/test_runtime_context_state_lcm_render_attempt.py` with both runtime selectors unset, bytecode disabled, and the supplied pinned-source `PYTHONPATH`: **26 passed in 2.20s**. Broader owner-reported gates were not independently rerun.
- Ran read-only, in-memory probes using the existing generated `RenderValues`, actual manager, existing fault participant, and an additional generated `@validate_commit` participant. Reproduced both findings below. The initial additional generated-class probe failed during decoration without postponed annotations; rerunning with the fixture’s annotation convention reproduced P2-1.
- Verified every tuple repository’s HEAD and `status --short` at start and end. All HEADs and tracked statuses remained unchanged. The only added Pyrolyze status entry was the permitted untracked SC1 review-loop ledger; it was not read. No current-round peer report was read.
- Inspection commands included scoped `git show/diff`, `rg/sed/nl/wc`, and an initial read-only `pwd`/`git submodule status` inventory. No files, reports, caches, or repository state were written.

## 1. Findings

### [P2-1] Validation exceptions bypass ownership-loss quarantine

**Location:** Pyrolyze `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:204–213`, particularly the exceptional path’s call to `_discard_owned` at `157–163`.

**Violated invariant:** Missing, replaced, or externally completed ownership must mark publication uncertain and prohibit reuse. The controlling plan’s Ownership And Admission and Local Pass And Failure Rules require this even when another failure is already propagating; SC1 documents the same guarantee at `dev-docs/PytoLifecyleIntegSC1.md:60–65`.

**Reproduction:** Create a generated managed integer, initially `1`, on the explicit render key. Give its generated `@validate_commit(key)` method this sequence: `manager.commit_only(key)` followed by raising a retained `ValueError`. Start an attempt, write candidate `9`, and exit it. The real manager externally publishes `9` during validation, then validation raises an `ExceptionGroup`. Because validation raised, line 206’s identity check never runs. `_discard_owned` sees no owned active transaction and silently does nothing. Observed result: `current.value == 9`, `finished == True`, `publication_uncertain == False`, and `reuse_ready == True`. `next_attempt()` successfully admitted and completed a fresh transaction afterward. Separate probes replacing or removing the transaction before raising likewise incorrectly certified reuse; replacement identity was preserved.

**Impact:** Unsupported external publication is misclassified as a reusable pre-publication failure. A later owner can proceed after an outcome that must instead remain quarantined. This does not require throwing apply/after hooks, resource wiring, or dirty dependency changes.

**Required correction:** Check and record identity loss on the validation-exception path before certifying discard/reuse. Preserve the validator failure, mark incomplete ownership/publication uncertainty, reject `next_attempt()`, and leave replacement transactions untouched.

**Closure test:** Parameterize validators that externally commit, remove, or replace the owned transaction and then raise. Assert original-error preservation, uncertainty, blocked reuse, and replacement preservation. Retain a control proving ordinary validation failure completely discards candidates and remains reusable.

### [P2-2] Local callbacks can recursively complete the same handle without poisoning the owner

**Location:** Pyrolyze `src/pyrolyze/runtime/context_state_lcm/render_attempt.py:297–321`; leaked-scope handling at `189–195` amplifies the abort case.

**Violated invariant:** Local completion must be one-shot; a failed local exit must poison the attempt before cleanup can raise. Cleanup errors must be reported and gate reuse. `_active` remains true throughout callbacks, and there is no local completion-in-progress guard.

**Reproduction:** Inside an owner context, obtain a handle with `begin_scope`, write candidate `9`, and make `on_exit` call that same handle’s `finish()` once using a boolean recursion limiter. Call `scope.finish()` and catch its exception inside the owner body. The callback executes twice. The inner call releases the handle; the outer release raises `ValueError("list.remove(x): x not in list")` outside the failure-recording `try`. Observed before owner exit: two exit callbacks, no active handle, and `first_failure is None`. Owner exit then publishes `9` and reports reuse readiness.

The same root cause affects abort: a leaked handle’s `on_abort` recursively calls its own `abort(primary)` once. Cleanup executes twice; the outer release error is swallowed by the owner’s blanket abort catch without entering `_cleanup_errors`. The result is only `RenderAttemptAborted`, with `reuse_ready == True`.

**Impact:** A caught local-completion failure permits publication, while an unrecorded cleanup failure permits reuse. Existing owner-level `_finishing` protection does not guard these per-handle transitions.

**Required correction:** Establish a local callback/completion-in-progress boundary before invoking callbacks. Reject recursive or competing completion without repeating callbacks, record the failure even when caught, release each handle exactly once, and ensure bookkeeping failures cannot bypass cleanup-error reporting.

**Closure test:** Add bounded recursive `on_exit` and `on_abort` probes. Assert one callback invocation, sticky failure and no publication after a caught exit error, preserved primary abort cause, and reported cleanup failure with reuse blocked when cleanup fails.

## 2. Invariant analysis

- Ordinary local success remains provisional. Genuine scopes borrow the retained transaction without another begin; scoped re-entry is a no-op, and direct duplicate or wrong-manager admission is diagnosed before reset.
- Ordinary caught failures remain sticky; successful siblings cannot rehabilitate them. Body exceptions and normal cleanup-error groups preserve primary errors. Ordinary complete discard permits a fresh identity and subsequent successful publication.
- Normal leaked-scope cleanup runs in reverse entry order and continues across callback failures. Missing/replaced tokens detected outside the exceptional validation path are quarantined without rolling back replacements.
- Opaque `commit_only` exceptions block reuse and avoid speculative rollback. Existing preparation/apply/after probes correctly distinguish unchanged current values from already-applied values without claiming undo.
- Other-key isolation held, including an additional probe retaining another active transaction during P2-1. The owner contains no copied field/map/dirty values. The reviewed diff adds no live render wiring or premature test-transition changes.
- The two findings expose exceptional transitions missing from the recovery grammar; passing nominal scenarios does not establish those transitions.

## 3. Risks and next action

SC1 introduces no filesystem persistence or disk-recovery protocol; this review establishes no process-crash durability or parallel-render guarantee. Opaque publication outcomes, resource participants, generation coordination, and retained-root quarantine remain the stated later gates, not additional findings.

**Next action:** Remediate P2-1 and P2-2 within the private owner, add the specified regressions, and obtain independent re-verdicts on a newly settled tuple before SC2 wiring.

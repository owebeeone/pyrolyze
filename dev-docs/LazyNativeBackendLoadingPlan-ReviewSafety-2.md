# LazyNativeBackendLoadingPlan — SAFETY-AXIS REVIEW

**Review object:** `dev-docs/LazyNativeBackendLoadingPlan.md` at `d0502025e65072d5892d05c39862396520cf6241`; design for review, not implementation or performance acceptance.
**Baseline:** Pyrolyze `d0502025e65072d5892d05c39862396520cf6241`; prior baseline `4f0812802d2abd951e46fb72995a66f9c94d45bb`. Committed documents and sources read with `git show`.
**Date:** 2026-10-10
**Axis:** Safety: degraded paths, recovery, concurrency, publication, compatibility and diagnosability. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: GO** — no open P0, P1 or P2 findings; no new findings. Prior Safety P2-1 closes for draft scope only.

---

## Prior-Finding Closure

This reviewer replaces the original Safety reviewer. Closure follows an independent retrace, not the remediation plan’s assertion.

| Finding | Disposition | Independently verified closure |
| --- | --- | --- |
| Safety P2-1: regeneration can leave an unrecoverable mixed catalog | Closed for draft scope | Lines 98–103 place all replaceable artifacts inside one root. Lines 248–285 prohibit filewise replacement, retain the complete old directory, specify rollback and admission fencing. Lines 370–381 require fault-injection evidence before catalog migration. |

**Original counterexample:** Begin with complete A and validated B. Previously, replacing B’s index before its shards, or its shards before its index, could interrupt into an admitted mixture. Neither sequence is now permitted: the index, facade and shards move together as a directory. Interruption between the two renames leaves an absent destination and retained A, not a mixture. Interruption after candidate promotion leaves complete B plus the marker; recovery moves B aside and restores A before admission.

## Changed-Range Analysis

Reviewed the plan changes across `4f0812802d2abd951e46fb72995a66f9c94d45bb..d0502025e65072d5892d05c39862396520cf6241`, including both intervening commits.

- **Lines 55–67 and 98–103:** Generated facade and stubs move inside `_generated/`; stable compatibility shims remain outside. This closes the replacement boundary without requiring regeneration to rewrite handwritten compatibility files.
- **Lines 248–285:** Whole-directory promotion replaces the intermediate filewise recovery protocol. Exclusive offline access, same-filesystem renames, retained old output and explicit recovery cover the original root cause.
- **Lines 370–381:** Acceptance expands to marker transitions, recovery failures, first generation, failed generator exit and post-admission cleanup. These are mandatory future gates, not claimed results.

## 0. Evidence Base

- Start and end `git rev-parse HEAD` returned the exact review SHA.
- Start/end `git status --short` retained the excluded modified fuzz test and three excluded untracked documents. Two untracked round-2 prompt files appeared by the final check; neither was read. The committed tuple did not move.
- Read process authority `review-loop/SKILL.md`, including replacement-reviewer closure and draft acceptance rules.
- Read committed `AGENTS.md`, `dev-docs/README.md`, `dev-docs/LazyLoadingOptimizationRequirements.md`, `dev-docs/ApiDesignRules.md`, `dev-docs/SemanticUiLibraryDesignRules.md`, and `dev-docs/PackageStructureRules.md`.
- Read the complete controlling plan, prior `dev-docs/LazyNativeBackendLoadingPlan-ReviewSafety.md`, and `dev-docs/LazyNativeBackendLoadingPlan-RemPlan-1.md`.
- Inspected committed `rewrite.py:2461–2619`, `import_hook.py:70–185`, `generate_semantic_library.py:1160–1210`, and `pyproject.toml:1–59`.
- Inspected committed PySide6 `generated_library.py:1–100`, package initializer `:1–7`, `unified/qt.py:1–170`, and `mountable_engine.py:35–95`, `:120–190`, `:262–285`.
- Used only inspection commands. Initial parent-checkout document/range attempts failed and supplied no authority; subsequent reads explicitly targeted Pyrolyze. No tests, builds, writes or git mutations occurred. Failure sequences were analyzed against the text, not executed.

## 2. Invariant Analysis

**Every original publication failure disposition was retraced.** Failed generation or incomplete staging cannot promote (248–250). Preparation failure precedes directory mutation (257–259). Failure of the first rename leaves A active; failure of the second leaves A recoverable from backup. Candidate-validation or marker-clearing failure requires rollback while A remains retained (266–275). Interrupted rollback is retryable because recovery recognizes A already active; failed restoration or validation keeps admission prohibited (267–271). First-generation failure restores absence, explicitly disallowed for packaging (272–274). Post-admission cleanup failure preserves complete B and blocks another promotion (275–277). Stale shards leave with A’s directory; unrelated handwritten files remain outside the root (263–264). No admitted-mixture counterexample survived these rules.

**First-load concurrency and reentry:** Lines 155–178 constrain shared imports to a DAG, prohibit shared modules from importing widgets or their facade, require serialized resolution and validation before publication, and diagnose reentrant cycles. I examined resolver-lock/import-lock inversion but established no concrete permitted cycle from the inspected dependencies. This is not an implementation deadlock proof.

**Partial failures and caches:** Lines 182–186 and 225–241 distinguish unknown keys from broken known entries, forbid partial publication and silent fallback, and require lightweight deterministic failure records without retained tracebacks. Successful shared imports may remain cached without invalidating other kinds. Fresh-process repair does not purport to repair disk publication.

**Compiler error preservation:** Existing import discovery suppresses exceptions at `rewrite.py:2475–2478`; hint resolution does likewise at 2612–2619. Plan lines 32, 208–221 and 344–350 explicitly require attributable lazy failures and recognition/source-error parity before compiler migration. The existing suppression is a required implementation attack surface, not newly authorized degraded behavior.

**Compatibility, disclosure and scope:** Explicit signatures, descriptor ownership and alias identity remain requirements (98–121). Mapping representation requires a recorded decision (320). Installed wheel/sdist coverage includes authored sources, sidecars and stubs (291–298). No external reporting or credential collection is introduced. Tk, DPG, member compaction and lifecycle changes remain deferred; offline maintenance does not claim uninterrupted availability or power-loss durability.

## 3. Risks and Next Action

Residual implementation risks are lock ordering, failure-state cleanup, descriptor binding, toolkit compatibility, compiler diagnostics and enforcement of every packaging admission path. None is demonstrated by this document review.

The next action is to obtain the lane owner’s independent verdict merge before proceeding through the declared decision and slice-1 proof gates. This GO does not accept runtime implementation, migration or performance claims.

# Lifecycle Integration Completion Plan — Safety-AXIS REVIEW

**Review object:** Pyrolyze dev-docs/PytoLifecyleIntegPlan.md at 723460d6c1dce75b70f03e355daf20c248bde8ad; DRAFT plan; 2026-10-03
**Baseline:** All reviewed tracked bytes were read through `git show <exact-sha>:<repository-relative-path>`.
- Pyrolyze: `723460d6c1dce75b70f03e355daf20c248bde8ad`
- yidl-lifecycle: `cdf08544deea846bca4fa7e0c468ebee8d41e138`
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`
- Parent, context only: `a20f8cfb633a268925464eb27728d1934a70aea9`

**Date:** 2026-10-03
**Axis:** Safety: degraded completion, containment, irreversible resource operations, recovery, and migration blast radius. Independent, adversarial, read-only. The other axis runs in parallel; nothing here relies on it. Filed verbatim by the lane owner.

**Verdict: NO-GO** — one P2 finding blocks. I pre-commit to GO on a revision that resolves P2-1 as specified. This is a document-gate verdict, not runtime authorization.

---

## 0. Evidence base

Commands were limited to read-only Git inspection, `rg`, `nl`, and `sed`. No tests, imports, builds, regeneration, or writes were performed. The supplied four-test rerun is operator evidence, not independent verification.

The parent HEAD and each submodule HEAD/status were checked at start and end. Every SHA remained pinned. Lifecycle and Astichi stayed clean; YIDL's excluded dirty-file inventory was unchanged. Pyrolyze contained only permitted untracked review documents; the review-loop ledger appeared during review. No peer prompt, report, or verdict was opened.

Read evidence, with paths relative to their owning repository:

- **Instructions:** committed parent and all four submodule `AGENTS.md` files. The supplied reviewer contract was applied; a separate review-loop skill/template was not located in the searched registered skill locations.
- **Pyrolyze documents:** `dev-docs/PytoLifecyleIntegPlan.md:1-1213`, `dev-docs/ContextLifecyleMetaprogrammingPlan.md:1-824`, `dev-docs/LifecyleAdoptionPatterns.md:1-493`, I0 findings `:1-205`, I0 inventory `:1-234`, and `tests/data/lcm_integration/README.md:1-74`.
- **I0 evidence:** `characterize.py:1-244`, `transaction_failures.py:1-152`, `tests/test_lcm_integration_characterization.py:1-42`; original/decomposed snapshots `:1-365`, monolithic snapshot `:1-166,290-310`, and transaction-failure snapshot `:1-706`.
- **Pyrolyze capability evidence:** `context_state_lcm/context_base.py:1-520`, `render_context.py:1-280`, `slot_context.py:1-76`, `component_call_slot_context.py:1-300`, `slot_expr_slot_context.py:1-152`, `app_context_override_slot_context.py:1-197`, `lifecycle_adapter.py:1-33`; also `src/pyrolyze/runtime/call_site_context.py:1-226`, `context.py:1-50`, and targeted resource-method inspection in `slot_call_semantics.py`, including `:225-304`.
- **Lifecycle capability evidence:** `src/yidl_lifecycle/transaction_yidl.py:1-463`, `bindings.py:1-416`, `lifecycle.py:1-220`, `lifecycle_harvester.py:357-431`; owned YIDL `:1-350`, managed hook templates/contributions `:454-503,1085-1131`, and core hook collections/assembly `:105-125,1295-1319`.
- **Lifecycle design/tests:** Phase F-1 terminology, staged publication, manager pipeline and failure semantics, especially `dev-docs/YidlTransactionalYidlPhaseF-1Plan.md:632-769,950-1057`; Phase B `:1-180`, G `:1-260`, H `:1-230`; generated owned golden `:130-323`; existing single-hook failure tests in `tests/test_lifecycle_decorator.py:865-885,1023-1044`.
- **Committed YIDL view:** `src/yidl/runtime/transaction_yidl.py:1-4`, confirming the extracted-runtime compatibility shim. Dirty replacement/removal bytes were not used.

## 1. Findings

### [P2-1] Participant-level draining does not guarantee completion of co-located hooks or callbacks

**Location:** Pyrolyze `dev-docs/PytoLifecyleIntegPlan.md:641-672`, particularly L0's three-participant proofs and exit condition; `:915-918` then attributes protection of unrelated required completion to L0.

**Violated invariant:** One failing completion action must not prevent independent mandatory retirement or cleanup from being attempted. The prerequisite currently specifies and tests isolation between participants without explicitly covering multiple actions inside one participant.

**New architectural root cause:** The failure-isolation unit is coarser than the required-work unit. A participant callback can contain several generated hooks or an entire domain delivery batch. Draining subsequent participants cannot resume skipped actions inside that callback.

**Evidence and reproduction:** Lifecycle permits multiple same-key hooks: `src/yidl_lifecycle/lifecycle_harvester.py:357-388,411-431` does not restrict their cardinality. `src/yidl_lifecycle/yidl/lifecycle_managed.yidl:466-475,498-503,1109-1131` composes them as ordinary sequential calls without per-hook exception isolation.
1. Enlist decorated participant A with two same-key after-commit hooks: first deliver a notification; second retire a displaced subscription. Enlist B and C as well.
2. A manager-only L0 correction drains callbacks across A, B, and C, satisfying the enumerated three-participant checks.
3. Fields publish. A's first hook raises; its second hook is never reached. The manager nevertheless attempts B and C and finalizes the key.
4. The old subscription remains active. An unchanged subsequent render need not enlist A, so it does not repair the skipped retirement. The analogous after-rollback sequence skips provisional-resource cleanup.

This is also reachable with the retained domain-batch shape: Pyrolyze `src/pyrolyze/runtime/context_state_lcm/render_context.py:257-261` and `slot_expr_slot_context.py:111-115` call batch entries sequentially. Capturing an immutable batch preserves its contents but does not ensure later entries execute after an earlier exception.

**Impact:** L0 can pass its stated concrete proofs while mandatory unsubscribe, retirement, or provisional cleanup remains skipped. Manager reset and field rollback do not repair those external obligations. This is a plan prerequisite defect, not a request to patch the baseline runtime during review.

**Required correction:** Extend L0/D4 explicitly to independently declared generated after-hooks, including inherited hooks. Require per-hook draining and failure context at the lifecycle-owned invocation boundary. Separately assign I4/I6 responsibility for draining independent actions within domain batches; do not claim the TM provides that automatically. An individual throwing action may remain incomplete and be reported, but later independent actions must still be attempted.

**Closure/regression test:** The revised plan must require generated lifecycle coverage with two same-key hooks, first throwing and second recording cleanup, plus another participant; cover commit and rollback and inherited-hook composition. Require an integration failure case with two actions in one delivery/retirement batch, first throwing and second observably unsubscribing. Assert exactly-once attempts, preserved publication/rollback results, useful error context, finalized keys/local scopes, and subsequent-render recovery.

## 2. Invariant analysis

- **Whole-boundary validity:** The attack “child completes, parent later fails, early child state survives” is addressed by one publication key and prohibited child completion ownership (`PytoLifecyleIntegPlan.md:209-241,723-770`). The plan correctly treats this as a proposed semantic change, not baseline parity.
- **Containment:** Failure before body mutation still includes framework registration/visitation. Failure after shared or ancestor writes must preserve working state at child entry, not restore `.current`. Cleanup uncertainty prevents acceptance; local recovery cannot clear another invalidating failure (`:243-290,764-770`). These attacks did not expose another plan defect.
- **Local scopes and borrowed keys:** I1 requires local reset/exit and ownership protection with live sharing, rather than postponing them to I2. Borrowed transactions cannot acquire completion rights merely from activity (`:674-758`).
- **Resources and reads:** Published dispatch reads `.current`; failed removal cannot clear it eagerly. Holder replacement, referent participation, acceptance, deterministic retirement, cycles, and async task tokens are distinguished (`:434-528`; I0 inventory `:173-197`). These remain gated obligations, not claims that `owned()` supplies deterministic teardown.
- **Publication ordering and scope:** Generation preparation, immutable batches, independently arriving invalidations, and completion reentry require explicit coordination (`:901-913`). Runtime routing/full-suite acceptance and unrelated host fixes remain bounded (`:920-948`). No additional disclosure or scope-expansion defect was established.

## 3. Risks and next action

D1-D5, concrete containment facilities, and runtime activation remain legitimately pending. In particular, pinned `owned()` calls `accepted()` during preparation; resource approval must not confuse that with successful whole-boundary publication. Existing test failures and dirty-environment provenance are disclosed, not waived.

**Next action:** Revise L0/D4 and the I4/I6 completion obligations to close P2-1, then re-review that bounded document change before proceeding to semantic approval or implementation.

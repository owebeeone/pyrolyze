# YIDL Lifecycle Integration Handoff

Updated: 2026-10-04. This is a resume guide, not a new design or an acceptance
verdict. Read repository instructions and the active contracts before changing
runtime behavior. The current request creates this handoff only; it does not
authorize another roll-build, runtime activation, or unrelated cleanup.

## Resume Point

**Next implementation checkpoint: SC3-L0 / L0-1 in `yidl-lifecycle`.**

The lifecycle completion design has passed its design review. Its manager
implementation, generated guards/hooks, implementation review, and private
Pyrolyze adoption have **not** landed. Do not interpret the recent compiler
fixes or passing library tests as completion of L0.

| Area | Actual State |
| --- | --- |
| Construction | Lifecycle-based common construction, explicit manager injection, and post-construction graph attachment are implemented and accepted through I1b |
| Single render completion | SC1 owner and SC2 real field-only render wiring are implemented; the accepted SC2 proof is private and graph-gated |
| Resource routes | Existing resource-bearing routes remain unactivated; SC2 deliberately rejects unsupported admission/retirement |
| Resource audit | SC3 caller/writer/resource audit is recorded, not an activated migration |
| Completion contract | L0 design accepted; L0-1, L0-2, L0-3, and private consumer adoption remain pending |
| Full field migration | I3a is not complete; callback selection, invocation values, resource holders, and remaining snapshot/transfer deletion remain unfinished |
| Generator detour | Astichi/YIDL native materialization regressions are fixed, committed, and pushed; original YIDL goldens are unchanged |

## Goal And Chosen Semantics

The objective is to replace bespoke context-state storage, candidate/current
transfers, and snapshot restoration with lifecycle declarations and generated
transaction behavior. Context evaluation and rendering algorithms remain domain
code. Resource delivery, subscriptions, effects, cancellation, and retirement
are not automatically handled by converting their holder fields.

The operator chose one outer render completion decision:

- Nested participating renders share the outer render's manager and render key.
- Local success remains provisional; only the outer owner publishes.
- Failure of an entered child pass makes the render attempt rollback-only, even
  when a parent catches that exception.
- A successful child does not independently publish values that survive a
  subsequent failure of that same outer render attempt.
- Local entry/reset/exit is separate from transaction completion.
- Multiple keys still gate which fields are writable. One manager does not
  imply all keys are active or that multi-key completion is atomic.
- Independently accepted work outside rendering, including invalidations and
  registrations, must not be erased by failed render cleanup. Existing writer
  routes need explicit policies; do not invent a new out-of-render registration
  API from this statement.

Earlier holder-first plans preserved independent child publication. Those
clauses are superseded only as specified in the single-cohort amendment. Do
not implement an old historical golden's observation as the new render contract.

## Read In This Order

1. [Current documentation index](README.md), repository `AGENTS.md`, and the
   owning library's `AGENTS.md`.
2. [Single-cohort amendment](PytoLifecyleIntegSingleCohortPlan.md): current
   ownership contract and explicit supersession of older assumptions.
3. [SC3 resource audit](PytoLifecyleIntegSC3.md): concrete writers, completion
   callers, resource categories, and activation gates.
4. [SC3-L0 completion plan](PytoLifecyleIntegSC3-L0Plan.md): the accepted design
   to implement next, including exact Phase F-1 supersession and stop conditions.
5. [Overall integration plan](PytoLifecyleIntegPlan.md) and
   [I3a detail](PytoLifecyleIntegI3aPlan.md), interpreted through the amendments.
6. [Lifecycle library index](../../yidl-lifecycle/dev-docs/README.md) and
   [implemented scope fencing](../../yidl-lifecycle/dev-docs/TransactionScopeOwnership.md).

For exact acceptance evidence, read only the relevant archived ledgers:
[SC2](history/lifecycle-integration/PytoLifecyleIntegSC2-ReviewLoop.md) and
[L0 design](history/lifecycle-integration/PytoLifecyleIntegSC3-L0Plan-ReviewLoop.md).
Their pinned revisions remain historical evidence; newer dependencies do not
automatically inherit those verdicts. Some older active-plan status text still
says draft; use the exact recorded acceptance scope rather than that label alone.

## Repository Checkpoint

These are the checked-out and published commits inspected for this handoff,
not a replacement for the older dependency tuple pinned in the design reviews.

| Owning Repository | Branch | Commit | Relevant Change |
| --- | --- | --- | --- |
| `pyrolyze` | `lcm-resume` | `a9596b32211abcdb28fa7684fbd51696d634d98e` | Documentation consolidation; latest accepted design checkpoint remains recorded below it |
| `yidl-lifecycle` | `lcm-resume` | `371dfa530a975c27f7a6c09a7648f7f00532ab29` | Documentation consolidation; published lazy/static mutable feature is already included |
| `yidl` | `main` | `a7cc1de7b630b55bd194940ecad83f3f1738cf8a` | Empty-resource test checks executable AST, not a deferred compile carrier |
| `astichi` | `main` | `54789e883f1a687d767a799381f68d395b4c57cb` | Deferred AST/provenance and native variadic materialization fixes |

At inspection, the three library/compiler repositories were clean. Pyrolyze
already had two untracked, unrelated documents:
`dev-docs/RenderingBackendBugList.md` and
`dev-docs/RenderingBackendDiscussionReport.md`. Leave them alone.

The parent checkout is dirty, with other projects, files, and unrecorded
submodule-pointer changes. Parent pointers were deliberately not updated by
the recent pushes. Do not commit/reset the parent, switch branches, create
worktrees, or absorb unrelated changes as part of this resume. Recheck status
at the start of the next task; this table is a checkpoint, not a live inventory.
This handoff and its index link are documentation-only additions on top of the
recorded Pyrolyze baseline. Their commit does not change the runtime checkpoint
or imply implementation of the pending completion contract.

## Code Map

Paths in this table are relative to the owning repository root.

| Repository / Path | Responsibility |
| --- | --- |
| Pyrolyze: `src/pyrolyze/runtime/context_state_lcm/render_attempt.py` | Private outer attempt, identity/ownership fencing, local completion guards, rollback-only propagation |
| Pyrolyze: `src/pyrolyze/runtime/context_state_lcm/field_only_render.py` | SC2 graph-level field-only admission and real render wiring; resource routes remain blocked |
| Pyrolyze: `src/pyrolyze/runtime/context_state_lcm/lifecycle_adapter.py` | Construction and lifecycle integration boundary |
| Pyrolyze: `context_state_lcm/context_base.py`, `_base.py`, `slot_context.py`, `render_context.py` under `src/pyrolyze/runtime` | Common slot/pass state and orchestration to migrate in bounded later steps |
| Pyrolyze: `src/pyrolyze/runtime/context_bare_refactor_lcm.py` | Decomposed context implementation exercised by the private proof |
| Pyrolyze: `src/pyrolyze/runtime/context_lcm.py` | Older monolithic LCM implementation/reference; not proof that the decomposed path is fully activated |
| Pyrolyze: `tests/data/lcm_integration` | Historical characterization and new construction/single-cohort canonical fixtures |
| Lifecycle: `src/yidl_lifecycle/transaction_yidl.py` | Existing manager and retained `LifecycleTransaction`; L0-1 implementation belongs here |
| Lifecycle: `src/yidl_lifecycle/yidl/lifecycle_core.yidl` | Core generated completion/preparation and common write boundary |
| Lifecycle: `src/yidl_lifecycle/yidl/lifecycle_managed.yidl` | Effective per-key helper and hook contributions used by the complete decorator |
| Lifecycle: `src/yidl_lifecycle/yidl/lifecycle_owned.yidl`, `lifecycle_transient.yidl` | Additional generated writers/materializing getters that must honor the same candidate-write guard |
| Lifecycle: `src/yidl_lifecycle/_generated_lifecycle_base.py` | Checked-in complete decorator artifact; regenerate from YIDL, never patch as independent authority |
| Lifecycle: `src/yidl_lifecycle/lifecycle.py` | Harvest/build boundary; class generation compiles and executes the emitted AST, not a source round-trip |

The manager currently lacks `TransactionCompletion` and retained terminal
completion evidence. Its existing prepare/apply/after/rollback loops do not yet
implement the accepted L0 phase-draining and eligibility contract. Token-bound
scope fencing was implemented earlier; do not conflate it with L0 completion.

## Next Checkpoints

### L0-1: Manager Outcome And Failure Protocol

Follow the detailed plan, with narrow red tests in the library's
`tests/test_transaction_yidl.py` before implementation.

- Add immutable, token-bound terminal completion evidence on the original
  transaction, including actual publication/discard/after-action facts and
  original failures. Nested nonfinal completion leaves evidence unset.
- Capture participants and stable commit order once. Preserve existing return
  values, nesting, per-key isolation, legacy callback compatibility, and stale
  scope fencing.
- Stop dependent preparation at its first failure, but attempt discard for all
  captured participants and drain eligible independent cleanup.
- Continue independent application after unexpected application failure; do
  not claim failed application was atomic or that already published values
  were undone. After-hook eligibility follows actual apply/discard success.
- Guard same-key reentry, membership changes, and preparation-write permission;
  preserve deterministic, contextual error aggregation.
- Pin empty entered/unentered phases, missing required callbacks, ownership
  loss, mutation-before-error, and poisoned cleanup as specified in the plan.

This is a change to the existing manager, not a new manager/cohort API. No new
marker, enum, magic phase tags, savepoint, or cross-key atomicity is authorized.

### L0-2: Generated Guards, Hooks, And Goldens

The manager-only checkpoint is insufficient for library acceptance:

- Implement the before-hook candidate-write window and irreversible
  hook-to-field preparation boundary in YIDL resources.
- Cover effective managed-layer helpers, not only core hook resources.
- Guard managed/owned setters and transient/thaw/factory getters that create
  working storage; an existing token/value cannot bypass the guard.
- Permit before-hook self-staging and staging of captured later/unprepared
  participants; reject writes to prepared participants and writes from
  conversion/application/after actions.
- Wrap each independently declared inherited/local after hook so one failure
  does not skip independent hooks. Keep dependent actions dependent.
- Add the canonical generated failure fixture, runtime assertions, complete
  decorator/output goldens, and human-inspection variants.

Generated guards do not intercept mutation through arbitrary retained mutable
aliases. The callback contract prohibits those out-of-window mutations; do
not add defensive copies/proxies or claim detection that does not exist.

### L0-3 And Private Consumer Adoption

Run focused/full library verification and fresh independent Code/State review
at an exact settled tuple. Then update the private Pyrolyze owner to consume
completion evidence rather than guessing whether failure occurred before or
after publication. Preserve the old transaction-failure observation with its
revision and add a separately named target outcome; do not silently bless a
changed historical baseline.

Reprove original SC1/SC2 closures and empty completion cases. Resource admission
stays blocked. Concrete resource/publication/generation/retirement/delivery
adapter design is the next gate, not automatic runtime activation or wholesale
snapshot deletion. Callback selection is a suggested first bounded adapter;
subscriptions/effects/mounts/overrides/legacy call sites are separate work.

## Verification And Commands

Verified after the compiler fixes, on Python 3.12 with the local native
extension rebuilt:

| Suite | Result |
| --- | --- |
| Astichi full suite, including its Python/native test matrix | 2292 passed, 92 skipped |
| Generic YIDL full suite | 299 passed, 2 skipped |
| YIDL-lifecycle full suite | 277 passed, 46 skipped |
| Pyrolyze seven-file integration baseline, rerun for this handoff | 127 passed |

Seven former generic YIDL failures were fixed without rewriting goldens:
an empty-resource carrier assumption, deferred source-file metadata, and five
dataclasses generation cases. Native fixes resolve deferred templates, use the
immediate argument slot instead of ancestor slots, traverse comparison targets,
and expand dictionary-display spreads. The native safety check remains enabled.
These fixes do not implement or certify Pyrolyze L0/resource migration.

The recorded SC2/SC3 focused Pyrolyze baseline was 127 passing tests; it was
reproduced during handoff preparation in 5.42s against the current dependency
commits in the table above, without changing runtime code. Historical
full-default evidence was 917 passed, 13 failed, 20 skipped; broader decomposed,
unactivated evidence was 41 passed, 14 failed. Those failures are recorded
baseline debt, not blanket permission to ignore new failures. Full/broader
Pyrolyze suites were not rerun during the compiler-fix detour.

From the Pyrolyze repository root, rerun the seven-file focused baseline:

```sh
env -u PYROLYZE_CONTEXT_IMPL -u PYROLYZE_USE_CONTEXT_LCM \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q --tb=short \
  tests/test_runtime_context_state_lcm_render_attempt.py \
  tests/test_runtime_context_state_lcm_field_only_render.py \
  tests/test_runtime_context_state_lcm_construction.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py \
  tests/test_lcm_integration_characterization.py
```

The existing environment discovers Pyrolyze's pytest plugin. Do not also pass
`-p pyrolyze.compiler.pytest_plugin`, which registers it twice. See the
[characterization README](../tests/data/lcm_integration/README.md) for inspection
commands and historical-versus-target baseline policy.

From the lifecycle repository root:

```sh
env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../astichi/src:../yidl/src \
  ../.venv/bin/python -m pytest tests/test_transaction_yidl.py -q

env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../astichi/src:../yidl/src \
  ../.venv/bin/python -m yidl_lifecycle.regenerate_lifecycle_base

# Only after intentionally changing and reviewing the YIDL source:
env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../astichi/src:../yidl/src \
  ../.venv/bin/python -m yidl_lifecycle.regenerate_lifecycle_base --write

env PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../astichi/src:../yidl/src \
  ../.venv/bin/python -m pytest -q
```

Golden fixture/run/regeneration mechanics are documented in the library's
[golden README](../../yidl-lifecycle/tests/data/goldens/readme.md). Review
generated diffs and run runtime assertions before accepting new output.
If native source changes, rebuild from the Astichi repository root using
`../.venv/bin/python native_engine/build.py`; otherwise the existing extension
can silently exercise an older native implementation.

## Scope And Stop Conditions

- Work in the owning repositories and current branches. No new worktree,
  parallel rollout branch, tag, or parent-pointer commit is implied by this
  handoff. Commit/push and roll-build instructions require the next task's
  explicit scope.
- Do not activate resource routes, replace legacy call-site authority halfway,
  invent selective child rollback, or redesign resource/refcount lifetime while
  implementing L0.
- Generic YIDL/Astichi changes are outside the accepted L0 scope. If existing
  holes cannot express the generated boundary, stop and discuss that exact
  limitation rather than changing the compiler under the library checkpoint.
- Audit real consumers before enforcing new completion guards. A legitimate
  incompatible callback/write is a stop-and-discuss case, not permission to
  discard work silently.
- Keep historical evidence unchanged except for an explicitly reviewed
  historical-versus-current disposition. Distinguish design acceptance,
  implementation acceptance, private adoption, and live activation throughout.

# LCM Integration Plan Review Ledger

## Scope And Authority

Status: **accepted at the corrected tuple below after both re-verdict reports
returned GO; this accepts the plan only**.

This loop reviews `dev-docs/PytoLifecyleIntegPlan.md` for consistency and
failure/recovery safety. Acceptance covers the plan only: it does not approve
the outstanding semantic decisions, runtime implementation, default-runtime
switch, or roll-build activation.

Process: the operator-requested `review-loop` skill, with independent
Consistency and Safety axes, reports filed verbatim, one merged remediation
patch per round, and a limit of two remediation rounds. Reviewer prompts were
generated from the skill's canonical `references/review-prompt-template.md`,
using its matching axis sections and the same settled tuple. Reviewers received
fresh contexts and could not access the other current-round report.

No Surface axis was added: this is an internal integration plan, not a new
author-facing API or CLI freeze. The existing authoring and runtime surfaces
remain compatibility constraints.

## Initial Settled Tuple

| Repository | Revision | Role |
| --- | --- | --- |
| Parent workspace | `a20f8cfb633a268925464eb27728d1934a70aea9` | Existing resume checkpoint; its Pyrolyze gitlink predates the plan-only commit |
| Pyrolyze | `7f373420d9fde14559985792125559cd4f60a3cb` | Committed plan and consumer code under review |
| yidl-lifecycle | `cdf08544deea846bca4fa7e0c468ebee8d41e138` | Extracted lifecycle contract and implementation |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` | Committed compiler baseline; unrelated working changes excluded |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` | Committed assembly baseline; parent gitlink differs |

The operator authorized commits of the plan and review/remediation documents
only. No runtime code, unrelated changes, parent gitlinks, tags, or pushes are
part of this loop. Reviewers inspect pinned committed sources rather than the
dirty YIDL working checkout and verify repository HEADs at start and end.
Review-output documents are authorized working-tree outputs.

## Local Verification

Date: 2026-10-03. These checks were run by the lane owner, not the read-only
reviewers, and did not change tracked source files.

From the Pyrolyze repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/test_runtime_context_lcm_phase3.py \
  tests/test_runtime_context_lcm_phase4.py \
  tests/test_runtime_context_lcm_phase5.py \
  tests/test_runtime_context_lcm_phase6.py \
  tests/test_runtime_context_state_lcm_context_base.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_runtime_context_state_lcm_leaf_rerender.py
```

Result: **32 passed in 3.60s**.

From the neighboring yidl-lifecycle repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m yidl_lifecycle.regenerate_lifecycle_base
```

Result: **generated lifecycle base matches**.

These are results for the live editable checkout, which includes excluded dirty
YIDL changes. They do not establish a reproducible all-clean dependency tuple.
The full Pyrolyze suite and performance benchmarks were not run in this review.
No new behavior tests are required for a documentation-only patch; proposed
runtime regression scenarios remain deliverables of the implementation slices.

## Review Rounds

| Round | Plan Revision | Consistency | Safety | Disposition |
| --- | --- | --- | --- | --- |
| Initial | `7f373420d9fde14559985792125559cd4f60a3cb` | NO-GO: one P2 | NO-GO: two P2 | Two unique root causes; one independently converged |
| Remediation 1 | `aecb23366f17123b2cb48fd6e862d79bcbc1deee` | GO; original P2 verified closed | GO; both original P2s verified closed | Plan accepted; runtime work and decisions still gated |

Reports are filed verbatim in
`dev-docs/PytoLifecyleIntegPlan-ReviewConsistency.md` and
`dev-docs/PytoLifecyleIntegPlan-ReviewSafety.md`.

Remediation round 1 is recorded in
`dev-docs/PytoLifecyleIntegPlan-RemPlan-1.md`. The merged patch:

- Records the actual fail-fast TM baseline and an approved, lifecycle-owned
  L0 prerequisite before dependent cleanup/notification integration.
- Moves local pass entry/reset/finalization safety into I1, the checkpoint that
  enables live shared-TM construction, with nested rerender/failure evidence.

Closure was verified by the originating reviewers in
`dev-docs/PytoLifecyleIntegPlan-ReviewConsistency-1.md` and
`dev-docs/PytoLifecyleIntegPlan-ReviewSafety-1.md`. Both retraced their original
counterexamples and classified the patch as prerequisite/checkpoint correction,
not a new architecture or interface. No new architectural root cause or other
finding was reported in remediation round 1.

No findings were self-closed. Runtime regression requirements are specified in
the plan; runtime fixes/tests were not part of this documentation-only review.

## Accepted Tuple And Remaining Work

| Repository | Accepted Revision |
| --- | --- |
| Parent workspace | `a20f8cfb633a268925464eb27728d1934a70aea9` |
| Pyrolyze plan | `aecb23366f17123b2cb48fd6e862d79bcbc1deee` |
| yidl-lifecycle | `cdf08544deea846bca4fa7e0c468ebee8d41e138` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |

This acceptance record and the final reports are filed in a subsequent
documentation-only commit; the accepted plan's content is not changed after
re-verdict. Parent gitlinks and dependency revisions remain untouched.

Discovery ledger: the initial plan review found two unique blocking planning
defects across three axis-specific finding IDs. Both were resolved in one
merged remediation round before integration implementation. No P3 findings or
new findings were reported. This is not a claim that existing runtime defects
were fixed or that unexecuted regressions pass.

The live runtime still needs L0 failure-completion work and I1 operational
scope/sharing verification. Broader regressions, dependency reproducibility,
and performance remain I0/I8 deliverables. The four operator decisions remain
open: publication/pass lifetimes, caught nested failures, resource ownership,
and generation/notification/retirement ordering.

## Next Action

Resolve I0's semantic/capability decisions and obtain separate implementation
authorization before considering a roll-build. Plan acceptance is not execution
approval. No tags, pushes, parent gitlink commits, or runtime changes were made
by this review loop.

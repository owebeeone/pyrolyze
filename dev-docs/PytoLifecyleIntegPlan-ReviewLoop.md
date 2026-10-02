# LCM Integration Plan Review Ledger

## Scope And Authority

Status: initial dual review NO-GO; merged remediation awaiting re-verdict.

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

Reports are filed verbatim in
`dev-docs/PytoLifecyleIntegPlan-ReviewConsistency.md` and
`dev-docs/PytoLifecyleIntegPlan-ReviewSafety.md`.

Remediation round 1 is recorded in
`dev-docs/PytoLifecyleIntegPlan-RemPlan-1.md`. The merged patch:

- Records the actual fail-fast TM baseline and an approved, lifecycle-owned
  L0 prerequisite before dependent cleanup/notification integration.
- Moves local pass entry/reset/finalization safety into I1, the checkpoint that
  enables live shared-TM construction, with nested rerender/failure evidence.

No findings are self-closed. Runtime regression requirements are specified in
the plan; runtime fixes/tests are not part of this documentation-only review.

## Next Action

Commit the merged documentation checkpoint and ask the original reviewers to
verify their original counterexamples on the corrected plan. Semantic decisions
remain with the operator even if both axes report GO.

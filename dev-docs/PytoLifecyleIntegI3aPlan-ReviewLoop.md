# I3a Common Pass Plan Acceptance

## Status

Status: **Plan accepted at Pyrolyze
`0a0968b848809d5cbaf33d66a61bb7705cd844d2` after
`PytoLifecyleIntegI3aPlan-ReviewConsistency.md` and
`PytoLifecyleIntegI3aPlan-ReviewSafety.md` both reported GO. This accepts the
gated implementation addendum only, not product implementation, implementation
feasibility, I3a completion, roll-build, or runtime activation.**

Date: 2026-10-03. The addendum's reviewed bytes remain unchanged; this adjacent
record supplies acceptance status without altering the reviewed object. The
controlling integration plan remains unchanged at blob
`81d004dc44bc84516a3484e2a64be9667f0657bc`.

## Tuple And Evidence

Review tuple: Pyrolyze `0a0968b848809d5cbaf33d66a61bb7705cd844d2`,
yidl-lifecycle `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`, YIDL
`95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`, Astichi
`387ca5e1da76204ee60922094734c13ee36383c0`, parent context
`a20f8cfb633a268925464eb27728d1934a70aea9`.

- Both fresh, peer-blind reviewers verified the tuple and product/object
  integrity at the start and end of their reviews. Dependency source inspection
  used committed views, excluding dirty adjacent work.
- Both axes reported zero P0/P1/P2/P3 findings. No remediation round was
  required; there are no blocking findings to self-close or defer.
- Both independently emphasized the same residual risk: the existing API may
  not support every dirty/metadata/borrowed-failure path. This is risk convergence,
  not a claim that either reviewer proved those paths feasible.
- Reports are saved verbatim, with generated canonical prompts and the package
  adjacent. The prompt-dispatch correction is recorded in the package; no
  verdict under malformed input counts toward acceptance.
- The lane-owner focused baseline passed **27 tests in 4.41s** on working
  dependencies. Reviewers ran no tests. This is not evidence that the committed
  dependency tuple reproduces that result or that new behavior is implemented.
- Product code, tests, historical JSON baselines, controlling-plan bytes,
  selector defaults, library work and parent pointers were not changed. Only
  the new planning/review documents are committed. No tag, push, merge, or
  default-runtime activation was requested or performed.

## Accepted Scope And Next Gate

The addendum specifies common candidate membership/UI, dirty/site metadata,
local visitation, local pass versus key activity, the deletion/retention ledger,
and a canonical common-pass test package. It preserves existing completion
cohorts, independent child publication, constructor/MI rules, and resource-domain
dispatch pending its own migration.

Next, after implementation authorization, settle the actual dependency tuple
and execute step 1: map every writer/read facade/key/completion owner and probe
out-of-pass invalidation, shared-key borrowed recovery, and cleanup versus field
discard. A failed permission/isolation gate requires a bounded user decision
before changing that path; it is not permission for snapshots, selective
callbacks, new cohorts, or false I3a completion.

The campaign remains accepted through **I1b implementation**. This document
adds **I3a plan acceptance**, not I3a implementation acceptance. I3b/I3c/I4,
D4/D5, U1/U2, full-suite debt, and activation retain their existing status.

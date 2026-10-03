# Single-Cohort Render Design Acceptance

## Status

Status: **Gated design accepted at Pyrolyze
`3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5` after
`PytoLifecyleIntegSingleCohortPlan-ReviewConsistency-1.md` and
`PytoLifecyleIntegSingleCohortPlan-ReviewSafety-1.md` both reported GO.
This accepts the single-cohort amendment only, not runtime implementation,
implementation feasibility, I3a completion, roll-build, or default activation.**

Date: 2026-10-03. Reviewed document bytes remain unchanged. The amendment's
DRAFT status describes its reviewed snapshot; this adjacent ledger supplies
acceptance without rewriting that snapshot or historical review reports.
The campaign still has implementation acceptance through I1b only.

## Settled Tuple

| Repository | Reviewed Revision |
| --- | --- |
| Pyrolyze | `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5` |
| yidl-lifecycle | `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

Both fresh reviewers used exact committed product/dependency views, verified
all tuple HEADs at start/end, and never read the current-round peer's report.
Dirty lazy/mutable lifecycle work, YIDL extraction/docs/paper changes and
parent/unrelated submodules were excluded throughout.

## Reviews And Corrections

Initial object: `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`.
Safety returned GO with no findings. Consistency returned GO with two P3
findings: two omitted supersession entries and an incomplete live-test
transition inventory. Reports are filed verbatim; P3 findings were not promoted
into blocking packages. No P0/P1/P2 was found.

A single bounded clarification supplied those entries, the transition ledger,
and the user's non-render registration/callback example as a field/key/writer
ordering audit. Both original reviewers independently classified this as
clarification of the existing design, not an architecture/API/mutation-boundary
change. Both returned GO at the corrected tuple above. Consistency verified
and closed both original counterexamples; Safety found no new P0-P3.

Counts: initial two independent GO verdicts; one nonblocking documentation
correction/re-verdict; **zero architectural remediation rounds**, zero open
P0-P3. Both axes independently emphasized phase-aware completion and resource/
writer gates; this is convergence on residual obligations, not two findings or
proof that those implementation obligations are solved.

### Process Discrepancy

During the Consistency re-verdict, the lane owner filed the completed Safety
re-verdict report. The initial package allowed object-external reports, but the
focused re-verdict prompt accidentally narrowed appearing output to prompts
only. Consistency recorded the unexpected untracked Safety report and did not
read it. All committed HEADs, reviewed document bytes, source/test files, and
excluded dependency listings remained unchanged. Its GO expressly does not
certify prompt-only workspace noise; acceptance here makes no such claim.

This is recorded rather than retrospectively erased or treated as reviewer
closure of a nonexistent finding. Future prompts must consistently permit all
owned review outputs, or reports must be held until both reviewers finish.
The lane owner ran the canonical skill; Safety noted it could not discover the
skill locally and did not claim independent process certification. Its report
nevertheless addresses the supplied read-only/tuple/blindness/verdict contract.

## Verification And Change Boundaries

The latest pinned-dependency focused baseline passed **29 tests in 11.50s**.
This verifies the existing runtime/preflight characterization only, not the new
contract. No source or test assertion changed during the documentation
correction, and no full-suite rerun is claimed for it. Historical preflight
counts remain 819 passed/13 failed/20 skipped in the default suite, and
41 passed/14 failed in the broader decomposed subset. Failure-name debt is
unchanged and not waived.

Whitespace/path checks passed for the final artifact range. Reports are saved
with their exact text and one terminal newline. Only Pyrolyze plan/preflight
and review artifacts were committed; no runtime/library changes, parent pointer,
tag, push, merge, worktree, or runtime-selector switch was made.

## Accepted Direction And Next Gate

One root manager supports multiple semantic keys. Nested render work shares
one outer render-key completion owner; local success remains provisional and
an entered pass failure is sticky even if caught. Separately accepted
registration/callback work keeps its own key/completion rules. A shared
registry still requires an explicit writer/authorization/removal-order audit;
independent keys are not separate overlays or atomic cross-key completion.

Next is **SC1**, after runtime implementation authorization: private completion
owner/local-scope mechanics, real-manager failure/admission tests, and independent
implementation review before SC2 wiring. Resource/notification routes, dirty/
metadata policies, L0/D5 prerequisites, and I3a snapshot removal remain explicit
gates. No broad production activation or I3a completion follows from this ledger.

### SC1 Implementation Review Outcome

The authorized next checkpoint was implemented privately at
`84d4ab6116e0a743394a6269f09e026607402d80`, without live wiring. Its independent
Code/State review returned NO-GO: two shared helper failure roots plus a
missing supported manager-ownership observation for failed-attempt reuse.
See `PytoLifecyleIntegSC1-ReviewLoop.md` and
`PytoLifecyleIntegSC1-RemPlan-1.md`. SC1 is not accepted; the next decision is
whether to authorize that bounded library prerequisite, not to start SC2.
This does not revoke the single-cohort design choice or certify the plan's
original no-library-change feasibility assertion.

### Authorized SC1 Remediation

On 2026-10-04 the operator approved the bounded ownership-observation and
stale-scope manager prerequisite plus private helper corrections. The controlling
plan now replaces its original no-library-change assertion explicitly. A fresh
dual implementation review is required because that shared boundary changed;
the original NO-GO reports remain verbatim. SC2 remains gated until correction,
tests, and reviewer closure agree on the same settled tuple.

### SC1 Remediation Accepted

The fresh Code/State reports both returned GO at Pyrolyze
`7a5d16cb5f6fea9a4d9640e6d443b7e5165a4ead` / yidl-lifecycle
`335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`, with YIDL/Astichi pinned as
recorded in the SC1 ledger. Both independently verified the original
counterexamples; all original blocking roots are closed, with no new finding.
This accepts private SC1 mechanics and its bounded manager prerequisite only.
Live integration remains accepted through I1b; SC2 render wiring, resources,
registration/removal policy, field migration, and activation are not accepted.

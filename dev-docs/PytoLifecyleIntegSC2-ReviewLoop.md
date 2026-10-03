# SC2 Field-Only Render Wiring Review

Status: **round 1 NO-GO; final bounded remediation pending fresh dual acceptance**.
Date: 2026-10-04. This does not activate production or resource-bearing routes.

## Settled Tuple

| Repository | Revision |
| --- | --- |
| Pyrolyze implementation | `53c41674f43ab97401ac9b30a79575c19ab5dca9` |
| Pyrolyze implementation base | `1b246d47e934835a4871fbbfc651fae78440b913` |
| yidl-lifecycle | `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

The controlling DRAFT is `PytoLifecyleIntegSC2.md`. The operator approved its
private graph-level gate instead of changing the mixed-resource live routes
before SC3. `PytoLifecyleIntegSingleCohortPlan.md` carries the precedence notice.
Historical assertions and JSON remain live on unactivated graphs; this is not
a skip or a full activation claim.

## Gates

| Gate | Result |
| --- | --- |
| Focused, after formatting | 80 passed in 13.68s |
| Full default, before final mechanical formatting | 870 passed, 13 failed, 20 skipped, 1 warning in 46.23s |
| Full default, settled implementation after formatting | 870 passed, 13 failed, 20 skipped, 1 warning in 45.20s |
| Broader decomposed, unactivated | 41 passed, 14 failed in 2.19s |
| Black, three new Python files | Check passes, Python 3.12 target |
| Implementation whitespace/paths | Check passes; no absolute machine paths added |

All tests use committed dependency exports rather than the dirty workspace
sources. Full failure names match the accepted baseline: eleven visitor/export
and two host-order failures; broader failure names match the nine app-context,
one mount-advert, one generation, and three event-handler cases. No full green
claim, failure waiver, or historical-golden regeneration is made. Lifecycle
source is unchanged, so its earlier acceptance evidence remains that tuple's
evidence rather than a newly run lifecycle gate.

## Review Dispatch

Fresh strongest-inherited, peer-blind reviewers Erdos (Code) and Popper (State)
were dispatched together against this tuple, with isolated contexts. Their
prompts were generated from the review-loop canonical template and filed as
`PytoLifecyleIntegSC2-PromptCode.md` and
`PytoLifecyleIntegSC2-PromptState.md`. They are read-only, verify the tuple at
both ends, may run pinned-source focused tests/in-memory probes, and cannot
read the other current-round report. Reports are held until both finish.

Unrelated `RenderingBackendBugList.md`, dirty lifecycle lazy/static/mutable
work, dirty YIDL docs/paper/extraction work, parent pointers, and unrelated
submodules are excluded. No tags, push, merge, worktree, or dependency changes.
The product tree and HEAD remain settled while review runs; only process
artifacts may appear untracked.

Remediation count: zero. No findings are self-closed. Any P0/P1/P2 requires
one merged remediation plan/patch and reviewer verification of its original
counterexample; the two-round architectural cap applies.

## Initial Verdict Merge

Code and State both returned NO-GO with five P2 findings. Reports were held
until both completed, then filed verbatim. Independent convergence covers
direct retirement (Code P2-3 / State P2-2) and published debug membership
(Code P2-5 / State P2-4). The other findings concern constructor ownership,
transitive retirement, lexical execution claims, no-op identity admission,
and discarded nested caches. See `PytoLifecyleIntegSC2-RemPlan-1.md` for every
disposition and closure test. No finding is self-closed; SC2 remains unaccepted.

## Remediation Round 1 Settlement

One bounded patch covers all ten IDs/eight correction groups, with tests run
red before source changes. Seventeen new narrow cases and the extended canonical
membership target are green; the accepted SC1 kernel and dependencies are
unchanged. Final gates: focused **97 passed in 13.61s**; full default **887
passed, 13 failed, 20 skipped, 1 warning in 45.75s**; broader unactivated
**41 passed, 14 failed in 2.34s**. Failure identities remain exactly baseline.

Fresh Code/State contexts are required because constructor admission and
terminal execution call graphs changed. The prior reports and merged
remediation plan are legitimate common inputs; current-round reports remain
peer-blind. Require an original-counterexample closure table and classification
of any new architectural root. No finding has been self-closed. Remediation
count: one implemented, zero accepted. The first review identified the SC2
execution-ownership root; the two-round cap remains in force.

Unrelated `RenderingBackendBugList.md` and `RenderingBackendDiscussionReport.md`
and dirty dependency/parent work remain excluded. No production/resource-route
activation, dependency change, tag, push, merge, or worktree is authorized here.

### Revised Tuple And Dispatch

Pyrolyze corrected implementation: `ca731d89a0086e0bff48dc426d1b5b1472aba869`.
All dependency/parent revisions in the initial tuple remain unchanged. The
implementation diff is `53c41674..ca731d89`, cumulative SC2
`1b246d47..ca731d89`. Its controlling DRAFT and merged remediation plan are
committed in that same corrected revision.

Fresh strongest-inherited reviewers Singer (Code) and Avicenna (State) were
dispatched in isolated contexts, from mechanically generated canonical prompts
`PytoLifecyleIntegSC2-PromptCode-1.md` and
`PytoLifecyleIntegSC2-PromptState-1.md`. Both prior reports are common inputs;
neither current report is shared. Reports are held until both finish. The
settled two-target review subset passed **33 tests in 4.22s**, after preserving
the original JSON indentation mechanically. No product bytes/HEAD change
during review; only process evidence may appear or change.

## Round 1 Verdict Merge And Round 2 Settlement

Singer and Avicenna both returned NO-GO. Their complete reports are filed
verbatim as `PytoLifecyleIntegSC2-ReviewCode-1.md` and
`PytoLifecyleIntegSC2-ReviewState-1.md`. Blind convergence identified candidate
deactivation losing a staged sibling and repeat-pass omission bypassing
component retirement. State also found incomplete publication-only cache
reconciliation and a direct constructor collision bypass. Both reviewers
classified all remaining findings as localized non-architectural omissions.

`PytoLifecyleIntegSC2-RemPlan-2.md` maps every finding to a correction and
original-counterexample test. The merged correction changes no accepted SC1
kernel, dependency, resource protocol, public option, or activation scope.
Candidate retirement references are admission data only; affected render roots
are references only, not copied managed state or another undo authority.

Final gates: focused **107 passed in 14.12s**; full default **897 passed,
13 failed, 20 skipped, 1 warning in 43.45s**; broader unactivated **41 passed,
14 failed in 2.23s**. Failure identities remain exactly baseline. No complete
green claim or self-closure is made. Remediation count: two implemented,
zero accepted. This is the final authorized bounded remediation; any further
architectural patch requires an operator decision.

Because constructor admission and cache/scheduler reconciliation call graphs
changed, use fresh peer-blind Code/State contexts rather than the prior
reviewers. Both initial and round-1 reports are legitimate common inputs;
current-round reports remain held until both reviewers finish. Require a full
prior-finding closure table and explicit architectural-root classification.

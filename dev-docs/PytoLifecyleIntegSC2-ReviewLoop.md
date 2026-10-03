# SC2 Field-Only Render Wiring Review

Status: **accepted at Pyrolyze `a7bf0e92001f1c881ed81cd6e58064d8e8b4da51`
with the pinned dependency tuple below, after fresh Code/State round-3 reports
both returned GO. This accepts only the private SC2 field-only checkpoint.**
Date: 2026-10-04. This does not activate production or resource-bearing routes.

## Accepted Tuple

| Repository | Revision |
| --- | --- |
| Pyrolyze implementation | `a7bf0e92001f1c881ed81cd6e58064d8e8b4da51` |
| yidl-lifecycle | `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent context only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

Reports: `PytoLifecyleIntegSC2-ReviewCode-3.md` and
`PytoLifecyleIntegSC2-ReviewState-3.md`. The reviewed controlling document
remains a DRAFT snapshot; this adjacent ledger supplies acceptance without
rewriting reviewed source/test bytes. Earlier NO-GO/pending entries below are
historical and superseded by the final verdict merge. Existing live routes
remain unactivated until their own SC3 gates; I3a completion is not claimed.

## Initial Settled Tuple (Historical)

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

### Round 2 Tuple And Dispatch

Settled Pyrolyze implementation: `4d1b9b089333e99cb98381939db311c2b7ce8bde`.
All dependency/parent revisions in the initial tuple are unchanged. Correction
diff: `ca731d89..4d1b9b08`; cumulative SC2: `1b246d47..4d1b9b08`.
The controlling DRAFT and final merged remediation plan are committed there.

Fresh strongest-inherited reviewers Hegel (Code) and Descartes (State) were
dispatched together in isolated contexts using mechanically generated canonical
prompts `PytoLifecyleIntegSC2-PromptCode-2.md` and
`PytoLifecyleIntegSC2-PromptState-2.md`. Both prior rounds are common evidence;
neither current report is shared. Reports remain held until both finish.
The implementation and HEAD remain frozen; only process evidence is edited.
The settled two-target review subset passed **43 tests in 4.25s** against
the same clean dependency exports. Black checks for the three new Python
files and owned-source/path whitespace checks pass. No excluded files were
staged in the corrected implementation commit.

## Round 2 Verdict Merge And Stop

Both reports were held until both completed, then filed verbatim:
`PytoLifecyleIntegSC2-ReviewCode-2.md` and
`PytoLifecyleIntegSC2-ReviewState-2.md`. Both returned **NO-GO**, each with
one new P2 finding. Both independently verified the same five HEADs unchanged
at start/end, reran the original counterexamples, and confirmed all original
counterexamples close. Their independent narrow/canonical gates passed
**43 tests in 4.34s** (Code) and **43 tests in 4.12s** (State).

The new findings have the same numeric ID on different axes but different
roots; this is not blind convergence on one defect:

| Axis / ID | Remaining defect | Required bounded correction and closure |
| --- | --- | --- |
| Code P2-9 | A second owned render root can execute and update a component whose actual child is another root | Reject duplicate owned-root construction before lifecycle initialization; require reciprocal owner/child identity before execution and UI propagation. Cover committed and candidate owners, inside/outside attempts, caught rejection, unchanged callbacks/queues/UI/generation, and normal nested reuse |
| State P2-9 | Newly introduced unseen component subtrees are filtered out without retirement preflight | Preflight every candidate subtree selected for removal, not only preceding/current children. Cover direct components and native leaves containing components, discarded current UI, no generation advance or queued orphan, and clean retry |

Both reviewers explicitly classify their findings as **localized,
non-architectural omissions**, not new architectural roots. The original SC2
execution-ownership root remains the only recorded architectural root. Two
bounded remediation rounds have nevertheless been implemented; this package
does not authorize an automatic third patch. Return the two findings to the
operator for a strictly non-architectural correction decision or a revised
checkpoint boundary. No finding is waived and no acceptance is claimed.

Current counts: three dual review rounds, two implemented remediation rounds,
zero accepted SC2 rounds, all original counterexamples verified closed, two
open P2 findings, zero open P0/P1/P3. The focused107/full897/broader41 evidence
above remains valid at the reviewed tuple but does not close these additional
sequences. The 13/14 unrelated baseline failures remain visible and unwaived.

**Next action:** obtain the operator's disposition on those two admission
corrections. Do not start SC3 resource adapters, broaden activation, or remove
snapshots while SC2 remains unaccepted. If a further localized patch is approved,
test these exact sequences red first, settle it, then obtain independent
original-counterexample closure and a new verdict. No architecture, manager,
resource protocol, or dependency change is implied by that proposal.

Artifact whitespace note: the verbatim State report retains a Markdown
hard-break space on its review-object line. This is preserved testimony,
not an owned-source whitespace defect. Reviewed source/test bytes remain
unchanged; the filing commit changes process records only.

## Operator-Authorized Localized Follow-Up

The operator subsequently directed "bounded correction and re-review" on
2026-10-04. This supersedes the stop for operator disposition above, but only
for the two non-architectural P2-9 findings. `PytoLifecyleIntegSC2-RemPlan-3.md`
pins that boundary and both original-counterexample closure requirements.
Any architectural root identified during this follow-up stops the lane; no
automatic fourth correction or scope expansion is authorized.

New narrow cases ran red: **17 failed, 1 passed, 42 deselected in 2.87s**.
The passing case already rejected a discarded owner through existing parent
membership admission. The merged correction adds only reciprocal owned-root
checks and preflight of unseen candidate subtrees. The initial narrow/canonical
green run passed **61 tests in 4.39s**; initial formatted seven-file focused
verification passed **125 tests in 12.68s**. Earlier canonical success targets
remain unchanged. Full and broader regression evidence will be recorded before
settling the review tuple; these green tests are not reviewer closure.

### Follow-Up Settlement Evidence

The additional direct attachment cases ran red before the reciprocal guard
was added to the existing constructor seam. Final gates after that addition
and formatting:

| Gate | Result |
| --- | --- |
| Focused seven files | 127 passed in 12.79s |
| Full default | 917 passed, 13 failed, 20 skipped, 1 warning in 43.96s |
| Broader decomposed, unactivated | 41 passed, 14 failed in 2.10s |
| Narrow/canonical review subset | 63 passed in 4.46s |
| Black three new Python files / owned-source whitespace and paths | Pass |

All gates use the unchanged committed dependency exports. Full failure
identities are the eleven visitor/export and two host-order baseline cases;
broader failure identities are the nine app-context, one mount-advert, one
generation, and three event-handler baseline cases. No full green claim,
failure waiver, canonical/historical target regeneration, dependency mutation,
or resource-route activation is made.

The follow-up changes four runtime modules plus narrow fault tests and process
documents. The small reciprocal check is shared by existing constructor,
execution, publication, and UI-propagation admission paths. Every candidate
selected by the unseen filter now receives the existing retirement preflight.
Neither correction introduces another field authority or resource callback.
Fresh dual review is required because those entry call graphs changed. Original
P2-9 closures and preservation of all earlier closures remain reviewer-owned.

### Follow-Up Tuple And Dispatch

Settled implementation: `a7bf0e92001f1c881ed81cd6e58064d8e8b4da51`.
Correction diff: `4d1b9b08..a7bf0e92`; settlement diff:
`85ee82a8..a7bf0e92`; cumulative SC2: `1b246d47..a7bf0e92`.
Lifecycle/YIDL/Astichi and parent revisions in the pinned tuple are unchanged.
The controlling document and RemPlan-3 are committed in this correction.

Fresh strongest-inherited McClintock (Code) and Harvey (State) were dispatched
together in isolated, peer-blind contexts using mechanically generated canonical
prompts `PytoLifecyleIntegSC2-PromptCode-3.md` and
`PytoLifecyleIntegSC2-PromptState-3.md`. Previous reports are legitimate common
inputs; neither current prompt/report is shared. Reports are held until both
finish. Source/test bytes and HEAD remain frozen; process evidence may appear
or change. Any new architectural root stops this localized follow-up.
The settled narrow/canonical subset passed **63 tests in 4.48s** with the
same committed dependency exports; source/tests and HEAD remained unchanged.

## Final Verdict Merge And Acceptance

McClintock (Code) and Harvey (State) both returned **GO**, with zero open
P0/P1/P2/P3 findings. Reports were held until both finished and filed verbatim.
Both verified every tuple HEAD unchanged at start/end, independently reran
both original P2-9 counterexamples, and preserved all earlier closures through
execution or source retracing. Their narrow/canonical runs passed **63 tests
in 4.44s** (Code) and **63 tests in 4.27s** (State).

Independent convergence here is on successful closure and the retained scope,
not discovery of another shared defect. Code additionally exercised a first
uninstalled root retained across actual child installation and queued stale
delivery; State checked the unseen filter before membership mutation and
recovery/generation behavior. Neither found a new architectural root or scope
widening. The implementer did not self-close the P2 findings.

Counts: four dual review rounds (initial plus three numbered follow-ups),
two prior remediation rounds and one operator-authorized strictly localized
follow-up; **all seventeen recorded P2 counterexamples verified closed** and
zero open SC2 review findings. The original execution-ownership architectural
root remains the only recorded one. This does not waive the unrelated default
13/broader 14 baseline failures or certify a fully green integration suite.

Acceptance is limited to the private, graph-level field-only proof on the
exact accepted tuple above. Root/leaf/plain/component value publication,
sticky caught failure, manager sharing, admission, and clean discard/retry are
covered. Resource-bearing routes, broad/default activation, L0/D5 completion
prerequisites, dirty/site metadata policy, and snapshot removal remain gated.
Lifecycle/dependency source and parent pointers are unchanged. No tag, push,
merge, worktree, or selector/default change is included.

**Next checkpoint: SC3.** Inventory binding/handler/component resource
completion, notifications, and registration/removal writers; settle each
pending L0/D5 prerequisite before activating its route. Move participating
render-owned delivery to the outer decision without duplicating lifecycle
field application or inventing resource rollback. SC4 follows only after
that proof, to remove redundant snapshots and finish I3a. Acceptance here is
not authorization to implement those separate checkpoints.

The filing commit changes review/status records only; accepted runtime/test
bytes stay at `a7bf0e92`. Reports and dispatched prompts retain their exact
text (with a terminal newline); owned-source whitespace/path checks passed.

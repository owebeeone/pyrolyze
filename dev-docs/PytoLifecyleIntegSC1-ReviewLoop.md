# SC1 Private Render Owner Acceptance

## Status

Status: **accepted at Pyrolyze
`7a5d16cb5f6fea9a4d9640e6d443b7e5165a4ead` / yidl-lifecycle
`335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`, with the pinned YIDL/Astichi
revisions below, after fresh Code/State reports returned GO. This accepts
private SC1 mechanics and the bounded manager prerequisite only.**
The implementation document remains a pending-review snapshot; this adjacent
ledger records gates and later acceptance without rewriting reviewed bytes.
Only private mechanics were reviewed. Live implementation acceptance stays
through I1b. SC1 is accepted but unwired; SC2/I3a and default activation are
not claimed. The initial NO-GO record below is historical and superseded by
the round-1 verdict merge at the end of this ledger.

## Settled Tuple

| Repository | Revision |
| --- | --- |
| Pyrolyze implementation | `84d4ab6116e0a743394a6269f09e026607402d80` |
| Pyrolyze implementation base | `0ab81be3a83eb8a5f3f1ab426353c9eb90c758a7` |
| Accepted controlling design | `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5` |
| yidl-lifecycle | `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent context/exclusions only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

Review tier: dual Code/State. Fresh peer-blind reviewers receive generated
canonical prompts and the same exact object, with separate mandates. The lane
owner holds current-round reports until both finish. Prompts and this ledger
may appear untracked during review; no product source/test edit or HEAD movement
is authorized inside that review window. Dirty dependency and parent work is
excluded. Tests use committed dependency source exports, not those dirty files.

## Verification

Python 3.12.12, existing workspace pytest environment; pinned source exports,
bytecode writes disabled and pytest cache provider disabled. Commands and
participant audit are in `PytoLifecyleIntegSC1.md`.

| Gate | Result |
| --- | --- |
| Focused SC1 plus five-file existing baseline | **55 passed in 10.47s** |
| Full default regression | **845 passed, 13 failed, 20 skipped, 1 warning in 41.93s** |
| Broader decomposed eight-file subset | **41 passed, 14 failed in 1.87s** |
| Formatting | Black check, Python 3.12 target, both new Python files pass |
| Whitespace/paths | Staged diff check passes; no committed absolute machine path |

The focused delta is 26 new narrow mechanics/adversity cases; the existing 29
tests remain green without changing assertions or historical snapshots. The
full-suite delta is the same 26 passes over the prior 819-pass baseline. The
13 default failures remain the visitor/export `own_committed_ui_entries`
cluster and the two host-order cases; the 14 decomposed failures remain the
nine app-context `_scope_active`, one mount-advert, one generation, and three
event-handler `ui_state` cases. These are recorded debt, not waivers or a full
green claim. The tkinter deprecation warning is unchanged.

Only the new owner module, its test module, and the implementation document
changed in the reviewed commit. No live context module, dependency library,
selector/default, legacy characterization, parent pointer, tag, push, merge,
or worktree changed.

## Review Record

`PytoLifecyleIntegSC1-ReviewCode.md` returned NO-GO with three P2 findings;
`PytoLifecyleIntegSC1-ReviewState.md` returned NO-GO with two P2 findings.
Reports were held until both finished, then filed verbatim. Both verified the
same tuple at start/end and independently reran the 26 narrow tests; passing
tests did not prevent their in-memory probes finding missing transitions.

Blind convergence: Code P2-1 / State P2-1 identify exceptional validation
ownership-loss misclassification; Code P2-3 / State P2-2 identify recursive
local completion bypassing sticky failure/cleanup accounting. Code P2-2 adds
the unsupported external-borrower reuse certificate. Five findings reduce to
three distinct roots, all accepted in `PytoLifecyleIntegSC1-RemPlan-1.md`.

The third root cannot be closed through the pinned public manager interface
without revisiting scope. No private-field workaround, unsafe commit probe,
silent retry-contract change, or dependency change was made. The lane stops
at that explicit decision, not at an invented successful checkpoint. Counts:
one dual review round, zero completed remediation rounds, zero closed P2 roots,
three open P2 roots, no P0/P1/P3. No reviewer proof or pre-commitment closes a
finding without its corrected counterexample being verified.

Artifact whitespace note: the verbatim State report has a Markdown hard-break
space on its date line, and both generated prompts retain a trailing template
substitution space on their tuple line. These three artifact-only diff-check
warnings are preserved rather than rewriting reviewer testimony or the
dispatched prompts. The reviewed implementation's whitespace/path gates passed;
no all-artifact whitespace-clean claim is made.

## Next Gate

SC1 remediation is now accepted. Next is the separately gated SC2: actual
root/local-pass wiring and the canonical resource-free render proof. Resource
completion, registration/removal writer policy, generation notifications,
dirty/metadata field authority, and snapshot removal remain later gated work.

## Remediation Round 1 Pending Review

The operator approved the library prerequisite and helper corrections. See
`PytoLifecyleIntegSC1-Remediation.md` for the exact corrected contract, TDD
counterexamples, clean-source commands, and regression evidence. Manager
checkpoint is `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901`; YIDL/Astichi remain
pinned. Fresh Code/State reviewers are required because the supported ownership
boundary changed. No original finding is self-closed and no live context path
has been wired. Original reports/prompts remain immutable historical evidence.

### Fresh Round 1 Object

| Repository | Revision |
| --- | --- |
| Pyrolyze corrected implementation | `7a5d16cb5f6fea9a4d9640e6d443b7e5165a4ead` |
| yidl-lifecycle corrected manager | `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901` |
| YIDL | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi | `387ca5e1da76204ee60922094734c13ee36383c0` |
| Parent context/exclusions only | `a20f8cfb633a268925464eb27728d1934a70aea9` |

Parfit (Code) and Locke (State) were dispatched as fresh, strongest-inherited,
peer-blind read-only reviewers from the canonical template. Their prompts are
`PytoLifecyleIntegSC1-PromptCode-1.md` and
`PytoLifecyleIntegSC1-PromptState-1.md`. Reports are held until both finish;
only review artifacts/ledger may change meanwhile. No product edit or HEAD
movement is permitted in that review window.

Clean-source gates: focused **64 passed in 11.04s**; default regression
**854 passed, 13 failed, 20 skipped, 1 warning in 47.20s**; decomposed broader
subset **41 passed, 14 failed in 2.48s**. The failure identities remain the
recorded debt. Lifecycle **273 passed, 1 failed, 46 skipped in 85.57s**; the
owned-field hygiene golden mismatch was reproduced on the prior lifecycle
revision with identical pinned dependencies (1 failed, 9 deselected, 6.09s).
No snapshot was changed. The mechanical targets are 35 owner and 18 manager
cases; all are green. Formatting and owned-source whitespace gates pass.

The following verdict merge supersedes the pending status at dispatch.
SC2/live render wiring, resource/registration policy, and field migration
remain separate gates.

### Round 1 Verdict Merge

Both fresh independent reports returned **GO**, with zero new findings, and
verified all original counterexamples against the same corrected tuple:

- `PytoLifecyleIntegSC1-ReviewCode-1.md`: Code P2-1/P2-2/P2-3 closed.
- `PytoLifecyleIntegSC1-ReviewState-1.md`: State P2-1/P2-2 closed, shared
  external-borrower/stale-scope prerequisite independently verified closed.

Reports were held until both finished, then filed verbatim. Both reviewers
reran the 35 owner and 18 manager cases and independently probed original
counterexamples, mixed stale/valid scopes, callback barriers, release faults,
and clean retry. They verified all five HEADs unchanged at start/end; no new
architectural root was reported. Their broader-gate discussion explicitly uses
main-session evidence rather than claiming independent full-suite reruns.

Acceptance is the exact round-1 tuple above, not the excluded dirty dependency
bytes or future live wiring. Counts: two dual review rounds (initial plus
fresh remediation), one accepted architectural remediation round, all three
unique P2 roots closed, zero open P0/P1/P2/P3. Existing regression debt remains
visible and unwaived. No parent pointer, selector/default, tag, push, merge, or
worktree change was made.

Artifact whitespace note: the State report's date retains its Markdown hard
break verbatim; the canonical prompts retain the tuple substitution's trailing
space. These artifact-only warnings do not change the owned product-source
whitespace result. Reviewed source bytes remain at the accepted revisions;
later filing commits change review records only.

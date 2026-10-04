# Holder-First Integration Plan Review Loop

Status: **plan-only acceptance at Pyrolyze
78e3184132eae33169ae3c329be35f3146ed338a after both original reviewers returned
GO on remediation 1; no runtime implementation certified**.

Scope: the revised integration plan's holder-first sequence, retained completion
cohorts, and I1a constructor prerequisite. This is a fresh campaign, not renewed
acceptance of a historical tuple. See the review package for authority and
deferrals. D4/D5 remain pending; U1/U2 are later unification work.

Review tier: dual Consistency/Safety, fresh isolated contexts, inherited model.
Reports are filed verbatim. Any open P0/P1/P2 blocks; two-remediation-round cap.
No tests or writes by reviewers. No implementation starts before this gate.

Exact tuple, prompt paths, agent IDs, verdicts, remediation counts, accepted plan
blob, and evidence will be appended after dispatch. No tags, pushes, or parent
pointer commit is part of this campaign.

## Round 1

Pyrolyze `0de04bc487b3e03c9444e40ce02587046b33dcec`; lifecycle
`cdf08544deea846bca4fa7e0c468ebee8d41e138`; YIDL committed view
`95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`; Astichi
`387ca5e1da76204ee60922094734c13ee36383c0`; parent context
`a20f8cfb633a268925464eb27728d1934a70aea9`. Dirty YIDL/parent bytes excluded.

| Axis | Reviewer | Agent ID | Verdict |
| --- | --- | --- | --- |
| Consistency | Goodall | 01a0feeb-1129-71d1-8f92-57a93d9b1358 | NO-GO: P2-1, P2-2; P3-1 |
| Safety | Tesla | 01a0feeb-11d1-7552-8079-346c92ab2430 | NO-GO: P2-1, P2-2 |

Both independently found raw callback-key receiver equality and the unclassified
B-then-A behavioral fix. One merged remedy restores the already controlling
reference contract; see `PytoLifecyleIntegHolderFirstPlan-RemPlan-1.md`.
No runtime source changes. Original reviewers must verify their own findings;
neither lane-owner disposition nor the peer's report closes them.

Pre-dispatch evidence: 5 characterization cases passed in 1.31s; seven focused
LCM files plus those cases passed all 37 tests in 1.99s. The new two callback
snapshot cases first failed on absent expected data; both actual reference
outputs were inspected and matched the one explicitly added snapshot.

## Independent Closure And Acceptance

Both original reviewers returned GO for Pyrolyze
`78e3184132eae33169ae3c329be35f3146ed338a`; the other four tuple revisions and
excluded dirty views above are unchanged. Their complete reports are filed
verbatim with suffix `-1`. Every P2 and the P3 were independently closed against
their original source-traced counterexamples. No new architectural root cause
was found; both classified the remedy as conformance to the controlling
reference rule, not a changed interface or completion boundary.

Remediation rounds: **1 of 2**. Accepted plan blob:
`81d004dc44bc84516a3484e2a64be9667f0657bc`. This evidence commit preserves those exact
plan bytes. Earlier campaign GO reports are historical, not transferred.

The new seven-case characterization suite passed in 1.74s. Before runtime edits,
the full default suite reported **809 passed, 13 failed, 20 skipped, 1 warning
in 30.55s**; all 13 failure names match I0's existing visitor/export and
host-ordering clusters. Source and five historical snapshot diffs from the
initial package are empty; whitespace checks passed. No runtime or library API
change is part of plan acceptance.

The user authorized proceeding with the holder-first sequence. I1a can now
start as a bounded constructor prerequisite with red/green/regression evidence;
this is not a roll-build/tag request or completed holder migration. D4/D5 and
U1/U2 remain outside that checkpoint. Both plan reviewer agents are closed
after filing their final reports.

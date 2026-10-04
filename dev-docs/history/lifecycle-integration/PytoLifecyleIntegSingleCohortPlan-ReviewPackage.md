# Single-Cohort Amendment Review Package

Status: **DRAFT review pending**, 2026-10-03. Dual peer-blind Consistency/Safety;
no runtime implementation or default activation.

## Settled Object

- Pyrolyze: `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7`, draft design and its precedence notices/preflight evidence.
- yidl-lifecycle: `1439d2fdc3776754cce2f4f8ff38dcc78ddc53c4`.
- YIDL: `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4`.
- Astichi: `387ca5e1da76204ee60922094734c13ee36383c0`.
- Parent context: `a20f8cfb633a268925464eb27728d1934a70aea9`.

Controlling DRAFT: `dev-docs/PytoLifecyleIntegSingleCohortPlan.md` at the Pyrolyze revision above.
Source code is unchanged from I1b; additional tests characterize the old runtime.
Both reviewers read committed dependency views only. Dirty lazy/mutable lifecycle,
YIDL extraction/docs/paper work and parent/unrelated edits are excluded.
The current Pyrolyze tree was clean immediately after the object commit;
only review prompts/package/reports/ledger may be added during this gate.

## Evidence And Process

The latest pinned-dependency five-file baseline passed **29 tests in 11.50s**.
Historical full/broader results remain 13/14 existing failures, not repaired.
No new semantic target test was implemented; this is design review only.

Canonical generated prompts are adjacent with `ReviewPromptConsistency` and
`ReviewPromptSafety` suffixes. Fresh reviewers are read-only and peer-blind,
verify all tuple heads and status at start/end, and return complete reports.
Lane owner files reports verbatim. Any P0/P1/P2 blocks; at most two remediation
rounds. Surface review is not required: no new public API is frozen.

No runtime edits, library edits, tags, push, merge, worktree, default switch or
parent-pointer change is authorized by acceptance of this package.

## Dispatch

Round 1 uses fresh contexts with the parent model inherited:

| Axis | Reviewer | Agent | Object |
| --- | --- | --- | --- |
| Consistency | Huygens | `01a10028-57e8-75e2-99a1-bbe12dd0d945` | `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7` |
| Safety | Carver | `01a10028-589e-7630-b2cd-72e1aa62ea9f` | `bad7b1c7eaae6b09eaede3803f036a1cbb9d05d7` |

Both prompts were generated from the canonical template with one axis role.
Reviewers receive no peer reports; the package stays settled until they finish.
No runtime-source diff exists between the I1b source and this design checkpoint.

## Round 1 Verdicts And Bounded Corrections

Both axes reported GO on the exact draft above. Safety found no P0-P3;
Consistency found two nonblocking P3 documentation issues. Reports are filed
verbatim. There are no blocking findings or architectural remediation packages.

| Finding | Disposition | Closure Check |
| --- | --- | --- |
| Consistency P3-1 | Explicitly enumerate Existing TM Limits' final publication deferral and Event Callback Selection's deactivation paragraph; retain all-key/resource-lifetime/visibility gates | Original reviewer traces those precise old clauses against the new table |
| Consistency P3-2 | Add the live-test transition ledger naming independent-manager/local-activity tests, the external-begin leaf helper, and mixed-resource I0 characterization; preserve source-pinned historical reproduction and original/monolithic observations | Original reviewer accounts for each named live entry and its SC2/SC3 transition, without expected-output normalization or unexplained skips |

The same bounded correction also records the user's discussion of independently
accepted non-render registration/callback work as an SC3 field/key/writer audit
requirement. It does not change the one-render-owner architecture, implicitly
activate other keys, or add a public/library API. Both reviewers will check the
changed range at the corrected exact tuple before final acceptance is recorded.

## Final Verdict

Corrected object: Pyrolyze `3c8a8167830c3c057b91f4ad7b2a0679d13e9ba5`; all dependency/context
revisions above unchanged. Both original reviewers returned GO in reports with
suffix `-1`. Consistency independently closed both P3 counterexamples; Safety
found no new P0-P3. Both classified the delta as bounded clarification, not a
new architecture. Exact acceptance, verification provenance, and the report
output/status discrepancy are recorded in
`PytoLifecyleIntegSingleCohortPlan-ReviewLoop.md`.

This acceptance is of the gated design only. SC1 implementation and all later
wiring/field/resource gates remain unimplemented and require their own evidence.

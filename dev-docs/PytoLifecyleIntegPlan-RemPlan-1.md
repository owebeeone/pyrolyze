# LCM Integration Plan Remediation 1

## Object And Verdict Merge

Initial review object: `dev-docs/PytoLifecyleIntegPlan.md` at Pyrolyze commit
`7f373420d9fde14559985792125559cd4f60a3cb`.

Both independent axes reported NO-GO. There are two unique blocking root
causes; the missing drain-first TM capability was found independently by both
axes. Reports are filed verbatim in
`dev-docs/PytoLifecyleIntegPlan-ReviewConsistency.md` and
`dev-docs/PytoLifecyleIntegPlan-ReviewSafety.md`.

This is one merged, documentation-only remediation patch. It does not implement
the runtime changes, approve unresolved semantics, or activate a roll-build.
The intended architecture is unchanged: one root TM, separate local scope
activity, one publication key, and lifecycle-owned transaction mechanics.

## Finding Dispositions

| Finding | Disposition | Correction | Closure Check |
| --- | --- | --- | --- |
| Consistency P2-1 | Accept; same root cause as Safety P2-1 | Record the pinned fail-fast dispatch, replace the nonexistent-guarantee wording, and require lifecycle-owned failure-completion work before dependent integration slices | Reviewer retraces early failing after-commit and rollback callbacks; plan must gate migration and name multi-participant lifecycle regressions |
| Safety P2-1 | Accept; independently converged with Consistency P2-1 | Use the same prerequisite and require remaining participants' cleanup/delivery attempts, failure reporting, retained publication, and recovery checks | Safety reviewer verifies its A/B/C retirement counterexample is explicitly covered by the prerequisite and that the plan does not assume a next render repairs missed work |
| Safety P2-2 | Accept | Move local-scope entry, per-pass reset/finalization, and completion-ownership guards into I1 before live shared-TM activation; leave I2 responsible for the publication/pass-key coordinator | Safety reviewer retraces nested direct-native rerender, child removal, and failing-pass recovery; all must be I1 exit checks, not deferred to I2 |

No finding is disputed or self-closed. The originating reviewers must verify
the corrected plan and return their closure tables before acceptance.

## Required Plan Changes

1. Distinguish the intended Phase F-1 failure contract from the pinned runtime.
   Existing prepare/apply/after and rollback dispatch can stop at the first
   participant failure; manager teardown does not repair skipped callbacks.
2. Add lifecycle prerequisite L0 after I0's capability/semantic audit. Specify
   owning repository, phase-draining/grouped-failure contract reconciliation,
   approved scope, regression evidence, and gate I2/I4/I6 on completion.
3. Require early failing after-commit, rollback, and after-rollback callbacks
   across multiple participants, including retained committed state, cleanup
   cardinality, error context, and subsequent recovery. Do not mistake a single
   participant's passing hook test for this capability.
4. Repair the I1/I2 checkpoint boundary without changing the final architecture.
   I1 cannot enable live nested TM sharing while local activity still depends
   on graph-wide key activity. Constructor-only seams may be partial preparatory
   work, not a completed operational checkpoint.
5. Update slice and acceptance checks so both prerequisites remain visible.

## Verification And Re-Review

- Check the documentation diff for whitespace errors and machine-specific
  absolute paths; verify no runtime source files changed.
- The focused 32-test baseline and generated-base consistency check were run
  before this documentation patch; they do not prove the proposed runtime
  failure regressions already pass.
- Commit the single plan/remediation/report checkpoint, record its exact tuple,
  and continue the same reviewers for a focused re-verdict. The patch clarifies
  an already stated failure contract and moves its already stated local-scope
  prerequisite into the correct slice; it introduces no new architecture or
  user-facing interface.
- The reviewers classify any newly exposed architectural root cause. The
  review-loop remediation cap remains two rounds.

Status: corrections proposed; no blocking finding is closed until re-review.

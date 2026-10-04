# Lifecycle Integration Completion Plan Remediation 1

## Scope

Initial tuple: Pyrolyze `723460d6c1dce75b70f03e355daf20c248bde8ad`, with the unchanged
dependency tuple in the review package. Both axes returned NO-GO with one P2.
Their reports are filed verbatim; duplicate numeric IDs are qualified by axis.

This is one merged documentation patch. No runtime code, YIDL source, public
API, storage model, transaction ownership boundary, or semantic decision is
changed. It corrects the prescribed facade read and makes the existing Phase
F-1 requirement to attempt all after-hooks precise at each invocation level.
D1-D5 remain pending execution gates.

## Finding Dispositions

| Finding | Disposition | Correction | Closure Evidence Required |
| --- | --- | --- | --- |
| Consistency/P2-1 | Accept; open until original reviewer verifies | Use effective default/working callback selection for staging-elision; retain current-only dispatch and dirty/key semantics | Corrected sketch statically traces published A, local B then A with dirty=False; canonical I3b must prove stable dispatch, pre-publication A, final A, and rollback |
| Safety/P2-1 | Accept; open until original reviewer verifies | Extend L0/D4 to per-hook draining of independently declared same-key/inherited hooks; separately require I4/I6 domain-batch per-action draining | Lifecycle generated coverage obligation: first same-key hook throws, second cleans up, another participant runs; commit/rollback and inherited composition. Integration obligation: first batch action throws, second unsubscribes; exactly-once attempts, state/error/key/scope/recovery observations |

No finding is disputed or silently waived. No independent convergence on one
root cause was reported: these are complementary facade-selection and
failure-isolation-unit findings.

## Root Cause And Re-Review Choice

Consistency classified its defect as bounded, not architectural. Safety
classified the missing required-work failure-isolation unit as a new
architectural root cause: **one architectural root cause discovered so far**.

The patch does not introduce a new interface or ownership/mutation boundary.
Phase F-1 already states that all after-commit/after-rollback hooks are attempted;
this correction covers composition inside an existing participant and explicit
domain batches instead of falsely crediting manager-level draining alone.
Use the original reviewers for focused counterexample verification, retaining
their context. Require them to state whether this patch materially changes the
reviewed architecture/interface boundary; if it does, start a fresh numbered
dual review before acceptance rather than transfer the old proof.

Remediation rounds used: **1 of 2**. A reviewer-identified third new architectural
root cause stops the object for an operator redesign-or-accept decision.

## Gate Verification

Documentation gate checks: Python-fence AST parsing, shell/fence/path policy,
scoped diff review, and `git diff --check`. Generated runtime regressions above
are mandatory implementation obligations, not tests claimed to exist or pass
during this document-only correction. The already committed four I0 cases
remain historical characterization and do not verify the future runtime fix.

The original reviewer must re-trace its own counterexample on the revised
committed tuple; the lane owner does not self-close either finding.

# Callback Selection Remediation 2

Reviewed revision: Pyrolyze `aa073c8df5ba1a2dc7f8697425298a02c5772f2f`.
Both axes closed their original findings, then independently found the same
pre-child argument-materialization failure gap. This second and final bounded
remediation records that failure on the original private attempt; no new
architecture, publication mechanism, resource category, or library change.

| Finding | Disposition | Closure Evidence |
| --- | --- | --- |
| Code P2-4; State P2-3 | Capture the original private owner before argument materialization. On invocation/preparation exception, record it on that owner before the private local-rollback bypass and rethrow. The unactivated route keeps its local selection discard and parent-catch behavior. | Canonical private fault, both initially absent and accepted first handler: stage B, throw the exact error from the second callback's key property before child execution, parent catches, outer aborts with that cause. Accepted callback/dispatch/invocation/generation survive, new handlers are unregistered/inactive, coherent discard allows retry. |

Run this red before the small exception-path correction, then the affected
native/Python harness, focused native suite, and full/default/broader checks.
Settle one revised commit; the same reviewers recheck this counterexample and
retained original closures. No separate design review or third reviewer.

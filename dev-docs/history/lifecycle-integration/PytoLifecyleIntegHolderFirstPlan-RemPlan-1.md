# Holder-First Plan Remediation 1

## Scope

Both peer-blind reviewers independently found the same two callback-policy
issues. Consistency also found a contradictory call-site deletion row. This is
one merged compatibility-text correction and canonical baseline probe, not a
runtime fix or new publication/ownership contract. The controlling migration-first
scope is unchanged: preserve reference behavior; separately approve bug fixes.

## Dispositions And Closure

| Finding | Disposition | Closure Evidence |
| --- | --- | --- |
| Consistency P2-1 / Safety P2-2 | Restore reference bound-method normalization using receiver identity plus function; raw callable equality is insufficient | Sketch matches reference helper; canonical fixture covers value-equal distinct receivers, repeated method objects, unpublished dispatch, accepted replacement, and failed replacement |
| Consistency P2-2 / Safety P2-1 | Preserve current-based guard and B-after-success/A-after-failure result; classify effective-candidate fix as deferred baseline debt | Canonical fixture runs original and monolithic selectors; one new structured snapshot, with historical snapshots unchanged; sketch/I3b proof agree |
| Consistency P3-1 | Delete legacy record access/implementation, not independent pass ownership | Migration map, I4a, ledger and U2 consistently retain a lifecycle-owned independent pass manager until unification |

No finding is self-closed. Both original reviewers must verify their own
counterexamples on the corrected committed tuple. The revised sketch conforms
to the already controlling reference contract, rather than changing a shared
interface or completion boundary; the same reviewers can re-verdict that
bounded correction. If either judges otherwise, dispatch fresh reviewers.

## Evidence To Record

Run new callback characterization first without its expected snapshot (red),
inspect both reference outputs, then add the expected JSON explicitly and rerun
the canonical characterization suite (green). No runtime source changes.
Report exact commands/results, revised tuple, unchanged historical snapshots,
and plan whitespace/path/fence checks in the campaign ledger.

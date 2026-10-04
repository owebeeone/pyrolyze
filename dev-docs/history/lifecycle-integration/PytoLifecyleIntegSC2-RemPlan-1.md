# SC2 Remediation Round 1

Status: **DRAFT bounded correction; findings remain open until reviewer verification.**
Date: 2026-10-04. Reviewed object: Pyrolyze
`53c41674f43ab97401ac9b30a79575c19ab5dca9`; dependencies stay pinned to SC2.

## Dispositions And Closure Tests

Both independent axes returned NO-GO, five P2 findings each. Direct retirement
and cache-backed published membership independently converged. All findings
are accepted; none require manager changes or activating deferred resource
routes. The original reports remain verbatim evidence.

| Finding | Correction | Closure |
| --- | --- | --- |
| Code P2-1 | Resolve gate from both constructor parent and render root; reject mismatched graph/nearest-render ownership before allocation/attachment | Cross-root admitted leaf and forbidden resource constructor; neither allocation/registration nor early publication |
| Code P2-2 | Validate owned render roots even with omitted/conflicting scheduler input; standalone gate rejects owned contexts | Owner-slot-only, conflicting-root constructors and owned-root activation all reject; normal sharing/root isolation still golden |
| Code P2-3 / State P2-2 | Gate direct component deactivation and disposal before scheduler/callback/pointer mutation; preflight recursive retirement | Inside/outside/caught/direct/ancestor retirement preserves identity, callback, queue, membership, UI, generation |
| Code P2-4 | Preflight the removed subtree, not only immediate component children | Leaf-contained component with queued boundary cannot be removed by an empty parent pass |
| Code P2-5 / State P2-4 | Published slot debug lookup traverses current membership instead of the candidate reuse cache | Canonical additions/removals before publication, after commit, after discard remain coherent |
| State P2-1 | Native invocation owns a lexical execution claim; direct outer completion is deferred while any lexical publication/native claim remains | Early local end followed by callback/publication-body failure never publishes, preserves primary error, permits clean retry |
| State P2-3 | Verify owner identity/open state before no-op re-entry yields | Replacement-token scope body never executes/enlists; replacement untouched, old owner quarantined |
| State P2-5 | Reconcile all participating nearest/nested render-root caches, including now-unreachable roots | Retained nested root after discarded first component has empty current membership and registry; clean retry remains golden |

## Shape And Boundaries

Keep `_RenderAttempt` and the accepted manager API unchanged. The coordinator
counts lexical execution claims, not transaction begins. A direct outer local
completion request waits for the final outstanding lexical claim to exit;
its failure is still sticky and cannot cause a replacement token to be adopted.
No field/snapshot copy becomes a second value authority.

No-op scoped re-entry also retains a lexical execution claim: it omits local
reset, not execution ownership. Its entry uses the same open/identity check as
every other lexical scope before admitting its body.

Constructor validation and retirement checks apply only when either relevant
graph is activated. Unactivated historical routes remain unchanged. Published
debug lookup and registry reconciliation are separate operations: the former
reads current membership, the latter clears/rebuilds affected lookup caches
after known clean completion. Neither performs resource retirement.

Add closure tests first and record red failures. Apply all corrections as one
patch, run focused/full/broader gates, and settle one corrected tuple. Because
constructor/terminal call graphs change, dispatch fresh peer-blind Code/State
reviewers with both prior reports and this merged plan. Require explicit
verification of all original counterexamples and a closure table, not merely
passing test names. Round count: one planned remediation, zero accepted.

## Implementation Evidence

Red: all sixteen initial narrow closure cases failed against the reviewed
implementation; the expanded authored membership golden failed on unpublished
activity. A further no-op re-entry early-end case failed against the initial
correction, before the lexical fence was applied to that shortcut too.

Green: the initial correction passed 96 focused tests. The final correction
passed **97 focused tests in 13.61s**. Full default: **887 passed, 13 failed,
20 skipped, 1 warning in 45.75s**. Broader unactivated decomposed subset:
**41 passed, 14 failed in 2.34s**. Failure identities match the recorded SC2
baseline; no waiver or full-green claim. Black checks the three new Python
files, and diff whitespace checks pass. The final authored JSON only extends
SC2's target, not historical fixtures.

Fresh dual review follows settlement. This evidence does not self-close any
finding. Dependencies and the accepted SC1 kernel remain unchanged.

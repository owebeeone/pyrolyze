# SC3-L0 Consumer Remediation 1

Date: 2026-10-08. Candidate reviewed: Pyrolyze
`223d04aa322df32e2adc5f5cd45b27111b111f4b`; dependency tuple unchanged.
Code and State each returned NO-GO. Reports in this directory are verbatim.
No blind convergence: the axes found three distinct bounded correctness gaps.

| Finding | Disposition | Closure |
| --- | --- | --- |
| Code P2-1 | Select a primary exception by explicit None presence, never truthiness | Falsy and raising-boolean after errors plus local cleanup failure retain exact errors in order; generation once; quarantine |
| State P2-1 | Extend the existing admission/terminal identity guard to the captured key and exact integer ID; observed loss remains sticky | Key/ID relabeling before scoped and no-op entry rejects before reset/body even if restored; boolean ID after completion cannot authorize generation/retry |
| State P2-2 | Reject unreachable publication/after/failure combinations before installing authoritative evidence; retain record errors separately from authority | Contradictory empty-publication/action-failure and successful-all-phases/error records quarantine on the real graph; errors retained; no generation or second completion |

One combined patch; red tests first, then focused native/Python gates and full
default/broader comparisons. No golden changes are expected. No library,
compiler, marker, resource admission, routing, or participant-engine changes.

The corrections implement the existing authority/phase/error contract at its
existing guard and observation sites. They do not change a shared interface,
call graph, or mutation boundary; continue the same two reviewers with their
original counterexamples, both reports, and the settled corrected tuple.
Only those reviewers can close their findings. Remediation rounds used: 1/2.

## Implementer Evidence

The nine targeted cases first failed on the reviewed candidate. Strengthening
the admission case to try re-entry after restoring metadata exposed four more
failures within State P2-1; the existing integrity-loss guard is now sticky at
admission too. No new contract or architectural mechanism was introduced.

The settled correction passes 147 focused native tests and 128 Python-backend
owner/field-only/characterization tests. Full default native reports 937 passed,
13 unchanged failures, 20 skipped, and one warning; the broader unactivated
comparison reports 41 passed and the same 14 failures. No golden changes.
Black and `git diff --check` pass. This is implementation evidence, not closure
of either reviewer's findings; focused re-verdicts remain required.

## Reviewed Disposition

The corrected settled consumer is
`b1461a1128da15c21dad482d41bd5792253904cd`, with the same dependency tuple.
Code and State each independently replayed their original counterexamples and
returned GO; the verbatim `-ReviewCode-2.md` and `-ReviewState-2.md` reports close
all three P2s. No new finding or architectural root cause was reported. One
remediation round was used. Acceptance is private-consumer-only; the resource
activation and D5 adapter-design gates are unchanged.

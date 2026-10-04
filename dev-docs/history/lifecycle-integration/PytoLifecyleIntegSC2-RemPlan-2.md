# SC2 Remediation Round 2

Status: **DRAFT final bounded remediation; SC2 remains unaccepted.**
Date: 2026-10-04. Reviewed Pyrolyze:
`ca731d89a0086e0bff48dc426d1b5b1472aba869`. Dependencies remain pinned.

## Dispositions And Closure

Both reports are filed verbatim. Code returned two P2 findings; State returned
three new P2 findings and an incomplete prior P2-5 disposition. Both classify
them as localized omissions, not new architectural roots. The converged
candidate-reader and repeated-pass retirement findings are high-confidence.

| Findings | Correction | Closure |
| --- | --- | --- |
| Code P2-6 / State P2-6 | Internal deactivation traverses/edits candidate child maps; published readers remain current-only | Canonical leaf/plain removal preserves a newly staged sibling and order/UI; narrow discard preserves old published membership |
| Code P2-7 / State P2-7 | Local pass retains a retirement-only inventory of preceding candidate child references and checks omissions against it as well as current membership | Two native invocations and two mounted root local passes cannot omit a previously staged component; revisiting the same component remains supported; queued unpublished boundary cannot execute after discard |
| State P2-5 | Track affected render roots at registry mutation, not only local-pass entry | Publication-only nested callback plus failed parent clears retained cache/current membership, does not reuse discarded leaf, and preserves unrelated roots/keys |
| State P2-8 | Direct constructor admission checks occupied slot/cache before initialization and attachment | Standalone and nested publication scopes reject a colliding constructor without allocation; caught rejection poisons the attempt; identity/callback/queue/current UI/generation preserved; retry works |

## Boundary

The preceding-candidate inventory is context-local retirement admission data,
not a copied field authority or restoration source. It holds child references
only until outer cleanup, alongside the already retained visitation snapshots.
Repeated entry may revisit those same objects; omission is what requires
retirement admission. No resource disposal or new snapshot-based undo.

Affected-root bookkeeping holds render references, not managed maps/values.
Certified cleanup rebuilds their current registry, including publication-only
roots. Unpublished nested boundaries queued during a discarded attempt must
also be removed from scheduler bookkeeping without resource callbacks. Existing
published boundaries and their queue entries remain untouched. This prevents
an aborted new component from executing as an orphan after clean discard.

Do not change the accepted SC1 kernel, manager/dependency APIs, resource
protocol, or activation scope. Constructor collision checks precede lifecycle
initialization; internal ensure/reuse still uses the candidate cache.

Run closure tests red first, apply one merged patch, run focused/full/broader
gates, and settle the tuple. Because admission/reconciliation call graphs change,
use fresh peer-blind Code/State reviewers. Require verification of every prior
counterexample and explicit classification of new architectural roots. This
is the second remediation round; no third architectural patch is authorized.

## Verification Before Settlement

The first narrow/canonical red run returned **7 failed, 32 passed** against
`ca731d89`. The repeated-pass retry test was corrected to reuse the same
component callback identity; replacing a callback remains rejected. Two
additional detached-root registry removal/clear cases failed red, then passed
after publication and registry writes tracked the affected root.

Final clean-export gates: focused seven files **107 passed in 14.12s**;
full default **897 passed, 13 failed, 20 skipped, 1 warning in 43.45s**;
broader unactivated **41 passed, 14 failed in 2.23s**. The thirteen full and
fourteen broader failure identities remain exactly baseline, not waived.
The canonical target adds successful sibling preservation and repeat-component
reuse observations; only that new target was edited, with its existing
two-space indentation retained. No historical target or dependency changed.

These are implementation evidence, not closure verdicts. Fresh Code/State
reviewers must verify all original counterexamples on the settled correction.

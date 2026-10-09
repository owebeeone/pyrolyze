# Override Read Acknowledgment

Status: implemented for the opt-in lifecycle adoption candidate after operator
authorization. The original design received a lightweight Safety GO; that review
does not certify the implementation. The existing override publication and
single-cohort contracts remain authoritative. Default activation is unchanged.

## Reproduction

`tests/test_use_app_context_runtime.py::test_use_app_context_rebinds_when_requested_key_changes`
now selects the correct locale value after the refresh/input ordering correction.
It subsequently observes an extra render: `dark, en_AU, en_AU` instead of
`dark, en_AU` after changing the previously selected theme stream.

The extra work was already queued by publication, not necessarily by that later
theme event. Candidate reads and accepted stream notifications currently have no
reader-specific acknowledgment relationship.

1. During rendering, `_OverrideDrip.get()` exposes the lexical candidate.
2. A subscription binding records that value before outer publication.
3. Override completion publishes the managed selection, then calls `sync_value()`
   or `sync_parent()` on the stable streams.
4. `Drip.next()` notifies the subscription; `_StoreSubscription` increments its
   revision and asks its weak host to mark refresh-only and queue the boundary.
5. Draining the queue renders a value that this reader already consumed.

## Contract

Suppress only the notification for a publication already consumed by the same
successfully published reader selection. Other readers must still receive it.

- Candidate reading does not publish a stream or emit a notification.
- A read receipt is provisional until its binding selection is published.
- Rollback discards the provisional receipt along with the candidate binding;
  it cannot acknowledge a change on behalf of the accepted reader.
- Independent `Drip.next()` events, including events during rendering, remain
  ordinary invalidations. Equal values or an active transaction are not proof
  that the reader consumed that event.
- Failed reads, stale tokens, failed preparation, and unknown publication cannot
  supply an acknowledgment. Existing failure/quarantine behavior stays intact.
- A clean/skipped reader retains its previous receipt, not the latest request.
- Resource reuse does not imply read reuse: the selected immutable binding record
  owns the read receipt, while the subscription resource owns its lifetime.
- Existing queue entries are not cleared wholesale. An acknowledgment prevents
  only this redundant scheduling request, never unrelated pending invalidations.

## Proposed Shape

Use runtime-only provenance, not a new public marker, transaction key, or manager.
Keep ordinary external stores and the public `ExternalStoreRef` protocol unchanged.

A private override-read adapter supplies a receipt when a successful read observes
an active lexical candidate. Its identity includes the stable source/key, exact
immutable override selection, and original render attempt. Do not use value
equality, generation number alone, or only the current transaction key.
Represent those identities with opaque lifetime-stable tokens and weak source
links; receipts must not retain an entire render attempt or graph. Bare numeric
object IDs are insufficient because they can be reused after collection.

Store that receipt beside the value in the detached subscription-binding selection.
The existing lifecycle-owned selection publishes/discards both together. Do not
mutate accepted subscription ownership to acknowledge an uncommitted read, and do
not put the receipt only in a newly returned ref's closure: a reused subscription
would still retain the old callback/closure.

Override completion marks its synchronous delivery with matching publication
provenance. This marker exists only around the domain's accepted delivery; plain
stream events are not marked, even when they happen during completion. Nested or
reentrant delivery must restore its previous marker in `finally`.

At notification, resolve the host's **currently published binding selection** via
its existing weak links. For both slot-call and expression hosts:

1. Verify the notification belongs to that selection's subscription resource.
2. Match its receipt to this exact accepted override publication.
3. If matched, do not increment refresh revision or enqueue a render for this event.
4. Otherwise, follow the existing revision/invalidation path unchanged.

No strong backlink from the resource/stream to the render graph is introduced.
Unknown or unavailable receipt/host provenance falls back to normal notification.
Receipt inspection must not invoke a factory/getter or arbitrary equality during
notification. Failed inspection follows the existing error policy, not silent
suppression.

Transparent overrides need effective-source provenance: a candidate read may come
from a parent, not the local override. Trace both `sync_parent()` and independent
parent callbacks before lowering the receipt. Ambiguity must retain notification,
not be resolved by assuming equal values mean the same event.

## Bounded Implementation

1. Pin the existing failing key-rebinding test and identify the already queued
   publication event separately from the subsequent old-source update.
2. Add private provenance capture/delivery at the authored override seam, with
   detached binding receipt storage and weak host lookup for both reader forms.
3. Exercise retained subscription resources with a new selected read record.
4. Verify the notification matrix below on both assembly backends; run normal
   regression and record the remaining adoption gates.

This does not optimize transaction ownership scans, admit opaque containers,
change Drip's general equality/error policy, or activate normal lifecycle routing.

## Test Matrix

Extend the canonical override fixture for successful publication outcomes. Use
narrow fault tests for ownership, interleaving, and failed reads, without duplicating
the same success trace in separate harnesses.

| Situation | Required outcome |
| --- | --- |
| Fresh reader consumed candidate; same selection publishes | Correct value, no extra render queued by publication |
| Older/clean-skipped reader did not consume new selection | Notification and one coalesced follow-up render |
| Two readers, only one consumed candidate | Suppress only the acknowledged reader |
| Same resource reused with a new candidate read | Receipt follows the published binding, not old callback closure |
| Theme-to-locale replacement | Correct locale; old source detached; no publication-only extra render |
| Parent event during render, before or after candidate read | Independent event remains observable; rollback cannot erase it |
| Candidate read followed by rollback or read/prepare failure | Accepted receipt unchanged; real later event still notifies |
| Multiple pending reads, latest selection wins | Only the final published selection can acknowledge |
| Transparent parent, then concrete replacement/removal | Preserve detach-before-delivery ordering and effective-source checks |
| Notification reentry or unknown completion outcome | No guessed acknowledgment, no new render writes, existing failure policy |
| Removed reader or collected graph | No resurrected scheduling target or new reference cycle |

Exit: the full existing app-context rebinding test passes, the genuine-event cases
remain observable, and no queue-clearing workaround or generic store polling has
been introduced. Update the adoption audit with actual evidence; this correction
alone does not certify default activation.

## Implementation Checkpoint

`_OverrideSelection` now records an opaque selection token and the original
attempt's opaque read token. `_OverrideRead` captures the value and provenance
together; `_SubscriptionBinding` stores its provisional receipt beside that value.
Receipts retain neither the attempt nor the graph.

During accepted delivery, `_StoreSubscription` checks only the host's published
binding and its exact source/resource receipt. A match suppresses that event's
revision increment and scheduling request. Reused subscriptions therefore consult
the latest selected record, not the ref closure that originally subscribed.

Transparent managed overrides compose their selected path with effective parent
provenance. The delivery batch installs accepted path identities before notifying
any parent. Initial parent subscription snapshots are not replayed over the
already synchronized identity. Independent `next()` calls have no publication
identity, including nested calls; failed delivery clears uncertified provenance.
Plain external parents remain conservatively unacknowledged.

The canonical trace is
`tests/data/lcm_integration/override_read_acknowledgment.py`, checked by
`test_override_read_acknowledgment_golden`. It covers both reader forms, three
override levels, selective notification, subscription reuse, independent events,
and final-read selection. Narrow fault coverage is in
`tests/test_lcm_override_read_acknowledgment.py`: rollback with events before/after
reading, failed projection/publication, notification reentry, parent changes
between read and delivery, and retained-snapshot graph collection.

See the adoption audit for final verification. No AST lowering, Astichi, YIDL,
lifecycle-library, generic Drip-policy, ownership, or default-routing changes
are part of this correction. Historical goldens are unchanged.

# Lifecycle Pass-State Consumption

Status: implemented and tested behind `_enable_pass_state_render`. Aggregate
review and normal-route activation remain pending. No YIDL, Astichi, lifecycle
library, or transaction-manager changes are required.

## Contract

One shared render transaction remains. We separate state responsibilities, not
transaction cohorts or completion rules:

| Member | Lifecycle kind | Responsibility |
| --- | --- | --- |
| `_requested_revision` | `field` | Independently arriving invalidations |
| `_handled_revision` | `managed`, `PASS_TX_KEY` | Successfully consumed revision |
| `_pass_requested_revision` | `local_store` | Revision captured before local work |
| `_pass_seen_in_pass` | `managed`, `PASS_TX_KEY` | Candidate visitation |

The existing `invoke_dirty` construction input initializes requested revision
to 1 or 0; handled revision starts at 0. Dirtiness is requested != handled.
Setting dirty increments the request. Visiting a slot captures the request
before its work runs. Successful local exit acknowledges only that capture,
not whichever request happens to be newest at exit. The acknowledgment stays
provisional until outer completion. Commit publishes it; rollback discards it.

Thus an invalidation during rendering or after local exit survives both commit
and rollback unless a subsequent local pass actually captures and consumes it.
No dirty-flag snapshot, restoration, or post-completion invalidation replay is
needed on this gate. Reading dirtiness does not acknowledge anything.

Explicit `invoke_dirty = False` outside an attempt retains the existing boolean
API as request cancellation: it resets the outstanding request to the current
handled revision. It does not write a managed field or start a transaction.
Request revisions therefore need not be globally monotonic across explicit
cancellation. Inside an attempt, clearing dirtiness acknowledges its captured
revision and requires the original active owner; a stale token cannot enlist
an acknowledgment into a replacement transaction.

Scheduled component rerenders capture and acknowledge both their render context
and owning component. They do not revisit or dirty unrelated siblings. Ordinary
pass exit also acknowledges the context's captured request. Notifications arriving
later still differ from those captures.

## Visitation And Compatibility

Managed candidate membership already controls child publication and ordering.
Visitation remains an explicit managed boolean because direct construction can
attach an unvisited child, and owned event handlers have a separate visitation
boundary. Reset/visit decisions remain ordinary domain operations; lifecycle
restores their accepted values on rollback, without a recovery loop.

`_invoke_dirty` and `_seen_in_pass` are compatibility properties. Earlier gates
and the unactivated route continue using `_legacy_invoke_dirty` and
`_legacy_seen_in_pass`. The construction golden changes only those two storage
names; flags, attachment ordering, and other observations are unchanged.

The newest gate does not populate `_pass_child_dirty`,
`_field_only_has_snapshot`, or I6b's `_invalidated_states`. Older gates retain
their bookkeeping until adoption removes them. Retirement admission inventories
and original-owner/local-scope identities are not rollback snapshots and remain.

This removes manual transaction recovery on the new path, not all imperative
rendering operations or all compatibility code. The remaining policy operations
are request, capture, acknowledgment, and visitation; existing lifecycle markers
own their publication and discard.

## Verification

Canonical fixture: `tests/data/lcm_integration/pass_state_lifecycle.py`, with
`baselines/pass_state_lifecycle.json`. It covers marker kinds, unchanged-call
elision, notifications during work and after local exit, provisional acknowledgment,
outer failure/retry, repeated local passes, candidate removal, independent roots,
explicit cancellation, partial rerendering, and owned-handler omission/rollback.

`tests/test_runtime_context_state_lcm_pass_state.py` contains narrow notification,
snapshot-elimination, and replacement-token faults. The characterization harness
also replays seven existing value/subscription/effect/async/mount/loop/container
baselines using the newest gate, without changing their expected behavior.
The older callback fixture includes out-of-render retirement that later gates
already exclude; it is not replayed wholesale. Owned handlers are covered by
the new canonical fixture instead. Historical callback coverage still runs on
its original gate.

Run the focused checkpoint from the repository root with the workspace source
dependencies installed or on `PYTHONPATH`:

```sh
ASTICHI_LOWER_ENGINE=native python -m pytest -q \
  tests/test_runtime_context_state_lcm_pass_state.py \
  tests/test_lcm_integration_characterization.py
```

Verification: 128 focused native tests pass. The affected faults, canonical
checkpoint, resource replays, and construction golden pass on Python assembly
under Python 3.12 and 3.14 (12 tests each). Full native regression has 1,120
passes, 20 skips, and the same two known host-ordering failures.

## Adoption Boundary

Aggregate review and default activation are still separate steps. A probe also
confirmed an existing compiled ordinary-component dispatch gap on the preceding
`_enable_container_render` gate: the compiler's generic visit creates a
`SlotContext` before `component_call` requests a `ComponentCallSlotContext`,
leading to "slot replacement is not admitted by SC2". This reproduces without
the pass-state changes and is not fixed here. The new partial-rerender fixture
uses the existing native component invocation protocol; compiled scope-container
coverage is replayed unchanged. Resolve ordinary-component dispatch before
claiming unrestricted compiled-route adoption.

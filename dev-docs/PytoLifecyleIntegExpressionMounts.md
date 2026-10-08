# Mount Expressions

Status: implemented behind `_enable_mount_expr_render`, extending the async-effect
expression proof. Normal routing and earlier gates remain unchanged. Aggregate
implementation review is deferred, not independently accepted here.

## Selection And Surfaces

The existing `_MountAdvertisementBinding` supplies immutable candidate
advertisements. This is graph data, not an external resource; selection needs no
resource wrapper, activation, or imperative withdrawal.

Expression finish prunes visitation, then stages advertisement anchors in its
managed `own_ui_state`. The expression collection, UI anchors, and parent graph
publish/discard with the shared outer render decision. Current surface queries
read committed selections only, including during replacement evaluation.

The existing mount completion validates the combined candidate surface before
publication and effect delivery. Its advertisement inventory now includes
expression collections as well as ordinary slot calls. Expression entries use
`SlotIdPath((expression_slot_id, call_site_id))` as internal inventory keys, so
separate expressions sharing a call-site ID cannot overwrite one another and
hide duplicate keys/defaults. Existing advertisement provenance is preserved.

Omission and replacement remove old selections through lifecycle publication,
not mutable registry updates. Retained snapshots remain immutable historical
values. Native-owner requirements, duplicate-surface diagnostics, and original
transaction-token fences reuse the existing mount implementation.

## Coverage

`tests/data/lcm_integration/expression_mount_lifecycle.py` and its authored JSON
baseline cover provisional visibility, committed UI anchors, provenance,
rollback, latest replacement, retained snapshots, scoped call sites, expression
omission, and container omission.

`tests/test_runtime_context_state_lcm_expression_mounts.py` covers duplicate keys
and defaults across expression/ordinary selections, duplicate entries across
expression collections, missing native owners, and token replacement during
key comparison. Invalid candidate surfaces prevent effect delivery.

Verification: full native suite **1056 passed, 2 unchanged host-ordering failures,
20 skipped**; affected expression proofs and characterization on Python assembly
**57 passed**. Historical goldens are unchanged.

## Remaining Work

The subscription and effect-expression checkpoints were committed and pushed as
`aa4a645` before this work. This mount extension was committed/pushed as `358ead7`. Remaining
graph/registration migration, aggregate review, normal-route adoption, and legacy
completion deletion are still pending. Opaque container helpers and structural
directive admission are unchanged; this checkpoint does not claim their migration.
No lifecycle-library, compiler, or shared legacy handler changes were required.

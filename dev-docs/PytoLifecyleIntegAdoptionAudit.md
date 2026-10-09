# Lifecycle Adoption Audit

Audited after I6b commit `583241e` on 2026-10-09. This is the remaining-state
and activation audit, not aggregate code-review acceptance or authorization to
switch normal routing. The single-cohort amendment remains authoritative.

## Current Routing

`src/pyrolyze/runtime/context.py` still maps the default `lcm` selection to
`context_lcm.py`, the older monolithic implementation. Explicit
`bare_refactor_lcm` selects the decomposed classes, but does not install
`_enable_completion_render`. Merely changing the import alias would therefore
not activate the integrated outer completion path.

The decomposed module still reports implementation identity `bare_refactor`.
Tests importing `context_lcm` directly also assert its existing class modules.
I7 must reconcile actual routing, reported identity, direct-import consumers,
root construction, and activation together. Keep the explicit original fallback
until its removal is separately approved.

## Confirmed Admission

Directly invoking the final completion gate's `require_slot_type` admits these
exact facade classes: SlotContext, LeafSlotContext, EventHandlerSlotContext,
SlotCallSlotContext, SlotExprSlotContext, ContainerSlotContext,
ComponentCallSlotContext, DirectiveSlotContext, and AppContextOverrideSlotContext.

It rejects both KeyedLoopSlotContext and LoopItemSlotContext. Earlier proof
classes still contain rejection messages for categories admitted by later
subclasses; a text search alone is not the final admission inventory.

## Remaining State

| State / Owner | Current role | Required action |
| --- | --- | --- |
| ContextBase children, own UI, projected UI | Managed under the shared pass key | Already authoritative on the final gate; retain domain projection/validation |
| Leaf/slot-call arguments and selected bindings | Managed records, with legacy adapters | Remove compatibility records only after normal-route adoption |
| Components and override selections | Managed records; accepted graph drives retirement/notifications | Aggregate review, not another holder migration |
| Directive selectors | Managed on I6b; legacy selector snapshot on unactivated routes | Delete legacy selector storage with compatibility removal |
| LoopItem `_current_value`, `_current_dirty`, `_current_initialized` | Plain attributes assigned by `update_current` | Migrate coherent item selection before admitting loops |
| `_invoke_dirty`, `_seen_in_pass` | Ordinary fields used by traversal/scheduling | Audit pass-specific versus independently arriving scheduling mutations before selecting markers |
| `_pass_child_dirty`, `_field_only_has_snapshot` | Final gate still saves/restores dirty flags after failed local work | Remaining I3a work; preserve the I6b independent-invalidation ledger while removing restoration |
| `_pass_child_order`, `_pass_started_tx` | Legacy local completion; order also written on private passes | Remove private-path redundant writes, then legacy declarations after adoption |
| `_field_only_prior_children` | Inventory used to validate retirement admission | Domain validation input, not a published-value rollback holder; do not delete blindly |
| Slot registries, mount advertisement maps | Accepted-membership caches / derived surfaces | Reconcile from accepted graph; do not make caches another publication engine |
| Scheduler queue, active/deferred boundaries, flush flags | Scheduling control, including independent external events | Preserve independently accepted work; not render candidate fields |
| I6b callback batch | Original-attempt delivery evidence, source-filtered after acceptance | Keep domain draining/quarantine; no transient reset before capture |
| Expression call-site collection | Lifecycle-owned collection; ordinary manager shell | Keep explicit binding ownership; remove only legacy completion paths |
| Expression runtime-locals map, site metadata, stable dispatch closures | Evaluation/identity machinery | Inspect retention/retirement during adoption; not automatically transactional holders |
| Native-container `_expects_native_root` | Local construction/projection input; accepted root shape is managed | Keep candidate validation distinct from published root shape |

`local_store` or a remaining imperative method is not itself a defect. The target
is authoritative lifecycle storage, not turning scheduler algorithms, graph
projection, explicit resource retain/release, or callback execution into fields.

## Activation Blockers

### A: Keyed Loop Selection And Lifetime

Owning files: `context_state_lcm/loop_item_slot_context.py`,
`keyed_loop_slot_context.py`, and `_KeyedLoopIterable` in `_support.py`.

The iterable opens a loop pass, computes keys, checks duplicates, installs items,
and calls `update_current` before yielding each item. Loop item values are not
transactional today. Key computation, hash/equality, iteration failure, and early
iterator exit must stay within the original attempt's ownership checks.

Next bounded implementation: introduce coherent managed item selection, admit
the two exact loop facade classes through an additional gate, and preserve the
existing keyed identity/reordering algorithm. Reuse inherited managed membership
and shared resource retirement; do not add another loop transaction manager.

Canonical verification: unchanged identity, value update, reorder, deletion,
nested key paths, successful retry, and rollback of the outer render after item
selection. Narrow faults: duplicate keys, failing key/hash/equality functions,
token replacement, caught iteration failure, and early exit. Record existing
iterator-finalization behavior before changing it; a new public iteration
contract requires discussion, not an incidental migration fix.

### B: Container Classification And Compiled Routes

Owning files: `ContextBaseStateMgr.container_call`, `_support.py` container
handles, and `_MountRenderCompletion.require_container_call`.

The final gate inherits a guard that accepts only functions recognized by
`_native_context_param_name`. Existing container dispatch also recognizes
ContainerCallRuntimeContext helpers and compiler-backed component metadata.
Those routes are not admitted by that guard. Additionally, dispatch initially
ensures a ContainerSlotContext before its directive branch tries to ensure a
DirectiveSlotContext at the same ID. The initial proof of direct `open_directive`
does not certify this separate dispatch path.

Next bounded implementation: classify the existing route before constructing its
slot, and prove the recognized compiled/native/directive routes through authored
compiler fixtures. Do not broaden the guard to arbitrary context managers.
Opaque helpers can run external `__enter__`/`__exit__` actions; establish their
existing completion contract separately before claiming rollback support.

Verify construction/evaluation failures, caught failures forcing outer discard,
native-root validation, directive projection, and resource cleanup through the
actual compiled entry points, not just direct state-manager methods.

Subsequent implementation: [scope-container checkpoint](PytoLifecyleIntegContainerRouting.md)
adds classification-before-construction behind `_enable_container_render`, with
authored compiled coverage and focused original-owner/admission faults. Default
activation and aggregate review remain pending.

### C: Common Pass-State Migration

Complete the I3a dirty/visitation audit after loop and container coverage exists.
Remove redundant private-path order snapshots, and replace dirty restoration
only where lifecycle semantics preserve both failed-attempt retry and independent
notifications. Keep local scope ownership/control objects and retirement
admission inventories where they have a real domain role.

Cover unchanged-call elision, partial rerender, repeated local passes in one
attempt, candidate removal, external invalidation during success/rollback, and
independent roots. Do not remove legacy storage while normal routing depends on
it, or force scheduler state under the render key merely to eliminate a snapshot.

Cleanup audit: the private path no longer captures or clears the legacy
`_pass_child_order`; lifecycle already restores child membership and ordering.
A narrow regression checks that a second pass with accepted children does not
populate that legacy snapshot. The legacy path retains its own bookkeeping.

`_pass_child_dirty` remains intentional: `_invoke_dirty` is nontransactional
scheduler state, and rollback must restore the retry baseline before I6b replays
independent invalidations. `_seen_in_pass` still participates in owned-handler
selection. Moving either into transaction-managed storage requires a separate
consumption/notification policy, not simply deleting restoration. Retirement
inventories and local scope identities also remain necessary. This is a bounded
cleanup, not completion of the entire dirty/visitation migration or permission
to activate the lifecycle path by default.

### D: Aggregate Review And I7 Adoption

After A-C, run the operator-requested aggregate implementation review over the
resource ownership adapters, preparation/publication sequence, notification
batch draining, original-token fencing, graph retirement, and actual compiled
routes. Resolve blocking findings before default activation.

Then make lifecycle-backed completion automatic for fresh canonical roots;
update exports/identity and migrate direct-import tests. Keep the original fallback.
Run authored/generic-backend scenarios through the real canonical selector,
including scheduling, event callbacks, subscriptions, effects, async effects,
mounts, loops, directives, overrides, and graph visitors. Delete compatibility
records, old dispatch methods, parallel local completion, and monolithic mixins
only after their consumers move. Performance/documentation acceptance is I8.

## Evidence And Limits

I6b native regression: 1083 passed, 2 known host-ordering failures, 20 skipped;
affected Python checks: 43 passed. These results certify the tested paths, not
normal-route activation. No runtime behavior changed during this audit.

The two host-placement failures remain separate backend work. The scheduler's
failure-path automatic repost/retry policy also remains unchanged; preserved
queued work does not imply automatic recovery after completion quarantine.
No new close protocol, multi-key atomicity, arbitrary external-action rollback,
or binding-library redesign is introduced by this audit.

## Recommended Next Checkpoint

Subsequent implementation: [keyed-loop checkpoint](PytoLifecyleIntegKeyedLoops.md)
adds managed selection and captured execution. Its approved execution scope
accepts `break` prefixes but aborts body failures; the inventory above describes
the pre-checkpoint
audit, not certification of that newer implementation.

Implement A first: keyed-loop item selection. Then B, C, aggregate review, and
I7 adoption/deletion in that order. This replaces the misleading implication
that I6b completion leaves only an import switch before adoption.

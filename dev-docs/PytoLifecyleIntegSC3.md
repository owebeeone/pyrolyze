# SC3 Resource Completion Audit

## Status And Scope

Status: **audit recorded; resource activation remains gated**.
Date: 2026-10-04. The operator authorized continuing SC3 after private SC2
acceptance, then approved the original proposal to design and review the
bounded lifecycle-library prerequisite before resource adapters.

This is the concrete inventory required by
`PytoLifecyleIntegSingleCohortPlan.md`, SC3. It does not accept SC3 live routing,
I3a completion, I4 legacy-holder replacement, or a default-runtime switch.
`PytoLifecyleIntegSC3-L0Plan.md` specifies the first prerequisite. Domain
completion ordering and individual resource adapters require their own review.

Prerequisite update, 2026-10-08: the L0 library and private owner-consumption
gates below are accepted. The consumer checkpoint is Pyrolyze
`b1461a1128da15c21dad482d41bd5792253904cd`, after Code/State GO/GO; see
[its exact tuple and verification](PytoLifecyleIntegSC3-L0Consumer.md).
The inspection, observations, and initial gate sequence below remain the
historical audit. D5/category adapter design is next, with resource admission
and every unreviewed retirement/delivery path still blocked.

## Inspected Tuple

| Repository | Revision |
| --- | --- |
| Pyrolyze source and existing tests | `407592f6a52f54e55833c4b1cfe7cae62959dfa3` |
| Accepted SC2 runtime/test bytes | `a7bf0e92001f1c881ed81cd6e58064d8e8b4da51` |
| yidl-lifecycle committed source | `335d2795cdd65b2542e0ac9ec70b7f16ee0b1901` |
| YIDL committed source | `95a6e3e52fc3d710d25c5d59315e791a3ed75cc4` |
| Astichi committed source | `387ca5e1da76204ee60922094734c13ee36383c0` |

Dependency inspection/execution uses committed views and the clean exports
recorded by the SC1/SC2 ledgers. Uncommitted lazy/mutable lifecycle changes,
YIDL documentation/paper changes, and unrelated rendering-backend documents
are excluded. No source, test, golden, selector, dependency, or parent gitlink
changes accompany this audit.

## Local Completion Inventory

Paths below are relative to the Pyrolyze repository. C = candidate assembly;
R = rollback/discard cleanup; P = published delivery/retirement. These labels
classify observations in this document, not runtime dispatch tags.

| Location / Entry | Current Action And Order | Class | SC3 Disposition |
| --- | --- | --- | --- |
| `context_state_lcm/context_base.py::end_pass` | Deactivate unseen children, commit binding/handler/component-handler state, build UI, clear dirty flags, then conditionally commit the local TM | C + P | Split assembly from outer completion. Remove each publication caller only with its adapter proof; never dispatch generated field application through child types |
| `context_state_lcm/context_base.py::rollback_pass` | Deactivate newly introduced children; roll back retained bindings/handlers; restore dirty flags; conditionally roll back the local TM | R | Outer discard owns participating field values; resource cleanup must drain independently. Dirty snapshots remain SC4 work |
| `context_state_lcm/render_context.py::end_pass` | After base exit, rebuild mount surface and flush the render-local callback queue | P | Deliver only after the outer decision; prevalidate surface constraints without accepting resources |
| `context_state_lcm/render_context.py::_run_boundary` | Local callback and its pass exits run before outer generation commit; a raised callback rolls back generation | C + P | Existing resource callbacks can observe pre-commit generation. D5 must explicitly approve their new visibility/timing |
| `context_state_lcm/render_context.py::_flush_post_commit` | Detach queue, then call entries in order; first exception skips later entries | P | A future domain batch must attempt independent entries and report failures; L0 manager draining alone cannot resume this loop |
| `context_state_lcm/event_handler_slot_context.py` | Four plain committed/staged callback/key stores; `commit_handler` copies, `rollback_handler` clears; stable dispatch reads committed callback | C + R + P | I3b replaces selection stores with lifecycle fields and removes both transfer callers. Do not publish a pending callback at local child exit |
| `context_state_lcm/component_call_slot_context.py::commit_owned_event_handlers` | Deactivate unseen owned handlers, commit surviving handlers, clear order snapshot | P | Component-owned handlers participate in the same outer decision; keep dispatch lifetime and receiver/key compatibility |
| `context_state_lcm/component_call_slot_context.py::rollback_owned_event_handlers` | Deactivate newly introduced handlers, clear pending selection on retained ones, restore visitation | R | Resource cleanup is distinct from managed membership discard; no selective field rollback |
| `context_state_lcm/component_call_slot_context.py::_dispose_child_context` | Remove scheduler work, recursively deactivate children, clear child registry/callback/link | P or R by caller | Replacement/removal stays blocked by SC2 until the exact retirement adapter is reviewed |
| `context_state_lcm/slot_call_slot_context.py::commit_binding` | Call binding commit then write binding-derived UI | C + P | Not an after-hook drop-in: UI writes require an active field transaction. Split candidate UI from resource delivery |
| `context_state_lcm/slot_call_slot_context.py::rollback_binding` | Roll back referent, then write binding-derived UI | R + C | Avoid writing lifecycle values after key finalization; retain referent-specific cleanup |
| `context_state_lcm/slot_expr_slot_context.py::commit_binding` | Commit visited bindings, commit legacy call-site manager, sync UI, capture/clear transient queues, run callbacks | C + P | Legacy call-site authority remains I4. Capture delivery records before transient clearing; no half-shared manager |
| `context_state_lcm/slot_expr_slot_context.py::rollback_binding` | Roll back visited bindings and legacy call-site manager, sync UI, clear queues | R + C | Separate field discard from legacy/domain cleanup; this route remains unmigrated |
| `context_state_lcm/app_context_override_slot_context.py` | Staging already updates drips/subscriptions; local commit publishes lookup; rollback restores values and may notify again | C + P + R | I6 work, not a completion-call relocation. Requires staged lookup/value ownership and approved notification timing |
| `call_site_context.py::CallSiteContextManager` | Separate legacy lifecycle TM/records; current replacement calls `accepted()` then closes previous context | P + R | I4 replaces the authority first. Do not inject a YIDL TM into legacy records or relabel early acceptance provisional |

All `context_state_lcm` paths in the table have the repository prefix
`src/pyrolyze/runtime/`; `call_site_context.py` has that same prefix.

## Effects Before Local Completion

The audit must include these paths; moving `end_pass` calls is insufficient.

| Location | Already Observable Effect | Required Boundary |
| --- | --- | --- |
| `slot_call_core.py::commit_slot_call_invocation` | Binding selection/rebind and immediate deactivation of a replaced binding during evaluation | A reviewed candidate resource/holder adapter before this route can join outer completion |
| `slot_call_semantics.py::ExternalStoreBinding.bind/rebind` | Subscribe/get during bind; rebind can unsubscribe the previously accepted ref immediately | Preserve accepted subscription through failed candidate work; explicitly unwind candidate subscriptions. Do not assume field rollback reverses unsubscribe |
| `slot_call_semantics.py::UseEffectBinding.commit` | Accept request/deps and enqueue effect; callback later cleans up prior effect then runs new setup | Split accepted selection from delivery. Cleanup and setup inside one effect action are dependent; later independent effect actions must still be attempted |
| `slot_call_semantics.py::UseEffectAsyncBinding` | Accept request/deps, then queued cancellation/cleanup/start; completion later queues invalidation | Keep token-based stale-completion suppression; do not cancel accepted work before successful replacement unless separately approved |
| `slot_call_semantics.py::PyrolyzeMountAdvertisementBinding.commit/deactivate` | Build/retain advertisement and withdraw it on deactivation | Validate candidate surface before publication; withdrawal follows the approved removal owner |
| `slot_expr.py::SlotExpr.evaluate` | Begin/finish the legacy call-site pass; direct mode runs evaluator/resource callbacks and delivery itself | Keep direct legacy mode distinct. Lifecycle-integrated mode cannot silently bypass I4 authority replacement |

These are source observations, not a new guarantee of atomic external effects.
Resource adapters must document creation failure, candidate discard, accepted
replacement, and post-publication delivery failure independently.

## Writer And Key Audit

| Field / Registry | Writers | Governing Key And Owner Today | Required Decision / Constraint |
| --- | --- | --- | --- |
| `children_state`, own/assembled UI | Register/ensure slot, local pass assembly, deactivation | Managed `PASS_TX_KEY`; legacy local owner or accepted private SC2 outer owner | One outer render owner for participating paths. No after-commit managed writes |
| `_slots_by_id` | Slot attachment, unregister, clear, private SC2 reconciliation | Ordinary cache; no independent transaction key | For SC2 it indexes current membership, not resource ownership. Do not overwrite independently accepted registrations by treating an actual registry as this cache |
| Handler selection stores | `stage_callback`, commit/rollback/deactivate handler | Plain stores; pass caller is the authority | I3b must name the managed selection key. Current `event_handler` entry requires a pass; this audit does not invent an out-of-render registration API |
| `_post_commit_callbacks` | Binding host enqueue; local flush/rollback clear | Ordinary render-local list; no token/attempt association | A bounded adapter must associate each batch with its owning attempt and capture it before scratch clearing; no replay after partial delivery |
| `_mount_advertisements_by_slot` | Surface rebuild and immediate withdrawal | Plain accepted surface, no field key | D5 plus mount-specific adapter. Shared-write/removal policy is not established by cache rebuilding |
| Call-site `contexts` and visitation | Stage/visit/commit/rollback; `replace_current` accepts directly | Legacy default key/manager; direct current mutation outside its pass | I4 and explicit independently accepted replacement/removal policy. No two keys assigned to one field to fabricate separate overlays |
| `_invoke_dirty`, scheduler queue | External-store/effect invalidation, pass reset, disposal | Ordinary invalidation/scheduler state; not render-owned rollback values | Preserve independent invalidations. Key/snapshot migration remains SC4; a failed render must not erase newly arriving accepted work |
| `_site_metadata` | Runtime site resolution during evaluation | Nontransactional local store | SC4 permission/writer policy remains open; this is not made transactional by manager sharing |
| Authored app-context drips/lookup | Stage override, parent subscription, commit/rollback/deactivate | Plain stores and externally visible subscriptions | I6 notification/selection adapter; existing `_scope_active` debt is not repaired by this audit |

An independently accepted registration must survive a later failed render.
A render-owned removal must remain provisional until that render succeeds.
The user chose those outcomes, but the current shared registries do not yet
provide the required authorization/stale-removal mechanism. Each affected
adapter must name accepted registry identity, writer, governing key, and
completion owner; identity-check the entry it intends to remove. A new
cross-key registry protocol would require a separate proposal, not inference
from this table.

## Confirmed Library Prerequisite

Existing `transaction_failures.py` observations were rerun against the exact
pinned exports. The baseline JSON was not changed.

| Fault | Observed At The Pinned Tuple |
| --- | --- |
| Participant 2 prepare | No apply; all rollback and after-rollback callbacks run if cleanup succeeds |
| Participant 2 apply | Participant 1 applies, participant 3 is skipped; no after-commit callbacks run |
| Participant 1 after-commit | All values applied; later after-commit callbacks are skipped |
| Participant 1 rollback | Later rollback and all after-rollback callbacks are skipped |
| Participant 1 after-rollback | All discard callbacks run; later after-rollback callbacks are skipped |
| Prepare plus rollback failure | Cleanup failure becomes outward error; original prepare failure survives only as context |

Every fault clears the manager's active token. That is not proof of complete
discard or successful publication. The private SC2 owner correctly marks a
`commit_only` exception publication-uncertain and blocks reuse; activating a
resource route under that same ambiguity would not be safe.

An ephemeral generated-class probe also checked two same-key after-commit and
after-rollback hooks. Both hooks execute when neither throws. When the first
throws, the second is skipped; commit leaves current value 1 and rollback
leaves it unchanged, with no active token. Thus manager-only draining cannot
meet the per-participant hook requirement. This probe added no files/tests and
does not replace the planned generated failure golden.

## Next Bounded Checkpoints

1. **SC3-L0 design gate:** settle and dual-review
   `PytoLifecyleIntegSC3-L0Plan.md`. It preserves existing commit return values,
   adds token-bound completion evidence, and drains required independent
   completion actions. No resource activation follows from document acceptance.
2. **SC3-L0 implementation gate:** implement only in `yidl-lifecycle` at the
   reviewed boundary, preserve unrelated work, run narrow protocol and generated
   golden evidence, then independently review the exact library tuple.
3. **SC3 owner-consumption gate:** teach the private render owner to consume
   terminal completion evidence. A published after-hook failure must not cause
   fictitious generation rollback; cleanup readiness remains separate. Keep
   resource constructors blocked and reprove every SC1/SC2 counterexample.
4. **SC3-D5 adapter design gate:** specify the exact candidate-prepare,
   publication, generation, accepted-registry/retirement, scratch, and delivery
   timeline for each first resource route. Audit reentry, independently accepted
   registrations, stale removals, and batches with an early throwing action.
   A route still depending on legacy I4 authority stays blocked.
5. **SC3 bounded adapters:** implement reviewed categories independently and
   transition their live expectations with their routes. Record removed local
   callers and remaining domain methods. Do not certify all resource categories
   or I3b/I4/I6 as complete from one passing adapter.

The first useful adapter candidate is callback selection, because field
publication needs no external subscription engine. Its exact sequencing with
SC4/I3b must be recorded explicitly rather than quietly relabeling that work.
Subscriptions, effects, mount delivery, overrides, and legacy call sites are
not bundled into that candidate.

## Verification And Unchanged Gates

The existing seven-file focused suite passed **127 tests in 12.51s** on the
inspected tuple, including the private SC2 golden and historical observations.
The failure probe and both generated-hook probes ran against committed exports.
No full/default/broader rerun is claimed for this documentation-only checkpoint.
The previous 13 default and 14 broader failures remain recorded debt, not
acceptance of unactivated resource routes.

Reproduce using `tests/data/lcm_integration/README.md` and the clean pinned
export procedure in the SC1/SC2 review ledgers. Inspect the failure probe with
`python tests/data/lcm_integration/transaction_failures.py`; compare it through
`tests/test_lcm_integration_characterization.py`, never regenerate to hide the
gap. Future library corrections require a separately named target golden and
an explicit historical-versus-current baseline disposition.

Only this audit and its prerequisite plan/status artifacts are in scope now.
No tags, push, merge, worktree, parent-pointer update, broad selector change,
resource lifetime redesign, savepoint, per-slot manager, or field snapshot
authority is introduced.

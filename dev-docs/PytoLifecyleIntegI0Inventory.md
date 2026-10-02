# Lifecycle Integration I0 Inventory

## Scope And Reading Key

Inventory at Pyrolyze `b8d189f`, with no runtime modifications. The target is
`src/pyrolyze/runtime/context_state_lcm/` through
`context_bare_refactor_lcm.py`, including its call-site/slot-expression and
resource dependencies. The monolithic default is a reference, not a second
implementation to finish. Archived `*-old.py` files are not active dependencies.

Rows group fields only when they share the same source, mutation, and lifetime
contract. Constructor source is the initial source, not a statement that all
future writes are constructor-only. Proposed dispositions require the I0
decisions in `dev-docs/PytoLifecyleIntegI0Findings.md`:

- **Publication:** candidate `managed`/supported `owned` state on
  `DEFAULT_TRANSACTION`; assign replacements or declare conversion, never
  mutate current collections and expect rollback to undo them.
- **Scratch:** local invocation work/pass-key data, explicitly reset on each
  invocation even if the graph transaction remains active.
- **Identity/helper:** constructor identity or genuine nontransactional helper
  storage. This does not make helper-owned observable state nontransactional.
- **Domain resource:** acceptance, unsubscribe, cancellation, and retirement
  remain explicit resource behavior, not generic field copying.
- **Remove:** redundant restoration/mirroring, not a new field classification.

## Manager And Legacy-Engine Sites

| Site | Current Behavior | Required Direction |
| --- | --- | --- |
| `context_state_lcm/render_context.py:37` | Allocates `TransactionManager(tx_keys={PASS_TX_KEY})` for every render context, including nested ones | Allocate only for independent root; inject root manager into nested construction |
| `context_state_lcm/context_base.py:91` | Factory replaces generated `_y_state._y_transaction_manager` after construction has started | Remove bootstrap dummy field and inject manager before factories |
| Lifecycle-generated constructor default | Omitting `transaction_manager=` permits a private default manager, which bootstrap can then replace | Audit each construction seam; slots must not allocate throwaway managers |
| `runtime/call_site_context.py:156` | Private legacy manager for every call-site collection | Migrate collection implementation before injecting extracted shared manager |
| `runtime/slot_expr.py`, `SlotExpr.call_site_context_manager` | Dataclass default constructs a legacy manager, even if a caller later injects another | Avoid hidden allocation in both standalone and lifecycle-integrated paths |
| `runtime/context_lcm.py:2781,2913,2961` and reset paths | `_lcm_txm` allocations, helper states, and `_lcm_sync` mirrors | Retire after decomposed routing passes, not parallel maintenance |

`call_site_context.py:8` still imports `pyrolyze.lifecycle`. Its `_current`,
`_staged`, and `replace_current` methods access/mutate legacy
`current_record.values` / `working_record.values` directly. `begin_pass`,
`commit_pass`, `rollback_pass`, and `close_all` use unqualified manager calls.
Replacing the import alone would not preserve these semantics.

The decomposed adapter imports the extracted public lifecycle surface. It does
not turn ordinary subclasses' attributes into managed fields automatically.
No active target module other than the call-site dependency needs legacy record
access; the archived variants are deliberately excluded from that claim.

## Base And Slot Fields

Paths in the next sections are relative to `src/pyrolyze/runtime/context_state_lcm/`.

| Owner / Fields | Current Storage And Constructor Source | Mutation / Observable Contract | Proposed Disposition |
| --- | --- | --- | --- |
| `_base.py`: `owner` | Decorated `const`, required constructor argument | Stable public facade identity; referenced by graph/resources | Identity; audit owner/state cycles |
| `context_base.py`: `render_context_state_mgr`, `render_context`, `_resolved_render_context_state_mgr` | Initvars; explicit arguments and resolution factory | Construction inputs to root ownership | Keep as inputs; resolve manager upstream |
| `_generation_tracker_key`, `_context_kind`, `_pass_scope_handle_cls`, `_owner_type_name` | Const factories read owner configuration | Immutable helper/configuration values | Identity/helper |
| `_render_context_state_mgr` | Const factory from resolved initvar | Root reference used by graph queries | Identity; not a manager-installation hook |
| `_transaction_manager_bootstrap_bad_program` | Const self-factory with private manager mutation | Side effect substitutes manager mid-construction | Remove |
| `children_state` | Managed dict factory, identity compare, **PASS_TX_KEY** | Assign copied/reordered maps during graph attachment/pruning; membership owns active children | Publication; retirement after acceptance, provisional cleanup on failure |
| `ui_state`, `own_ui_state`, `own_ui_entries_state` | Managed tuple factories, **PASS_TX_KEY** | Candidate UI/entries, visitor/generation observables | Publication; validate projection before publish |
| `_pass_child_order`, `_pass_child_dirty` | Local-store tuple/dict factories | Old membership/dirty snapshots restored on rollback | Remove, not retained scratch |
| `_pass_started_tx` | Local-store bool default false | Tracks whether local scope owns transaction completion | Replace with explicit boundary/local-scope ownership |
| `slot_context.py`: `_parent_state_mgr`, `_slot_id`, `_render_context_state_mgr`, `_context_kind` | Ordinary constructor assignments | Stable identity/configuration, attachment/registration references | Identity; explicit provisional attachment |
| `_invoke_dirty` | Ordinary constructor bool then invalidation/invocation writes | Controls whether published invocation reruns, including outside render | Publication-sensitive flag; specify authorized out-of-render mutation |
| `_seen_in_pass` | Ordinary constructor bool then per-pass writes | Visitation, not published value | Scratch, reset per local invocation |
| `_site_metadata` | Ordinary empty tuple then invocation assignment | Visitor/debug metadata of accepted invocation | Publication |
| `leaf_slot_context.py`: `_last_args`, `_last_kwargs` | Ordinary empty tuples | Assigned after leaf execution; drive unchanged-call elision | Publication; no duplicate argument snapshots |
| `container_slot_context.py`: `_expects_native_root` | Ordinary false, set by container invocation | Candidate native-root requirement | Local invocation/configuration input; classify when container identity is locked |
| `_committed_native_root` | Ordinary false, copied at pass completion | Published structural validation state | Publication; remove eager committed copy |
| `_site_metadata` | Ordinary empty tuple | Accepted invocation metadata | Publication |
| `loop_item_slot_context.py`: `_current_value`, `_current_initialized` | Ordinary None/false | Immediately replaced by `update_current`; previous input affects dirty projection | Publication candidate, not inert loop cache |
| `_current_dirty` | Ordinary true | Structured dirty projection for this invocation | Scratch/result paired with candidate loop value |
| `directive_slot_context.py`: `_committed_selectors` | Ordinary empty tuple | Published mount routing; computed from binding at scope commit | Publication with mount/UI validation |
| `_pass_committed_selectors` | Ordinary empty tuple, copied/restored around pass | Rollback snapshot | Remove |

`rerunnable_slot_context.py` and `keyed_loop_slot_context.py` add behavior without
new instance storage. `is_scope_active()` currently reads shared key activity,
not a context-local marker. `_PassScopeHandle.activate` is a local control
object, but derives entry from that global test; I1 must repair the distinction
as part of live sharing, not postpone it.

## Component, Event, And Slot-Call Fields

| Owner / Fields | Current Storage And Constructor Source | Mutation / Observable Contract | Proposed Disposition |
| --- | --- | --- | --- |
| `component_call_slot_context.py` and `slot_expr_slot_context.py`: `parent_state_mgr`, `slot_id`, `invoke_dirty`, `seen_in_pass` | Explicit/default initvars | Feed corresponding storage factories | Keep constructor inputs, not a second authoritative copy |
| `_parent_state_mgr`, `_slot_id` | Const copies of initvars | Stable identity | Identity |
| `_invoke_dirty`, `_seen_in_pass` | Plain lifecycle fields copied from initvars | Same published-invalidation / invocation-visitation distinction as ordinary slots | Separate publication-sensitive flag from scratch |
| `_attach_to_graph_bad_program` | Const self-factory calls `attach_to_graph()` | Attaches/registers before construction has a clear success boundary | Remove; explicit provisional attachment |
| Component `_component_identity`, `_schema` | Local-store None/schema tuple | Changes can dispose/recreate child graph; affects rerender identity | Publication, coupled to child replacement |
| Component `_child_context_state_mgr` | Local-store None then render-context factory | Strong child reference; current code disposes eagerly | Publication/ownership adapter; old child survives candidate failure |
| Component `_site_metadata` | Local-store tuple factory | Published invocation metadata | Publication |
| Component `_call_state` | Managed frozen invocation record factory, **PASS_TX_KEY** | Replaced invocation arguments/dirty state; drives reruns | Publication key; retain immutable-record assignment |
| Component `_pass_owned_event_handler_order` | Local-store tuple factory | Saves handler membership/order for rollback reconstruction | Remove; transactional membership plus explicit retirement |
| `event_handler_slot_context.py`: `_committed_callback`, `_committed_key` | Ordinary None | Accepted callback/key read by stable dispatch | One managed publication selection |
| `_staged_callback`, `_staged_key` | Ordinary None | Pending copy transferred/reset manually | Remove duplicate engine once selection is authoritative |
| `_dispatch` | Ordinary None then stable closure | Must retain identity across callback replacement | Helper; closure reads current selection, deactivation stays explicit |
| `slot_call_slot_context.py`: `_slot_call_result_cls`, `_slot_runtime_context_cls` | Ordinary owner-class configuration | Helpers | Identity/helper |
| `_function_identity`, `_schema`, `_last_args`, `_last_kwargs` | Ordinary None/tuples | Immediately assigned from invocation result, used for elision | Publication selection |
| `_binding` | Ordinary None then binding factory/reuse | Published resource reference; referent can mutate before holder commit | Publication holder plus domain resource participant/adapter |
| `_site_metadata` | Ordinary tuple | Accepted call metadata | Publication |
| `_runtime_locals` | Ordinary dict factory | Runtime helper lookup/cache, may contain mutable context objects | Audit each payload; not automatically rollback-inert |
| Slot-expression `_site_metadata` | Local-store tuple factory | Accepted invocation metadata | Publication |
| `_call_site_context_manager` | Local-store factory allocates legacy service | Published collection lives inside the helper | Inject migrated shared-TM collection; helper identity may remain stable |
| `_runtime_locals_by_slot_id` | Local-store dict factory | Per-site helpers cleared on deactivate | Audit payload and unpublished-site lifetime |
| `_staged_call_site_ids` | Transient tuple factory, **PASS_TX_KEY** | Per-pass visitation/commit delivery list | Scratch/collection visitation; eliminate field-publication dispatch |
| `_staged_post_commit_callbacks` | Transient tuple factory, **PASS_TX_KEY** | Effects delivered after call-site publication | Capture immutable delivery batch before scratch cleanup |

`ComponentCallInvocationState` is a single value record containing
`runtime_func`, `bound_receiver`, `args`, `kwargs`, `author_args`, `author_kwargs`,
`dirty_state`, `pending_dirty_state`, `uses_dirty_state_api`, `packed_kwargs`,
`packed_kwarg_param_names`, and `param_names`. It is converted to its frozen
counterpart before `_call_state` assignment. These are not independently keyed
participants; audit referenced mutable dirty carriers when deciding rollback.

## Root And Override Fields

| Owner / Fields | Current Storage And Constructor Source | Mutation / Observable Contract | Proposed Disposition |
| --- | --- | --- | --- |
| `render_context.py`: `_owner_slot_state_mgr`, `_scheduler_root_state_mgr` | Ordinary constructor references | Nested ownership, shared scheduler root | Identity; same root must supply TM |
| `_scheduler`, `_app_context_store` | New root helper or inherited reference | Scheduler/invalidation and domain generation store | Root services; coordinate, do not replace with a second field engine |
| `_authored_app_context_lookup` | Constructor/parent reference | Lookup visible to authored rendering | Identity for root input; override selection is publication state |
| `_slots_by_id` | Ordinary dict factory, mutated on registration/deactivation | Public debug/visitor graph membership | Publication-sensitive registry; provisional entries must unwind on failure |
| `_mount_advertisements_by_slot` | Ordinary dict factory, rebuilt/published | Mount routing observable | Publication registry with pre-publication validation |
| `_mounted_callback` | Ordinary None then mount assignment | Determines scheduled boundary reruns | Root domain command; specify failed-mount retention |
| `_post_commit_callbacks` | Ordinary list | Drains effect/notification delivery | Root delivery batch, not inert helper storage |
| `_queued_invalidations` | Ordinary list | External invalidations may arrive independently of a candidate pass | Domain queue; preserve legitimate external work, discard candidate-only work explicitly |
| `_flush_poster`, `_flush_posted`, `_flush_running` | Ordinary None/false | Host scheduling and reentry guards | Scheduler service state, not automatically transaction fields |
| `app_context_override_slot_context.py`: `_structure_error_cls` | Ordinary owner-class configuration | Diagnostic class | Identity/helper |
| `_declared_keys` | Ordinary empty tuple then first declaration | Fixed-key invariant; failed first declaration may otherwise lock it | Publication/schema candidate with validation |
| `_committed_values`, `_committed_lookup` | Ordinary tuple/empty lookup | Accepted authored values/lookup | Managed publication selection |
| `_pass_committed_values`, `_pass_committed_lookup` | Ordinary snapshots | Manual rollback restore | Remove |
| `_pending_values`, `_pending_lookup`, `_pending_initialized` | Ordinary tuples/lookup/bool | Candidate state transferred manually | Use working publication selection; scratch only where truly invocation-local |
| `_committed_key_states` | Ordinary dict, creates mutable key state | Drips/parent links can notify during staging | Publication membership plus explicit subscription/notification adapter |
| Key state `key` | Dataclass constructor argument | Fixed identity | Identity |
| Key state `drip`, `parent_drip`, `unsubscribe_parent` | Drip factory, None references | Eager `next()`, subscribe/unsubscribe; externally observable | Domain resource; field rollback alone cannot undo delivered notifications |

`_InvalidationScheduler.queue`, `deferred`, and `active` are root-owned domain
queues/stacks. `active` is local boundary execution, not a transaction token;
queued external invalidation must survive the appropriate failure paths.
Refactor registries and immutable UI/scope handles are configuration/value
objects, not additional publication stores.

## Call-Site And Slot-Expression Dependency

| Owner / Fields | Current Contract | Migration Boundary |
| --- | --- | --- |
| `_CallSitePassContext.contexts` | Legacy `owned` dict on default key, direct record access also used | Shared-TM publication membership with explicit referent lifetime |
| `_CallSitePassContext.visited` | Legacy transient set on default key | Per-invocation visitation/pass scratch, reset even when joining outer transaction |
| `CallSiteContextManager._transaction_manager`, `_pass_context` | Private legacy manager/service; begin can rollback existing work | Inject migrated root TM, join without completing caller-owned transactions |
| `CallSiteContext.binding`, `function_identity`, `last_args`, `site_metadata` | Value carrier with explicit BindingBase reference ownership and replace behavior | Publication value/referent; choose one ownership system |
| `invoke_state.value` | Mutable sidecar, mark/get/dirty updates can affect reused current context | Separate external invalidation from candidate mutation; not an immutable snapshot |
| Legacy `BindingBase` reference count/accepted/closed state | Explicit inc/dec; `close()` decrements once; replacement shares refs | Do not mix with extracted intrinsic-ref ownership or assume collection assignment retires it |
| `_SlotExprCallSiteBinding.binding` | Legacy owner wrapper forwards resource commit/rollback; `_close` deactivates | Narrow domain lifetime adapter, not mechanical `binding()` marker replacement |
| `SlotExpr.value_lambda`, `dirty_lambda`, `dm`, `slot_ctx`, `host_factory`, `runtime_locals_provider`, `committed_ui_sync`, `lifecycle_slot_ctx` | Explicitly supplied or None configuration/delegates | Helper identity; some delegates lead to graph/resource side effects |
| `SlotExpr.evaluators`, `evaluators_by_slot_id`, `_runtime_locals_by_slot_id` | Dict factories; persistent evaluator identities and runtime helper lookup | Helpers may remain; newly-created entries require failed-pass lifetime audit |
| `SlotExpr.call_site_context_manager` | Default private legacy collection or explicitly injected service | Migrate collection and constructor seam together |
| `SlotExpr._pass_id`, `_pass_active`, `_staged_post_commit_callbacks` | Explicit expression-evaluation scope, not graph key lifetime | Local scratch/reset; preserve outer ownership |
| `SlotCallEvaluator.current_pass_id`, `_visited`, `_evaluated`, `_current_value`, `_current_dirty` | Reset at each expression evaluation, used for memoized expression results | Local invocation scratch |
| `_current_context`, `_staged_context` | Current/candidate references obtained from legacy collection | Collection facades are authoritative; avoid mirrored published state |
| `_pass_invoke_state`, `_next_invoke_state` | Per-evaluation dirt plus future invalidation | Distinguish local scratch from durable external invalidation |
| `_pass_binding`, `_rollback_binding` | Resource delivery/undo selection | Explicit domain participant/adapter, not ad hoc field restoration |
| Evaluator `host`, `_runtime_context_slot` | Stable helper references and resource host routing | Helper ownership; audit cycles and deactivation |
| Host `expr`, `slot_id`, `evaluator`, `delegate`, `advertisement` | Dataclass arguments/None defaults; delegates publication and caches retained advertisement | Helper identity plus publication-sensitive advertisement; unwind provisional host/resource links |

`SlotExpr.evaluate()` directly begins/rolls back the legacy manager, calls
evaluator commit/rollback outside lifecycle integration, or hands staged IDs
and callbacks to `SlotExprSlotContextStateMgr` when integrated. Both branches
must remain supported; migrating only the state-manager class leaves a legacy
transaction engine reachable through the evaluator.

## Resource-Category Mapping Proposal

| Resource | Fields / Current Mutation | Holder And Participant Proposal | Acceptance / Retirement |
| --- | --- | --- | --- |
| Slot value | `value`, immediately rebound | Managed publication value or small value participant | No external cleanup |
| External store | `host`, `ref`, `value`, `initialized`, `dirty`, `unsubscribe`; rebind may replace subscription immediately | Publication reference/selection plus subscription adapter; avoid mutating accepted resource in place before candidate succeeds | New candidate subscription must unwind on failure; old subscription retires after successful replacement; notification timing needs approval |
| Sync effect | `host`, `request`, `deps`, `staged_request`, `cleanup` | Publication request/dependency participant, domain after-publication delivery | Old cleanup before replacement effect; failed render must not run effect; preserve one delivery per accepted change |
| Async effect | Same request/dependency state plus `handle`, `active_token`, `cleanup` | Publication request participant and external task adapter | Cancel/cleanup prior task on accepted replacement/deactivation; reject stale completions; lifecycle tx token is not async task token |
| Mount advertisement | `host`, `request`, `staged_request`, `advertisement` | Publication registry/request participant with mount validation | Do not publish invalid/failed candidate; withdraw retired advert exactly once |
| Event handler | Callback/key plus stable dispatch closure | Managed callback/key selection | Dispatch reads committed selection; explicit deactivation makes old handles inactive |
| Component child graph | Identity/schema/child context and child-owned handlers | Transactional membership plus graph lifetime adapter | Preserve old child on failed replacement; release provisional child; retire accepted removals once |
| Override parent/drip link | Drip, parent ref, unsubscribe handle | Managed lookup/membership plus domain link adapter | Validate before delivery; subscription rollback cannot retract an already delivered notification |

All `SlotCallBinding` implementations are domain classes, not extracted
`BindingBase` subclasses. Sharing a TM does not enlist them. Either decorate
internal candidate state or provide a protocol adapter, and separately choose
the holder's replacement policy. Supported `owned()` is appropriate only after
its acceptance/lifetime contract is deliberately implemented. Mere `binding()`
storage is nontransactional reference storage, not a substitute for these roles.

Reference-cycle risks include owner -> state -> owner, parent/child/root graph
links, subscription callbacks -> host, and expression -> evaluator -> expression.
Observable cleanup must not depend on prompt garbage collection. This plan
does not invent a generic lifecycle `close()` protocol; domain deactivation
already exists and must have explicit publication/failure timing.

## Manual Completion To Remove Or Rehome

- `ContextBaseStateMgr.end_pass` / `rollback_pass`: class-name dispatch to
  slot-call, slot-expression, event-handler, component handler, and override
  commit/rollback; dirty/order restoration. Keep domain candidate UI computation,
  not generic child field publication.
- `ComponentCallSlotContextStateMgr`: handler commit/rollback and membership
  restoration; eager `_dispose_child_context()` on candidate identity changes.
- `SlotCallSlotContextStateMgr`: `commit_binding`, `rollback_binding`, and
  eager retirement inside call-result processing.
- `SlotExprSlotContextStateMgr`: binding loops, private call-site completion,
  UI sync, callback delivery, and `close_all()` on deactivate.
- `DirectiveSlotContextStateMgr`: selector copying/restoration before mount
  projection.
- `AppContextOverrideSlotContextStateMgr`: snapshots, pending-to-committed copy,
  drip restoration, and immediate subscription mutation.
- `RenderContextStateMgr`: separate `GenerationTracker.begin/commit/rollback`,
  mount registry rebuild, and callback flush. Coordinate domain generation and
  effects with publication; do not rename these all into generic lifecycle work.
- `CallSiteContextManager` / `SlotExpr` / `SlotCallEvaluator`: legacy ownership,
  private transactions, and delegated domain callbacks. These are active
  dependencies even when focused decomposed tests pass.

## Existing Coverage And Remaining Proof

I0 ran the existing external-store, effect, slot-expression, scheduler,
call-site, override, and mount subsets. They already express resource success,
refresh, subscription removal, replacement, cancellation, and rollback. Their
success assertions were not duplicated in the new characterization fixture.

Still required during the relevant integration slices: root failure after a
candidate resource replacement/removal; subscription/retirement counts across
that failure; local scope recovery when an after-hook throws; generation/UI
agreement at the chosen publication point. Existing passing standalone resource
tests do not establish those graph-wide contracts. L0 must pass before mandatory
cleanup is moved from legacy loops onto manager hooks.

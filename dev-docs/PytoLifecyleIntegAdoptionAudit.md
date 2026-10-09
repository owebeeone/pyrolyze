# Lifecycle Adoption Audit

Audited after I6b commit `583241e` on 2026-10-09. This is the remaining-state
and activation audit, not aggregate code-review acceptance or authorization to
switch normal routing. The single-cohort amendment remains authoritative.

## Current Routing

### I7 Trial After Aggregate Review

The aggregate review reproduced caught preparation errors publishing candidates
in component resolution and callback selection. Commit `0f88db2` encloses both
operations in the existing attempt scope: record the original failure immediately,
then discard at outer completion even when the caller catches it. Regression
coverage pins original exception identity, accepted-state preservation, and retry.
The correction passed 1143 tests, with 20 skips and the two known host failures.

The next checkpoint adds an **opt-in adoption candidate**, not default activation:
`PYROLYZE_CONTEXT_IMPL=lifecycle` selects `context_lifecycle.py`. It reuses the
decomposed facades and automatically installs the final pass-state completion on
fresh independent roots; nested roots join their owner's completion. The explicit
root-type guards admit this canonical facade, not arbitrary subclasses. Normal
`lcm` and the original fallback remain unchanged while adoption gaps are resolved.

Run a real UI trial from the repository root:

```sh
PYROLYZE_CONTEXT_IMPL=lifecycle \
PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python examples/run_grid_app_pyside6.py
```

The hello sample launched successfully. The existing native grid interaction test
passed through this candidate: cell updates, text edits, resizing, and layout
replacement. Both runners now reconcile after `mount()` returns, with subsequent
updates reconciled after the posted flush callback. They no longer read committed
UI before the outer render callback returns.

The initial default-activation experiment reported 1092 passing tests, 20 skips,
and 53 failures (including the two known host failures). Default activation was
withdrawn; do not treat these as new baseline debt or regenerate snapshots:

- Remaining sample/host callbacks reconcile before outer publication.
- Legacy handwritten container helpers remain deliberately unadmitted; classify
  actual consumers before choosing an adapter or migrating test scaffolding.
- Tests use old concrete binding types, manual slot preallocation, local completion,
  or caught-error continuation expectations. Separate those assumptions from real
  regressions before changing assertions.
- `test_use_app_context_rebinds_when_requested_key_changes` originally returned the
  old key's value on rerender. The refresh/input collision correction now checks
  prepared invocation inputs before binding refresh. Its positional, keyword, and
  callable-change regressions pass; clean notifications still avoid helper invocation.
  The existing app-context test now advances past the correct locale selection but
  fails on an extra rerender queued by override publication. That notification
  acknowledgment issue was a separate candidate-route defect; see the correction
  checkpoint below.
- Historical characterization snapshots describe the superseded completion model;
  preserve that evidence rather than bless the new output blindly.
- The 20-by-20 grid operation-budget trial was interrupted after extended execution
  in transaction completion. Its stack showed `_CompletionSession._check_ownership`
  repeatedly scanning the participant list. Profile the scaling before changing
  ownership enforcement; this trial did not establish a passing large-grid budget.

Next: close the candidate's functional and performance gaps, migrate canonical
consumers, then switch `lcm` and retire the monolithic engine. Compatibility
deletion remains gated on that verified adoption, not the successful small UI trial.

### Publication-Timing Consumer Migration (2026-10-10)

The current lifecycle-selected baseline reproduced 48 failures, with 1125 passing
tests and 20 skips. Five remaining runners reconciled committed UI inside the
initial render callback: the general grid, native Tk grid, unified grid, native
DearPyGui grid, and studio runners. They now reconcile after `mount()` returns;
their posted update callbacks already reconcile after flush completion. Six
native-host test setup calls use the same outer-completion ordering. No runtime
admission rules or test assertions were relaxed.

The affected lifecycle-selected UI files now have 17 passing tests and only the
known nested-row host-ordering failure. This also resolves both native Tk grid
failures from the activation baseline. Full normal routing has 1171 passing
tests, 20 skips, and the two known host-ordering failures. Full lifecycle routing
has 1136 passing tests, 20 skips, and 37 failures: 11 activation failures are
resolved. The remaining failures still include legacy container/slot routing,
concrete binding assumptions, and caught-error outer-abort expectations. Default
activation remains blocked. Next: classify and migrate the container/slot
consumers without weakening admission or blindly updating assertions.

### Remaining Adoption Failure Classification (2026-10-10)

The 37 failures after publication-timing migration are classified by their
first observed blocker, not certified root cause. Fixing one blocker may expose
another. This classification does not authorize relaxing a runtime contract.

| Count | Observed blocker | Next action |
| --- | --- | --- |
| 17 | Opaque container helpers rejected by `container_render.container_call` | Inventory actual helpers. Handwritten `contextmanager` scaffolds, such as phase-1 `_section`, yield without a declared native-context parameter or compiled-component metadata. Migrate scaffolds to supported forms where equivalent; decide separately whether real opaque consumers need support. Preserve recognition and failure tests. |
| 9 | Existing slot has a different type; `ensure_resolved_slot` rejects replacement | Handwritten guards call `visit_slot_and_dirty` before typed dispatch, including directives, native calls, and component bodies. Trace each allocation; migrate guards to allocation-free lookup and explicit clean retention, preserving ownership/removal tests. Do not simply allow arbitrary replacement. |
| 4 | Inner validation error is caught, then outer exit raises `RenderAttemptAborted` | Update outer-boundary expectations to the agreed rollback-only contract. Keep original diagnostic checks and prove accepted state survives and retry works. Cases are override arity/fixed-key validation and app-context invalid-key/missing-provider errors. |
| 3 | Concrete binding-type assertions | Two external-store tests expect `ExternalStoreBinding`; the advertisement test expects its legacy binding type. Preserve refresh, unsubscribe, publication, and retirement assertions while checking the selected lifecycle behavior rather than old implementation identity. Later assertions remain unverified until the type blocker is removed. |
| 1 | Subscription replacement cleanup order | `test_rebinding_external_store_subscribes_new_before_unsubscribing_old` expects old unsubscribe before reading the new value. The candidate reads the new value before retiring the accepted subscription. Check this against the approved outer-completion ownership contract before changing the expectation; it is not merely a type assertion. |
| 1 | Missing invalidation boundary trace records | `test_render_context_emits_invalidation_flush_and_boundary_records` receives no expected `start`/`end` records. Inspect tracing on the new boundary; do not remove observability assertions without checking the intended trace contract. |
| 2 | Known backend host-ordering failures | Keep the generic fault-mode and native PySide nested-row placement work separate from lifecycle adoption. |

The routing groups occur in `test_context_graph_phase1.py`,
`test_context_graph_phase3_phase4.py`, `test_context_graph_phase5_component_call.py`,
`test_context_graph_phase5a_invalidation_kernel.py`,
`test_context_graph_phase7_native_ui.py`, `test_context_graph_phase8_scheduler.py`,
`test_mount_advert_binding.py`, `test_mount_directive_context.py`,
`test_runtime_pyro_call.py`, and `test_visitor_context_graph.py`, all under `tests/`.
Start with the handwritten container/guard consumers, one verified group at a
time. No runtime or test-expectation changes accompany this classification.

### Compiler-Driven Scaffold Migration (2026-10-10)

The phase-1, keyed-loop, helper-selected component, and invalidation scaffolds
now use authored source through `load_transformed_namespace`, rather than
handwritten lowering. Obsolete helper factories and their fixed slot identifiers
are removed. Tests discover generated graph identities and continue to check
published UI, clean retention, keyed reorder, subscription reuse/removal,
callback identity, notification coalescing, child-only rerenders, and FIFO queues.

Scopes use supported native context parameters and badges produce concrete UI;
scope execution logs replace artificial context-manager enter/exit logs. These
fixtures do not certify arbitrary Python context-manager compatibility. The
dynamic component fixture resolves its constant fallback before the scope:
placing that local selection inside the scope makes current lowering
conservatively rerun the scope, so that shape cannot prove clean scope elision.

Direct runtime probes remain where they deliberately control dirty forwarding,
callback ownership, invalid calls, or failure injection. Two leaf guards in the
component identity probe use allocation-free `slot_needs_execution`, avoiding
the old generic slot preallocation. No runtime implementation or admission
policy changes accompany this checkpoint. Explicit opaque context-manager and
permissive-callable compatibility tests remain unresolved, not rewritten away.

Focused verification: all 29 tests in the four affected files pass on normal
routing and lifecycle routing; lifecycle also passes all 29 with Python
assembly. Full normal regression: 1170 passed, 20 skipped, and only the two
known host-ordering failures. Full lifecycle regression: 1150 passed, 20 skipped,
and 22 failures, down from the classified 37. The remaining opaque compatibility
cases, other slot-preallocation consumers, binding assumptions, caught-error
expectations, cleanup-order check, and boundary tracing remain unresolved.

Subsequent operator-requested migration replaces all component/container bodies
in the phase-5 component-call file, including the failed-pass fixture, with
compiled source. Small wrappers observe incoming dirty flags; direct test drivers
dispatch controlled inputs but no longer reproduce compiler-generated guards or
component bodies. The earlier full-suite counts precede this follow-up.

This exposed a compiler gap: an annotated callback passed to
`call_native(button_element)` remained a raw lambda, failing retained callback
identity. The previous handwritten body explicitly called `event_handler`,
bypassing the gap. The operator authorized a bounded compiler correction:
local/imported factories with declared handler parameters now use immediate
context-owned event handlers; component arguments retain deferred attachment.
Ordinary callable parameters remain untouched. Positional/keyword recognition,
stable callback identity, refreshed closures, and lifecycle outer rollback are
covered. The rollback fixture also proves accepted UI identity and clean retry.
Legacy local completion does not acquire lifecycle outer rollback semantics.

Follow-up verification: 24 focused native/component-handler checks pass on
normal routing; 45 affected checks pass on lifecycle with Python assembly.
The concurrent full runs report 1174 passed / 3 failed on normal routing and
1154 passed / 23 failed on lifecycle, both with 20 existing skips. Both runs
also wrote the same basic-shape diagnostic graph and hit a Graphviz syntax
error. That exact test passes in isolated reruns on each route, confirming
shared diagnostic-output interference rather than a reproduced compiler defect.
Do not run those suites concurrently when writing the same graph artifacts.
All other failures match the known normal/adoption inventories.

Further handwritten-body candidates are external-store readers in
`tests/test_context_graph_phase2_external_store.py`, the toolbar in
`tests/test_context_graph_phase7_native_ui.py`, the visitor graph in
`tests/test_visitor_context_graph.py`, hook guards in `tests/test_hooks_module.py`,
and component bodies in `tests/test_app_context_framework.py`,
`tests/test_app_context_override_context.py`, and
`tests/test_context_graph_no_comp_value_api.py`. Inspect each by purpose:
authored behavior should use compiled input; explicit runtime misuse,
introspection, and native context helpers are not automatically obsolete.

### Handwritten Lowering Removal Project

Goal: authored behavior tests must run compiler-generated code, not a second
hand-maintained approximation of lowering. Keep behavioral assertions, not old
allocation details. Wrappers may observe inputs and inject controlled test
conditions; they must delegate component execution to compiled bodies.

- [x] Phase-1, keyed-loop, component-call, and invalidation fixtures migrated.
- [x] Component/container dirty-forwarding and rollback bodies compiled.
- [x] Native callback lowering discrepancy reproduced and corrected.
- [x] Visitor graph and hook-render success fixtures migrated.
- [x] Native toolbar success fixture migrated; native API misuse kept separate.
- [x] App-context and component-introspection bodies compiled behind wrappers.
- [x] External-store reader bodies compiled; binding/dirty-result/injection
  assertions retained as runtime-level observations of generated execution.
- [ ] Audit remaining tests for hand-maintained lowering, document intentional
  exceptions, and verify the final batch on both routes and assembly backends.

Check each group with focused tests. Run broad regressions at checkpoint
boundaries, sequentially because graph diagnostics share output paths. Do not
activate lifecycle, relax resource cleanup, erase generic-context-manager
compatibility tests, or rewrite generated goldens merely to reduce failures.

The app-context/introspection/external-store batch replaces component and reader
bodies with authored input. `ObservedCompiledContext` in
`tests/slot_expr_test_utils.py` delegates generated expression construction and
evaluation unchanged, then records the returned value and compiler dirt sink.
It does not synthesize slots, argument dirt, or pass scopes. Method wrappers
retain descriptor-binding coverage while delegating execution to compiled bodies.
External-store assertions discover generated call sites rather than pinning the
old handwritten slot IDs; binding observation retains accepted-first visibility.

Intentional direct probes remain: app-context store identity and shutdown,
lexical overrides and notification forwarding, plain-call dirt projection,
callback-handle commit/rollback and descriptors, and drivers supplying controlled
component dirt. These are API-contract tests, not substitute component bodies.
No assertion about cleanup order, concrete binding type, or caught-error
completion has been relaxed in this fixture migration.

Verification for this batch: all 33 affected tests pass on normal routing with
both assembly backends. Lifecycle has 28 passes and the same five known failures
in these files (two caught-error expectations, two legacy binding-type checks,
one subscription cleanup-order check); all 28 passing cases also pass on Python
assembly. Sequential full native runs: normal routing 1,175 passed, 20 skipped,
two known host-ordering failures; lifecycle routing 1,156 passed, 20 skipped,
21 existing adoption/backend failures. The compiled visitor fixture clears one
previous adoption failure. No shared diagnostic-file collision occurred.
`git diff --check` passes; Ruff is unavailable in the current environment.

### Large-Grid Performance Correction (2026-10-09)

Profiling confirmed O(N^2) ownership checks in `yidl-lifecycle`: each callback
check copied and compared all participants. Versioned membership now preserves
those checks in constant time; the ordered participants are captured once.
The same unprofiled logical 20x20 update dropped from 9.468 s to 0.866 s and the
first logical layout toggle from 60.419 s to 1.278 s. The unchanged full UI
operation-budget test passed on an isolated rerun. See the library's
`dev-docs/L0CompletionVerification.md` for the measurement and guard details.

The next bounded correction batches overlapping roots in component/override
completion, with separate visitation for committed and candidate views. Mount
advertisement walks stop at nested render boundaries because each advertisement
belongs to one render owner. Detached roots are still visited. No traversal
results are cached across staging or publication, and the other adapters still
walk their own fresh graph views.

On the same sequential 5/10/20 logical-update workload, the graph correction
reduced the 20x20 update further to 0.720 s and the first layout toggle to 1.101 s.
These measurements exclude host reconciliation and are observations, not test
thresholds. Deterministic regressions cover overlapping roots at 10/100/1,000
nodes, nested roots, independent graph views, later mutation, and local render
boundaries. Existing canonical traces remain the behavioral acceptance surface.
This does not activate normal lifecycle routing or resolve the host-ordering bugs.

Verification after the graph correction: 59 native focused/canonical checks and
31 targeted Python-backend checks pass, with no golden changes. The full normal
route suite reports 1,167 passed, 20 existing skips and the same two known
host-ordering failures. The graph correction is committed as `9f52d76`; the
library ownership correction is committed in `yidl-lifecycle` as `029c4a8`.

With normal routing restored and the two sample runners corrected, regression
verification reports 1144 passed, 20 skipped, and only the two known host failures.
Candidate native checks pass the existing grid interaction and generic-harness
tests; Python-backend checks pass the generic harness and preparation-failure
regressions. These results do not certify the excluded large-grid trial or the
remaining admission paths.

After the refresh/input collision correction, normal regression reports 1147
passed, 20 skipped, and the same two host failures. Focused native expression/store
checks pass 58 tests, and Python-backend expression checks pass 50. The candidate
app-context test still fails at its no-extra-render assertion, after correctly
selecting the new key; redundant override-publication invalidation is not fixed
by changing invocation precedence.

### Override Read Acknowledgment Correction

The operator-authorized
[read acknowledgment correction](PytoLifecyleIntegOverrideReadAcknowledgment.md)
is implemented on the opt-in candidate. A selected binding carries its exact
override-read receipt; publication checks the current accepted reader before
incrementing subscription revision or queuing invalidation. Skipped readers and
independent events remain on the ordinary notification path. Resource ownership,
AST lowering, compiler libraries, and normal routing are unchanged.

The new canonical trace covers slot-call and expression readers through three
override levels, resource reuse, selective acknowledgment, independent events,
and the final selected read. Fault tests cover rollback, reentry, failed
projection/publication, plain parent changes, and retained-snapshot collection.
The original key-rebinding test and parent-through-None case pass under the
explicit lifecycle selector. Two historical caught-error tests in the same file
still require the recorded outer-abort consumer migration under that selector;
they have not been weakened or reclassified as normal-route regressions.

The lightweight review applies to the original design draft, not the runtime
patch. Default activation, legacy consumer migration, and large-grid scaling
remain separate gates. No historical snapshot was regenerated.

Verification: normal native regression reports **1161 passed, 20 skipped, and
the same two known host-ordering failures**. The **23 targeted Python-backend
checks pass**, including the new canonical trace, fault cases, existing override
tests, and the two app-context success cases under the lifecycle selector.
No tests were disabled for this correction. `git diff --check` passes.

Reproduce with the workspace dependencies available: run `pytest -q` for normal
regression; for the focused correction use
`tests/test_lcm_override_read_acknowledgment.py` and
`tests/test_lcm_integration_characterization.py::test_override_read_acknowledgment_golden`.
Set `ASTICHI_LOWER_ENGINE=python` to repeat on Python assembly. Set
`PYROLYZE_CONTEXT_IMPL=lifecycle` for
`tests/test_use_app_context_runtime.py::test_use_app_context_rebinds_when_requested_key_changes`
and `test_use_app_context_reads_parent_value_through_none_override`.

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
| LoopItem value/dirty/initialized | Managed `_selection` record on the keyed-loop gate; legacy compatibility record retained | Remove compatibility record after adoption; checkpoint is committed as `053dd3c` |
| `_invoke_dirty`, `_seen_in_pass` | Compatibility properties; pass-state gate derives dirtiness from revisions and manages visitation | Delete legacy backing fields only after adoption; keep requests independent |
| `_pass_child_dirty`, `_field_only_has_snapshot` | Earlier gates save/restore dirty flags; pass-state gate uses request/managed acknowledgment | Remove compatibility stores during adoption; no restoration/replay on the new gate |
| `_pass_child_order`, `_pass_started_tx` | Legacy local completion; private order writes removed in `53b0ec1` | Delete legacy declarations after adoption |
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

Subsequent operator-approved implementation:
[pass-state consumption](PytoLifecyleIntegPassState.md) adds ordinary request
revisions, managed acknowledgment and visitation, and a local captured revision.
The newest gate does not capture/restore dirty snapshots or replay I6b's
invalidation ledger. Earlier gates retain their compatibility behavior. The
canonical checkpoint covers retry, late notifications, repeated local passes,
partial rerender, independent roots, and owned-handler omission. Aggregate review
and ordinary compiled-component admission remain before default adoption.

### D: Aggregate Review And I7 Adoption

After A-C, run the operator-requested aggregate implementation review over the
resource ownership adapters, preparation/publication sequence, notification
batch draining, original-token fencing, graph retirement, and actual compiled
routes. Resolve blocking findings before default activation.

The pass-state probe identified an existing ordinary compiled-component
admission gap: generic visitation constructs a `SlotContext` before component
dispatch requests a different slot type. Correct classification/construction
and prove that actual compiled route before activation; this is distinct from
the completed scope-container routing and invalidation-consumption checkpoints.

Subsequent correction: the [pass-state checkpoint](PytoLifecyleIntegPassState.md)
now records allocation-free dirty lookup and explicit clean retention across
all five compiled guard paths. Component resolution precedes construction;
null component/container selection omits candidate membership. Outcome tests
cover retention, replacement, removal, rollback, subscription cleanup, and
late invalidation. This closes the reproduced admission gap, not aggregate
review or default-activation approval.

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

Current next checkpoint, after the subsequent loop, container, pass-state, and
compiled-admission implementations: aggregate integration review under D.
Review the actual compiled routes and resource/notification ownership together;
then undertake I7 canonical-root activation and compatibility removal only
after blocking findings are resolved.

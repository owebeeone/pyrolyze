# AST Fixes For Calling Slots Plan AB/AC

## Purpose

This addendum narrows Phases AB and AC to the specific remaining parity gaps between:

- the old `PlainCallSlotContext.evaluate(...)` path in `pyrolyze/src/pyrolyze/runtime/context.py`
- the new `SlotExpr` runtime in `pyrolyze/src/pyrolyze/runtime/slot_expr.py`

Phase AA already covered:

- shared handler/binding extraction and reuse
- staged commit/rollback
- unvisited-call deactivation
- handler-family runtime parity tests
- callable dirt support
- provider optimization

Phases AB and AC are the remaining runtime-parity work needed before compiler
migration should start.

## Remaining AB Scope

### 1. `invoke_dirty` parity

Old `plain_call` reinvokes when `self.invoke_dirty` is true, even if:

- function identity is unchanged
- args/kwargs are unchanged
- input dirt is clean

`SlotExpr` does not yet have an equivalent forced-invoke surface.

Phase AB needs:

- a runtime model for forced reinvocation
- tests proving it overrides stable-input elision
- commit/rollback behavior that matches the rest of `SlotExpr`

### 2. `PlainCallRuntimeContext` parity or explicit replacement

Old `plain_call` inspects the callable signature and automatically injects `PlainCallRuntimeContext` when requested.

`SlotExpr` does not currently do this.

Phase AB must either:

- implement the same runtime-context injection behavior

or

- define and document a replacement model that is intentionally different

and then cover that behavior in tests.

### 3. Registration/deactivation pairing audit

Phase AA established the main lifecycle behavior, but AB should explicitly close the pairing guarantee:

- no committed registration without a later possible deactivation path
- no staged activation/deactivation leaks after failure
- no handler-family mismatch across reachability transitions

This should be tested across:

- plain values where replacement occurs
- external stores
- effects
- async effects
- mount advertisements

### 4. Retained-reference audit

The plan still requires avoiding unnecessary retained raw-result references.

Phase AB should verify that:

- bindings retain only what their semantics require
- evaluator caches do not hold onto larger objects than necessary
- replacement/deactivation does not accidentally keep stale raw objects alive

This is partly code inspection and partly targeted tests.

## Remaining AC Scope

### 1. Real call-site identity using `SlotId`

Current `SlotExpr` call sites still use authored/local ids such as:

- `"v1"`
- `"a"`
- `"b"`

Those are rewrite conveniences, not real runtime identities.

Phase AC needs:

- call-site identity carried as a real compiler-generated `SlotId`
- tests proving evaluator variable names do not determine runtime identity
- a runtime API shape that does not imply string ids are sufficient long-term

### 2. Real host integration instead of local host shim

`SlotExpr` currently uses a local `_SlotExprPlainCallHost` that provides:

- no-op invalidation
- local staged post-commit callback handling
- local advertisement object storage

That is enough for isolated runtime tests, but not yet full runtime integration.

Phase AC must decide and implement one of:

- real slot/render-context integration for invalidation and mount advertisement publication

or

- an explicit documented equivalence boundary if the shim is intentionally retained

The preferred direction is real integration if feasible without destabilizing the runtime.

## Recommended AB/AC Test Additions

Suggested file targets:

- `pyrolyze/tests/test_runtime_slot_expr.py`
- optional: `pyrolyze/tests/test_runtime_slot_expr_lifecycle.py`

### `invoke_dirty` tests

- stable callable + stable args + clean arg dirt + forced invoke => reinvokes
- forced invoke with effect-like handler still stages/commits correctly
- forced invoke with external store still preserves refresh semantics

### runtime-context injection tests

- callable annotated for `PlainCallRuntimeContext` receives runtime context under `SlotExpr`
- runtime context is not injected twice when already supplied
- callable identity/caching still works with injected context

### call-site identity tests

- same evaluator parameter names with different compiler-generated `SlotId`s remain distinct
- different evaluator names with same call-site `SlotId` remain the same runtime call site
- deactivation and retained bindings key off `SlotId`, not temporary parameter names

### real host integration tests

- external store invalidation reaches the real slot/render invalidation path if integration is implemented
- mount advertisement publish/withdraw goes through the real host path if integration is implemented
- post-commit callbacks use the real scheduling path if integration is implemented

### registration/deactivation pairing tests

- activation followed by exception does not leak committed state
- activation followed by successful branch removal deactivates exactly once
- replacement across handler kinds deactivates the old binding exactly once

### retained-reference tests

- replacing a large plain-value result does not keep the previous raw result reachable through the evaluator
- effect and advert bindings expose only their semantic value surface
- external-store binding refresh does not retain stale store values beyond the binding contract

## Precise AB/AC Test Set

This section is the concrete implementation checklist for Phases AB and AC.

Unless there is a strong reason to split files, these should initially land in:

- `pyrolyze/tests/test_runtime_slot_expr.py`

If the lifecycle coverage becomes too dense, move the more involved cases into:

- `pyrolyze/tests/test_runtime_slot_expr_lifecycle.py`

Each test below should validate both:

- the immediate expression-visible result/value behavior
- the lifecycle side effects on staged state, committed state, and deactivation

Where a behavior is expected to match old `plain_call`, the test should compare against the legacy runtime behavior directly when practical, or else encode the same externally visible contract in the assertion set.

### `invoke_dirty` parity tests

Implement all of these:

1. `test_slot_expr_invoke_dirty_forces_reinvoke_on_plain_value_handler`
   - stable callable
   - stable args/kwargs
   - clean arg dirt
   - forced invoke set
   - callable is reinvoked

2. `test_slot_expr_invoke_dirty_forces_reinvoke_on_external_store_handler`
   - stable store identity
   - no input dirt
   - forced invoke set
   - source callable reinvokes rather than only refreshing binding

3. `test_slot_expr_invoke_dirty_forces_reinvoke_on_use_effect_handler`
   - forced invoke set
   - request is restaged and committed correctly

4. `test_slot_expr_invoke_dirty_forces_reinvoke_on_use_effect_async_handler`
   - forced invoke set
   - request is restaged and committed correctly

5. `test_slot_expr_invoke_dirty_forces_reinvoke_on_mount_advert_handler`
   - forced invoke set
   - advert source reinvokes and commit path still publishes correctly

6. `test_slot_expr_invoke_dirty_does_not_bypass_commit_rollback_rules`
   - forced invoke set
   - later expression step raises
   - no staged state leaks through

7. `test_slot_expr_invoke_dirty_single_call_fast_path_matches_general_slot_call`
   - same callable/args through `single_call(...)` and `slot_call(...)`
   - forced invoke set
   - both paths reinvoke with identical lifecycle behavior

### `PlainCallRuntimeContext` parity tests

Implement all of these:

1. `test_slot_expr_injects_runtime_context_when_callable_requests_it`
   - callable has annotated runtime-context parameter
   - injected context is present

2. `test_slot_expr_does_not_double_inject_runtime_context_when_explicitly_supplied`
   - callable already receives runtime-context kwarg through args lambda
   - runtime does not add a second one

3. `test_slot_expr_runtime_context_injection_preserves_memoization_contract`
   - stable callable/args
   - injected runtime context present
   - no extra reinvokes caused by injection alone

4. `test_slot_expr_runtime_context_injection_works_with_callable_dirt`
   - callable dirt true
   - reinvoke still receives context properly

5. `test_slot_expr_runtime_context_injection_works_with_effect_like_handler`
   - effect/effect-async request callable asks for runtime context
   - request still stages and commits correctly

6. `test_slot_expr_runtime_context_injection_works_for_single_call_fast_path`
   - `single_call(...)` path
   - runtime context requested
   - injected value matches general `slot_call(...)` behavior

### Phase AC: Call-site identity / `SlotId` tests

Implement all of these:

1. `test_slot_expr_call_site_identity_uses_slot_id_not_parameter_name`
   - same parameter name reused in different lowered sites
   - distinct `SlotId`s
   - runtime treats them as distinct call sites

2. `test_slot_expr_call_site_identity_stable_across_parameter_rename`
   - same call-site `SlotId`
   - different temporary evaluator variable name
   - runtime identity remains stable

3. `test_slot_expr_call_site_identity_controls_deactivation`
   - retained call site under same `SlotId` stays live
   - changed `SlotId` deactivates old binding and creates new one

4. `test_slot_expr_call_site_identity_controls_cached_binding_reuse`
   - same `SlotId` reuses binding/cached state
   - changed `SlotId` does not

5. `test_slot_expr_call_site_identity_controls_external_store_subscription_reuse`
   - same `SlotId` reuses existing subscription/binding
   - changed `SlotId` unsubscribes old binding and creates new one

6. `test_slot_expr_call_site_identity_controls_effect_cleanup_boundary`
   - effect-like call under one `SlotId`
   - new `SlotId` causes old cleanup/cancel path and new activation path

### Phase AC: Real host integration or shim-equivalence tests

If real integration is implemented, add:

1. `test_slot_expr_external_store_invalidation_flows_to_real_runtime_host`
2. `test_slot_expr_mount_advert_publish_withdraw_flows_to_real_runtime_host`
3. `test_slot_expr_post_commit_callbacks_use_real_runtime_host`

If the shim remains, replace the above with:

1. `test_slot_expr_host_shim_matches_plain_call_invalidation_contract`
2. `test_slot_expr_host_shim_matches_plain_call_mount_advert_contract`
3. `test_slot_expr_host_shim_matches_plain_call_post_commit_contract`

In either case, also add:

4. `test_slot_expr_host_path_is_identical_between_single_call_and_general_slot_call`
   - confirms the fast path does not bypass required host semantics

### Registration/deactivation pairing tests

Implement all of these:

1. `test_slot_expr_external_store_registration_deactivation_pairing`
   - subscribe on activation
   - unsubscribe exactly once on deactivation

2. `test_slot_expr_use_effect_cleanup_pairs_with_activation`
   - effect run implies later cleanup path
   - cleanup occurs exactly once on branch removal/replacement

3. `test_slot_expr_use_effect_async_cancel_pairs_with_activation`
   - async start implies later cancel path
   - cancel occurs exactly once on branch removal/replacement

4. `test_slot_expr_mount_advert_publish_withdraw_pairing`
   - publish on commit
   - withdraw exactly once on deactivation/replacement

5. `test_slot_expr_handler_kind_replacement_deactivates_previous_binding_once`
   - replace one handler kind with another
   - old binding deactivates exactly once

6. `test_slot_expr_exception_does_not_commit_registration_pairing_changes`
   - staged activation/deactivation exists in failing pass
   - no registration or deregistration leak through

7. `test_slot_expr_short_circuit_branch_removal_deactivates_exactly_one_previous_call`
   - first pass reaches right-hand branch
   - second pass short-circuits before it
   - deactivation occurs exactly once after successful commit

8. `test_slot_expr_eager_any_keeps_all_calls_registered`
   - all calls evaluated every pass
   - no unwanted deactivation from reachability logic

### Retained-reference tests

Implement all of these:

1. `test_slot_expr_plain_value_replacement_does_not_retain_old_raw_result`
   - replace a large object result
   - evaluator/binding no longer exposes old object after commit

2. `test_slot_expr_external_store_binding_does_not_retain_stale_value_beyond_binding_contract`
   - store updates
   - current binding value updates
   - stale value is not still reachable through runtime caches except as required by equality/diff logic

3. `test_slot_expr_effect_binding_exposes_only_semantic_none_value`
   - runtime does not expose internal staged request object as expression value

4. `test_slot_expr_mount_advert_binding_exposes_request_but_not_retired_advertisement_state`
   - expression-visible value is current request surface
   - retired advertisement state is not leaked back through evaluator value

5. `test_slot_expr_deactivated_call_site_does_not_retain_previous_raw_value_through_evaluator_cache`
   - call site was live
   - later becomes unreachable and deactivates
   - prior raw value is no longer exposed through the evaluator after commit

### Cross-cutting regression tests

Implement all of these:

1. `test_slot_expr_reachability_contract_matches_plain_call_branch_behavior`
   - short-circuit form deactivates previously reached branch call sites
   - eager form keeps them reachable

2. `test_slot_expr_exception_rolls_back_dirty_binding_and_call_site_lifecycle_together`
   - a failing pass leaves both `dm.bind` outputs and handler state unchanged

3. `test_slot_expr_general_slot_call_and_single_call_have_identical_reinvoke_rules`
   - stable inputs
   - dirty args
   - dirty callable/provider
   - forced invoke
   - each case behaves the same across both APIs

4. `test_slot_expr_handler_family_matrix_covers_all_plain_call_semantics_handlers`
   - plain value
   - external store
   - mount advert
   - use effect
   - use effect async
   - verifies that each family participates in the same commit/rollback protocol

### Expected assertion shape

For the tests above, assertions should explicitly cover the following where relevant:

- returned expression value
- returned dirty shape
- committed `dm.bind` outputs
- staged vs committed handler state after success
- staged vs committed handler state after failure
- registration/subscription counts
- cleanup/cancel/withdraw call counts
- reinvocation count of the source callable
- reuse vs replacement of binding objects
- identity keyed by `SlotId`, not temporary evaluator name

### Recommended implementation order

To minimize churn, implement the tests in this order:

1. `invoke_dirty` tests
2. runtime-context injection tests
3. registration/deactivation pairing tests
4. retained-reference tests
5. `SlotId` identity tests
6. host integration or shim-equivalence tests

## AB Completion Gate

Phase AB is complete when:

- `invoke_dirty` parity is closed
- runtime-context injection parity is closed or replaced by an explicit documented design
- registration/deactivation pairing is covered by tests
- retained-reference behavior has been reviewed and covered where practical

At that point, the remaining runtime-parity differences should be limited to:

- real `SlotId` identity
- host integration or formal shim equivalence

## AC Completion Gate

Phase AC is complete when:

- call-site identity is carried as real `SlotId`
- host-shim behavior is replaced or formally justified
- identity-sensitive reuse/deactivation is covered by tests
- host semantics are covered by tests for both `single_call(...)` and `slot_call(...)`

At that point, the remaining differences should be compiler-lowering concerns, not runtime-parity gaps.

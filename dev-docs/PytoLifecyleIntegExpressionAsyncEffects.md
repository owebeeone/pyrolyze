# Async Effect Expressions

Status: implemented behind `_enable_async_effect_expr_render`, extending the
synchronous-effect expression proof. Normal routing and the earlier gates remain
unchanged. Aggregate implementation review remains deferred.

## Ownership And Delivery

The existing `_AsyncEffectBinding` and `_AsyncEffectResource` provide dependency
reuse, startup, completion fencing, cancellation, and cleanup. Expression
collections retain the same private resource wrapper used by subscriptions and
synchronous effects. The shared expression delivery loop now uses the existing
delivery-resource protocol rather than requiring a synchronous resource type.

Async requests remain inert until outer publication. Rollback releases pending
ownership without starting or cleaning an unstarted operation. Replacement and
removal release accepted ownership even when value snapshots survive. Cancel and
cleanup drain independently; failure suppresses only that call site's replacement
while other delivery actions run. Published state is not undone after startup or
cleanup fails, and reuse is quarantined on failure.

Each selected operation uses a stable resource host with weak state links.
Completion requests expression reevaluation through existing invalidation paths;
subscription notifications continue using refresh-only flags. Those independent
invalidation flags are not candidate lifecycle-value publication. External
callbacks hold weak resource links and cannot retain the graph. Teardown fences
callbacks before cancellation; completion during startup cannot resurrect a
finished handle. Original transaction-token checks still fence dependency
comparison and candidate writes.

## Coverage

`tests/data/lcm_integration/expression_async_effect_lifecycle.py` and its authored
JSON baseline record actual startup/cancel/cleanup order, provisional requests,
stable dependency reuse, rollback, latest pending selection, retained snapshots,
stale/cancel-time callbacks, valid completion invalidation, and removal.

`tests/test_runtime_context_state_lcm_expression_async_effects.py` covers failing
startup, cancellation plus cleanup errors, completion during startup, weak graph
lifetime, startup reentry, replaced-token dependency comparison, and rejection of
mount expression results before advertisement publication.

Verification: full native suite **1050 passed, 2 unchanged host-ordering failures,
20 skipped**; affected expression proofs and characterization on Python assembly
**51 passed**. Historical goldens remain unchanged.

## Remaining Gates

Mount expressions are the next adapter checkpoint. Existing mount and async
slot-call routes are unaffected. Normal-route adoption, remaining graph and
registration migration, and deletion of legacy completion paths remain pending.
No lifecycle-library, shared handler, or compiler changes were required.

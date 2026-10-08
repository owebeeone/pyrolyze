# Synchronous Effect Expressions

Status: implemented behind `_enable_effect_expr_render`, extending the separate
subscription-expression proof. Normal routing, the earlier proofs' admission,
and shared legacy handlers are unchanged. Aggregate implementation review remains
deferred; this checkpoint is not independently accepted.

## Completion

Expression invocation records and visitation publish with the outer render's
`PASS_TX_KEY`. New `_EffectResource` instances are inert during evaluation. The
existing `_EffectBinding` handles dependency comparison and active-resource reuse;
the expression resource wrapper retains explicit ownership through the existing
lifecycle-owned call-site collection.

Collection retirement completes before expression effect delivery. Only confirmed
publication starts the captured accepted effects. Rollback never starts candidate
effects. Stable dependencies reuse a started resource; repeated unpublished
requests select the latest callback, including when dependencies are equal.
`None` dependencies do not reuse an active effect; empty dependencies do.

Replacement/removal releases old ownership even if Python snapshots survive.
Failed cleanup suppresses that call site's replacement, not independent setup.
Independent setup actions drain ordinary and system exceptions, preserving a lone
exception or grouping multiple failures. Setup failure does not undo publication;
it quarantines reuse. Setup/cleanup reentry remains guarded, and dependency
comparison cannot stage into a replaced transaction token.

## Coverage

`tests/data/lcm_integration/expression_effect_lifecycle.py` with its authored JSON
baseline covers provisional delivery, stable dependency reuse, failed replacement,
cleanup-before-setup, latest pending selection, retained snapshots, omission,
and `None`/empty dependency cases. The characterization harness runs the fixture.

`tests/test_runtime_context_state_lcm_expression_effects.py` covers setup-error
draining, cleanup failure, invalid cleanup results, setup reentry, replaced-token
dependency comparison, and a caught expression failure preventing delivery.

Verification: full native suite **1042 passed, 2 unchanged host-ordering failures,
20 skipped**; affected expression proofs and characterization tests on Python
assembly **43 passed**; final native resource-expression goldens/fault tests
**14 passed**. Historical snapshots remain unchanged.

## Remaining Gates

The separate [async-effect expression proof](PytoLifecyleIntegExpressionAsyncEffects.md)
now extends the same ownership and delivery path. Mount expressions remain
rejected before binding. Their adapters,
remaining graph/registration migration, normal-route adoption, and deletion of
legacy completion paths remain later work. No lifecycle-library or compiler
changes are needed for this checkpoint.

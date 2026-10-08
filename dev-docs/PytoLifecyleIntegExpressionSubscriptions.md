# Subscription Expressions

Status: implemented behind `_enable_subscription_expr_render`; normal rendering
and the earlier plain-expression proof remain unchanged. Aggregate integration
review is still deferred, not independently accepted by this checkpoint.

## Completion And Ownership

Expression selection and visitation share the outer render's `PASS_TX_KEY`.
Notifications request refresh outside rendering; refreshed values become detached
candidate snapshots, never in-place mutations of accepted bindings. Stable store
identity reuses the subscription and its notification target across evaluations.

The existing `_StoreSubscription` supplies explicit resource ownership.
Each private call-site binding retains a `_ResourceOwner`; the lifecycle-owned
collection owns that binding through the existing explicit context references.
The subscription completion's opening reference is separate and drains through
its existing completion path. Collection retirement releases discarded ownership
even when Python snapshots or exception tracebacks survive. This is not another
transaction manager, nor a lifecycle-library change.

Notification targets hold weak state links. Value bindings retain the underlying
resource, not its private ownership wrapper. Cleanup uses the existing guarded,
idempotent release path, drains independent failures, and quarantines reuse on a
cleanup error. Unknown publication retains ownership evidence rather than
claiming rollback succeeded.

## Coverage

`tests/data/lcm_integration/expression_subscription_lifecycle.py` and its authored
JSON baseline pin actual subscribe/get/unsubscribe order, notification refresh,
accepted snapshots during refresh, rollback, replacement with retained snapshots,
and removal. Run it through `tests/test_lcm_integration_characterization.py`.

`tests/test_runtime_context_state_lcm_expression_subscriptions.py` covers failed
reads with retained tracebacks, replaced-token fencing, effect rejection,
unsubscribe failure after publication, weak graph lifetime, and cleanup reentry.

Verification: full native suite **1035 passed, 2 unchanged host-ordering failures,
20 skipped**; affected Python-assembly tests **83 passed**, with the final expanded
same-identity subscription golden also rerun successfully on Python assembly.
No historical goldens, shared resource handlers, or lifecycle-library code changed.

## Remaining Work

The separate [synchronous-effect expression proof](PytoLifecyleIntegExpressionEffects.md)
now adds setup-after-publication and cleanup-before-replacement.
The separate [async-effect expression proof](PytoLifecyleIntegExpressionAsyncEffects.md)
also reuses this ownership path. Mount expressions remain excluded. Their admission and
delivery must be connected separately; this proof does not activate normal
rendering or remove legacy completion paths. The collection/plain-expression
checkpoint was committed and pushed as `9ed7372` before this work began.

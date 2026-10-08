# Render-Owned Expression Checkpoint

Status: implemented behind a separate private plain-value expression gate.
Standalone expressions and unactivated expression routing retain their existing
completion behavior. Expression subscriptions, effects, async effects, and mount
advertisements are not admitted by this checkpoint. Normal routing is unchanged.

## Ownership And Lowering

`RenderCallSitePassContext` inherits the migrated collection definitions and
declares their existing fields under `PASS_TX_KEY`. Its generated state uses the
root's transaction manager. The borrowed `CallSiteContextManager` can stage and
filter visitation, but cannot commit or roll back the enclosing render. There is
no independently completing expression transaction on this route.

The runtime-only `SlotExprExecution` bridge surrounds evaluation with a local
render scope. Local exit stages selection; only the outer completion owner can
publish or discard it. Exceptions in builders, providers, normalization, body,
or dirt assignment poison that attempt even when the caller catches them.
Original owner/token checks precede selection and follow user-controlled work.
A stale execution cannot write into a replacement transaction.

Plain results use the existing detached slot-value selection implementation.
The approved handler is selected once; external resource results are rejected
before binding, not silently routed through legacy resource handlers. Candidate
function identity, arguments, metadata, value binding, and invoke-state reset
live in a replacement call-site context, rather than mutating the accepted
selection. Repeated evaluation reads the visible candidate to preserve elision.
Existing independent invalidation state is not broadly redesigned here.

After successful evaluation, visitation filters the candidate collection without
publication. The private route bypasses evaluator binding commit/rollback and
the local collection commit. Omitted expression slots stage collection removal
before participant capture. Existing resource-free UI behavior is unchanged.

The completion adapter retains private collection ownership evidence until the
outer outcome is known. It then explicitly releases collections no longer held
by current state, draining independent cleanup and preserving failures. Unknown
publication retains evidence and remains quarantined; it does not invent an
undo or a retry. These are resource retirement calls, not manual field transfers.

Execution validates the exact borrowed collection manager and rejects recursive
evaluation of the same expression collection. Different expressions may still
join the same outer attempt. Standalone nested transaction exits retain both
current and pending collection ownership until actual completion.

## Evidence

Canonical fixture:
`tests/data/lcm_integration/slot_expr_selection_lifecycle.py`.
Its authored golden covers initial provisional selection, shared manager
identity, unchanged-call and candidate elision, replacement, parent failure,
caught expression failure, retry, omission, and transactional branch pruning.
A retained context snapshot observes retirement only after accepted removal.

Faults in `tests/test_runtime_context_state_lcm_expression_render.py` cover
resource exclusion before setup, caught argument-preparation failure, token
replacement during the source call, attempted local completion, foreign manager
substitution, and recursive evaluation. Collection faults also verify that a
nested standalone scope exit cannot retire its still-current collection.

Run from the repository root with either assembly backend:

```sh
env PYTHONDONTWRITEBYTECODE=1 ASTICHI_LOWER_ENGINE=native \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/test_runtime_context_state_lcm_expression_render.py \
  tests/test_lcm_integration_characterization.py::test_slot_expr_selection_lifecycle_golden
```

## Remaining Scope

The separate [subscription-expression proof](PytoLifecyleIntegExpressionSubscriptions.md)
now connects subscription selection, refresh, and cleanup to outer completion.
The [synchronous-effect proof](PytoLifecyleIntegExpressionEffects.md) now connects
effect selection, delivery, and retirement. The separate
[async-effect proof](PytoLifecyleIntegExpressionAsyncEffects.md) adds cancellation
and callback fencing. The separate [mount-expression proof](PytoLifecyleIntegExpressionMounts.md)
connects candidate validation and committed UI anchors. These resource-expression
proofs do not activate normal routing; do not bypass their completion paths by
simply removing the earlier gates' result-type admission checks.
Graph/registration migration, normal-route adoption, and deletion of legacy
expression completion remain subsequent work. Implementation review is deferred
to the aggregate integration review.

## Verification

- Full native suite: **1028 passed, 2 known host-ordering failures, 20 skipped**.
- Affected Python assembly collection/expression tests and integration goldens:
  **96 passed**.
- Focused native expression golden and fault cases: **7 passed**.

No compiler or lifecycle library changes, historical golden regeneration,
default-route activation, or resource-expression admission were required.

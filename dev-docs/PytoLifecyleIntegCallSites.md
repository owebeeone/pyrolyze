# Call-Site Collection Migration

Status: implemented collection-storage checkpoint; outer-render expression
admission is still pending. The operator approved removal of the unused
`CallSiteContextManager.replace_current()` direct-publication escape.

## Implemented Boundary

`CallSitePassContext` now uses the YIDL lifecycle decorator and transaction
manager. Its owned `contexts` collection publishes/discards through generated
facades; `visited` is a transient immutable set. No caller reads or writes
`current_record`, `working_record`, or their value dictionaries. The integrated
slot-expression state manager uses `get_visible()` and `iter_current()` instead
of reaching into collection internals.

`CallSiteContext` and its resource binding retain their existing explicit
reference-count policy. A private `_CallSiteCollection` bridges that policy to
lifecycle's Python-lifetime owned field. Each collection owns one explicit
reference per entry; copying a selection retains reused contexts, while newly
created contexts transfer their initial reference. Current and pending selections
are both considered when reselecting a context within one pass.

Publication is lifecycle's job, not a manual map transfer. The remaining domain
cleanup releases superseded candidate collections, replaced accepted collections,
or discarded candidates explicitly. Public context snapshots and exception
tracebacks cannot delay those releases. Cleanup detaches entries first, drains
independent releases, and preserves a lone exception or groups multiple failures.
An error retiring an old collection does not claim to undo published values.

Completion and retirement reject reentry. Staging and visitation fence the
original transaction after hashing keys, before writing generated fields.

## Remaining Expression Work

This replaces the legacy collection implementation for standalone expressions
and the existing integrated expression route. It deliberately preserves their
current local completion boundary for this checkpoint. The private outer-render
proof still does not admit slot-expression slots.

Next, connect render-owned expression collections to the outer completion owner
and replace evaluator binding commit/rollback dispatch with detached candidate
selection and the existing resource adapters. Standalone expressions still need
their own completion. Do not join managers while legacy handlers can accept or
mutate resources early, and do not claim this checkpoint completes that wiring.
Normal render routing is unchanged.

## Evidence

Existing call-site and expression tests cover selection, visitation pruning,
unchanged calls, shared binding ownership, replacement, rollback, removal,
teardown, and reuse. New narrow tests in
`tests/test_runtime_call_site_lifecycle.py` cover the generated boundary and
removed escape, retained failed snapshots, cleanup draining, retirement failure
after publication, reselecting a current context, and token replacement in key
hashing. Existing integration goldens are not regenerated.

Run from the repository root, using either assembly engine:

```sh
env PYTHONDONTWRITEBYTECODE=1 ASTICHI_LOWER_ENGINE=native \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/test_runtime_call_site_lifecycle.py \
  tests/test_runtime_call_site_context.py \
  tests/test_runtime_slot_expr.py \
  tests/test_runtime_context_state_lcm_slot_expr.py \
  tests/test_lcm_integration_characterization.py
```

## Generator Limitation

The decorated implementation class is named `CallSitePassContext`, without a
leading underscore: a leading underscore currently makes generated external
names collide with Python's class name-mangling rules. This is a runtime-private
implementation class, not a new author-facing API. Fixing generator naming is
separate work; this checkpoint changes no compiler or lifecycle library code.

## Verification

- Full native suite: **1020 passed, 2 known host-ordering failures, 20 skipped**.
- Affected Python assembly collection/expression tests and integration goldens:
  **88 passed**.
- Focused native collection and standalone expression tests: **62 passed**.

Implementation review remains deferred to the aggregate integration review.

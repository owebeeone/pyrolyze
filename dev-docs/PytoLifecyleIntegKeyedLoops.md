# Keyed Loop Lifecycle Checkpoint

## Scope

Extend the I6b proof through `_enable_keyed_loop_render`, admitting exact keyed
loop and loop-item facade classes. Normal routing remains unchanged. No new
transaction manager, public loop API, compiler syntax, or lifecycle-library
feature is introduced.

Loop items hold one managed `_LoopItemSelection` containing value, structured
dirty projection, and initialization state under the shared pass key. The
unactivated route uses `_legacy_selection` to preserve its existing behavior.
Keyed identity, nested key paths, and graph projection remain domain algorithms.
Inherited managed membership handles reorder/removal; the existing resource
adapters retire omitted subscriptions and discard failed candidates.

## Original Owner And Iterator Lifetime

Normalize values inside the original attempt and fence normalization, key
selection, hashing, graph insertion, and value comparison before candidate
writes. Captured execution rejects stale iterators and recursive iteration of
the same loop context. Registration now fences key-dependent dictionary updates
before assigning membership/cache replacements; no writes may migrate into a
replacement transaction accidentally.

The loop owns a local scope tracked directly by `_RenderAttempt`, not an
`attempt_scope` held across yields. Otherwise a suspended generator could retain
execution depth and postpone outer completion indefinitely. The outer owner can
abort an unexited loop and discard candidate values/resources. Later closing
that iterator must not clean up or join a newer attempt.

## Early Exit Policy

A compatibility probe of the unactivated decomposed route found that explicitly
closing a partially consumed iterator rolls back the local loop while the outer
render can succeed, retaining an empty loop on initial construction.

The operator clarified that `break` is normal control flow and approved an
explicit loop execution boundary. Pyrolyze AST lowering now wraps the generated
`for` in `keyed_loop_scope(...)`, while retaining each item's existing pass scope.
Normal exit, including `break`, accepts the visited prefix provisionally; body
exceptions make the shared attempt rollback-only. Iterator disposal is not an
independent commit/rollback signal.

The runtime bridge delegates to the lifecycle iterable's `pass_scope()` and is
a no-op for older iterable implementations, preserving unactivated behavior.
Direct runtime callers can use `with loop.pass_scope():` around iteration to
report body exceptions explicitly. Fully consumed direct iteration remains
supported; disposal is normal termination, but retaining an unscoped suspended
iterator past outer completion still violates the unexited-scope invariant.
An iterator bound to an explicit scope cannot resume after that scope exits.

No ad hoc field snapshots/savepoints, Astichi changes, or YIDL changes are needed.
Normal-route activation and aggregate implementation review remain pending.

## Coverage

`tests/data/lcm_integration/keyed_loop_lifecycle.py` and its authored JSON baseline
pin item identity, updates, dirty projection, reorder, outer rollback/retry,
subscription retirement, nested key paths, omission, and actual compiled
`@pyrolyze`/`keyed` source through a component invocation.

Focused faults cover caught duplicates/normalization failures, failing keys and
hashes, transaction replacement during key selection/value comparison/membership
insertion, recursive iteration, stale iterators, and provisional early-exit
behavior. The canonical compiled example also pins `break` prefix publication.
Historical runtime baselines are not regenerated. Two compiler source goldens
(`phase4_nested_grid.py` and `phase5_method_structures.py`) are regenerated with
the matching Python 3.14 harness to expose the new execution wrapper. Aggregate review remains
deferred, not independently accepted.

## Verification

The native focused and characterization run passed 125 tests; the affected
Python-backend run passed 24. The full native run passed 1,095 tests, with 20
skips and the same two known host sibling-ordering failures. No historical
baselines changed, and `git diff --check` passed.

After the approved correction, native keyed-loop, characterization, compiler
structural, and compiler golden checks passed 82 tests. The focused ownership
faults also passed 14 tests on Python 3.14's Python assembly backend, including
started and unstarted expired iterators. The hash-insertion fault is armed by
operation rather than hash-call count because tuple caching varies by interpreter.
Changes remain uncommitted and do not authorize normal-route activation.

Final affected Python-backend checks passed 15 tests. The final full native
regression passed 1,098 tests, with 20 skips and only the same two known generic
fault-simulation/PySide6 host sibling-ordering failures. `git diff --check`
passed. This checkpoint is implemented and tested, with aggregate review still
deferred rather than independently accepted.

## Next

Continue adoption-audit B:
recognized compiled/native/directive container classification before slot
construction. Opaque external context-manager semantics remain separate.

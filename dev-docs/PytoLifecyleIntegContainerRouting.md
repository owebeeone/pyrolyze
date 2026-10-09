# Lifecycle Scope Container Routing

Status: implemented behind `_enable_container_render`, uncommitted. Normal-route
activation and aggregate implementation review remain pending. This completes
adoption-audit B's bounded dispatch work, not adoption of the entire runtime.

## Scope

Existing authored `with` calls already lower to `container_call(...)` and a
runtime handle. No compiler, Astichi, YIDL, or lifecycle-library changes are
required for this checkpoint.

The private gate now resolves the callable and classifies it before constructing
a slot. Compiled components and native UI helpers select `ContainerSlotContext`;
helpers accepting `ContainerCallRuntimeContext` select `DirectiveSlotContext`.
The latter must return the runtime's directive scope, as `mount(...)` does.
Unsupported opaque helpers are rejected before slot construction or invocation.
An annotation alone does not authorize arbitrary external context-manager entry.

The previous dispatcher constructed a generic container before recognizing a
directive and then tried to construct a second slot type at the same identity.
Its inherited admission guard also rejected supported compiler-backed calls.
The new route resolves once, selects the existing handle once, and binds it to
the correct slot without changing older gates or unactivated compatibility paths.

## Ownership And Completion

`container_render.py` owns the bounded dispatch and original-owner guard. A small
site carrier preserves slot-path metadata during resolution before a facade
exists. Checks fence resolution, classification, construction, and entry/exit
against the original render transaction.

Returned handles cannot enter a later render attempt. Their guarded execution
scope reports caught construction/evaluation/body failures to the shared owner,
while existing handles retain native-root validation, compiled receiver/argument
binding, and directive projection. Successful local exit keeps the result
provisional until outer completion. Resource acceptance/discard reuses the
existing subscription/effect/mount completion machinery.

For mount helpers, the returned host is validated before calling `__enter__`.
Arbitrary external `__enter__`/`__exit__` actions remain outside the contract;
there is no claim that lifecycle can undo arbitrary user side effects.

## Coverage

`tests/data/lcm_integration/container_routing_lifecycle.py` compiles authored
source nesting a compiled frame, a dynamically supplied native container, and
`mount(...)`. Its JSON baseline pins provisional versus accepted UI, nested
directive projection, rollback/retry, replacement/removal, and actual subscription
cleanup. Failed candidates unsubscribe without retiring accepted subscriptions.

Focused faults cover opaque rejection before construction, annotated external
host rejection before entry, caught native/compiled evaluation errors with their
original causes, zero/multiple native roots, resolution/entry token replacement,
and stale handles. Historical baselines and compiler source goldens are unchanged.

## Verification

The earlier characterization/fault run passed 40 tests, and the expanded native
scope/loop/compiler compatibility run passed 39. Final container faults and the
canonical fixture passed 10 tests on each of the Python 3.12 and 3.14 Python
assembly backends. Full native regression: 1,108 passed, 20 skipped, and only the
same two known generic fault-simulation/PySide6 sibling-ordering failures.
`git diff --check` passed. Aggregate review remains deferred, not independently
accepted.

## Next

Adoption-audit C: common dirty/visitation pass-state cleanup. Remove redundant
snapshots only where lifecycle preserves failure retry and independent
notifications. Aggregate review precedes default activation and legacy deletion.

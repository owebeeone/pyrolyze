# Mount Advertisement Completion Checkpoint

Status: implemented behind a separate private proof gate. Normal rendering and
shared legacy handlers remain unchanged. This continues the slot-call resource
proofs; it does not yet migrate slot-expression call-site collections or enable
opaque host context managers, structural mount directives, or keyed loops.

## Existing Behavior And Lowering

Unlike subscriptions/effects, mount advertisements are immutable graph metadata,
not external resources. The host's existing publication method constructs an
advertisement with source, surface, and mount owner provenance; it does not alter
the published surface. A private detached binding retains that candidate value
alongside its request. No refcount wrapper or finalizer is required.

Lifecycle stores the selected binding in the existing managed invocation record.
Its managed UI value contains the advertisement at its child anchor. Removal or
replacement publishes/discards those values normally, rather than imperatively
mutating an advertisement cache during candidate evaluation. The proof's public
surface is derived from committed graph membership and committed selections;
the legacy surface cache and its withdrawal/rebuild machinery remain untouched.
There is no external mount cleanup or notification API to invent here: existing
consumers observe the accepted advertisement through the UI and debug surface.

The separate gate admits exact native-container slots and slot-call mount results.
Opaque container factories/context managers are rejected before invoking them.
Native emission remains domain code; this is not enabling arbitrary host-side
enter/exit actions or all remaining invocation paths.

Native-container storage is declared through lifecycle: the temporary
`_expects_native_root` flag is local scratch, while `_committed_native_root` is
managed under the existing pass key. Local success stages the flag, but a failed
outer render discards it along with the candidate UI. Container construction
remains complete before graph attachment and retains the existing shared manager.

## Completion Boundary

1. Resolve the candidate advertisement through the existing host provenance
   checks. Root/non-native owners remain invalid. Fence original render ownership
   before and after resolution, just as for other selected bindings.
2. After local scopes exit, collect candidate advertisements from reachable graph
   state, separately per render boundary. Reuse the existing duplicate-key and
   duplicate-default surface validation before any lifecycle publication.
3. Close completion to render reentry before invoking key equality. Recheck the
   original transaction identity after validation; replacement authority cannot
   receive candidate writes or authorize publication.
4. A validation failure poisons and discards the outer attempt. Report the actual
   validation error (not merely a successful rollback), preserve accepted mounts,
   and do not deliver provisional effects. Clean discard permits retry.
5. Full outer publication exposes the managed UI and advertisement selections.
   Omission, explicit removal, and replacement require no second surface store or
   transfer loop. Partial/uncertain outcomes retain the existing quarantine rule.

Native-container helper error handling also records the original cause on the
private completion owner before rollback. The unactivated helper sequence remains
unchanged; a caught helper failure must not become an anonymous abort placeholder.

## Evidence

Canonical fixture: `tests/data/lcm_integration/mount_selection_lifecycle.py`.
Its authored golden covers failed initial publication, local success still being
provisional, native-root flag publication/discard, owner provenance, UI anchors,
failed/successful replacement and removal, retained immutable snapshots,
superseded requests, and container omission.

Narrow faults in `tests/test_runtime_context_state_lcm_mounts.py` cover duplicate
keys/defaults with no provisional effect delivery, retry, invalid root ownership,
key-equality token replacement, validation reentry, opaque factory exclusion, and
original native-helper failure identity.

Run from the repository root with either assembly engine:

```sh
env PYTHONDONTWRITEBYTECODE=1 ASTICHI_LOWER_ENGINE=native \
  PYTHONPATH=src:../yidl-lifecycle/src:../yidl/src:../astichi/src \
  ../.venv/bin/python -m pytest -p no:cacheprovider -q \
  tests/test_runtime_context_state_lcm_mounts.py \
  tests/test_lcm_integration_characterization.py::test_mount_selection_lifecycle_golden
```

No existing golden, compiler library, or lifecycle library change is required.
Remaining work includes call-site/slot-expression migration, other graph and
registration state, normal-route adoption, and deletion of compatibility holders.

## Verification

- Full native suite: **1015 passed, 2 failed, 20 skipped**. The failures are the
  existing generic fault-simulation and PySide6 mixed-child placement cases.
- Affected Python assembly and legacy mount/resource tests: **51 passed**.
- Focused native mount golden and fault tests: **8 passed**.

Implementation review remains deferred to the aggregate integration review.

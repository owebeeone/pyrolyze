# TODOs

Current known unimplemented or partially implemented work in `py-rolyze`,
grouped by milestone priority.

## Milestone: Initial Release (PyPI)

### Release Blockers

- ~~Fix callable-annotation cache writes for non-attribute callables (for example builtins).~~ Resolved on 2026-03-20.
  - Implemented safe callable cache read/write fallback when direct `setattr(...)` is unsupported.
  - Added signature-introspection fallback for `inspect.signature(...)` `TypeError`/`ValueError` paths.
  - Covered by regression tests for `call_plain(...)`, `leaf_call(...)`, and `container_call(...)`.

- Fix `AppContextStore` cache miss detection for `None` values.
  - `AppContextStore.get(...)` currently uses `dict.get(...)` and treats `None` as missing.
  - Factories returning `None` are re-run on every access and can duplicate close-callback execution order entries.
  - Use an explicit sentinel for cache misses so `None` can be a valid cached value.

- Implement compiler-generated `call_site_id` emission for every lexical UI emission site.
  - The authoring guide specifies compiler-generated `call_site_id` identity for reconciliation.
  - The runtime UI normalization can consume `call_site_id`.
  - The current compiler does not stamp emitted sites with `call_site_id`.
  - This is core correctness work for deterministic reconciliation and stable identity.

- Implement explicit `emit_component(...)` source-form lowering.
  - The authoring guide and design docs describe `emit_component(...)` as the explicit dynamic component emission form.
  - The current compiler/runtime source surface supports direct `ComponentRef[...]` local calls but does not provide the documented `emit_component(...)` path.
  - This should either be implemented or removed from the documented public source model before release.

- Decide and align the `use_external_store(...)` surface.
  - The authoring guide still presents `use_external_store(...)` as the primary third-party subscription hook.
  - `PyrolyzeContextManagement_V2.md` says to remove `use_external_store(...)` from the primary design.
  - The runtime has external-store machinery, but there is no corresponding public helper in `py-rolyze`.
  - This needs either implementation or a docs/API cleanup before release.

- Enforce the documented rejection of plain bare non-PyRolyze expression calls in render scope.
  - The authoring guide says bare render-scope statements must be native emitters, component calls, or other PyRolyze-recognized forms.
  - The current rewrite still leaves unknown expression calls as plain Python expression statements.
  - The compiler should reject invalid authoring forms instead of silently accepting them.

### Strongly Recommended Before Release

- Invalidate transformer-fingerprint hash cache when compiler files change in-process.
  - `active_transformer_fingerprint(...)` depends on `_transform_hash_for_selected_kernel(...)`, which is currently `lru_cache`d by version only.
  - In a long-lived process, editing compiler/kernel source can leave the cached transformer hash stale, so persistent artifact cache keys do not change.
  - Verified behavior: after a compiler source edit, import-hook compile count stayed unchanged until manually calling `_transform_hash_for_selected_kernel.cache_clear()`.
  - Add change detection or explicit cache-bust mechanics so compiler edits reliably invalidate artifact cache keys.

- Remove quadratic replacement-path work in `reconcile_owner(...)`.
  - The detach pass currently checks replacement membership with a nested `any(...)` over `replaced_nodes`.
  - Large replacement-heavy updates can degrade toward O(n^2) and cause visible UI stalls.
  - Replace linear membership checks with set-based tracking.

- Reduce quadratic child placement work in reconciliation/backends.
  - `reconcile_owner(...)` currently calls `place_child(...)` for every node every pass.
  - Backend placement helpers perform linear index scans (`_layout_index(...)`, repeated `pack_slaves()` scans), which compounds into O(n^2) behavior on large trees.
  - Skip unchanged placement where possible and use position tracking to avoid repeated linear scans.

- Improve invalidation scheduler data structures for bursty updates.
  - `_InvalidationScheduler` currently relies on list operations such as `pop(0)` and repeated full-list scans/filtering in `_merge_boundary(...)`.
  - Under heavy invalidation bursts this can add avoidable quadratic overhead.
  - Use queue/set-oriented structures to keep enqueue/dequeue and membership checks near O(1).

- Reduce invalidation fan-out cost in wide trees.
  - `_queue_invalidation_from(...)` walks ancestors and eagerly marks all children dirty at each level.
  - Repeated event-driven invalidations can become expensive and amplify render latency.
  - Introduce more targeted dirtiness propagation (for example generation/version marks) instead of broad sibling marking.

- Add focused performance regression tests for large-tree reconciliation.
  - Current tests validate correctness but do not enforce scaling expectations for reorder/replace-heavy updates.
  - Add benchmark-style guard tests for large owner regions and event-driven update storms to catch UX-freeze regressions early.

- Enforce UI-thread checks for the Tkinter backend.
  - `reconcile_owner(...)` expects backend thread assertions.
  - `_TkBackend.assert_ui_thread(...)` is currently a no-op.
  - Add an explicit thread-identity guard so off-thread UI reconciliation fails fast.

- Replace or harden persistent cache `pickle` deserialization.
  - `PersistentArtifactCache` currently uses `pickle.load(...)` on files from a configurable cache directory.
  - This creates a code-execution risk if cache files are tampered with.
  - Prefer a safe serialization format or enforce strict trust-boundary protections.

- Lower `use_effect_async(...)` and its async task lifecycle.
  - The authoring guide documents `use_effect_async(...)`.
  - The design docs describe async completion posting invalidation through the scheduler.
  - The public/runtime implementation does not currently expose this hook.
  - If this is not in scope for the first release, remove it from the documented API for now.

- Lower nested `@pyrolyse` definitions directly inside render scope.
  - The authoring guide describes local nested `@pyrolyse` lowering through private component ids with synthetic props.
  - The current structural rewrite still rejects nested component definitions.

- Add the next integrated graph test scenarios from [AdvancedTestingPlan.md](../docs/AdvancedTestingPlan.md).
  - `integrated_use_effect_lifecycle`
  - `integrated_use_grip_store_refresh`
  - `integrated_nested_grid_reorder`
  - These are the highest-value missing confidence tests for rerender correctness before release.

- Add the remaining helper assertions recommended by [AdvancedTestingPlan.md](../docs/AdvancedTestingPlan.md).
  - Keep small integrated-test helpers such as `assert_only_ui_changed(...)`, `assert_no_unexpected_context_churn(...)`, and `assert_ui_elements_present(...)` in the integrated graph test module so scenario expectations stay readable and deterministic.

### Can Defer Until After Initial Release

- Split oversized mixed-responsibility modules into smaller units.
  - `runtime/context.py` currently combines slot lifecycle, scheduling, binding semantics, event dispatch behavior, and committed-UI propagation.
  - Backend modules (especially PySide6) also mix reconciler bindings with legacy widget-rendering helpers.
  - Extract focused submodules to improve separation of concerns, testability, and maintenance cost.

- Support multiple independently keyed `use_state()` calls inside a single custom plain-call helper runtime context.
  - `use_state()` currently stores under fixed local keys inside one `PlainCallRuntimeContext`.
  - Custom helper composition currently has to use a tuple state or another manual aggregation strategy.

- Lower async `@pyrolyse` functions.

- Lower the remaining unsupported render-scope control-flow forms:
  - `async for`
  - `while`
  - `async with`
  - `try`
  - `match`

- Lower `for ... else` in render scope.

- Lower starred-keyword component calls.

- Lift Python-version-independent compiler helpers out of the versioned kernel package.
  - The `compiler/kernels/v3_14` package currently contains a mix of Python-AST-version-specific logic and general compiler helpers.
  - Version-independent analysis, planning, and lowering utilities should live in shared compiler modules so future kernel versions do not duplicate non-AST-specific behavior.

- Replace the handwritten frozen semantic node registry with emitter-derived descriptor contracts.
  - The UI node binding design expects semantic node descriptors to come from emitter signatures and annotations.
  - The current runtime still uses the handwritten `FROZEN_V1_REGISTRY`.
  - This is a design-cleanliness issue more than a release blocker if the documented node set stays narrow.

- Add explicit backend-swap handling in owner reconciliation.
  - The reconciliation design calls for a full owner remount when the backend adapter changes.
  - The current reconciler does not track backend identity or force a remount on backend swap.
  - This is not critical if backend selection happens only at application startup.

- Add the remaining lower-priority integrated graph test scenarios from [AdvancedTestingPlan.md](../docs/AdvancedTestingPlan.md).
  - `integrated_conditional_branch_swap`
  - `integrated_component_method_dispatch`
  - `integrated_call_native_mixed_tree`
  - `integrated_large_composite_dashboard`

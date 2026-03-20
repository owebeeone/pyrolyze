# TODOs

Current known unimplemented or partially implemented work in `py-rolyze`,
grouped by milestone priority.

## Milestone: Initial Release (PyPI)

### Release Blockers

- [P1] ~~Fix callable-annotation cache writes for non-attribute callables (for example builtins).~~ Resolved on 2026-03-20.
  - Implemented safe callable cache read/write fallback when direct `setattr(...)` is unsupported.
  - Added signature-introspection fallback for `inspect.signature(...)` `TypeError`/`ValueError` paths.
  - Covered by regression tests for `call_plain(...)`, `leaf_call(...)`, and `container_call(...)`.

- [P1] ~~Fix `AppContextStore` cache miss detection for `None` values.~~ Resolved on 2026-03-20.
  - `AppContextStore.get(...)` now uses an explicit sentinel for cache misses, so `None` is a valid cached value.
  - Factories returning `None` are no longer re-run on repeated access.
  - Close-callback order entries no longer duplicate when cached values are `None`.

- [P1] ~~Implement compiler-generated `call_site_id` emission for every lexical UI emission site.~~ Resolved on 2026-03-20.
  - The v3.14 compiler now stamps lowered `call_native(...)` emissions with `__pyr_call_site_id`.
  - Runtime native emission metadata now carries both `call_site_id` and slot identity/slot-path lineage for instance disambiguation.
  - UI normalization/reconciliation now consumes this metadata for deterministic, stable node identity.

- [P1] Implement explicit `emit_component(...)` source-form lowering.
  - The authoring guide and design docs describe `emit_component(...)` as the explicit dynamic component emission form.
  - The current compiler/runtime source surface supports direct `ComponentRef[...]` local calls but does not provide the documented `emit_component(...)` path.
  - This should either be implemented or removed from the documented public source model before release.

- [P1] Decide and align the `use_external_store(...)` surface.
  - The authoring guide still presents `use_external_store(...)` as the primary third-party subscription hook.
  - `PyrolyzeContextManagement_V2.md` says to remove `use_external_store(...)` from the primary design.
  - The runtime has external-store machinery, but there is no corresponding public helper in `py-rolyze`.
  - This needs either implementation or a docs/API cleanup before release.

### Strongly Recommended Before Release

- [P2] ~~Invalidate transformer-fingerprint hash cache when compiler files change in-process.~~ Resolved on 2026-03-20.
  - `active_transformer_fingerprint(...)` now derives a source-state token from fingerprint-file metadata and keys transform-hash caching by `(version, source_state_token)`.
  - In-process compiler/kernel edits and file add/remove now force transform-hash recomputation without manual cache clears.
  - Added explicit `invalidate_transformer_fingerprint_cache()` and regression tests for edit detection, file-set changes, and unchanged-state cache hits.

- [P2] ~~Remove quadratic replacement-path work in `reconcile_owner(...)`.~~ Resolved on 2026-03-20.
  - Replaced replacement tracking list scans with set-based membership (`id(old) in replaced_node_ids`) in the detach pass.
  - This removes the replacement-heavy O(n^2) detach predicate path.
  - Added reconciliation regression coverage for replacement-heavy updates and detach/dispose behavior.

- [P2] ~~Reduce quadratic child placement work in reconciliation/backends.~~ Resolved on 2026-03-20.
  - Reconciliation now uses minimal placement planning and skips unchanged `place_child(...)` operations.
  - PySide6 layout placement now tracks widget order/index with cached state plus resync fallback, reducing repeated `_layout_index(...)` scans.
  - Tkinter pack placement now tracks packed order/index and avoids repeated `pack_slaves()` scans in hot placement paths.

- [P2] Improve invalidation scheduler data structures for bursty updates.
  - `_InvalidationScheduler` currently relies on list operations such as `pop(0)` and repeated full-list scans/filtering in `_merge_boundary(...)`.
  - Under heavy invalidation bursts this can add avoidable quadratic overhead.
  - Use queue/set-oriented structures to keep enqueue/dequeue and membership checks near O(1).

- [P2] Reduce invalidation fan-out cost in wide trees.
  - `_queue_invalidation_from(...)` walks ancestors and eagerly marks all children dirty at each level.
  - Repeated event-driven invalidations can become expensive and amplify render latency.
  - Introduce more targeted dirtiness propagation (for example generation/version marks) instead of broad sibling marking.

- [P2] Add focused performance regression tests for large-tree reconciliation.
  - Current tests validate correctness but do not enforce scaling expectations for reorder/replace-heavy updates.
  - Add benchmark-style guard tests for large owner regions and event-driven update storms to catch UX-freeze regressions early.

- [P2] Enforce UI-thread checks for the Tkinter backend.
  - `reconcile_owner(...)` expects backend thread assertions.
  - `_TkBackend.assert_ui_thread(...)` is currently a no-op.
  - Add an explicit thread-identity guard so off-thread UI reconciliation fails fast.

- [P2] Harden Tkinter availability probing and test gating for transient Tcl init failures.
  - Tk tests currently use `@pytest.mark.skipif(not tkinter_available(), ...)`, which is evaluated at collection time.
  - `tkinter_available()` can report available, but later `tk.Tk()` calls may still fail with `_tkinter.TclError` (for example intermittent `init.tcl` lookup/read failures), producing flaky test outcomes.
  - Make availability checks and test skipping resilient at runtime (fixture/helper around actual root creation), and avoid stale availability cache decisions.

- [P2] Replace or harden persistent cache `pickle` deserialization.
  - `PersistentArtifactCache` currently uses `pickle.load(...)` on files from a configurable cache directory.
  - This creates a code-execution risk if cache files are tampered with.
  - Prefer a safe serialization format or enforce strict trust-boundary protections.

- [P2] Lower `use_effect_async(...)` and its async task lifecycle.
  - The authoring guide documents `use_effect_async(...)`.
  - The design docs describe async completion posting invalidation through the scheduler.
  - The public/runtime implementation does not currently expose this hook.
  - If this is not in scope for the first release, remove it from the documented API for now.

- [P2] Lower nested `@pyrolyse` definitions directly inside render scope.
  - The authoring guide describes local nested `@pyrolyse` lowering through private component ids with synthetic props.
  - The current structural rewrite still rejects nested component definitions.

- [P2] Add the next integrated graph test scenarios from [AdvancedTestingPlan.md](../docs/AdvancedTestingPlan.md).
  - `integrated_use_effect_lifecycle`
  - `integrated_use_grip_store_refresh`
  - `integrated_nested_grid_reorder`
  - These are the highest-value missing confidence tests for rerender correctness before release.

- [P2] Add the remaining helper assertions recommended by [AdvancedTestingPlan.md](../docs/AdvancedTestingPlan.md).
  - Keep small integrated-test helpers such as `assert_only_ui_changed(...)`, `assert_no_unexpected_context_churn(...)`, and `assert_ui_elements_present(...)` in the integrated graph test module so scenario expectations stay readable and deterministic.

### Can Defer Until After Initial Release

- [P3] Split oversized mixed-responsibility modules into smaller units.
  - `runtime/context.py` currently combines slot lifecycle, scheduling, binding semantics, event dispatch behavior, and committed-UI propagation.
  - Backend modules (especially PySide6) also mix reconciler bindings with legacy widget-rendering helpers.
  - Extract focused submodules to improve separation of concerns, testability, and maintenance cost.

- [P3] Support multiple independently keyed `use_state()` calls inside a single custom plain-call helper runtime context.
  - `use_state()` currently stores under fixed local keys inside one `PlainCallRuntimeContext`.
  - Custom helper composition currently has to use a tuple state or another manual aggregation strategy.

- [P3] Lower async `@pyrolyse` functions.

- [P3] Lower the remaining unsupported render-scope control-flow forms:
  - `async for`
  - `while`
  - `async with`
  - `try`
  - `match`

- [P3] Lower `for ... else` in render scope.

- [P3] Lower starred-keyword component calls.

- [P3] Lift Python-version-independent compiler helpers out of the versioned kernel package.
  - The `compiler/kernels/v3_14` package currently contains a mix of Python-AST-version-specific logic and general compiler helpers.
  - Version-independent analysis, planning, and lowering utilities should live in shared compiler modules so future kernel versions do not duplicate non-AST-specific behavior.

- [P3] Replace the handwritten frozen semantic node registry with emitter-derived descriptor contracts.
  - The UI node binding design expects semantic node descriptors to come from emitter signatures and annotations.
  - The current runtime still uses the handwritten `FROZEN_V1_REGISTRY`.
  - This is a design-cleanliness issue more than a release blocker if the documented node set stays narrow.

- [P3] ~~Add explicit backend-swap handling in owner reconciliation.~~ Resolved on 2026-03-20.
  - `UiOwnerCommitState` now tracks `last_backend_identity` and `reconcile_owner(...)` computes semantic backend identity (`type + backend_id`).
  - On backend identity change, reconciliation now performs a full owner clear/remount rather than attempting incremental reuse.
  - Added tests covering swap-remount behavior and non-remount behavior for same-identity backend instances.

- [P3] Add the remaining lower-priority integrated graph test scenarios from [AdvancedTestingPlan.md](../docs/AdvancedTestingPlan.md).
  - `integrated_conditional_branch_swap`
  - `integrated_component_method_dispatch`
  - `integrated_call_native_mixed_tree`
  - `integrated_large_composite_dashboard`

### Not Recommended Before Release

- [P5] Enforce the documented rejection of plain bare non-PyRolyze expression calls in render scope.
  - The authoring guide says bare render-scope statements must be native emitters, component calls, or other PyRolyze-recognized forms.
  - The current rewrite still leaves unknown expression calls as plain Python expression statements.
  - The compiler should reject invalid authoring forms instead of silently accepting them.

## Milestone: Studio App Enablement (PyRolyze + PySide6)

### Development Prerequisites (Must-Have)

- [P1] Add semantic node support for Studio layout primitives.
  - Required kinds: `splitter` (horizontal/vertical), `tabs`, `tab_page`, `toolbar_row`, `text_area`, and a generic `container` node.
  - Implement end-to-end in descriptor registry normalization, reconciliation, and PySide6 bindings.
  - Without these, the Studio explorer/editor/panel shell cannot be expressed in PyRolyze source.

- [P1] ~~Define and adopt a standard `UIElement` component helper surface for app code.~~ Resolved on 2026-03-20.
  - Added canonical helper component refs in `src/pyrolyze/ui/elements.py` and re-exported via `pyrolyze.ui`.
  - Refactored `examples/grid_app.py` and `Studio/ui/studio_root.py` to consume the shared helper surface.
  - Replaced duplicated Studio helper definitions with a compatibility re-export module and added focused helper-surface regression tests.

- [P1] Add a model-backed tree node contract for explorer/hierarchy views.
  - Introduce a semantic node/binding path for `QTreeView` + `QFileSystemModel` style usage with root-path updates.
  - Support selection and activation events with stable row identity.
  - The existing node set cannot represent file explorer or inspector hierarchy views.

- [P1] Add explicit host-shell interop for `QMainWindow` surfaces.
  - Define a stable mount-point contract so a native shell can host one or more PyRolyze-rendered subtrees.
  - Add a narrow action bridge for menu/status/title-bar commands to dispatch into component state/actions.
  - Studio requires frameless window/native chrome behavior that should stay host-managed while content is declarative.

- [P1] Add a reusable custom-widget bridge for advanced native controls.
  - Provide a supported pattern for host-owned/custom widgets (for example screenshot canvas and highlight overlay helpers) to participate in PyRolyze-driven flows.
  - Define lifecycle ownership rules (create/update/dispose) so custom widgets do not leak or remount unexpectedly.

- [P1] Add tab lifecycle semantics with stable keyed identity.
  - Ensure add/remove/reorder/select tab operations preserve backing widgets when identity is unchanged.
  - Add explicit tests for reorder-heavy tab updates to avoid accidental remounts.
  - Studio editor/panel UX depends on preserving tab-local state.

- [P1] Add async-to-UI event boundary guidance and helper API for PySide6 apps.
  - Provide a first-class pattern for posting async completion into invalidation/reconciliation without off-thread UI access.
  - Studio flow includes async operations and needs a supported runtime path that avoids ad-hoc loop pumping in app code.

### Required Verification Before Building Studio Features

- [P1] Add TDD coverage for each new Studio-required semantic node.
  - Red/green tests in normalization, reconciliation, and PySide6 wrapper suites must land before feature usage.
  - Include behavior tests for visibility toggles, property updates, and event callback wiring.

- [P1] Add focused reconciliation performance guards for Studio-shaped trees.
  - Add large-tree tests for explorer/hierarchy updates and reorder-heavy tab/splitter updates.
  - Use these as a regression gate against UI-stall patterns during Studio migration.

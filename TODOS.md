# TODOs

Current known unimplemented or partially implemented work in `py-rolyze`,
grouped by milestone priority.

## Milestone: Initial Release (PyPI)

### Release Blockers

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

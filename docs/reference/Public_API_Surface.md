# Public API Surface

## Source-facing API

Defined in `src/pyrolyze/api.py` (see `__all__` for the authoritative list):

- `pyrolyze`
- `reactive_component` (alias of `pyrolyze`)
- `pyrolyze_slotted`
- `pyrolyze_component_ref`
- `call_native`
- `keyed`
- `KeyedIterable`
- `mount`
- `UIElement`
- `MountDirective`
- `MountSelector`
- `SlotSelector`
- `ComponentMetadata`
- `ComponentRef[...]`
- `PyrolyzeHandler[...]` (event-boundary callable annotation)
- `PyrolyteHandler` (compatibility alias for the pre-release spelling; prefer
  `PyrolyzeHandler` in new code)
- `PyrolyzeEventParam`, `PyrolyzeSlottedParam`
- `SlotCallable[...]`
- `default`, `no_emit`
- `validate_mount_selectors`
- `CallFromNonPyrolyzeContext`
- `ui_interface` (binds `UiInterface` onto a library class)
- `Label` (small `UIElement` helper)
- `MISSING`, `MissingType` (sentinel for generated UI libraries)

Hooks re-exported from `src/pyrolyze/hooks.py`:

- `use_state`
- `use_effect`
- `use_mount`
- `use_unmount`
- `use_grip`

## Compiler-facing public API

Defined in `src/pyrolyze/compiler/__init__.py`:

- `analyze_source`
- `lower_plan_to_ast`
- `emit_transformed_source`
- `build_debug_artifacts_for_source`
- `load_transformed_namespace`
- `compile_source`
- `compile_source_with_env`
- `write_debug_artifacts`
- `kernel_loader`
- artifact and plan types: `CompileArtifact`, `CompileMetadata`, `CompileWarning`,
  `ComponentFactory`, `ComponentTransformPlan`, `DebugArtifacts`, `HookRecord`,
  `ModuleTransformPlan`, `TransformFlags`
- `PyRolyzeCompileError` (from diagnostics)

## Runtime-facing public API

Defined in `src/pyrolyze/runtime/__init__.py` (large surface; this is a summary):

- Context graph: `RenderContext`, `dirtyof`, `PlainCallRuntimeContext`,
  `PlainCallResult`, `CompValue`, `DirtyStateContext`, `ExternalStoreRef`,
  `ExternalStoreBinding`, `ModuleId`, `ModuleRegistry`, `module_registry`,
  `SlotId`, slot context types (`PlainCallSlotContext`, `ContainerSlotContext`,
  `KeyedLoopSlotContext`, `ComponentCallSlotContext`, …), `UseEffectRequest`,
  `UseEffectAsyncRequest`, `UseEffectBinding`, `UseEffectAsyncBinding`, …
- App context: `AppContextKey`, `AppContextStore`, `GENERATION_TRACKER_KEY`,
  `GenerationTracker`
- Trace: `TraceChannel`, `TraceRecord`, `TraceSink`, `configure_trace`,
  `configure_trace_from_env`, `disable_trace`, `enable_trace`, `emit_trace`,
  `reset_trace`, `trace_enabled`
- Reconciler / UI nodes: `UiBackendAdapter`, `UiNode`, `UiNodeBinding`,
  `UiNodeSpec`, `UiOwnerCommitState`, `FROZEN_V1_REGISTRY`, `mount_subtree`,
  `reconcile_owner`, `reconcile_children`, `normalize_ui_inputs`,
  `normalize_ui_elements`, and related helpers (see `runtime/__init__.py` for
  the full `__all__`)
